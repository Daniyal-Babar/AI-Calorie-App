import os
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.upload_service import UploadService

uploads_bp = Blueprint("uploads", __name__, url_prefix="/api/uploads")

@uploads_bp.route("", methods=["POST"])
@jwt_required()
def upload_file():
    user_id = int(get_jwt_identity())
    if "file" not in request.files:
        return jsonify({"error": "No file attached in multipart form"}), 400

    file = request.files["file"]
    try:
        saved = UploadService.save_upload(file, user_id)
        return jsonify({
            "message": "File uploaded successfully",
            "image_id": saved["image_id"],
            "filename": saved["filename"],
            "url": f"/api/uploads/{saved['image_id']}",
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@uploads_bp.route("/<image_id>", methods=["GET"])
def get_uploaded_file(image_id: str):
    file_path = UploadService.get_file_path(image_id)
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Image not found"}), 404
    return send_file(file_path)
