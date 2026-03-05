import time
import uuid
from services.test_service import TestService


class TestController:
    def __init__(self):
        self.service = TestService()

    def run_all_tests(self, session_id: str, source_dir: str, options: dict) -> dict:
        started_at = time.time()

        results = self.service.run_tests(session_id, source_dir, options)

        duration = round(time.time() - started_at, 2)
        results["meta"] = {
            "session_id": session_id,
            "duration_seconds": duration,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        return results