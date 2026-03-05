import re
from typing import List, Dict


class SecurityAnalyzer:
    """Analyzes security: OWASP top 10, dependency risks, auth patterns, secrets."""

    SUITE_NAME = "Security & Load Testing"

    def analyze(self, files: List[Dict]) -> Dict:
        tests = []
        tests.extend(self._check_xss(files))
        tests.extend(self._check_csrf(files))
        tests.extend(self._check_https_enforcement(files))
        tests.extend(self._check_sensitive_data_exposure(files))
        tests.extend(self._check_security_headers(files))
        tests.extend(self._check_password_hashing(files))
        tests.extend(self._check_jwt_security(files))
        tests.extend(self._check_env_variables(files))
        tests.extend(self._check_dependency_security(files))
        tests.extend(self._check_load_testing_readiness(files))
        tests.extend(self._check_dos_protection(files))
        return self._build_suite(tests)

    def _check_xss(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_xss_risk = bool(re.search(r"dangerouslySetInnerHTML|\.innerHTML\s*=|v-html=|document\.write\(", c))
            if has_xss_risk:
                has_sanitize = bool(re.search(r"DOMPurify|sanitize|escapeHtml|htmlspecialchars|xss", c, re.IGNORECASE))
                results.append(self._make_test(
                    f"XSS protection [{f['path']}]",
                    "failed" if not has_sanitize else "warning",
                    "HTML injection detected. Sanitization: " + ("present" if has_sanitize else "MISSING — XSS risk"),
                    "xss"
                ))
        return results

    def _check_csrf(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_forms = bool(re.search(r"<form|FormData|POST|post\(", all_content))
        if has_forms:
            has_csrf = bool(re.search(r"csrf|CSRF|_token|csrfToken|WTForms|flask_wtf|csurf", all_content, re.IGNORECASE))
            results.append(self._make_test(
                "CSRF protection",
                "passed" if has_csrf else "warning",
                "CSRF protection: " + ("present" if has_csrf else "not found for form submissions"),
                "csrf"
            ))
        return results

    def _check_https_enforcement(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        http_urls = re.findall(r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)\S+", all_content)
        if http_urls:
            results.append(self._make_test(
                "HTTPS enforcement",
                "warning",
                f"Non-HTTPS URLs found: {', '.join(set(http_urls[:3]))}",
                "https"
            ))
        else:
            results.append(self._make_test(
                "HTTPS enforcement",
                "passed",
                "No non-HTTPS URLs detected in production code",
                "https"
            ))
        return results

    def _check_sensitive_data_exposure(self, files):
        results = []
        for f in files:
            c = f["content"]
            sensitive = []
            if re.search(r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']+["\']', c):
                sensitive.append("hardcoded password")
            if re.search(r'(?i)(api_key|apikey|api-key)\s*[=:]\s*["\'][^"\']+["\']', c):
                sensitive.append("hardcoded API key")
            if re.search(r'(?i)(secret_key|secret)\s*[=:]\s*["\'][a-z0-9]{8,}["\']', c):
                sensitive.append("hardcoded secret")
            if re.search(r"-----BEGIN\s+(?:RSA\s+)?PRIVATE KEY", c):
                sensitive.append("private key in source code")
            if sensitive:
                results.append(self._make_test(
                    f"Sensitive data exposure [{f['path']}]",
                    "failed",
                    "CRITICAL: " + ", ".join(sensitive),
                    "data_exposure"
                ))
        return results

    def _check_security_headers(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_helmet = bool(re.search(r"helmet\(|flask_talisman|Talisman|secure_headers|HSTS|X-Frame-Options|Content-Security-Policy", all_content))
        results.append(self._make_test(
            "Security headers",
            "passed" if has_helmet else "warning",
            "Security headers (Helmet/CSP/HSTS): " + ("configured" if has_helmet else "not found"),
            "headers"
        ))
        return results

    def _check_password_hashing(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_password_field = bool(re.search(r"password|passwd", all_content, re.IGNORECASE))
        if has_password_field:
            has_proper_hash = bool(re.search(r"bcrypt|argon2|scrypt|pbkdf2|werkzeug\.security|check_password_hash|make_password|hashpw", all_content))
            has_weak_hash = bool(re.search(r"md5|sha1\b|sha256.*password", all_content, re.IGNORECASE))
            status = "passed" if has_proper_hash else ("failed" if has_weak_hash else "warning")
            results.append(self._make_test(
                "Password hashing",
                status,
                "Hash algorithm: " + ("bcrypt/argon2 ✓" if has_proper_hash else ("WEAK HASH (md5/sha1) ✗" if has_weak_hash else "not detected")),
                "auth"
            ))
        return results

    def _check_jwt_security(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_jwt = bool(re.search(r"jwt|JWT|jsonwebtoken|flask_jwt", all_content))
        if has_jwt:
            has_expiry = bool(re.search(r"exp|expiresIn|expires_in|EXPIRE|ACCESS_TOKEN_EXPIRE", all_content))
            has_refresh = bool(re.search(r"refresh_token|refreshToken|REFRESH", all_content))
            issues = []
            if not has_expiry:
                issues.append("no token expiry")
            if not has_refresh:
                issues.append("no refresh token pattern")
            results.append(self._make_test(
                "JWT security",
                "passed" if not issues else "warning",
                ("JWT secure: expiry + refresh found" if not issues else "JWT issues: " + ", ".join(issues)),
                "auth"
            ))
        return results

    def _check_env_variables(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_env_usage = bool(re.search(r"process\.env\.|os\.environ|os\.getenv|\.env", all_content))
        has_dotenv = bool(re.search(r"dotenv|load_dotenv|python-dotenv", all_content))
        results.append(self._make_test(
            "Environment variable usage",
            "passed" if has_env_usage else "warning",
            f"Env vars: {'used' if has_env_usage else 'not found'}. dotenv: {'configured' if has_dotenv else 'not found'}",
            "config"
        ))
        return results

    def _check_dependency_security(self, files):
        results = []
        pkg_files = [f for f in files if f["name"] in {"package.json", "requirements.txt", "Pipfile", "pyproject.toml"}]
        if pkg_files:
            for f in pkg_files:
                c = f["content"]
                # Check for known vulnerable patterns
                has_audit_script = bool(re.search(r"npm audit|safety check|bandit|snyk", c))
                results.append(self._make_test(
                    f"Dependency security audit [{f['path']}]",
                    "warning",
                    "Dependency file found. Run npm audit / pip-audit for vulnerability scan.",
                    "dependencies"
                ))
        return results

    def _check_load_testing_readiness(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_health_check = bool(re.search(r"/health|/ping|/status|health_check", all_content))
        has_graceful_shutdown = bool(re.search(r"SIGTERM|graceful|beforeExit|atexit", all_content))
        has_connection_pool = bool(re.search(r"pool|Pool|connection_pool|max_connections|pool_size", all_content))

        results.append(self._make_test(
            "Load testing readiness: health endpoint",
            "passed" if has_health_check else "warning",
            "Health check endpoint: " + ("present" if has_health_check else "missing — needed for load balancers"),
            "load_testing"
        ))
        results.append(self._make_test(
            "Load testing readiness: connection pooling",
            "passed" if has_connection_pool else "warning",
            "DB connection pooling: " + ("configured" if has_connection_pool else "not found — may fail under load"),
            "load_testing"
        ))
        results.append(self._make_test(
            "Load testing readiness: graceful shutdown",
            "passed" if has_graceful_shutdown else "warning",
            "Graceful shutdown: " + ("implemented" if has_graceful_shutdown else "not found"),
            "load_testing"
        ))
        return results

    def _check_dos_protection(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_rate_limit = bool(re.search(r"rateLimit|rate_limit|throttle|limiter|flask.limiter", all_content, re.IGNORECASE))
        has_max_size = bool(re.search(r"MAX_CONTENT_LENGTH|maxFileSize|max_upload|body-parser.*limit|MAX_SIZE", all_content))

        results.append(self._make_test(
            "DoS protection: rate limiting",
            "passed" if has_rate_limit else "warning",
            "Rate limiting: " + ("configured" if has_rate_limit else "not found — DoS risk"),
            "dos_protection"
        ))
        results.append(self._make_test(
            "DoS protection: request size limits",
            "passed" if has_max_size else "warning",
            "Max request size: " + ("set" if has_max_size else "not configured"),
            "dos_protection"
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
            "icon": "lock",
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "tests": tests,
        }