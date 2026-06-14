from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}
MAX_FILE_SIZE = 10 * 1024 * 1024


class LocalStorageService:
    def __init__(self, base_path: Path | None = None) -> None:
        self.base_path = base_path or Path(__file__).resolve().parents[2] / "storage" / "uploads"
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile, entity_type: str) -> tuple[str, str, int]:
        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

        content = await file.read()
        file_size = len(content)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

        suffix = Path(file.filename or "upload").suffix
        stored_file_name = f"{uuid4().hex}{suffix}"
        folder = self.base_path / entity_type
        folder.mkdir(parents=True, exist_ok=True)
        storage_key = f"{entity_type}/{stored_file_name}"
        (folder / stored_file_name).write_bytes(content)
        return stored_file_name, storage_key, file_size

    def get_file_path(self, storage_key: str) -> Path:
        path = self.base_path / storage_key
        if not path.exists() or not path.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        return path

    def delete_file(self, storage_key: str) -> None:
        path = self.base_path / storage_key
        if path.exists() and path.is_file():
            path.unlink()


storage_service = LocalStorageService()

