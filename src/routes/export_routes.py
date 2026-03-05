from flask import Blueprint, request, jsonify, send_file
from controllers.export_controller import ExportController

export_bp = Blueprint("export", __name__)
controller = ExportController()


@export_bp.route("/pdf", methods=["POST"])
def export_pdf():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    filepath = controller.export_pdf(data)
    return send_file(filepath, as_attachment=True, download_name="testa_report.pdf", mimetype="application/pdf")


@export_bp.route("/pptx", methods=["POST"])
def export_pptx():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    filepath = controller.export_pptx(data)
    return send_file(filepath, as_attachment=True, download_name="testa_report.pptx",
                     mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation")


@export_bp.route("/docx", methods=["POST"])
def export_docx():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    filepath = controller.export_docx(data)
    return send_file(filepath, as_attachment=True, download_name="testa_report.docx",
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")