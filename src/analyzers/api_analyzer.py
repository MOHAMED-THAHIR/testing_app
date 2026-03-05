import re
from typing import List, Dict


class APIAnalyzer:
    """Analyzes API definitions: REST patterns, validation, error handling, versioning."""

    SUITE_NAME = "API Validation Testing"

    def analyze(self, files: List[Dict]) -> Dict:
        tests = []
        tests.extend(self._check_api_versioning(files))
        tests.extend(self._check_http_methods(files))
        tests.extend(self._check_request_validation(files))
        tests.extend(self._check_response_codes(files))
        tests.extend(self._check_error_handling(files))
        tests.extend(self._check_authentication(files))
        tests.extend(self._check_rate_limiting(files))
        tests.extend(self._check_cors(files))
        tests.extend(self._check_api_documentation(files))
        tests.extend(self._check_pagination(files))
        tests.extend(self._check_input_sanitization(files))
        tests.extend(self._check_timeout_handling(files))

        return self._build_suite(tests)

    def _check_api_versioning(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_versioning = bool(re.search(r"/api/v\d+|/v\d+/|version.*=.*[\"']\d|apiVersion", all_content))
        results.append(self._make_test(
            "API versioning",
            "passed" if has_versioning else "warning",
            "API versioning pattern (e.g., /api/v1): " + ("detected" if has_versioning else "not found"),
            "api_design"
        ))
        return results

    def _check_http_methods(self, files):
        results = []
        for f in files:
            c = f["content"]
            if f["ext"] in {".py", ".js", ".ts"}:
                has_get = bool(re.search(r'@app\.get|router\.get|\.get\(|"GET"', c))
                has_post = bool(re.search(r'@app\.post|router\.post|\.post\(|"POST"', c))
                has_put_patch = bool(re.search(r'@app\.put|router\.put|\.put\(|"PUT"|PATCH|router\.patch', c))
                has_delete = bool(re.search(r'@app\.delete|router\.delete|\.delete\(|"DELETE"', c))
                methods = [m for m, present in [("GET", has_get), ("POST", has_post), ("PUT/PATCH", has_put_patch), ("DELETE", has_delete)] if present]
                if methods:
                    results.append(self._make_test(
                        f"HTTP methods [{f['path']}]",
                        "passed",
                        f"Methods found: {', '.join(methods)}",
                        "api_design"
                    ))
        return results

    def _check_request_validation(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_route = bool(re.search(r'@app\.(get|post|put|delete|patch)|router\.(get|post|put|delete)', c))
            if has_route:
                has_validation = bool(re.search(
                    r"Joi|zod|yup|pydantic|marshmallow|cerberus|jsonschema|validator|validate|request\.json\.get|body\.",
                    c
                ))
                results.append(self._make_test(
                    f"Request body validation [{f['path']}]",
                    "passed" if has_validation else "failed",
                    "Input validation: " + ("present" if has_validation else "MISSING — inputs not validated"),
                    "api_validation"
                ))
        return results

    def _check_response_codes(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_route = bool(re.search(r'@app\.(get|post|put|delete)|router\.(get|post)', c))
            if has_route:
                has_proper_codes = bool(re.search(
                    r"201|204|400|401|403|404|422|500|status_code|status=|\.status\(", c
                ))
                results.append(self._make_test(
                    f"HTTP status codes [{f['path']}]",
                    "passed" if has_proper_codes else "warning",
                    "Proper HTTP status codes: " + ("used" if has_proper_codes else "only 200 detected"),
                    "api_design"
                ))
        return results

    def _check_error_handling(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_route = bool(re.search(r'@app\.(get|post|put|delete)|router\.(get|post)', c))
            if has_route:
                has_try_catch = bool(re.search(r"try:|try\s*{|except\s+|\.catch\(|onError", c))
                results.append(self._make_test(
                    f"API error handling [{f['path']}]",
                    "passed" if has_try_catch else "failed",
                    "Error handling: " + ("present" if has_try_catch else "MISSING — unhandled exceptions possible"),
                    "api_validation"
                ))
        return results

    def _check_authentication(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_auth = bool(re.search(
            r"jwt|JWT|bearer|Bearer|token|Token|auth|Auth|passport|@login_required|authenticate|middleware.*auth",
            all_content
        ))
        results.append(self._make_test(
            "Authentication mechanisms",
            "passed" if has_auth else "warning",
            "Auth patterns (JWT/token/middleware): " + ("detected" if has_auth else "not found"),
            "security"
        ))
        return results

    def _check_rate_limiting(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_rate_limit = bool(re.search(r"rateLimit|rate.limit|throttle|limiter|flask.limiter|express-rate-limit", all_content, re.IGNORECASE))
        results.append(self._make_test(
            "Rate limiting",
            "passed" if has_rate_limit else "warning",
            "Rate limiting: " + ("configured" if has_rate_limit else "not detected"),
            "security"
        ))
        return results

    def _check_cors(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_cors = bool(re.search(r"cors|CORS|flask.cors|Access-Control", all_content, re.IGNORECASE))
        results.append(self._make_test(
            "CORS configuration",
            "passed" if has_cors else "warning",
            "CORS: " + ("configured" if has_cors else "not found — cross-origin may fail"),
            "api_design"
        ))
        return results

    def _check_api_documentation(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_docs = bool(re.search(r"swagger|openapi|apidoc|@api|@swagger|flasgger|fastapi|@Operation", all_content, re.IGNORECASE))
        results.append(self._make_test(
            "API documentation",
            "passed" if has_docs else "warning",
            "API docs (Swagger/OpenAPI): " + ("present" if has_docs else "not found"),
            "api_design"
        ))
        return results

    def _check_pagination(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_list_endpoints = bool(re.search(r"getAll|findAll|list|\.find\(\)", all_content))
        has_pagination = bool(re.search(r"page|limit|offset|cursor|per_page|pageSize|paginate", all_content))
        if has_list_endpoints:
            results.append(self._make_test(
                "Pagination on list endpoints",
                "passed" if has_pagination else "warning",
                "Pagination: " + ("implemented" if has_pagination else "missing on list endpoints"),
                "api_design"
            ))
        return results

    def _check_input_sanitization(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_sql = bool(re.search(r"SELECT|INSERT|UPDATE|DELETE|FROM|WHERE", c, re.IGNORECASE))
            if has_sql:
                has_parameterized = bool(re.search(r"%s|:param|bindparams|cursor\.execute\(.+,|\.filter\(|ORM", c))
                results.append(self._make_test(
                    f"SQL injection prevention [{f['path']}]",
                    "passed" if has_parameterized else "failed",
                    "Parameterized queries: " + ("used" if has_parameterized else "MISSING — SQL injection risk"),
                    "security"
                ))
        return results

    def _check_timeout_handling(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_http_calls = bool(re.search(r"requests\.|fetch\(|axios|http\.get|urllib", all_content))
        has_timeout = bool(re.search(r"timeout=|timeout:|TIMEOUT|request_timeout", all_content))
        if has_http_calls:
            results.append(self._make_test(
                "HTTP timeout configuration",
                "passed" if has_timeout else "warning",
                "Timeout on HTTP calls: " + ("set" if has_timeout else "not configured — potential hanging requests"),
                "api_validation"
            ))
        return results

    def _make_test(self, name, status, message, category):
        return {"name": name, "status": status, "message": message, "category": category}

    def _build_suite(self, tests):
        passed = sum(1 for t in tests if t["status"] == "passed")
        failed = sum(1 for t in tests if t["status"] == "failed")
        warnings = sum(1 for t in tests if t["status"] == "warning")
        return {
            "suite": self.SUITE_NAME,
            "icon": "network",
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "tests": tests,
        }