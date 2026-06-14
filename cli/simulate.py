"""
Attack Simulation Mode
Demonstrates AI Guard's defenses by simulating common attack scenarios
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from security.policy_manager import PolicyManager
from security.secret_scanner import SecretScanner

console = Console()


def run_simulation():
    """Run attack simulation to demonstrate AI Guard defenses"""
    console.print(
        Panel(
            "[bold red]ATTACK SIMULATION MODE[/bold red]\n\n"
            "[cyan]Simulating common AI agent attacks...[/cyan]",
            title="Simulation",
            border_style="red"
        )
    )

    attacks = [
        {"name": "Read .env file", "filepath": ".env", "expected": "BLOCKED"},
        {"name": "Read SSH private key", "filepath": "id_rsa", "expected": "BLOCKED"},
        {"name": "Read credentials.json", "filepath": "credentials.json", "expected": "BLOCKED"},
        {"name": "Read .pem certificate", "filepath": "cert.pem", "expected": "BLOCKED"},
        {"name": "Read source code (.py)", "filepath": "src/App.py", "expected": "ALLOWED"},
        {"name": "Read JS source", "filepath": "src/components/Header.jsx", "expected": "ALLOWED"},
        {"name": "Read markdown docs", "filepath": "docs/README.md", "expected": "ALLOWED"},
    ]

    pm = PolicyManager()
    scanner = SecretScanner()

    results_table = Table(title="Attack Simulation Results", border_style="red")
    results_table.add_column("Attack", style="cyan")
    results_table.add_column("File", style="yellow")
    results_table.add_column("Result", style="green")
    results_table.add_column("Expected", style="magenta")

    passed = 0
    failed = 0

    for attack in attacks:
        allowed, reason = pm.check_access(attack['filepath'])

        result = "ALLOWED" if allowed else "BLOCKED"
        expected = attack['expected']

        if result == expected:
            status_icon = "[green]PASS[/green]"
            passed += 1
        else:
            status_icon = "[red]FAIL[/red]"
            failed += 1

        result_color = "green" if result == "ALLOWED" else "red"
        expected_color = "green" if expected == "ALLOWED" else "red"

        results_table.add_row(
            status_icon,
            attack['filepath'],
            f"[{result_color}]{result}[/{result_color}]",
            f"[{expected_color}]{expected}[/{expected_color}]"
        )

    console.print(results_table)

    # Secret scan demo
    console.print("\n[bold cyan]Secret Detection Demo:[/bold cyan]")
    test_content = """
DATABASE_PASSWORD=super_secret_123
AWS_ACCESS_KEY=AKIA1234567890ABCDEF
GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz123456
"""
    secrets = scanner.scan_content(test_content, "simulation")
    scanner.display_secrets(secrets, "Simulated Content")

    score = (passed / len(attacks)) * 100
    result_panel = Panel(
        f"[bold]Results: {passed}/{len(attacks)} passed ({score:.0f}%)[/bold]\n\n"
        f"{'[green]All security controls working correctly![/green]' if score == 100 else '[yellow]Some controls need attention[/yellow]'}\n\n"
        f"[cyan]Policy Engine:[/cyan] {'Working' if passed > 0 else 'Failed'}\n"
        f"[cyan]Secret Scanner:[/cyan] {len(secrets)} secrets detected\n"
        f"[cyan]Blocked Attacks:[/cyan] {len([a for a in attacks if a['expected'] == 'BLOCKED'])}",
        title="Simulation Complete",
        border_style="green" if score == 100 else "yellow"
    )
    console.print(result_panel)
