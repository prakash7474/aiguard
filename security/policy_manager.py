import os
from typing import List, Tuple


class PolicyManager:
    BLOCKED_PATTERNS = [
        r"\.env$",
        r"\.pem$",
        r"id_rsa$",
        r"id_dsa$",
        r"credentials\.json$",
        r"config\.json$",
        r"\.secret$",
        r"service-account\.json$",
        r"\.htpasswd$",
        r"\.netrc$",
    ]

    ALLOWED_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs",
        ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".ini",
        ".css", ".scss", ".html", ".vue", ".svelte",
    }

    def __init__(self):
        self.custom_rules = []

    def check_access(self, file_path: str) -> Tuple[bool, str]:
        filename = os.path.basename(file_path)
        for pattern in self.BLOCKED_PATTERNS:
            import re
            if re.search(pattern, filename):
                return False, f"Blocked by policy: sensitive file pattern '{pattern}'"
        for rule in self.custom_rules:
            if rule in file_path:
                return False, f"Blocked by custom rule: '{rule}'"
        return True, "Allowed"

    def add_blocked_pattern(self, pattern: str):
        self.custom_rules.append(pattern)
