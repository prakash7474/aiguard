import re
from pathlib import Path
from typing import List, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class SecretScanner:
    """
    Secret Detection Engine for Local AI (Ollama)
    Detects secrets that actually matter on a developer's machine
    """

    SECRET_PATTERNS = {
        'aws_access_key': {
            'pattern': r'AKIA[a-zA-Z0-9]{16}',
            'description': 'AWS Access Key ID',
            'severity': 'CRITICAL'
        },
        'aws_secret_key': {
            'pattern': r'(?i)(aws_secret_access_key|AWS_SECRET_KEY)\s*[=:]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?',
            'description': 'AWS Secret Access Key',
            'severity': 'CRITICAL'
        },
        'github_token': {
            'pattern': r'ghp_[a-zA-Z0-9]{36}',
            'description': 'GitHub Personal Token',
            'severity': 'CRITICAL'
        },
        'github_oauth': {
            'pattern': r'gho_[a-zA-Z0-9]{36}',
            'description': 'GitHub OAuth Token',
            'severity': 'CRITICAL'
        },
        'google_api_key': {
            'pattern': r'AIza[a-zA-Z0-9_\-]{35}',
            'description': 'Google Cloud API Key',
            'severity': 'CRITICAL'
        },
        'stripe_key': {
            'pattern': r'sk_live_[a-zA-Z0-9]{24,32}',
            'description': 'Stripe Secret Key',
            'severity': 'CRITICAL'
        },
        'private_key': {
            'pattern': r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH)\s+PRIVATE KEY-----',
            'description': 'Private Key File Content',
            'severity': 'CRITICAL'
        },
        'ssh_private_key': {
            'pattern': r'id_(rsa|ed25519|ecdsa|dsa)',
            'description': 'SSH Private Key File',
            'severity': 'CRITICAL'
        },

        'db_password': {
            'pattern': r'(?i)(DATABASE_PASSWORD|DB_PASSWORD|POSTGRES_PASSWORD|MYSQL_PASSWORD|MONGO_PASSWORD|REDIS_PASSWORD)\s*[=:]\s*["\']?([^\s"\']+)["\']?',
            'description': 'Database Password',
            'severity': 'CRITICAL'
        },
        'jwt_token': {
            'pattern': r'eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+',
            'description': 'JWT Token',
            'severity': 'HIGH'
        },
        'slack_token': {
            'pattern': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}',
            'description': 'Slack Bot Token',
            'severity': 'CRITICAL'
        },
        'env_file': {
            'pattern': r'^\.env$',
            'description': '.env File (contains secrets)',
            'severity': 'HIGH',
            'is_filename': True
        },
        'env_local': {
            'pattern': r'^\.env\.local$',
            'description': '.env.local File',
            'severity': 'HIGH',
            'is_filename': True
        },
        'env_production': {
            'pattern': r'^\.env\.production$',
            'description': '.env.production File',
            'severity': 'HIGH',
            'is_filename': True
        },
        'credentials_json': {
            'pattern': r'^credentials\.json$',
            'description': 'Cloud Credentials File',
            'severity': 'HIGH',
            'is_filename': True
        },
        'firebase_admin': {
            'pattern': r'^firebase-adminkey\.json$',
            'description': 'Firebase Admin Key',
            'severity': 'HIGH',
            'is_filename': True
        },
        'pem_file': {
            'pattern': r'\.pem$',
            'description': 'PEM Certificate File',
            'severity': 'HIGH',
            'is_filename': True
        },
        'key_file': {
            'pattern': r'\.key$',
            'description': 'Private Key File',
            'severity': 'HIGH',
            'is_filename': True
        },
    }

    def __init__(self):
        self.patterns = self.SECRET_PATTERNS

    def scan_content(self, content: str, source: str = "content") -> List[Dict]:
        found_secrets = []

        for secret_type, config in self.patterns.items():
            if config.get('is_filename'):
                continue

            pattern = config['pattern']
            matches = re.findall(pattern, content, re.IGNORECASE)

            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        secret_value = match[-1] if match else match[0]
                    else:
                        secret_value = match

                    found_secrets.append({
                        'type': secret_type,
                        'description': config['description'],
                        'severity': config['severity'],
                        'value': secret_value[:40],
                        'source': source,
                        'line': self._find_line_number(content, secret_value)
                    })

        return found_secrets

    def _read_file_content(self, filepath: str) -> str:
        """Try multiple encodings to read file content"""
        encodings = ['utf-8', 'ascii', 'latin-1', 'utf-16', 'cp1252']
        for enc in encodings:
            try:
                return Path(filepath).read_text(encoding=enc)
            except (UnicodeDecodeError, UnicodeError):
                continue
        return Path(filepath).read_text(encoding='utf-8', errors='ignore')

    def scan_file(self, filepath: str) -> List[Dict]:
        found_secrets = []
        file_path = Path(filepath)

        filename = file_path.name
        for secret_type, config in self.patterns.items():
            if config.get('is_filename'):
                if re.search(config['pattern'], filename, re.IGNORECASE):
                    found_secrets.append({
                        'type': secret_type,
                        'description': config['description'],
                        'severity': config['severity'],
                        'value': filename,
                        'source': filepath,
                        'line': 0
                    })

        try:
            content = self._read_file_content(filepath)
            content_secrets = self.scan_content(content, filepath)
            found_secrets.extend(content_secrets)
        except Exception:
            pass

        return found_secrets

    def scan_directory(self, dirpath: str, recursive: bool = True) -> List[Dict]:
        found_secrets = []
        dir_path = Path(dirpath)

        if not dir_path.exists():
            return found_secrets

        files = dir_path.rglob('*') if recursive else dir_path.glob('*')

        for file_path in files:
            if file_path.is_file():
                found_secrets.extend(self.scan_file(str(file_path)))

        return found_secrets

    def redact_content(self, content: str) -> str:
        redacted = content
        for secret_type, config in self.patterns.items():
            if config.get('is_filename'):
                continue
            redacted = re.sub(config['pattern'], '[REDACTED]', redacted, flags=re.IGNORECASE)
        return redacted

    def _find_line_number(self, content: str, secret: str) -> int:
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if secret[:20] in line:
                return i
        return 0

    def display_secrets(self, secrets: List[Dict], source: str = ""):
        if not secrets:
            console.print("[green]No secrets detected[/green]")
            return

        console.print(
            Panel(
                f"[bold red]SECRETS DETECTED[/bold red]\n"
                f"[cyan]Source:[/cyan] {source}\n"
                f"[cyan]Total:[/cyan] {len(secrets)}",
                title="Secret Scanner",
                border_style="red"
            )
        )

        table = Table(title="Detected Secrets", border_style="red")
        table.add_column("Type", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Severity", style="yellow")
        table.add_column("Line", style="magenta")

        for secret in secrets:
            severity_color = {
                'CRITICAL': 'red',
                'HIGH': 'yellow',
                'MEDIUM': 'blue',
                'LOW': 'green'
            }.get(secret['severity'], 'white')

            table.add_row(
                secret['type'],
                secret['description'],
                f"[{severity_color}]{secret['severity']}[/{severity_color}]",
                str(secret['line'])
            )

        console.print(table)
