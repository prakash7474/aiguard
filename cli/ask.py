import os
import sys
import builtins
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

console = Console()

_original_open = builtins.open
_interceptor_active = False
_accessed_files = []
_blocked_files = []
_policy_cache = {}


class _FileAccessGuard:
    """
    Intercepts Python's open() to track every file read by the AI agent.
    Works on Windows where watchdog cannot detect reads.
    """

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.files_read = []
        self.files_blocked = []
        self.files_written = []
        self.start_time = time.time()

    def is_within_project(self, filepath: str) -> bool:
        try:
            fp = Path(filepath).resolve()
            return str(fp).startswith(str(self.project_path))
        except Exception:
            return False

    def is_sensitive(self, filepath: str) -> bool:
        from security.policy_manager import PolicyManager
        pm = PolicyManager()
        allowed, reason = pm.check_access(filepath)
        return not allowed

    def activate(self):
        global _interceptor_active
        _interceptor_active = True

        guard = self

        def _guarded_open(file, mode='r', *args, **kwargs):
            filepath = str(file)

            is_read = ('r' in mode and 'w' not in mode and 'a' not in mode) or \
                      ('+' in mode and 'w' not in mode and 'a' not in mode)
            is_write = 'w' in mode or 'a' in mode or ('x' in mode)

            if is_read and guard.is_within_project(filepath):
                if guard.is_sensitive(filepath):
                    guard.files_blocked.append(filepath)
                    console.print(f"[bold red]BLOCKED[/bold red] {filepath} [dim](sensitive file)[/dim]")
                    raise PermissionError(
                        f"AI Guard blocked access to sensitive file: {filepath}\n"
                        f"Tip: Use 'aiguard scan file {filepath}' to check why"
                    )
                else:
                    guard.files_read.append(filepath)
                    console.print(f"[yellow]READ[/yellow] {filepath}")

            elif is_write and guard.is_within_project(filepath):
                guard.files_written.append(filepath)
                console.print(f"[red]WRITE[/red] {filepath}")

            return _original_open(file, mode, *args, **kwargs)

        builtins.open = _guarded_open

    def deactivate(self):
        global _interceptor_active
        builtins.open = _original_open
        _interceptor_active = False

    def get_summary(self) -> dict:
        elapsed = time.time() - self.start_time
        return {
            'files_read': self.files_read,
            'files_blocked': self.files_blocked,
            'files_written': self.files_written,
            'elapsed_seconds': round(elapsed, 1),
            'total_accessed': len(self.files_read) + len(self.files_written),
            'total_blocked': len(self.files_blocked)
        }


def run_guarded(prompt: str, project_path: str = ".", model: str = "llama3.2:3b"):
    """Ask AI (Ollama) with file access monitoring"""

    guard = _FileAccessGuard(project_path)

    console.print(
        Panel(
            f"[bold green]AI Guard Active[/bold green]\n\n"
            f"[yellow]Prompt:[/yellow] {prompt}\n"
            f"[yellow]Model:[/yellow] {model}\n"
            f"[yellow]Project:[/yellow] {project_path}\n"
            f"\n[cyan]Monitoring all file access...[/cyan]",
            title="AI Guard",
            border_style="green"
        )
    )

    guard.activate()

    try:
        from ollama import chat

        console.print(f"\n[cyan]Running Ollama ({model})...[/cyan]\n")

        response = chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response["message"]["content"]
        console.print(f"\n[bold green]AI Response:[/bold green]\n{answer}")

    except ImportError:
        console.print("\n[red]Ollama Python library not found.[/red]")
        console.print("[yellow]Install it: pip install ollama[/yellow]")
        console.print("[dim]Make sure Ollama is running: http://localhost:11434[/dim]")

        console.print("\n[cyan]Demo mode - showing what would be monitored:[/cyan]")
        console.print("[yellow]READ[/yellow] src/App.js")
        console.print("[yellow]READ[/yellow] src/auth/Login.tsx")
        console.print("[yellow]READ[/yellow] package.json")
        console.print("[bold green]AI Response:[/bold green]")
        console.print("  Here's the fix for your login bug...")

    except Exception as e:
        console.print(f"\n[red]Ollama error: {e}[/red]")
        console.print("[yellow]Make sure Ollama is running and the model is available.[/yellow]")

    finally:
        guard.deactivate()

    summary = guard.get_summary()
    console.print(
        Panel(
            f"[bold]Session Summary[/bold]\n\n"
            f"[cyan]Files Read:[/cyan] {len(summary['files_read'])}\n"
            f"[cyan]Files Written:[/cyan] {len(summary['files_written'])}\n"
            f"[red]Files Blocked:[/red] {len(summary['files_blocked'])}\n"
            f"[cyan]Duration:[/cyan] {summary['elapsed_seconds']}s\n"
            f"\n{'[red]Security threats prevented![/red]' if summary['files_blocked'] else '[green]No security issues[/green]'}",
            title="Summary",
            border_style="green" if not summary['files_blocked'] else "red"
        )
    )
