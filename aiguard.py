#!/usr/bin/env python3
"""
AI Guard CLI - The Antivirus for AI Coding Agents
Security layer between developers and local AI agents (Ollama, LM Studio)
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from pathlib import Path

console = Console()

app = typer.Typer(
    name="aiguard",
    help="[AI Guard] The Antivirus for AI Coding Agents",
    add_completion=False
)


@app.command()
def ask(
    prompt: str = typer.Argument(..., help="Your question or task for the AI agent"),
    project_path: str = typer.Option(".", "--path", "-p", help="Project path to monitor"),
    model: str = typer.Option("llama3.2:3b", "--model", "-m", help="Ollama model to use")
):
    """Ask AI with file access monitoring (Ollama)"""
    from cli.ask import run_guarded

    run_guarded(prompt, project_path, model)


@app.command()
def monitor(
    project_path: str = typer.Option(".", "--path", "-p", help="Project path to monitor"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Disable verbose output")
):
    """Start live file monitoring (tracks reads via interceptor + writes via watchdog)"""
    from monitor.file_access_interceptor import HybridFileMonitor
    import time

    console.print(
        Panel(
            "[bold blue]AI Guard File Monitor Active[/bold blue]\n\n"
            f"[cyan]Monitoring:[/cyan] {project_path}\n"
            "[cyan]Reads:[/cyan] Python open() interceptor (Windows-compatible)\n"
            "[cyan]Writes:[/cyan] Watchdog\n"
            "\n[yellow]Press Ctrl+C to stop[/yellow]",
            title="Hybrid Monitor",
            border_style="blue"
        )
    )

    monitor = HybridFileMonitor()
    monitor.start(project_path)

    try:
        while monitor.is_monitoring:
            if not quiet:
                stats = monitor.get_stats()
                console.print(
                    f"Stats: Read={stats['read_count']} Write={stats['write_count']} Total={stats['total_files']}"
                )
            time.sleep(5)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping monitor...[/yellow]")

    monitor.stop()


@app.command()
def report(
    output: str = typer.Option("reports/report.html", "--output", "-o",
                               help="Output file path"),
    session_id: int = typer.Option(None, "--session", "-s", help="Session ID to report")
):
    """Generate security report"""
    from report.html_generator import HTMLReportGenerator

    console.print("[cyan]Generating security report...[/cyan]")
    gen = HTMLReportGenerator()
    gen.generate(
        output_path=output,
        session_id=session_id,
        risk_score=0.3,
        files_read=["src/App.js", "src/auth/Login.tsx"],
        blocked_attempts=[".env (blocked: sensitive file)"]
    )
    console.print(f"[green]Report generated: {output}[/green]")


@app.command()
def simulate():
    """Attack simulation mode - test AI Guard defenses"""
    from cli.simulate import run_simulation
    run_simulation()


@app.command()
def version():
    """Show AI Guard version"""
    console.print("[bold green]AI Guard CLI v0.1.0[/bold green]")
    console.print("[cyan]The Antivirus for Local AI Coding Agents[/cyan]")
    console.print("[dim]Works with: Ollama, LM Studio, OpenCode[/dim]")


@app.command(name="help")
def help_cmd():
    """Show all available commands"""
    table = Table(title="AI Guard CLI Commands", border_style="cyan")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")
    table.add_row("ask", "Ask AI (Ollama) with file access monitoring")
    table.add_row("monitor", "Start live file monitoring dashboard")
    table.add_row("scan file", "Scan a file for secrets")
    table.add_row("scan content", "Scan text for secrets")
    table.add_row("scan dir", "Scan directory for secrets")
    table.add_row("report", "Generate HTML security report")
    table.add_row("simulate", "Run attack simulation")
    table.add_row("version", "Show version")
    table.add_row("help", "Show this help")
    console.print(table)


# Add scan subcommands
from cli.scan import app as scan_app
app.add_typer(scan_app, name="scan")

if __name__ == "__main__":
    app()
