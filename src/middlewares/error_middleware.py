from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad Request", "message": str(e), "status": 400}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not Found", "message": str(e), "status": 404}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File Too Large", "message": "Max upload size is 100MB", "status": 413}), 413

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred", "status": 500}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.exception(f"Unhandled exception: {e}")
        return jsonify({"error": "Server Error", "message": str(e), "status": 500}), 500