from rich.console import Console
from rich.panel import Panel

console = Console()


def generate(output: str = "reports/report.html", session_id: int = None):
    console.print(
        Panel(
            "[bold magenta][Report] Generating Security Report[/bold magenta]\n\n"
            f"[cyan]Output:[/cyan] {output}\n\n"
            "[cyan]Processing...[/cyan]",
            title="Report Generator",
            border_style="magenta"
        )
    )
