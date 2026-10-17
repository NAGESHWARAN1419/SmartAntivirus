from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
SIGNATURES_FILE = BASE_DIR / "signatures.txt"

SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


def load_signatures():
    """Load valid SHA-256 signatures into a set."""
    signatures = set()

    if not SIGNATURES_FILE.exists():
        SIGNATURES_FILE.touch()

    with SIGNATURES_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            value = line.strip().lower()

            if SHA256_PATTERN.fullmatch(value):
                signatures.add(value)

    return signatures


def validate_signatures(text):
    """Return valid hashes, or raise an error if any line is invalid."""
    lines = text.splitlines()
    hashes = []

    for line in lines:
        value = line.strip().lower()

        if not value:
            continue

        if not SHA256_PATTERN.fullmatch(value):
            raise ValueError("Invalid SHA-256 signature: " + value)

        hashes.append(value)

    if not hashes:
        raise ValueError("The database contains no valid hashes.")

    return set(hashes)
