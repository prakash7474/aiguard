#!/usr/bin/env python3
"""
Monitor Command
Starts live file monitoring dashboard
"""

import typer
import time
from monitor.file_watcher import FileMonitor
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

console = Console()
app = typer.Typer()


def on_file_event(action: str, filepath: str):
    """Callback for file events"""
    # This will be called when files are accessed
    pass


@app.command()
def start(
    project_path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Project path to monitor (default: current directory)"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Disable verbose output"
    )
):
    """
    Start live file monitoring

    Example:
        python -m aiguard monitor
        python -m aiguard monitor --path ./my-project
    """
    console.print(
        Panel(
            "[bold blue]AI Guard File Monitor Active[/bold blue]\n\n"
            f"[cyan]Monitoring:[/cyan] {project_path}\n"
            "[cyan]Status:[/cyan] MONITORING\n\n"
            "[yellow]Press Ctrl+C to stop[/yellow]",
            title="Live Monitor",
            border_style="blue"
        )
    )

    # Create monitor
    monitor = FileMonitor()

    # Start monitoring
    success = monitor.start(project_path, on_file_event)

    if not success:
        return

    # Keep monitoring
    try:
        while monitor.is_monitoring:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping monitor...[/yellow]")

    # Stop and show stats
    monitor.stop()


@app.command()
def check(
    filepath: str = typer.Argument(
        ...,
        help="File path to check if accessed"
    ),
    project_path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Project path (default: current directory)"
    )
):
    """
    Check if a file was accessed during monitoring

    Example:
        python -m aiguard monitor check src/App.js
    """
    console.print(f"[cyan]Checking if file was accessed:[/cyan] {filepath}")

    # This would check during actual monitoring
    console.print("[yellow]Start monitoring first to check files[/yellow]")


if __name__ == "__main__":
    app()
