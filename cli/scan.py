import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from security.secret_scanner import SecretScanner

console = Console()
app = typer.Typer()


@app.command()
def file(
    filepath: str = typer.Argument(..., help="File path to scan"),
    redact: bool = typer.Option(False, "--redact", "-r", help="Redact secrets in output")
):
    """Scan a file for secrets"""
    if not Path(filepath).exists():
        console.print(f"[red]File not found: {filepath}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[cyan]Scanning file:[/cyan] {filepath}")
    scanner = SecretScanner()
    secrets = scanner.scan_file(filepath)
    scanner.display_secrets(secrets, filepath)

    if redact and secrets:
        content = Path(filepath).read_text(encoding='utf-8', errors='ignore')
        redacted = scanner.redact_content(content)
        console.print("\n[cyan]Redacted Content:[/cyan]")
        console.print(redacted)


@app.command()
def content(
    text: str = typer.Argument(..., help="Text content to scan"),
    redact: bool = typer.Option(False, "--redact", "-r", help="Redact secrets in output")
):
    """Scan text content for secrets"""
    scanner = SecretScanner()
    secrets = scanner.scan_content(text, "input")
    scanner.display_secrets(secrets, "Input Content")

    if redact and secrets:
        redacted = scanner.redact_content(text)
        console.print("\n[cyan]Redacted:[/cyan]")
        console.print(redacted)


@app.command()
def dir(
    dirpath: str = typer.Argument(..., help="Directory path to scan"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r/-R",
                                   help="Scan subdirectories (default: True)")
):
    """Scan a directory for secret files"""
    if not Path(dirpath).exists():
        console.print(f"[red]Directory not found: {dirpath}[/red]")
        raise typer.Exit(code=1)

    console.print(f"[cyan]Scanning directory:[/cyan] {dirpath}")
    scanner = SecretScanner()
    secrets = scanner.scan_directory(dirpath, recursive)
    scanner.display_secrets(secrets, dirpath)

    if secrets:
        critical = len([s for s in secrets if s['severity'] == 'CRITICAL'])
        high = len([s for s in secrets if s['severity'] == 'HIGH'])
        console.print(f"\n[cyan]Summary:[/cyan] Total={len(secrets)} Critical={critical} High={high}")


if __name__ == "__main__":
    app()
