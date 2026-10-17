from pathlib import Path
from datetime import datetime
import csv
import threading

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
REPORT_FILE = REPORT_DIR / "scan_report.csv"

_report_lock = threading.Lock()


def log_result(result):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "timestamp",
        "file",
        "sha256",
        "status",
        "details"
    ]

    with _report_lock:
        new_file = not REPORT_FILE.exists() or REPORT_FILE.stat().st_size == 0

        with REPORT_FILE.open(
            "a", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=fields)

            if new_file:
                writer.writeheader()

            writer.writerow({
                "timestamp": datetime.now().astimezone().isoformat(
                    timespec="seconds"
                ),
                "file": result.get("file", ""),
                "sha256": result.get("sha256", ""),
                "status": result.get("status", ""),
                "details": result.get("details", "")
            })
