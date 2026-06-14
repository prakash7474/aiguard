#!/usr/bin/env python3
"""
File Access Monitor
Tracks every file read/write operation by AI agents
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

console = Console()


class FileAccessHandler(FileSystemEventHandler):
    """Handles file system events"""

    def __init__(self, project_path=".", callback=None):
        self.project_path = project_path
        self.callback = callback
        self.files_read = []
        self.files_written = []
        self.files_deleted = []

    def on_modified(self, event):
        """Handle file modified (write) event"""
        if not event.is_directory:
            filepath = event.src_path
            console.print(f"[red][WRITE][/red] {filepath}")
            self.files_written.append(filepath)
            if self.callback:
                self.callback("WRITE", filepath)

    def on_created(self, event):
        """Handle file created event"""
        if not event.is_directory:
            filepath = event.src_path
            console.print(f"[green][CREATE][/green] {filepath}")
            self.files_written.append(filepath)
            if self.callback:
                self.callback("CREATE", filepath)

    def on_deleted(self, event):
        """Handle file deleted event"""
        if not event.is_directory:
            filepath = event.src_path
            console.print(f"[bold red][DELETE][/bold red] {filepath}")
            self.files_deleted.append(filepath)
            if self.callback:
                self.callback("DELETE", filepath)

    def on_moved(self, event):
        """Handle file moved event"""
        if not event.is_directory:
            console.print(f"[cyan][MOVE][/cyan] {event.src_path} -> {event.dest_path}")

    def get_stats(self):
        """Get monitoring statistics"""
        return {
            'read_count': len(self.files_read),
            'write_count': len(self.files_written),
            'delete_count': len(self.files_deleted),
            'total_files': len(self.files_read) + len(self.files_written) + len(self.files_deleted)
        }

    def watch_file(self, filepath):
        """Check if a specific file was accessed"""
        return filepath in self.files_read or filepath in self.files_written


class FileMonitor:
    """Main file monitoring class"""

    def __init__(self):
        self.observer = None
        self.event_handler = None
        self.is_monitoring = False
        self.stats = {
            'read_count': 0,
            'write_count': 0,
            'delete_count': 0,
            'total_files': 0
        }

    def start(self, project_path=".", callback=None):
        """Start monitoring file system"""
        self.event_handler = FileAccessHandler(project_path, callback)
        self.observer = Observer()

        watch_path = project_path if project_path else "."
        if not os.path.exists(watch_path):
            console.print(f"[red]Error: Path does not exist: {watch_path}[/red]")
            return False

        self.observer.schedule(self.event_handler, watch_path, recursive=True)
        self.observer.start()
        self.is_monitoring = True

        console.print(
            Panel(
                f"[bold green]Monitoring Started[/bold green]\n\n"
                f"[cyan]Path:[/cyan] {watch_path}\n"
                f"[cyan]Recursive:[/cyan] Yes\n"
                f"[yellow]Press Ctrl+C to stop[/yellow]",
                title="File Monitor",
                border_style="green"
            )
        )

        return True

    def stop(self):
        """Stop monitoring"""
        if self.observer and self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            self.stats = self.event_handler.get_stats()

            console.print(
                Panel(
                    f"[bold red]Monitoring Stopped[/bold red]\n\n"
                    f"[cyan]Files Read:[/cyan] {self.stats['read_count']}\n"
                    f"[cyan]Files Written:[/cyan] {self.stats['write_count']}\n"
                    f"[cyan]Files Deleted:[/cyan] {self.stats['delete_count']}\n"
                    f"[cyan]Total:[/cyan] {self.stats['total_files']}",
                    title="Summary",
                    border_style="red"
                )
            )

    def get_stats(self):
        """Get current statistics"""
        if self.event_handler:
            return self.event_handler.get_stats()
        return self.stats

    def watch_file(self, filepath):
        """Check if a specific file was accessed"""
        if self.event_handler:
            return self.event_handler.watch_file(filepath)
        return False


def test_monitor():
    """Test file monitoring"""
    console.print("[bold blue]Testing File Monitor...[/bold blue]\n")

    monitor = FileMonitor()
    monitor.start(".")

    console.print("\n[cyan]Create/edit a file to see monitoring...[/cyan]\n")

    try:
        while monitor.is_monitoring:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")

    monitor.stop()

    stats = monitor.get_stats()
    console.print(
        Panel(
            f"[bold]Test Results:[/bold]\n\n"
            f"Files Read: {stats['read_count']}\n"
            f"Files Written: {stats['write_count']}\n"
            f"Total: {stats['total_files']}",
            title="Stats",
            border_style="cyan"
        )
    )


if __name__ == "__main__":
    test_monitor()
