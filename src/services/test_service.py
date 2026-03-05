import os
from analyzers.ui_analyzer import UIAnalyzer
from analyzers.api_analyzer import APIAnalyzer
from analyzers.chart_analyzer import ChartAnalyzer
from analyzers.sonarqube_analyzer import SonarQubeAnalyzer
from analyzers.performance_analyzer import PerformanceAnalyzer
from analyzers.security_analyzer import SecurityAnalyzer
from repositories.test_repository import TestRepository


class TestService:
    def __init__(self):
        self.ui_analyzer = UIAnalyzer()
        self.api_analyzer = APIAnalyzer()
        self.chart_analyzer = ChartAnalyzer()
        self.sonar_analyzer = SonarQubeAnalyzer()
        self.perf_analyzer = PerformanceAnalyzer()
        self.sec_analyzer = SecurityAnalyzer()
        self.repo = TestRepository()

    def run_tests(self, session_id: str, source_dir: str, options: dict) -> dict:
        all_files = self._collect_files(source_dir)
        suites = []
        summary = {"total": 0, "passed": 0, "failed": 0, "warnings": 0, "skipped": 0}

        if options.get("ui_testing"):
            suite = self.ui_analyzer.analyze(all_files)
            suites.append(suite)
            self._accumulate(summary, suite)

        if options.get("api_testing"):
            suite = self.api_analyzer.analyze(all_files)
            suites.append(suite)
            self._accumulate(summary, suite)

        if options.get("chart_testing"):
            suite = self.chart_analyzer.analyze(all_files)
            suites.append(suite)
            self._accumulate(summary, suite)

        if options.get("sonarqube"):
            suite = self.sonar_analyzer.analyze(all_files)
            suites.append(suite)
            self._accumulate(summary, suite)

        if options.get("performance"):
            suite = self.perf_analyzer.analyze(all_files)
            suites.append(suite)
            self._accumulate(summary, suite)

        if options.get("security"):
            suite = self.sec_analyzer.analyze(all_files)
            suites.append(suite)
            self._accumulate(summary, suite)

        pass_rate = round((summary["passed"] / summary["total"] * 100), 1) if summary["total"] > 0 else 0

        return {
            "session_id": session_id,
            "summary": {**summary, "pass_rate": pass_rate},
            "suites": suites,
            "file_count": len(all_files),
            "files_analyzed": [f["path"] for f in all_files[:50]],
        }

    def _collect_files(self, source_dir: str) -> list:
        files = []
        code_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".vue", ".html",
            ".css", ".scss", ".java", ".cs", ".go", ".rb", ".php",
            ".swift", ".kt", ".rs", ".cpp", ".c", ".h", ".json",
            ".yaml", ".yml", ".xml",
        }
        skip_dirs = {"node_modules", ".git", "__pycache__", "dist", "build", ".next", "venv", ".venv"}

        for root, dirs, filenames in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in code_extensions:
                    full_path = os.path.join(root, fname)
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        files.append({
                            "path": os.path.relpath(full_path, source_dir),
                            "name": fname,
                            "ext": ext,
                            "content": content,
                            "size": os.path.getsize(full_path),
                            "lines": content.count("\n") + 1,
                        })
                    except Exception:
                        pass
        return files

    def _accumulate(self, summary: dict, suite: dict):
        for test in suite.get("tests", []):
            summary["total"] += 1
            status = test.get("status", "skipped")
            if status == "passed":
                summary["passed"] += 1
            elif status == "failed":
                summary["failed"] += 1
            elif status == "warning":
                summary["warnings"] += 1
            else:
                summary["skipped"] += 1