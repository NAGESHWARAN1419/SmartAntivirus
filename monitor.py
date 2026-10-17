from pathlib import Path
from threading import Timer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from scanner import scan_file


class ScanEventHandler(FileSystemEventHandler):
    def __init__(self, on_result=None):
        self.on_result = on_result
        self.pending = {}
        self.lock = __import__("threading").Lock()

    def _schedule_scan(self, file_path):
        path = Path(file_path)

        if path.is_symlink() or not path.is_file():
            return

        key = str(path.resolve())

        with self.lock:
            old_timer = self.pending.get(key)

            if old_timer:
                old_timer.cancel()

            timer = Timer(1.0, self._scan, args=[key])
            timer.daemon = True
            self.pending[key] = timer
            timer.start()

    def _scan(self, file_path):
        try:
            result = scan_file(file_path)

            if self.on_result:
                self.on_result(result)
        finally:
            with self.lock:
                self.pending.pop(file_path, None)

    def on_created(self, event):
        if not event.is_directory:
            self._schedule_scan(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._schedule_scan(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._schedule_scan(event.dest_path)


def start_monitor(folder_path, on_result=None):
    folder = Path(folder_path)

    if not folder.is_dir():
        raise ValueError("Please select a valid folder to monitor.")

    handler = ScanEventHandler(on_result)
    observer = Observer()
    observer.schedule(handler, str(folder), recursive=False)
    observer.start()

    return observer
