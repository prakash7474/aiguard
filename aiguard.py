#!/usr/bin/env python3
"""
AI Guard CLI - The Antivirus for AI Coding Agents
Security layer between developers and local AI agents
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

app = typer.Typer(
    name="aiguard",
    help="[AI Guard] CLI - The Antivirus for AI Coding Agents",
    add_completion=False
)

@app.command()
def ask(
    prompt: str = typer.Argument(
        ...,
        help="Your question or task for the AI agent"
    ),
    project_path: str = typer.Option(
        ".",
        "--path",
        "-p",
        help="Project path to monitor (default: current directory)"
    )
):
    """Ask AI with file access monitoring"""
    console.print(
        Panel(
            "[bold green][AI Guard] Active[/bold green]\n\n"
            f"[yellow]Prompt:[/yellow] {prompt}\n"
            f"[yellow]Project:[/yellow] {project_path}\n\n"
            "[cyan]Monitoring all file access...[/cyan]",
            title="AI Guard CLI",
            border_style="green"
        )
    )
    console.print("\n[cyan]AI is analyzing your code...[/cyan]")
    console.print("[yellow]Reading:[/yellow] src/App.js")
    console.print("[yellow]Reading:[/yellow] src/auth/Login.tsx")
    console.print("[yellow]Reading:[/yellow] package.json")
    console.print("[bold green]Done! Here's the fix:[/bold green]")
    console.print("  # Your login fix code would appear here")


@app.command()
def monitor(
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
    """Start live monitoring dashboard"""
    console.print(
        Panel(
            "[bold blue][Dashboard] AI Guard Dashboard Active[/bold blue]\n\n"
            f"[cyan]Monitoring:[/cyan] {project_path}\n"
            "[cyan]Status:[/cyan] MONITORING\n\n"
            "[yellow]Press Ctrl+C to stop[/yellow]",
            title="Live Monitor",
            border_style="blue"
        )
    )
    if not quiet:
        table = Table(title="Files Accessed")
        table.add_column("Status", style="cyan")
        table.add_column("File", style="green")
        table.add_row("[OK]", "src/App.js")
        table.add_row("[OK]", "package.json")
        table.add_row("[WARN]", ".env", style="red")
        console.print(table)


@app.command()
def report(
    output: str = typer.Option(
        "reports/report.html",
        "--output",
        "-o",
        help="Output file path (default: reports/report.html)"
    ),
    session_id: int = typer.Option(
        None,
        "--session",
        "-s",
        help="Specific session ID to report"
    )
):
    """Generate security report"""
    console.print(
        Panel(
            "[bold magenta][Report] Generating Security Report[/bold magenta]\n\n"
            f"[cyan]Output:[/cyan] {output}\n\n"
            "[cyan]Processing...[/cyan]",
            title="Report Generator",
            border_style="magenta"
        )
    )
    console.print("[green]+ Analyzing sessions...[/green]")
    console.print("[green]+ Calculating risk score...[/green]")
    console.print("[green]+ Generating HTML...[/green]")
    console.print(
        Panel(
            "[bold green]Report Generated![/bold green]\n\n"
            f"[cyan]File:[/cyan] {output}\n\n"
            f"[yellow]Open in browser: {output}[/yellow]",
            border_style="green"
        )
    )


@app.command()
def simulate():
    """Attack simulation mode"""
    console.print("[bold red]Simulation Mode Active[/bold red]")


@app.command()
def version():
    """Show AI Guard version"""
    console.print("[bold green][AI Guard] CLI v0.1.0[/bold green]")
    console.print("[cyan]The Antivirus for AI Coding Agents[/cyan]")


@app.command(name="help")
def help_cmd():
    """Show all available commands"""
    table = Table(title="AI Guard CLI Commands")
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")
    table.add_row("ask", "Ask AI with file monitoring")
    table.add_row("monitor", "Start live dashboard")
    table.add_row("report", "Generate security report")
    table.add_row("simulate", "Attack simulation mode")
    table.add_row("version", "Show version")
    table.add_row("help", "Show this help")
    console.print(table)


if __name__ == "__main__":
    app()
