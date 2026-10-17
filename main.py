import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import threading

from scanner import scan_folder
from monitor import start_monitor
from updater import update_signatures
from database import load_signatures

BASE_DIR = Path(__file__).resolve().parent


class SmartAntivirus:
    def __init__(self, window):
        self.window = window
        self.window.title("Smart Antivirus")
        self.window.geometry("760x580")
        self.window.minsize(620, 460)

        self.selected_folder = tk.StringVar(value="")
        self.status = tk.StringVar(value="Ready")
        self.signature_count = tk.StringVar(value="")

        self.observer = None

        title = tk.Label(
            window,
            text="Smart Antivirus",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=(15, 5))

        subtitle = tk.Label(
            window,
            text="Educational SHA-256 Signature Scanner"
        )
        subtitle.pack()

        folder_frame = tk.Frame(window)
        folder_frame.pack(fill="x", padx=15, pady=15)

        tk.Label(folder_frame, text="Folder:").pack(side="left")

        self.folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.selected_folder
        )
        self.folder_entry.pack(
            side="left", fill="x", expand=True, padx=8
        )

        tk.Button(
            folder_frame,
            text="Browse",
            command=self.choose_folder
        ).pack(side="right")

        buttons = tk.Frame(window)
        buttons.pack(pady=5)

        tk.Button(
            buttons,
            text="Scan Folder",
            command=self.start_scan,
            width=15
        ).grid(row=0, column=0, padx=5, pady=5)

        tk.Button(
            buttons,
            text="Update Signatures",
            command=self.ask_update_url,
            width=18
        ).grid(row=0, column=1, padx=5, pady=5)

        self.monitor_button = tk.Button(
            buttons,
            text="Start Monitoring",
            command=self.toggle_monitor,
            width=18
        )
        self.monitor_button.grid(row=0, column=2, padx=5, pady=5)

        tk.Label(
            window,
            text="Scan Results",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=15, pady=(10, 0))

        self.output = tk.Text(
            window,
            height=16,
            wrap="word",
            state="disabled"
        )
        self.output.pack(fill="both", expand=True, padx=15, pady=8)

        tk.Label(
            window,
            textvariable=self.status,
            anchor="w"
        ).pack(fill="x", padx=15, pady=(0, 3))

        tk.Label(
            window,
            textvariable=self.signature_count,
            anchor="w"
        ).pack(fill="x", padx=15, pady=(0, 10))

        self.refresh_signature_count()
        self.write_output(
            "Welcome! Select a folder and click Scan Folder.\n"
            "No-match results do not guarantee a file is safe.\n"
        )

        self.window.protocol("WM_DELETE_WINDOW", self.close_app)

    def write_output(self, message):
        self.output.configure(state="normal")
        self.output.insert("end", message + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def display_result(self, result):
        message = (
            f"[{result['status']}] {result['file']}\n"
            f"SHA-256: {result['sha256'] or 'Unavailable'}\n"
            f"{result['details']}\n"
            + "-" * 55
        )
        self.write_output(message)

    def refresh_signature_count(self):
        try:
            count = len(load_signatures())
            self.signature_count.set(
                f"Loaded signatures: {count}"
            )
        except OSError as error:
            self.signature_count.set(
                f"Could not load signatures: {error}"
            )

    def choose_folder(self):
        folder = filedialog.askdirectory(
            title="Select a folder to scan"
        )

        if folder:
            self.selected_folder.set(folder)
            self.status.set("Folder selected")

    def start_scan(self):
        folder = self.selected_folder.get().strip()

        if not folder or not Path(folder).is_dir():
            messagebox.showerror(
                "Invalid Folder",
                "Please select an existing folder first."
            )
            return

        self.status.set("Scanning...")
        self.write_output(f"Starting scan: {folder}")

        def worker():
            try:
                results = scan_folder(
                    folder,
                    on_result=lambda result: self.window.after(
                        0, self.display_result, result
                    )
                )

                detected = sum(
                    result["status"] == "DETECTED"
                    for result in results
                )

                errors = sum(
                    result["status"] == "ERROR"
                    for result in results
                )

                summary = (
                    f"Scan complete. Files scanned: {len(results)}; "
                    f"signature matches: {detected}; errors: {errors}."
                )

                self.window.after(
                    0, self.status.set, summary
                )

            except Exception as error:
                self.window.after(
                    0,
                    self.status.set,
                    "Scan failed: " + str(error)
                )

        threading.Thread(target=worker, daemon=True).start()

    def ask_update_url(self):
        url = simpledialog.askstring(
            "Update Signatures",
            "Enter the HTTPS URL of a trusted plain-text SHA-256 database:"
        )

        if not url:
            return

        self.status.set("Downloading and validating signatures...")

        def worker():
            try:
                count = update_signatures(url)

                self.window.after(
                    0, self.refresh_signature_count
                )
                self.window.after(
                    0,
                    self.status.set,
                    f"Signature database updated: {count} hashes."
                )

            except Exception as error:
                self.window.after(
                    0,
                    self.status.set,
                    "Update failed; previous database was preserved: "
                    + str(error)
                )

        threading.Thread(target=worker, daemon=True).start()

    def toggle_monitor(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join(timeout=3)
            self.observer = None
            self.monitor_button.config(text="Start Monitoring")
            self.status.set("Monitoring stopped")
            return

        folder = self.selected_folder.get().strip()

        if not folder or not Path(folder).is_dir():
            messagebox.showerror(
                "Invalid Folder",
                "Please select an existing folder first."
            )
            return

        try:
            self.observer = start_monitor(
                folder,
                on_result=lambda result: self.window.after(
                    0, self.display_result, result
                )
            )
            self.monitor_button.config(text="Stop Monitoring")
            self.status.set("Monitoring: " + folder)

        except Exception as error:
            self.observer = None
            messagebox.showerror("Monitor Error", str(error))

    def close_app(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join(timeout=3)

        self.window.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = SmartAntivirus(window)
    window.mainloop()
