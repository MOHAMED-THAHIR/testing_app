import re
from typing import List, Dict


class ChartAnalyzer:
    """Analyzes chart/visualization rendering: library usage, data binding, responsiveness."""

    SUITE_NAME = "Chart Rendering Testing"

    CHART_LIBRARIES = {
        "recharts": r"recharts|Recharts|LineChart|BarChart|PieChart|AreaChart",
        "chart.js": r"Chart\.js|chartjs|new Chart\(",
        "d3": r"d3\.|import.*d3|require.*d3",
        "victory": r"VictoryChart|VictoryLine|VictoryBar|victory-chart",
        "apexcharts": r"ApexCharts|apexcharts|ReactApexChart",
        "highcharts": r"Highcharts|highcharts",
        "visx": r"@visx|visx",
        "nivo": r"@nivo|ResponsiveBar|ResponsiveLine",
        "plotly": r"plotly|Plotly|Plot\s*from",
        "vega": r"vega-lite|vega\.embed",
        "echarts": r"echarts|ECharts",
        "tremor": r"@tremor|BarChart.*tremor|AreaChart.*tremor",
        "matplotlib": r"matplotlib|plt\.|pyplot",
        "seaborn": r"seaborn|sns\.",
    }

    def analyze(self, files: List[Dict]) -> Dict:
        tests = []
        tests.extend(self._check_chart_library_usage(files))
        tests.extend(self._check_data_binding(files))
        tests.extend(self._check_responsive_charts(files))
        tests.extend(self._check_chart_accessibility(files))
        tests.extend(self._check_loading_states(files))
        tests.extend(self._check_empty_states(files))
        tests.extend(self._check_color_theming(files))
        tests.extend(self._check_tooltip_legends(files))

        return self._build_suite(tests)

    def _check_chart_library_usage(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        detected = [lib for lib, pattern in self.CHART_LIBRARIES.items() if re.search(pattern, all_content)]

        if detected:
            results.append(self._make_test(
                "Chart library detection",
                "passed",
                f"Detected: {', '.join(detected)}",
                "chart_rendering"
            ))
        else:
            results.append(self._make_test(
                "Chart library detection",
                "skipped",
                "No chart libraries detected in codebase",
                "chart_rendering"
            ))
        return results

    def _check_data_binding(self, files):
        results = []
        for f in files:
            c = f["content"]
            lib_detected = any(re.search(pat, c) for pat in self.CHART_LIBRARIES.values())
            if lib_detected:
                has_data_prop = bool(re.search(r"data=\{|data:\s*\[|chartData|series=|datasets=", c))
                results.append(self._make_test(
                    f"Chart data binding [{f['path']}]",
                    "passed" if has_data_prop else "warning",
                    "Data prop binding: " + ("present" if has_data_prop else "unclear"),
                    "chart_rendering"
                ))
                has_transform = bool(re.search(r"\.map\(|transform|format|normalize|chartData\s*=", c))
                results.append(self._make_test(
                    f"Chart data transformation [{f['path']}]",
                    "passed" if has_transform else "warning",
                    "Data transformation before render: " + ("present" if has_transform else "raw data passed directly"),
                    "chart_rendering"
                ))
        return results

    def _check_responsive_charts(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        lib_detected = any(re.search(pat, all_content) for pat in self.CHART_LIBRARIES.values())
        if lib_detected:
            has_responsive = bool(re.search(
                r"ResponsiveContainer|responsive=|width=[\"']100%|useResizeObserver|autoFit|viewBox", all_content
            ))
            results.append(self._make_test(
                "Responsive chart containers",
                "passed" if has_responsive else "warning",
                "Responsive wrappers: " + ("used" if has_responsive else "not found — charts may not resize"),
                "chart_rendering"
            ))
        return results

    def _check_chart_accessibility(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        lib_detected = any(re.search(pat, all_content) for pat in self.CHART_LIBRARIES.values())
        if lib_detected:
            has_aria = bool(re.search(r"aria-label|aria-describedby|role=[\"']img[\"']|title=", all_content))
            results.append(self._make_test(
                "Chart ARIA accessibility",
                "passed" if has_aria else "warning",
                "ARIA labels on charts: " + ("present" if has_aria else "missing — screen readers won't describe charts"),
                "accessibility"
            ))
        return results

    def _check_loading_states(self, files):
        results = []
        for f in files:
            c = f["content"]
            lib_detected = any(re.search(pat, c) for pat in self.CHART_LIBRARIES.values())
            if lib_detected:
                has_loading = bool(re.search(r"isLoading|loading|skeleton|Skeleton|spinner", c, re.IGNORECASE))
                results.append(self._make_test(
                    f"Chart loading state [{f['path']}]",
                    "passed" if has_loading else "warning",
                    "Loading state for chart data: " + ("present" if has_loading else "missing"),
                    "chart_rendering"
                ))
        return results

    def _check_empty_states(self, files):
        results = []
        for f in files:
            c = f["content"]
            lib_detected = any(re.search(pat, c) for pat in self.CHART_LIBRARIES.values())
            if lib_detected:
                has_empty = bool(re.search(
                    r"isEmpty|empty|noData|No data|length\s*===\s*0|data\s*\|\|\s*\[\]", c, re.IGNORECASE
                ))
                results.append(self._make_test(
                    f"Chart empty state [{f['path']}]",
                    "passed" if has_empty else "warning",
                    "Empty data state handling: " + ("present" if has_empty else "not found"),
                    "chart_rendering"
                ))
        return results

    def _check_color_theming(self, files):
        results = []
        all_content = " ".join(f["content"] for f in files)
        lib_detected = any(re.search(pat, all_content) for pat in self.CHART_LIBRARIES.values())
        if lib_detected:
            has_color_config = bool(re.search(r"fill=|stroke=|colors=|colorScheme|palette|COLORS\s*=", all_content))
            results.append(self._make_test(
                "Chart color configuration",
                "passed" if has_color_config else "warning",
                "Custom color config: " + ("present" if has_color_config else "using defaults"),
                "chart_rendering"
            ))
        return results

    def _check_tooltip_legends(self, files):
        results = []
        for f in files:
            c = f["content"]
            lib_detected = any(re.search(pat, c) for pat in self.CHART_LIBRARIES.values())
            if lib_detected:
                has_tooltip = bool(re.search(r"<Tooltip|tooltip=|CustomTooltip|tooltipProps", c))
                has_legend = bool(re.search(r"<Legend|legend=|showLegend|legendProps", c))
                results.append(self._make_test(
                    f"Tooltip & legend [{f['path']}]",
                    "passed" if (has_tooltip or has_legend) else "warning",
                    f"Tooltip: {'✓' if has_tooltip else '✗'} | Legend: {'✓' if has_legend else '✗'}",
                    "chart_rendering"
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
            "icon": "bar-chart",
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "tests": tests,
        }