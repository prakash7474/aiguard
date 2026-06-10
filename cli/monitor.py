from monitor.file_watcher import FileMonitor
import typer

app = typer.Typer()

@app.command()
def start(path: str = "."):
    """Start file monitoring"""
    monitor = FileMonitor()
    monitor.start(path)

    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
