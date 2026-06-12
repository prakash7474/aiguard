from rich.console import Console
from rich.panel import Panel

console = Console()


def run(attacks: int = 3):
    console.print(
        Panel(
            "[bold red]ATTACK SIMULATION MODE[/bold red]\n\n"
            f"[cyan]Simulating {attacks} attacks...[/cyan]\n\n"
            "[yellow]Testing security controls...[/yellow]",
            title="Simulation",
            border_style="red"
        )
    )
