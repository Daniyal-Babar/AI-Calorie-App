import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app

class UploadService:
    @staticmethod
    def allowed_file(filename: str) -> bool:
        allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "webp"})
        return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

    @staticmethod
    def save_upload(file_storage, user_id: int) -> dict:
        """Validate and save an uploaded image file."""
        if not file_storage or file_storage.filename == "":
            raise ValueError("No file uploaded or empty filename.")

        if not UploadService.allowed_file(file_storage.filename):
            raise ValueError("File type not allowed. Please upload PNG, JPG, JPEG, or WEBP.")

        upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
        upload_folder.mkdir(parents=True, exist_ok=True)

        ext = file_storage.filename.rsplit(".", 1)[1].lower()
        image_id = f"img_{uuid.uuid4().hex[:16]}"
        safe_name = f"{image_id}_{user_id}.{ext}"
        target_path = upload_folder / safe_name

        file_storage.save(str(target_path))

        return {
            "image_id": image_id,
            "filename": safe_name,
            "path": str(target_path),
            "size_bytes": target_path.stat().st_size,
        }

    @staticmethod
    def get_file_path(image_id: str) -> str | None:
        """Find the file corresponding to image_id in upload folder."""
        upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
        if not upload_folder.exists():
            return None

        for file_path in upload_folder.glob(f"{image_id}*"):
            return str(file_path)
        return None
