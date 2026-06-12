import re
import os
from typing import List


class SecretScanner:
    SENSITIVE_PATTERNS = {
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "SSH Key": r"-----BEGIN (RSA|OPENSSH|DSA|EC) PRIVATE KEY-----",
        "GitHub Token": r"gh[pousr]_[A-Za-z0-9_]{36,}",
        "Generic Secret": r"(?i)(secret|password|api[_-]?key|token).{0,5}[=:].{0,5}['\"][A-Za-z0-9_\-]{8,}['\"]",
    }

    def __init__(self):
        self.findings = []

    def scan_file(self, file_path: str) -> List[dict]:
        if not os.path.isfile(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return []
        return self.scan_content(content, file_path)

    def scan_content(self, content: str, source: str = "<memory>") -> List[dict]:
        findings = []
        for name, pattern in self.SENSITIVE_PATTERNS.items():
            for match in re.finditer(pattern, content):
                findings.append({
                    "type": name,
                    "match": match.group()[:20] + "...",
                    "position": match.start(),
                    "source": source,
                })
        self.findings.extend(findings)
        return findings
