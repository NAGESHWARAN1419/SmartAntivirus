Smart Antivirus — Python GUI File Scanner
<img width="749" height="605" alt="image" src="https://github.com/user-attachments/assets/61f2a09a-bffe-4475-93d1-4c19db3253ec" />

Overview

Smart Antivirus is an educational cybersecurity project built with Python. It demonstrates how file hashing, signature matching, quarantine, real-time folder monitoring, and CSV reporting can work together in a simple desktop application.

This project was developed to practise Python programming and understand basic file-scanning concepts.

Features

Graphical User Interface: Built with Tkinter.

SHA-256 Hashing: Calculates a file's SHA-256 hash.

Signature-Based Detection: Compares file hashes against a local signature database.

Quarantine: Moves files with matching signatures into a quarantine directory.

Real-Time Monitoring: Watches a selected folder for file creation and modification events.

Signature Updating: Downloads and validates a plain-text SHA-256 database from a supplied HTTPS URL.

CSV Reports: Records scan results, hashes, timestamps, and statuses.

Modular Design: Separates scanning, monitoring, quarantine, updating, and reporting into individual Python modules.


Technologies Used

1.Python 3

2.Tkinter

3.hashlib

4.pathlib

5.watchdog

6.CSV file handling

7.Kali Linux

8.Project Structure


SmartAntivirus/

└──main.py

└──scanner.py

└──database.py

└──quarantine_manager.py

└──monitor.py

└──updater.py

└──report_logger.py

└──signatures.txt

└──requirements.txt

└──README.md

└──.gitignore

└──test_folder/

└──quarantine/

└── reports/


Installation

1. Install system dependencies

On Kali Linux or a compatible Debian-based system:

sudo apt update
sudo apt install python3-tk python3-venv

2. Clone the repository

Replace the placeholder with your GitHub repository URL:

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SmartAntivirus

3. Create and activate a virtual environment

python3 -m venv .venv
source .venv/bin/activate

4. Install dependencies

python -m pip install -r requirements.txt

Usage

Start the application:

python main.py

Select a folder using Browse.

Click Scan Folder to scan its files.

Use Start Monitoring to scan newly created or modified files in the selected folder.

Use Update Signatures to supply a trusted HTTPS URL containing SHA-256 hashes, one per line.

Review scan history in reports/scan_report.csv.

Signature Database Format

The signatures.txt file contains one SHA-256 hash per line.

Only add signatures from sources you trust. This prototype validates the hash format but does not authenticate the publisher or verify a digital signature for the downloaded database.

Testing

The application was tested with harmless text files to verify:

SHA-256 calculation and signature matching.

Detection of a deliberately matching test hash.

Moving a matching file into quarantine.

Automatic scanning after a file-system event.

CSV scan-report creation.

The matching test hash was removed after testing.

Limitations

This is an educational prototype, not a replacement for commercial antivirus or endpoint detection software.

A NO_MATCH result does not prove a file is safe.

Detection depends on the signatures available in the local database.

Real-time monitoring covers only the selected folder's immediate contents, not its subfolders.

Signature format validation does not establish that a downloaded database is authentic.

This project does not provide behavioural analysis, memory scanning, kernel protection, or comprehensive ransomware protection.

Quarantine functionality should be improved before use on important files.

Future Improvements

Authenticate signature databases using digital signatures.

Add safe quarantine restoration.

Add recursive monitoring and scan progress.

Add automated unit tests.

Improve error handling and application logging.

Package the application for easier installation.

Disclaimer

This project is intended for educational use and authorised testing. Do not rely on it as your only security protection.

Author

Nageshwaran

