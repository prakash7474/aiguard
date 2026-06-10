import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console

console = Console()

class FileAccessHandler(FileSystemEventHandler):
    def __init__(self, ai_agent_name="unknown"):
        self.ai_agent_name = ai_agent_name

    def on_read(self, event):
        if not event.is_directory:
            console.print(f"[bold yellow]📖 [READ][/bold yellow] {event.src_path}")

    def on_write(self, event):
        if not event.is_directory:
            console.print(f"[bold red]📝 [WRITE][/bold red] {event.src_path}")

class FileMonitor:
    def __init__(self):
        self.observer = None

    def start(self, path="."):
        event_handler = FileAccessHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()
        console.print("[bold green]✅ Monitoring started[/bold green]")

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            console.print("[bold red]❌ Monitoring stopped[/bold red]")
