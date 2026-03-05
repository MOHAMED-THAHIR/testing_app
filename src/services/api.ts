import axios from 'axios';
import type { TestReport, TestOptions, ExportFormat } from '../types/index';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.error || err.message || 'Unknown error';
    return Promise.reject(new Error(message));
  }
);

export const testService = {
  async runTests(files: FileList | File[], options: TestOptions): Promise<TestReport> {
    const formData = new FormData();
    // Array.from(files).forEach(f => formData.append('paths', (f as any).webkitRelativePath || f.name));
    Array.from(files)
      .filter(f => f.size > 0 && f.name)  // skip empty/phantom files
      .forEach(f => {
        formData.append('file', f);
        formData.append('paths', (f as any).webkitRelativePath || f.name);
      });
    Object.entries(options).forEach(([key, val]) => {
      formData.append(key, String(val));
    });
    const res = await api.post<TestReport>('/tests/run', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};

export const exportService = {
  async exportReport(format: ExportFormat, data: TestReport): Promise<void> {
    const res = await api.post(`/export/${format}`, data, {
      responseType: 'blob',
    });
    const blob = new Blob([res.data]);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `testa_report.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  },
};