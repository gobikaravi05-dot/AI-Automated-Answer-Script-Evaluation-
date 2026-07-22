from flask import Blueprint, request
import os
from werkzeug.utils import secure_filename
from database.models import save_upload

upload_bp = Blueprint("upload", __name__)

UPLOAD_FOLDER = "uploads"


@upload_bp.route("/upload", methods=["POST"])
def upload_file():

    if "file" not in request.files:
        return {
            "status": "error",
            "message": "No file uploaded"
        }, 400

    file = request.files["file"]

    if file.filename == "":
        return {
            "status": "error",
            "message": "No file selected"
        }, 400

    filename = secure_filename(file.filename)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    save_upload(filename, filepath)

    return {
        "status": "success",
        "message": "File uploaded successfully",
        "filename": filename,
        "path": filepath
    }