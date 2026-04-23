from pathlib import Path
from uuid import uuid4


class LocalStorageService:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, data: bytes, original_name: str) -> str:
        target = self.root / f"{uuid4()}_{original_name}"
        target.write_bytes(data)
        return str(target)

    def open_file(self, path: str) -> Path:
        return Path(path)
