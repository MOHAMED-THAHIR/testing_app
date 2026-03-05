import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart2, CheckCircle2, XCircle, AlertTriangle,
  Clock, FileCode, ChevronDown, ChevronRight,
  Download, FileText, Presentation, FileSpreadsheet,
  RotateCcw, Monitor, Network, Shield, Zap, Lock, BarChart
} from 'lucide-react';
import {
  BarChart as ReBar, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadialBarChart, RadialBar, Legend
} from 'recharts';
import { useStore } from '../../store/index';
import { exportService } from '../../services/api';
import type { TestSuite, ExportFormat } from '../../types/index';
import './ResultPage.css';

const SUITE_ICONS: Record<string, typeof Monitor> = {
  monitor: Monitor, network: Network, 'bar-chart': BarChart,
  'shield-check': Shield, zap: Zap, lock: Lock,
};

const PIE_COLORS = ['#22C55E', '#EF4444', '#EAB308', '#64748B'];

function StatCard({ label, value, icon, color }: { label: string; value: string | number; icon: React.ReactNode; color: string }) {
  return (
    <div className="statCard">
      <div className="statIcon" style={{ background: `${color}20`, color }}>
        {icon}
      </div>
      <div>
        <div className="statValue" style={{ color }}>{value}</div>
        <div className="statLabel">{label}</div>
      </div>
    </div>
  );
}

