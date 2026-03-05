from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import zipfile
import tarfile
import shutil
from werkzeug.utils import secure_filename

from controllers.test_controller import TestController

test_bp = Blueprint("tests", __name__)
controller = TestController()


def allowed_file(filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@test_bp.route("/run", methods=["POST"])
def run_tests():
   # AFTER
    uploaded_files = request.files.getlist("file")
    uploaded_files = [f for f in uploaded_files if f and f.filename]  # filter empty
    if not uploaded_files:
        return jsonify({"error": "No file uploaded"}), 400

    session_id = str(uuid.uuid4())
    upload_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], session_id)
    os.makedirs(upload_dir, exist_ok=True)

    for file in uploaded_files:
        if not file.filename:
            continue
        rel_path = request.form.getlist("paths")[uploaded_files.index(file)] if request.form.getlist("paths") else file.filename
        safe_path = os.path.join(upload_dir, "extracted", rel_path)
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        file.save(safe_path)

    # Extract archives
    # extract_dir = os.path.join(upload_dir, "extracted")
    # os.makedirs(extract_dir, exist_ok=True)

    # if filename.endswith(".zip"):
    #     with zipfile.ZipFile(filepath, "r") as z:
    #         z.extractall(extract_dir)
    # elif filename.endswith((".tar.gz", ".tar")):
    #     with tarfile.open(filepath, "r:*") as t:
    #         t.extractall(extract_dir)
    # else:
    #     shutil.copy(filepath, extract_dir)

    options = {
        "ui_testing": request.form.get("ui_testing", "true") == "true",
        "api_testing": request.form.get("api_testing", "true") == "true",
        "chart_testing": request.form.get("chart_testing", "true") == "true",
        "sonarqube": request.form.get("sonarqube", "true") == "true",
        "performance": request.form.get("performance", "true") == "true",
        "security": request.form.get("security", "true") == "true",
    }

    # result = controller.run_all_tests(session_id, extract_dir, options)
    extract_dir = os.path.join(upload_dir, "extracted")
    result = controller.run_all_tests(session_id, extract_dir, options)

    # Cleanup
    shutil.rmtree(upload_dir, ignore_errors=True)

    return jsonify(result)


@test_bp.route("/status/<session_id>", methods=["GET"])
def get_status(session_id):
    return jsonify({"session_id": session_id, "status": "completed"})