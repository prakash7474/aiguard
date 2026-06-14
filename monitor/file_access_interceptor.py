#!/usr/bin/env python3
"""
File Access Interceptor
Monkey-patches Python's open() to intercept file reads on Windows
(watchdog cannot detect reads on Windows)
Hybrid: interceptor for reads + watchdog for writes/deletes
"""

import os
import sys
import builtins
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel

console = Console()


class FileAccessInterceptor:
    """
    Intercept file access by wrapping Python's open() function
    Works on Windows (where watchdog doesn't detect reads)
    """

    _original_open = builtins.open
    _is_active = False

    def __init__(self, callback=None):
        self.callback = callback
        self.files_read = []
        self.files_written = []
        self.files_deleted = []

    def start(self, callback=None):
        """Start intercepting file access"""
        if callback:
            self.callback = callback
        self._is_active = True

        # Save reference to self for use in closure
        _self = self

        # Wrapped open - intercept file reads/writes
        def _wrapped_open(file, mode='r', *args, **kwargs):
            filepath = str(file)

            is_read = 'r' in mode or ('+' in mode and 'w' not in mode and 'a' not in mode)
            is_write = 'w' in mode or 'a' in mode or ('+' in mode and ('r' in mode or 'a' in mode))

            if is_read and not is_write:
                _self.files_read.append(filepath)
                console.print(f"[yellow][READ][/yellow] {filepath}")
                if _self.callback:
                    _self.callback("READ", filepath)
            elif is_write:
                _self.files_written.append(filepath)
                console.print(f"[red][WRITE][/red] {filepath}")
                if _self.callback:
                    _self.callback("WRITE", filepath)

            return _self._original_open(file, mode, *args, **kwargs)

        builtins.open = _wrapped_open

        console.print(
            Panel(
                "[bold green]File Access Interceptor Active[/bold green]\n\n"
                "[cyan]Tracking:[/cyan] Reads, Writes\n"
                "[yellow]Press Ctrl+C to stop[/yellow]",
                title="File Interceptor",
                border_style="green"
            )
        )

    def stop(self):
        """Stop intercepting - restore original open()"""
        if self._is_active:
            builtins.open = self._original_open
            self._is_active = False

            console.print(
                Panel(
                    f"[bold red]Interceptor Stopped[/bold red]\n\n"
                    f"[cyan]Files Read:[/cyan] {len(self.files_read)}\n"
                    f"[cyan]Files Written:[/cyan] {len(self.files_written)}\n"
                    f"[cyan]Total:[/cyan] {len(self.files_read) + len(self.files_written)}",
                    title="Summary",
                    border_style="red"
                )
            )

    def get_stats(self):
        return {
            'read_count': len(self.files_read),
            'write_count': len(self.files_written),
            'delete_count': len(self.files_deleted),
            'total_files': len(self.files_read) + len(self.files_written) + len(self.files_deleted)
        }


class HybridFileMonitor:
    """
    Hybrid monitor: interceptor for reads + watchdog for writes/deletes
    Works on Windows!
    """

    def __init__(self):
        self.observer = None
        self.interceptor = None
        self.is_monitoring = False
        self.stats = {'read_count': 0, 'write_count': 0, 'delete_count': 0, 'total_files': 0}

    def start(self, project_path=".", callback=None):
        """Start hybrid monitoring"""

        # Start the open() interceptor (catches reads)
        self.interceptor = FileAccessInterceptor(callback)
        self.interceptor.start()

        # Start watchdog for write/delete events
        self.observer = Observer()

        class _WriteHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if not event.is_directory:
                    console.print(f"[red][WRITE][/red] {event.src_path}")
                    if callback:
                        callback("WRITE", event.src_path)

            def on_created(self, event):
                if not event.is_directory:
                    console.print(f"[green][CREATE][/green] {event.src_path}")
                    if callback:
                        callback("CREATE", event.src_path)

            def on_deleted(self, event):
                if not event.is_directory:
                    console.print(f"[bold red][DELETE][/bold red] {event.src_path}")
                    if callback:
                        callback("DELETE", event.src_path)

        self.observer.schedule(_WriteHandler(), project_path, recursive=True)
        self.observer.start()
        self.is_monitoring = True

        console.print(
            Panel(
                f"[bold blue]Hybrid Monitor Active[/bold blue]\n\n"
                f"[cyan]Path:[/cyan] {project_path}\n"
                "[cyan]Reads:[/cyan] Intercepted (Python open)\n"
                "[cyan]Writes:[/cyan] Watchdog + Interceptor\n\n"
                "[yellow]Press Ctrl+C to stop[/yellow]",
                title="Hybrid Monitor",
                border_style="blue"
            )
        )

    def stop(self):
        """Stop monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        if self.interceptor:
            self.interceptor.stop()

        self.is_monitoring = False
        self.stats = self.interceptor.get_stats() if self.interceptor else self.stats

    def get_stats(self):
        if self.interceptor:
            return self.interceptor.get_stats()
        return self.stats

    def was_file_read(self, filepath):
        if self.interceptor:
            return filepath in self.interceptor.files_read
        return False


def test_monitor():
    """Test the hybrid monitor"""
    console.print("[bold blue]Testing Hybrid Monitor...[/bold blue]\n")

    monitor = HybridFileMonitor()
    monitor.start(".")

    console.print("\n[cyan]Read/write files to see monitoring...[/cyan]\n")

    import time

    try:
        while monitor.is_monitoring:
            stats = monitor.get_stats()
            console.print(
                f"[cyan]Stats:[/cyan] Read={stats['read_count']} Write={stats['write_count']} Total={stats['total_files']}"
            )
            time.sleep(5)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted[/yellow]")

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
