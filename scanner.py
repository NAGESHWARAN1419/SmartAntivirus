from pathlib import Path
import hashlib

from database import load_signatures
from quarantine_manager import quarantine_file
from report_logger import log_result


def calculate_sha256(file_path):
    """Calculate a file's SHA-256 hash without loading it all into memory."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def scan_file(file_path, signatures=None):
    path = Path(file_path)

    result = {
        "file": str(path),
        "sha256": "",
        "status": "ERROR",
        "details": ""
    }

    try:
        if path.is_symlink() or not path.is_file():
            result["details"] = "Skipped: not a regular file."
            return result

        # Do not scan files that are already in quarantine.
        quarantine_dir = (Path(__file__).resolve().parent / "quarantine").resolve()
        resolved_path = path.resolve()

        if resolved_path == quarantine_dir or quarantine_dir in resolved_path.parents:
            result["details"] = "Skipped: already in quarantine."
            return result

        file_hash = calculate_sha256(path)
        result["sha256"] = file_hash

        if signatures is None:
            signatures = load_signatures()

        if file_hash in signatures:
            result["status"] = "DETECTED"

            try:
                destination = quarantine_file(path)
                result["details"] = "Signature match. Quarantined at: " + destination
            except OSError as error:
                result["details"] = (
                    "Signature match, but quarantine failed: " + str(error)
                )
            except ValueError as error:
                result["details"] = (
                    "Signature match, but quarantine failed: " + str(error)
                )

        else:
            result["status"] = "NO_MATCH"
            result["details"] = (
                "No known signature matched; this does not prove the file is safe."
            )

    except (OSError, PermissionError) as error:
        result["details"] = "File could not be scanned: " + str(error)

    log_result(result)
    return result


def scan_folder(folder_path, on_result=None):
    """Scan regular files directly inside the chosen folder."""
    folder = Path(folder_path)

    if not folder.is_dir():
        raise ValueError("Please select a valid folder.")

    signatures = load_signatures()
    results = []

    for path in folder.iterdir():
        if path.is_symlink() or not path.is_file():
            continue

        result = scan_file(path, signatures)
        results.append(result)

        if on_result:
            on_result(result)

    return results
