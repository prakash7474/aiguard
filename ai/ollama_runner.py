"""
Ollama AI integration for AI Guard
Runs Ollama models with file access monitoring
"""

from typing import Optional
from rich.console import Console
from rich.panel import Panel

console = Console()


class OllamaRunner:
    """
    Run Ollama models within AI Guard's monitored environment.
    Requires: pip install ollama, ollama server running on http://localhost:11434
    """

    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model

    def chat(self, prompt: str) -> Optional[str]:
        """
        Send a prompt to Ollama and get response.
        File access is intercepted by the guard layer.
        """
        try:
            from ollama import chat as ollama_chat
        except ImportError:
            console.print("[red]ollama package not installed.[/red]")
            console.print("[yellow]Run: pip install ollama[/yellow]")
            return None

        try:
            console.print(f"[cyan]Ollama ({self.model}): processing...[/cyan]")
            response = ollama_chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]

        except Exception as e:
            console.print(f"[red]Ollama error: {e}[/red]")
            console.print("[yellow]Is Ollama running? Check: http://localhost:11434[/yellow]")
            return None

    def list_models(self) -> list:
        """List available Ollama models"""
        try:
            from ollama import list as ollama_list
            models = ollama_list()
            return [m['name'] for m in models.get('models', [])]
        except Exception:
            return []
