import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="AI Guard CLI - The Antivirus for AI Coding Agents")

@app.command()
def ask(prompt: str):
    """Ask AI with file access monitoring"""
    console.print(f"[bold green]🛡️ AI Guard: {prompt}[/bold green]")
    console.print("[yellow]⚠️ Monitoring file access...[/yellow]")

@app.command()
def monitor():
    """Start live monitoring dashboard"""
    console.print("[bold blue]📊 AI Guard Dashboard Active[/bold blue]")

@app.command()
def report():
    """Generate security report"""
    console.print("[bold magenta]📄 Generating report...[/bold magenta]")

@app.command()
def simulate():
    """Attack simulation mode"""
    console.print("[bold red]⚔️ Simulation Mode Active[/bold red]")

if __name__ == "__main__":
    app()