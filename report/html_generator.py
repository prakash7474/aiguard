from datetime import datetime
from typing import Optional


class HTMLReportGenerator:
    def __init__(self):
        self.template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Guard Report - {date}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #0d1117; color: #c9d1d9; }}
        h1 {{ color: #58a6ff; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; margin: 12px 0; }}
        .risk-high {{ color: #f85149; }}
        .risk-medium {{ color: #d29922; }}
        .risk-low {{ color: #3fb950; }}
    </style>
</head>
<body>
    <h1>[AI Guard] Security Report</h1>
    <div class="card">
        <p><strong>Generated:</strong> {date}</p>
        <p><strong>Session ID:</strong> {session_id}</p>
        <p><strong>Risk Score:</strong> <span class="{risk_class}">{risk_score}</span></p>
    </div>
    <h2>Files Accessed</h2>
    <div class="card">
        <ul>{file_list}</ul>
    </div>
    <h2>Blocked Attempts</h2>
    <div class="card">
        <ul>{blocked_list}</ul>
    </div>
</body>
</html>"""

    def generate(
        self,
        output_path: str,
        session_id: Optional[int] = None,
        risk_score: float = 0.0,
        files_read: list = None,
        blocked_attempts: list = None,
    ):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        risk_class = "risk-low"
        if risk_score > 0.5:
            risk_class = "risk-high"
        elif risk_score > 0.2:
            risk_class = "risk-medium"

        file_list = "".join(f"<li>{f}</li>" for f in (files_read or []))
        blocked_list = "".join(f"<li>{b}</li>" for b in (blocked_attempts or []))

        html = self.template.format(
            date=now,
            session_id=session_id or "N/A",
            risk_score=risk_score,
            risk_class=risk_class,
            file_list=file_list if file_list else "<li>None</li>",
            blocked_list=blocked_list if blocked_list else "<li>None</li>",
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