function SuiteRow({ suite }: { suite: TestSuite }) {
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState<string>('all');
  const Icon = SUITE_ICONS[suite.icon] || Shield;
  const pct = suite.total > 0 ? (suite.passed / suite.total * 100) : 0;
  const barColor = pct >= 70 ? '#22C55E' : pct >= 40 ? '#EAB308' : '#EF4444';

  const filtered = suite.tests.filter(t => filter === 'all' || t.status === filter);

  return (
    <div className="suiteRow">
      <button className="suiteHeader" onClick={() => setOpen(o => !o)}>
        <div className="suiteLeft">
          {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          <Icon size={18} className="suiteIcon" />
          <span className="suiteName">{suite.suite}</span>
        </div>
        <div className="suiteRight">
          <div className="suiteBar">
            <div className="suiteBarFill" style={{ width: `${pct}%`, background: barColor }} />
          </div>
          <span className="suitePct" style={{ color: barColor }}>{pct.toFixed(0)}%</span>
          <div className="suiteBadges">
            <span className="badgePass">{suite.passed} pass</span>
            {suite.failed > 0 && <span className="badgeFail">{suite.failed} fail</span>}
            {suite.warnings > 0 && <span className="badgeWarn">{suite.warnings} warn</span>}
          </div>
        </div>
      </button>

      {open && (
        <div className="suiteBody">
          <div className="filterBar">
            {['all', 'passed', 'failed', 'warning', 'skipped'].map(f => (
              <button
                key={f}
                className={`filterBtn ${filter === f ? 'filterActive' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f} {f === 'all' ? `(${suite.tests.length})` : `(${suite.tests.filter(t => t.status === f).length})`}
              </button>
            ))}
          </div>
          <div className="testList">
            {filtered.map((test, i) => (
              <div key={i} className={`testItem status_${test.status}`}>
                <div className="testLeft">
                  {test.status === 'passed' && <CheckCircle2 size={14} color="#22C55E" />}
                  {test.status === 'failed' && <XCircle size={14} color="#EF4444" />}
                  {test.status === 'warning' && <AlertTriangle size={14} color="#EAB308" />}
                  {test.status === 'skipped' && <div className="skipDot" />}
                  <span className="testName">{test.name}</span>
                </div>
                <span className="testCategory">{test.category}</span>
                <span className="testMessage">{test.message}</span>
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="noResults">No {filter} tests in this suite</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function ResultsPage() {
  const navigate = useNavigate();
  const { report, reset } = useStore();
  const [exporting, setExporting] = useState<string | null>(null);

  if (!report) {
    return (
      <div className="empty">
        <BarChart2 size={48} color="#3B82F6" />
        <h2>No test results yet</h2>
        <p>Upload your source code to run automated tests</p>
        <button className="uploadBtn" onClick={() => navigate('/')}>
          Go to Upload
        </button>
      </div>
    );
  }

  const { summary, suites, file_count, meta } = report;

  const pieData = [
    { name: 'Passed', value: summary.passed },
    { name: 'Failed', value: summary.failed },
    { name: 'Warnings', value: summary.warnings },
    { name: 'Skipped', value: summary.skipped },
  ].filter(d => d.value > 0);

  const barData = suites.map(s => ({
    name: s.suite.replace(' Testing', '').replace(' Checks', ''),
    Passed: s.passed,
    Failed: s.failed,
    Warnings: s.warnings,
  }));

  const handleExport = async (fmt: ExportFormat) => {
    setExporting(fmt);
    try {
      await exportService.exportReport(fmt, report);
    } catch (e) {
      console.error('Export failed:', e);
    } finally {
      setExporting(null);
    }
  };

  return (
    <div className="page">
      {/* Header */}
      <div className="pageHeader">
        <div>
          <h1 className="pageTitle">Test Results</h1>
          <div className="metaRow">
            <Clock size={13} />
            <span>{meta.duration_seconds}s</span>
            <FileCode size={13} />
            <span>{file_count} files analyzed</span>
            <span className="dot" />
            <span>{new Date(meta.timestamp).toLocaleString()}</span>
          </div>
        </div>
        <div className="headerActions">
          <button className="resetBtn" onClick={() => { reset(); navigate('/'); }}>
            <RotateCcw size={15} /> New Test
          </button>
          <div className="exportGroup">
            {([
              { fmt: 'pdf', icon: FileText, label: 'PDF' },
              { fmt: 'pptx', icon: Presentation, label: 'PPT' },
              { fmt: 'docx', icon: FileSpreadsheet, label: 'DOCX' },
            ] as { fmt: ExportFormat; icon: typeof FileText; label: string }[]).map(({ fmt, icon: Icon, label }) => (
              <button
                key={fmt}
                className="exportBtn"
                onClick={() => handleExport(fmt)}
                disabled={!!exporting}
              >
                {exporting === fmt ? <span className="spin">⟳</span> : <Icon size={14} />}
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="statsGrid">
        <StatCard label="Total Tests" value={summary.total} icon={<BarChart2 size={20} />} color="#3B82F6" />
        <StatCard label="Passed" value={summary.passed} icon={<CheckCircle2 size={20} />} color="#22C55E" />
        <StatCard label="Failed" value={summary.failed} icon={<XCircle size={20} />} color="#EF4444" />
        <StatCard label="Warnings" value={summary.warnings} icon={<AlertTriangle size={20} />} color="#EAB308" />
        <StatCard label="Pass Rate" value={`${summary.pass_rate}%`} icon={<Shield size={20} />} color={summary.pass_rate >= 70 ? '#22C55E' : summary.pass_rate >= 40 ? '#EAB308' : '#EF4444'} />
      </div>

      {/* Charts */}
      <div className="chartsRow">
        <div className="chartCard">
          <h3 className="chartTitle">Results by Suite</h3>
          <ResponsiveContainer width="100%" height={220}>
            <ReBar data={barData} barSize={14}>
              <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748B', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2D45', borderRadius: 8, fontSize: 12 }} />
              <Bar dataKey="Passed" fill="#22C55E" radius={[3, 3, 0, 0]} />
              <Bar dataKey="Failed" fill="#EF4444" radius={[3, 3, 0, 0]} />
              <Bar dataKey="Warnings" fill="#EAB308" radius={[3, 3, 0, 0]} />
            </ReBar>
          </ResponsiveContainer>
        </div>

        <div className="chartCard">
          <h3 className="chartTitle">Overall Distribution</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={3} dataKey="value">
                {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2D45', borderRadius: 8, fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12, color: '#94A3B8' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chartCard">
          <h3 className="chartTitle">Pass Rate by Suite</h3>
          <ResponsiveContainer width="100%" height={220}>
            <RadialBarChart cx="50%" cy="50%" innerRadius={20} outerRadius={90}
              data={suites.map((s, i) => ({
                name: s.suite.split(' ')[0],
                value: s.total > 0 ? Math.round(s.passed / s.total * 100) : 0,
                fill: PIE_COLORS[i % PIE_COLORS.length],
              }))}>
              <RadialBar dataKey="value" label={{ fill: '#94A3B8', fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1F2D45', borderRadius: 8, fontSize: 12 }}
                formatter={(value) => [`${value ?? 0}%`, 'Pass Rate']} />
            </RadialBarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Suite detail accordion */}
      <div className="suitesSection">
        <h2 className="sectionTitle">
          <Download size={16} /> Detailed Test Results
        </h2>
        <div className="suiteList">
          {suites.map((suite, i) => (
            <SuiteRow key={i} suite={suite} />
          ))}
        </div>
      </div>
    </div>
  );
}