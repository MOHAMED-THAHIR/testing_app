import re
from typing import List, Dict


class UIAnalyzer:
    """Analyzes UI components: filters, checkboxes, buttons, form validation."""

    SUITE_NAME = "UI Testing"

    def analyze(self, files: List[Dict]) -> Dict:
        tests = []
        ui_files = [f for f in files if f["ext"] in {".jsx", ".tsx", ".vue", ".html", ".js", ".ts"}]

        tests.extend(self._check_buttons(ui_files))
        tests.extend(self._check_forms_and_inputs(ui_files))
        tests.extend(self._check_filters(ui_files))
        tests.extend(self._check_checkboxes(ui_files))
        tests.extend(self._check_accessibility(ui_files))
        tests.extend(self._check_event_handlers(ui_files))
        tests.extend(self._check_conditional_rendering(ui_files))
        tests.extend(self._check_loading_states(ui_files))
        tests.extend(self._check_error_boundaries(ui_files))

        if not ui_files:
            tests.append(self._make_test("No UI files found", "skipped", "No JSX/TSX/Vue/HTML files detected", "info"))

        return self._build_suite(tests)

    def _check_buttons(self, files):
        results = []
        for f in files:
            c = f["content"]
            # Check button onClick handlers
            buttons = re.findall(r"<[Bb]utton[^>]*>", c)
            if buttons:
                has_onclick = bool(re.search(r"onClick|@click|v-on:click|\(click\)", c))
                results.append(self._make_test(
                    f"Button click handlers [{f['path']}]",
                    "passed" if has_onclick else "warning",
                    f"Found {len(buttons)} button(s). Click handlers: {'present' if has_onclick else 'missing'}",
                    "ui"
                ))
            # Check disabled state
            if re.search(r"<[Bb]utton", c):
                has_disabled = bool(re.search(r"disabled=|:disabled|isDisabled|isLoading", c))
                results.append(self._make_test(
                    f"Button disabled state [{f['path']}]",
                    "passed" if has_disabled else "warning",
                    "Disabled/loading states: " + ("present" if has_disabled else "not detected"),
                    "ui"
                ))
        return results

    def _check_forms_and_inputs(self, files):
        results = []
        for f in files:
            c = f["content"]
            inputs = re.findall(r"<input[^>]*>|<Input[^>]*>", c)
            if inputs:
                has_validation = bool(re.search(
                    r"required|pattern=|minLength|maxLength|validate|yup|zod|formik|react-hook-form|v-model", c
                ))
                has_error_msg = bool(re.search(r"error|invalid|helperText|errorMessage|formError", c, re.IGNORECASE))
                results.append(self._make_test(
                    f"Form input validation [{f['path']}]",
                    "passed" if has_validation else "failed",
                    f"{len(inputs)} input(s) found. Validation: {'present' if has_validation else 'MISSING'}. Error messages: {'present' if has_error_msg else 'missing'}",
                    "ui"
                ))
                # Check for uncontrolled inputs
                has_value_or_state = bool(re.search(r"value=|useState|v-model|formData|register\(", c))
                results.append(self._make_test(
                    f"Input controlled state [{f['path']}]",
                    "passed" if has_value_or_state else "warning",
                    "Inputs appear " + ("controlled" if has_value_or_state else "potentially uncontrolled"),
                    "ui"
                ))
        return results

    def _check_filters(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_filter = bool(re.search(r"filter|Filter|search|Search|sort|Sort", c))
            if has_filter:
                has_filter_logic = bool(re.search(
                    r"\.filter\(|filterBy|filterValue|searchTerm|queryParam|useFilter|filteredData|filtered\w+", c
                ))
                has_reset = bool(re.search(r"reset|clear|Reset|Clear|clearFilter|resetFilter", c))
                results.append(self._make_test(
                    f"Filter functionality [{f['path']}]",
                    "passed" if has_filter_logic else "warning",
                    f"Filter UI detected. Logic: {'present' if has_filter_logic else 'unclear'}. Reset: {'present' if has_reset else 'missing'}",
                    "ui"
                ))
        return results

    def _check_checkboxes(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_checkbox = bool(re.search(r'type=["\']checkbox["\']|Checkbox|<checkbox', c, re.IGNORECASE))
            if has_checkbox:
                has_state = bool(re.search(r"checked=|isChecked|onChange|v-model|@change", c))
                results.append(self._make_test(
                    f"Checkbox state management [{f['path']}]",
                    "passed" if has_state else "failed",
                    "Checkbox state handling: " + ("present" if has_state else "MISSING — uncontrolled checkboxes"),
                    "ui"
                ))
        return results

    def _check_accessibility(self, files):
        results = []
        for f in files:
            c = f["content"]
            if re.search(r"<img[^>]*>", c):
                has_alt = bool(re.search(r"alt=", c))
                results.append(self._make_test(
                    f"Image alt attributes [{f['path']}]",
                    "passed" if has_alt else "failed",
                    "Alt attributes: " + ("present" if has_alt else "MISSING on images"),
                    "accessibility"
                ))
            if re.search(r"<input[^>]*>", c):
                has_label = bool(re.search(r"<label|aria-label|aria-labelledby|htmlFor|for=", c))
                results.append(self._make_test(
                    f"Form label accessibility [{f['path']}]",
                    "passed" if has_label else "warning",
                    "Labels/aria attributes: " + ("present" if has_label else "missing"),
                    "accessibility"
                ))
            has_role = bool(re.search(r"role=|aria-|tabIndex", c))
            if re.search(r"<div[^>]*onClick|<span[^>]*onClick", c):
                results.append(self._make_test(
                    f"Interactive element roles [{f['path']}]",
                    "passed" if has_role else "warning",
                    "Clickable non-button elements: " + ("have ARIA roles" if has_role else "missing role/tabIndex"),
                    "accessibility"
                ))
        return results

    def _check_event_handlers(self, files):
        results = []
        for f in files:
            c = f["content"]
            handlers = re.findall(r"on[A-Z]\w+={|@\w+=|v-on:", c)
            if handlers:
                has_prevent = bool(re.search(r"preventDefault|stopPropagation|\.prevent|\.stop", c))
                results.append(self._make_test(
                    f"Event handling [{f['path']}]",
                    "passed",
                    f"{len(handlers)} event handler(s) found. Default prevention: {'present' if has_prevent else 'not used'}",
                    "ui"
                ))
        return results

    def _check_conditional_rendering(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_conditional = bool(re.search(r"\?\s*<|v-if|v-show|\&\&\s*<|isLoading|isEmpty|isError", c))
            if has_conditional:
                results.append(self._make_test(
                    f"Conditional rendering [{f['path']}]",
                    "passed",
                    "Conditional rendering patterns detected",
                    "ui"
                ))
        return results

    def _check_loading_states(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_async = bool(re.search(r"async|await|\.then\(|useQuery|useSWR|axios|fetch\(", c))
            has_loading = bool(re.search(r"isLoading|loading|spinner|Skeleton|skeleton|Loading", c))
            if has_async and not has_loading:
                results.append(self._make_test(
                    f"Loading state handling [{f['path']}]",
                    "warning",
                    "Async operations detected but no loading state/spinner found",
                    "ui"
                ))
            elif has_async and has_loading:
                results.append(self._make_test(
                    f"Loading state handling [{f['path']}]",
                    "passed",
                    "Async operations have loading states",
                    "ui"
                ))
        return results

    def _check_error_boundaries(self, files):
        results = []
        for f in files:
            c = f["content"]
            has_async = bool(re.search(r"fetch\(|axios|useQuery|api\.", c))
            has_error_handling = bool(re.search(
                r"catch\(|onError|isError|ErrorBoundary|try\s*{|error\s*&&|\.catch\(", c
            ))
            if has_async:
                results.append(self._make_test(
                    f"Error handling [{f['path']}]",
                    "passed" if has_error_handling else "failed",
                    "Error handling: " + ("present" if has_error_handling else "MISSING for async operations"),
                    "ui"
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
            "icon": "monitor",
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "tests": tests,
        }