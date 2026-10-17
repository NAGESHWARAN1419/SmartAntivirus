from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import os
import tempfile

from database import SIGNATURES_FILE, validate_signatures


def update_signatures(url):
    parsed = urlparse(url)

    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Please provide a valid HTTPS URL.")

    request = Request(
        url,
        headers={"User-Agent": "SmartAntivirus-Educational/1.0"}
    )

    with urlopen(request, timeout=15) as response:
        content = response.read(5 * 1024 * 1024 + 1)

    if len(content) > 5 * 1024 * 1024:
        raise ValueError("Signature download is too large.")

    text = content.decode("utf-8")

    # Validate before changing the existing database.
    signatures = validate_signatures(text)

    database_path = Path(SIGNATURES_FILE)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=database_path.parent,
            delete=False
        ) as temporary_file:
            temporary_path = temporary_file.name
            for signature in sorted(signatures):
                temporary_file.write(signature + "\n")

        os.replace(temporary_path, database_path)
        temporary_path = None

    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)

    return len(signatures)
