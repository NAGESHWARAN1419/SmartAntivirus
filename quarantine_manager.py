from pathlib import Path
import shutil
import uuid

BASE_DIR = Path(__file__).resolve().parent
QUARANTINE_DIR = BASE_DIR / "quarantine"


def quarantine_file(file_path):
    source = Path(file_path).resolve()
    quarantine_dir = QUARANTINE_DIR.resolve()

    if not source.is_file():
        raise ValueError("The selected path is not a regular file.")

    if source.is_symlink():
        raise ValueError("Symbolic links are not supported.")

    if source == quarantine_dir or quarantine_dir in source.parents:
        raise ValueError("The file is already inside quarantine.")

    quarantine_dir.mkdir(parents=True, exist_ok=True)

    destination = quarantine_dir / (
        source.name + "." + uuid.uuid4().hex[:8] + ".quarantined"
    )

    shutil.move(str(source), str(destination))

    return str(destination)
