import logging
import time
from flask import request, g

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("testa")


def register_logging(app):
    @app.before_request
    def before_request():
        g.start_time = time.time()
        logger.info(f"→ {request.method} {request.path}")

    @app.after_request
    def after_request(response):
        duration = time.time() - getattr(g, "start_time", time.time())
        logger.info(f"← {request.method} {request.path} [{response.status_code}] {duration*1000:.1f}ms")
        return response