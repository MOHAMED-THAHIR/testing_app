import re
from typing import List, Dict


class PerformanceAnalyzer:
    """Analyzes performance: lazy loading, memoization, bundle size indicators, DB query patterns."""

    SUITE_NAME = "Performance Testing"

    def analyze(self, files: List[Dict]) -> Dict:
        tests = []
        tests.extend(self._check_lazy_loading(files))
        tests.extend(self._check_memoization(files))
        tests.extend(self._check_database_queries(files))
        tests.extend(self._check_bundle_size_indicators(files))
        tests.extend(self._check_image_optimization(files))
        tests.extend(self._check_caching(files))
        tests.extend(self._check_n_plus_one(files))
        tests.extend(self._check_render_optimization(files))
        tests.extend(self._check_async_patterns(files))
        tests.extend(self._check_loop_efficiency(files))
        return self._build_suite(tests)

    def _check_lazy_loading(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_react = bool(re.search(r"import.*React|from.*react", all_content))
        if has_react:
            has_lazy = bool(re.search(r"React\.lazy|lazy\(|Suspense|dynamic\(|loadable", all_content))
            results.append(self._make_test(
                "React lazy loading",
                "passed" if has_lazy else "warning",
                "Code splitting with React.lazy/dynamic: " + ("implemented" if has_lazy else "not found"),
                "performance"
            ))
        return results

    def _check_memoization(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_expensive_ops = bool(re.search(r"\.map\(.*\.filter\(|\.reduce\(|sort\(|\.find\(", c))
            if has_expensive_ops and f["ext"] in {".jsx", ".tsx", ".js", ".ts"}:
                has_memo = bool(re.search(r"useMemo|useCallback|React\.memo|memo\(", c))
                results.append(self._make_test(
                    f"Memoization [{f['path']}]",
                    "passed" if has_memo else "warning",
                    "Expensive operations detected. useMemo/useCallback: " + ("used" if has_memo else "not found"),
                    "performance"
                ))
        return results

    def _check_database_queries(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_db = bool(re.search(r"SELECT|query\(|\.find\(|\.findOne\(|\.filter\(.*models\.", c, re.IGNORECASE))
            if has_db:
                has_index_hint = bool(re.search(r"index|INDEX|CREATE INDEX|@Index|indexed=True", c))
                has_select_specific = bool(re.search(r"SELECT\s+\w|\.only\(|\.values\(|\.values_list\(", c))
                results.append(self._make_test(
                    f"DB query optimization [{f['path']}]",
                    "passed" if (has_index_hint or has_select_specific) else "warning",
                    f"Indexes: {'present' if has_index_hint else 'not found'}. SELECT *: {'avoided' if has_select_specific else 'possible'}",
                    "performance"
                ))
        return results

    def _check_bundle_size_indicators(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        heavy_imports = []
        if re.search(r"import.*from.*lodash[\"']|require.*lodash", all_content):
            if not re.search(r"import\s+\w+\s+from\s+[\"']lodash/\w+[\"']", all_content):
                heavy_imports.append("lodash (use specific imports: lodash/map instead of lodash)")
        if re.search(r"import.*moment[\"']|require.*moment[\"']", all_content):
            heavy_imports.append("moment.js (consider date-fns or dayjs)")
        if re.search(r"import.*antd[\"']|from\s+[\"']antd[\"']", all_content):
            if not re.search(r"antd/lib|antd/es", all_content):
                heavy_imports.append("antd (use tree-shaking)")
        if heavy_imports:
            results.append(self._make_test(
                "Bundle size optimization",
                "warning",
                "Heavy libraries without optimization: " + ", ".join(heavy_imports),
                "performance"
            ))
        else:
            results.append(self._make_test(
                "Bundle size indicators",
                "passed",
                "No unoptimized heavy library imports detected",
                "performance"
            ))
        return results

    def _check_image_optimization(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_images = bool(re.search(r"<img|Image.*src|background.*url\(", all_content))
        if has_images:
            has_opt = bool(re.search(r"next/image|gatsby-image|webp|lazy|loading=[\"']lazy[\"']|srcSet|sizes=", all_content))
            results.append(self._make_test(
                "Image optimization",
                "passed" if has_opt else "warning",
                "Image optimization (lazy/webp/srcset): " + ("present" if has_opt else "not found"),
                "performance"
            ))
        return results

    def _check_caching(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        has_api_calls = bool(re.search(r"fetch\(|axios\.|requests\.", all_content))
        if has_api_calls:
            has_cache = bool(re.search(
                r"useSWR|useQuery|react-query|RTK Query|Cache-Control|redis|cache|staleTime|cacheTime",
                all_content, re.IGNORECASE
            ))
            results.append(self._make_test(
                "API caching strategy",
                "passed" if has_cache else "warning",
                "Caching (SWR/React Query/Redis): " + ("implemented" if has_cache else "not found"),
                "performance"
            ))
        return results

    def _check_n_plus_one(self, files):
        results = []
        for f in files:
            c = f["content"]
            # N+1 pattern: query inside loop
            has_loop_query = bool(re.search(
                r"for\s+\w+\s+in\s+\w+[^:]*:\s*\n(?:\s+.*\n)*\s+.*\.(query|find|get|filter|execute)\(",
                c
            ))
            if has_loop_query:
                results.append(self._make_test(
                    f"N+1 query risk [{f['path']}]",
                    "warning",
                    "Potential N+1 query pattern detected (query inside loop)",
                    "performance"
                ))
        return results

    def _check_render_optimization(self, files):
        results = []
        for f in files:
            c = f["content"]
            if f["ext"] in {".jsx", ".tsx"}:
                # Inline function in render = new reference each render
                inline_funcs = len(re.findall(r"onClick=\{(?!\s*\w+\s*\})\s*(?:\([^)]*\)|)\s*=>", c))
                if inline_funcs > 3:
                    results.append(self._make_test(
                        f"Inline functions in JSX [{f['path']}]",
                        "warning",
                        f"{inline_funcs} inline arrow functions in JSX (causes re-renders — use useCallback)",
                        "performance"
                    ))
        return results

    def _check_async_patterns(self, files):
        results = []
        for f in files:
            c = f["content"]
            # Parallel async vs sequential
            sequential_awaits = re.findall(r"await\s+\w+\(.*\);\s*\n\s*.*await\s+\w+\(", c)
            if len(sequential_awaits) > 1:
                has_promise_all = bool(re.search(r"Promise\.all|Promise\.allSettled|await.*\[.*\]", c))
                if not has_promise_all:
                    results.append(self._make_test(
                        f"Sequential awaits [{f['path']}]",
                        "warning",
                        "Multiple sequential awaits — consider Promise.all() for parallel execution",
                        "performance"
                    ))
        return results

    def _check_loop_efficiency(self, files):
        results = []
        for f in files:
            c = f["content"]
            # Repeated .length in loop condition
            bad_loops = re.findall(r"for\s*\([^;]+;\s*\w+\s*<\s*\w+\.length\s*;", c)
            if bad_loops:
                results.append(self._make_test(
                    f"Loop optimization [{f['path']}]",
                    "warning",
                    f"{len(bad_loops)} loop(s) call .length on each iteration — cache length in variable",
                    "performance"
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
            "icon": "zap",
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "tests": tests,
        }