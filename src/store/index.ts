import { create } from 'zustand';
import type { TestReport, TestOptions } from '../types/index';

interface AppState {
  report: TestReport | null;
  isLoading: boolean;
  error: string | null;
  activeFile: File | null;
  options: TestOptions;
  activeTab: string;
  activeSuite: string | null;

  setReport: (report: TestReport | null) => void;
  setLoading: (v: boolean) => void;
  setError: (e: string | null) => void;
  setActiveFile: (f: File | null) => void;
  setOptions: (o: Partial<TestOptions>) => void;
  setActiveTab: (t: string) => void;
  setActiveSuite: (s: string | null) => void;
  reset: () => void;
}

const defaultOptions: TestOptions = {
  ui_testing: true,
  api_testing: true,
  chart_testing: true,
  sonarqube: true,
  performance: true,
  security: true,
};

export const useStore = create<AppState>((set) => ({
  report: null,
  isLoading: false,
  error: null,
  activeFile: null,
  options: defaultOptions,
  activeTab: 'dashboard',
  activeSuite: null,

  setReport: (report) => set({ report }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setActiveFile: (activeFile) => set({ activeFile }),
  setOptions: (o) => set((s) => ({ options: { ...s.options, ...o } })),
  setActiveTab: (activeTab) => set({ activeTab }),
  setActiveSuite: (activeSuite) => set({ activeSuite }),
  reset: () => set({ report: null, error: null, activeFile: null, isLoading: false }),
}));