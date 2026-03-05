import re
import ast
import os
from typing import List, Dict


class SonarQubeAnalyzer:
    """
    Simulates SonarQube-style analysis with metrics:
    - Code smells, Bugs, Vulnerabilities, Security Hotspots
    - Cognitive Complexity, Cyclomatic Complexity
    - Duplications, Test Coverage signals
    - Maintainability Rating, Reliability Rating, Security Rating
    - Technical Debt, Lines of Code
    """

    SUITE_NAME = "SonarQube Code Quality"

    def analyze(self, files: List[Dict]) -> Dict:
        tests = []
        tests.extend(self._check_complexity(files))
        tests.extend(self._check_duplications(files))
        tests.extend(self._check_code_smells(files))
        tests.extend(self._check_bugs(files))
        tests.extend(self._check_vulnerabilities(files))
        tests.extend(self._check_security_hotspots(files))
        tests.extend(self._check_test_coverage_signals(files))
        tests.extend(self._check_maintainability(files))
        tests.extend(self._check_documentation(files))
        tests.extend(self._check_naming_conventions(files))
        tests.extend(self._check_dead_code(files))
        tests.extend(self._check_cognitive_complexity(files))
        tests.extend(self._check_function_length(files))
        tests.extend(self._check_file_length(files))
        tests.extend(self._check_nesting_depth(files))
        tests.extend(self._check_type_safety(files))
        tests.extend(self._check_console_logs(files))
        tests.extend(self._check_todo_fixme(files))

        return self._build_suite(tests)

    def _check_complexity(self, files):
        results = []
        for f in files:
            if f["ext"] == ".py":
                try:
                    tree = ast.parse(f["content"])
                    func_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))
                    # Estimate cyclomatic complexity by counting branches
                    branch_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)))
                    avg_complexity = (branch_count / func_count) if func_count > 0 else 0
                    status = "passed" if avg_complexity < 10 else ("warning" if avg_complexity < 15 else "failed")
                    results.append(self._make_test(
                        f"Cyclomatic complexity [{f['path']}]",
                        status,
                        f"Avg complexity: {avg_complexity:.1f} (threshold: 10). Functions: {func_count}, Branches: {branch_count}",
                        "complexity"
                    ))
                except SyntaxError as e:
                    results.append(self._make_test(
                        f"Syntax check [{f['path']}]",
                        "failed",
                        f"Syntax error: {e}",
                        "bugs"
                    ))
            elif f["ext"] in {".js", ".ts", ".jsx", ".tsx"}:
                # JS complexity heuristic
                branches = len(re.findall(r"\bif\b|\bfor\b|\bwhile\b|\bswitch\b|\bcatch\b|\?\s*\w", f["content"]))
                funcs = len(re.findall(r"function\s+\w|=>\s*{|\bfunction\b\s*\(", f["content"]))
                if funcs > 0:
                    avg = branches / funcs
                    status = "passed" if avg < 10 else ("warning" if avg < 15 else "failed")
                    results.append(self._make_test(
                        f"Cyclomatic complexity [{f['path']}]",
                        status,
                        f"Estimated avg complexity: {avg:.1f}",
                        "complexity"
                    ))
        return results

    def _check_duplications(self, files):
        results = []
        # Check for duplicated function/block signatures
        seen_signatures = {}
        for f in files:
            c = f["content"]
            func_sigs = re.findall(r"def\s+(\w+)\s*\(|function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\(", c)
            for sig_tuple in func_sigs:
                sig = next((s for s in sig_tuple if s), None)
                if sig:
                    if sig in seen_signatures and sig not in {"__init__", "constructor", "render", "main", "index"}:
                        results.append(self._make_test(
                            f"Code duplication: '{sig}'",
                            "warning",
                            f"Function '{sig}' defined in multiple files: {seen_signatures[sig]} and {f['path']}",
                            "duplications"
                        ))
                    else:
                        seen_signatures[sig] = f["path"]
        if not results:
            results.append(self._make_test(
                "Code duplication check",
                "passed",
                "No significant duplicate function definitions detected",
                "duplications"
            ))
        return results

    def _check_code_smells(self, files):
        results = []
        for f in files:
            c = f["content"]
            smells = []
            # Long parameter lists
            long_params = re.findall(r"def\s+\w+\(([^)]{100,})\)", c)
            if long_params:
                smells.append(f"functions with >5 params")
            # Magic numbers
            magic_nums = re.findall(r"(?<!\w)[2-9]\d{2,}(?!\w)(?!\.\d)", c)
            if len(magic_nums) > 3:
                smells.append(f"{len(magic_nums)} magic numbers")
            # Empty catch blocks
            empty_catches = re.findall(r"except\s*(?:\w+\s*)?:\s*pass|catch\s*\([^)]*\)\s*\{\s*\}", c)
            if empty_catches:
                smells.append(f"{len(empty_catches)} empty catch block(s)")
            # God classes (>500 lines)
            if f["lines"] > 500:
                smells.append(f"large file ({f['lines']} lines)")

            if smells:
                results.append(self._make_test(
                    f"Code smells [{f['path']}]",
                    "warning",
                    "Issues: " + ", ".join(smells),
                    "code_smells"
                ))
            else:
                results.append(self._make_test(
                    f"Code smells [{f['path']}]",
                    "passed",
                    "No major code smells detected",
                    "code_smells"
                ))
        return results

    def _check_bugs(self, files):
        results = []
        for f in files:
            c = f["content"]
            bugs = []
            # Null pointer risks
            if re.search(r"\.length\b", c) and not re.search(r"\?\.|&&.*\.length|if.*length", c):
                bugs.append("potential null reference on .length")
            # == instead of === in JS
            if f["ext"] in {".js", ".ts", ".jsx", ".tsx"}:
                loose_eq = re.findall(r"(?<!=)={2}(?!=)", c)
                if len(loose_eq) > 2:
                    bugs.append(f"{len(loose_eq)} loose equality (==) comparisons")
            # Unclosed resources in Python
            if f["ext"] == ".py":
                open_files = re.findall(r"open\(", c)
                with_files = re.findall(r"with\s+open\(", c)
                unclosed = len(open_files) - len(with_files)
                if unclosed > 0:
                    bugs.append(f"{unclosed} file(s) opened without 'with' context manager")
            # Unreachable code after return
            if re.search(r"return\s+.+\n\s+[^\s#]", c):
                bugs.append("potential unreachable code after return")

            if bugs:
                results.append(self._make_test(
                    f"Bug detection [{f['path']}]",
                    "failed",
                    "Bugs: " + "; ".join(bugs),
                    "bugs"
                ))
            else:
                results.append(self._make_test(
                    f"Bug detection [{f['path']}]",
                    "passed",
                    "No bugs detected",
                    "bugs"
                ))
        return results

    def _check_vulnerabilities(self, files):
        results = []
        for f in files:
            c = f["content"]
            vulns = []
            # Hardcoded secrets
            if re.search(r'(?i)(password|secret|api_key|apikey|token|passwd)\s*=\s*["\'][^"\']{4,}["\']', c):
                vulns.append("hardcoded credentials detected")
            # Eval usage
            if re.search(r"\beval\s*\(|\bexec\s*\(", c):
                vulns.append("dangerous eval/exec usage")
            # Pickle (Python deserialization)
            if re.search(r"pickle\.loads|pickle\.load\b", c):
                vulns.append("unsafe pickle deserialization")
            # Weak hash
            if re.search(r"md5|sha1\b", c, re.IGNORECASE):
                vulns.append("weak hash algorithm (md5/sha1)")
            # Shell injection
            if re.search(r"subprocess\.call\(.+shell=True|os\.system\(", c):
                vulns.append("shell injection risk")

            if vulns:
                results.append(self._make_test(
                    f"Vulnerability scan [{f['path']}]",
                    "failed",
                    "VULNERABILITIES: " + "; ".join(vulns),
                    "vulnerabilities"
                ))
            else:
                results.append(self._make_test(
                    f"Vulnerability scan [{f['path']}]",
                    "passed",
                    "No vulnerabilities detected",
                    "vulnerabilities"
                ))
        return results

    def _check_security_hotspots(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        hotspots = []
        if re.search(r"dangerouslySetInnerHTML|v-html=|innerHTML\s*=", all_content):
            hotspots.append("XSS risk: HTML injection (dangerouslySetInnerHTML/v-html)")
        if re.search(r"localStorage\.|sessionStorage\.", all_content):
            hotspots.append("Sensitive data may be stored in browser storage")
        if re.search(r"http://(?!localhost|127\.0\.0\.1)", all_content):
            hotspots.append("Non-HTTPS URLs in production code")
        if re.search(r"debug\s*=\s*True|DEBUG\s*=\s*True", all_content):
            hotspots.append("Debug mode enabled in code")
        if re.search(r"allow_origins=\[\"\\*\"\]|origins=\[\"\\*\"\]|Access-Control-Allow-Origin.*\*", all_content):
            hotspots.append("Wildcard CORS origin (*) — overly permissive")

        status = "failed" if hotspots else "passed"
        results.append(self._make_test(
            "Security hotspots",
            status,
            ("HOTSPOTS: " + "; ".join(hotspots)) if hotspots else "No security hotspots detected",
            "security_hotspots"
        ))
        return results

    def _check_test_coverage_signals(self, files):
        results = []
        test_files = [f for f in files if "test" in f["name"].lower() or "spec" in f["name"].lower() or f["path"].startswith("tests/")]
        source_files = [f for f in files if "test" not in f["name"].lower() and "spec" not in f["name"].lower()]
        ratio = len(test_files) / max(len(source_files), 1)

        results.append(self._make_test(
            "Test file coverage",
            "passed" if ratio >= 0.3 else ("warning" if ratio >= 0.1 else "failed"),
            f"Test files: {len(test_files)}, Source files: {len(source_files)}, Ratio: {ratio:.0%}",
            "coverage"
        ))
        # Check for test assertions
        if test_files:
            has_assertions = any(re.search(r"assert|expect\(|should\.|toBe\(|assertEqual", f["content"]) for f in test_files)
            results.append(self._make_test(
                "Test assertions present",
                "passed" if has_assertions else "warning",
                "Assertions in test files: " + ("found" if has_assertions else "none found"),
                "coverage"
            ))
        return results

    def _check_maintainability(self, files):
        results = []
        for f in files:
            c = f["content"]
            # Check for magic strings
            magic_strings = re.findall(r'"[a-zA-Z_]{8,}"', c)
            has_constants = bool(re.search(r"CONSTANT|CONST|const\s+[A-Z_]+=|[A-Z_]{4,}\s*=", c))
            if len(magic_strings) > 5 and not has_constants:
                results.append(self._make_test(
                    f"Magic strings [{f['path']}]",
                    "warning",
                    f"{len(magic_strings)} string literals — consider extracting to constants",
                    "maintainability"
                ))
        if not results:
            results.append(self._make_test(
                "Maintainability rating",
                "passed",
                "Maintainability looks good — no major issues",
                "maintainability"
            ))
        return results

    def _check_documentation(self, files):
        results = []
        for f in files:
            c = f["content"]
            if f["ext"] == ".py":
                funcs = re.findall(r"def\s+\w+\s*\([^)]*\):", c)
                docstrings = re.findall(r'""".*?"""|\'\'\'.*?\'\'\'', c, re.DOTALL)
                if funcs:
                    doc_ratio = len(docstrings) / len(funcs)
                    results.append(self._make_test(
                        f"Documentation coverage [{f['path']}]",
                        "passed" if doc_ratio >= 0.5 else "warning",
                        f"{len(docstrings)} docstrings for {len(funcs)} functions ({doc_ratio:.0%})",
                        "documentation"
                    ))
        return results

    def _check_naming_conventions(self, files):
        results = []
        for f in files:
            c = f["content"]
            if f["ext"] == ".py":
                bad_names = re.findall(r"\bdef\s+([A-Z]\w+)\s*\(", c)  # CamelCase functions in Python
                if bad_names:
                    results.append(self._make_test(
                        f"Python naming convention [{f['path']}]",
                        "warning",
                        f"CamelCase functions (should be snake_case): {', '.join(bad_names[:5])}",
                        "code_smells"
                    ))
            elif f["ext"] in {".js", ".ts", ".jsx", ".tsx"}:
                bad_const = re.findall(r"\bconst\s+([A-Z]{2,}\w*)\s*=\s*(?!{|\[|class\b)", c)
                if bad_const:
                    results.append(self._make_test(
                        f"JS naming convention [{f['path']}]",
                        "warning",
                        f"ALL_CAPS variables that may be constants: {', '.join(bad_const[:5])}",
                        "code_smells"
                    ))
        return results

    def _check_dead_code(self, files):
        results = []
        for f in files:
            c = f["content"]
            # Commented-out code blocks
            commented_code = re.findall(r"#\s*(if|for|while|def|class|return|import|from)\s+\w+", c)
            if len(commented_code) > 3:
                results.append(self._make_test(
                    f"Commented-out code [{f['path']}]",
                    "warning",
                    f"{len(commented_code)} lines of commented-out code detected",
                    "code_smells"
                ))
        return results

    def _check_cognitive_complexity(self, files):
        results = []
        for f in files:
            c = f["content"]
            # Nested control flow = cognitive complexity
            max_nesting = 0
            current_nesting = 0
            for line in c.split("\n"):
                stripped = line.lstrip()
                indent = len(line) - len(stripped)
                if re.match(r"(if|for|while|with|try|except|elif)\s", stripped):
                    current_nesting = indent // 4
                    max_nesting = max(max_nesting, current_nesting)

            status = "passed" if max_nesting <= 3 else ("warning" if max_nesting <= 5 else "failed")
            if max_nesting > 2:
                results.append(self._make_test(
                    f"Cognitive complexity [{f['path']}]",
                    status,
                    f"Max nesting depth: {max_nesting} (recommended: ≤3)",
                    "complexity"
                ))
        return results

    def _check_function_length(self, files):
        results = []
        for f in files:
            c = f["content"]
            if f["ext"] == ".py":
                try:
                    tree = ast.parse(c)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if hasattr(node, "end_lineno"):
                                length = node.end_lineno - node.lineno
                                if length > 50:
                                    results.append(self._make_test(
                                        f"Function length: {node.name} [{f['path']}]",
                                        "warning" if length < 100 else "failed",
                                        f"Function '{node.name}' is {length} lines (max recommended: 50)",
                                        "code_smells"
                                    ))
                except Exception:
                    pass
        return results

    def _check_file_length(self, files):
        results = []
        for f in files:
            if f["lines"] > 300:
                results.append(self._make_test(
                    f"File length [{f['path']}]",
                    "warning" if f["lines"] < 500 else "failed",
                    f"{f['lines']} lines (recommended: <300)",
                    "code_smells"
                ))
        return results

    def _check_nesting_depth(self, files):
        results = []
        for f in files:
            c = f["content"]
            if f["ext"] in {".js", ".ts", ".jsx", ".tsx"}:
                max_braces = 0
                depth = 0
                for ch in c:
                    if ch == "{":
                        depth += 1
                        max_braces = max(max_braces, depth)
                    elif ch == "}":
                        depth = max(0, depth - 1)
                if max_braces > 6:
                    results.append(self._make_test(
                        f"Nesting depth [{f['path']}]",
                        "warning",
                        f"Max block nesting: {max_braces} (recommended: ≤4)",
                        "complexity"
                    ))
        return results

    def _check_type_safety(self, files):
        results = []
        ts_files = [f for f in files if f["ext"] in {".ts", ".tsx"}]
        if ts_files:
            for f in ts_files:
                c = f["content"]
                any_count = len(re.findall(r":\s*any\b|as\s+any\b", c))
                if any_count > 3:
                    results.append(self._make_test(
                        f"TypeScript any usage [{f['path']}]",
                        "warning",
                        f"{any_count} uses of 'any' type — reduces type safety",
                        "code_smells"
                    ))
                else:
                    results.append(self._make_test(
                        f"TypeScript type safety [{f['path']}]",
                        "passed",
                        f"Good type coverage ({any_count} 'any' usages)",
                        "code_smells"
                    ))
        return results

    def _check_console_logs(self, files):
        results = []
        for f in files:
            c = f["content"]
            if f["ext"] in {".js", ".ts", ".jsx", ".tsx"}:
                logs = re.findall(r"console\.(log|warn|error|debug)\(", c)
                if logs:
                    results.append(self._make_test(
                        f"Console statements [{f['path']}]",
                        "warning",
                        f"{len(logs)} console.log/warn/error statements (remove before production)",
                        "code_smells"
                    ))
        return results

    def _check_todo_fixme(self, files):
        results = []
        for f in files:
            c = f["content"]
            todos = re.findall(r"#\s*(TODO|FIXME|HACK|XXX|BUG)\s*:?", c, re.IGNORECASE)
            if todos:
                results.append(self._make_test(
                    f"TODO/FIXME markers [{f['path']}]",
                    "warning",
                    f"{len(todos)} TODO/FIXME comments — technical debt markers",
                    "code_smells"
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
            "icon": "shield-check",
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "tests": tests,
        }