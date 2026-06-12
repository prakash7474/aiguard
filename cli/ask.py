from rich.console import Console
from rich.panel import Panel

console = Console()


def run(prompt: str, project_path: str = "."):
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
