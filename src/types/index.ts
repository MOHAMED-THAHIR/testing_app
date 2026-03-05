export interface TestResult {
  name: string;
  status: 'passed' | 'failed' | 'warning' | 'skipped';
  message: string;
  category: string;
}

export interface TestSuite {
  suite: string;
  icon: string;
  total: number;
  passed: number;
  failed: number;
  warnings: number;
  tests: TestResult[];
}

export interface TestSummary {
  total: number;
  passed: number;
  failed: number;
  warnings: number;
  skipped: number;
  pass_rate: number;
}

export interface TestReport {
  session_id: string;
  summary: TestSummary;
  suites: TestSuite[];
  file_count: number;
  files_analyzed: string[];
  meta: {
    session_id: string;
    duration_seconds: number;
    timestamp: string;
  };
}

export interface TestOptions {
  ui_testing: boolean;
  api_testing: boolean;
  chart_testing: boolean;
  sonarqube: boolean;
  performance: boolean;
  security: boolean;
}

export type ExportFormat = 'pdf' | 'pptx' | 'docx';