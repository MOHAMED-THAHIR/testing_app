from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "app": "Testa", "version": "1.0.0"})