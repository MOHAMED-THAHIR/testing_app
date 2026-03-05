import { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Upload, FlaskConical, Monitor, Network, BarChart2,
    Shield, Zap, Lock, CheckCircle2, XCircle, AlertTriangle,
    FileCode, Loader2
} from 'lucide-react';
import { useStore } from '../../store/index';
import { testService } from '../../services/api';
import type { TestOptions } from '../../types/index';
import './UploadPage.css';

const SUITE_OPTIONS: { key: keyof TestOptions; label: string; desc: string; icon: typeof Monitor }[] = [
    { key: 'ui_testing', label: 'UI Testing', desc: 'Filters, checkboxes, buttons, forms, accessibility', icon: Monitor },
    { key: 'api_testing', label: 'API Validation', desc: 'REST design, validation, auth, error codes', icon: Network },
    { key: 'chart_testing', label: 'Chart Rendering', desc: 'Chart libraries, data binding, responsiveness', icon: BarChart2 },
    { key: 'sonarqube', label: 'SonarQube Checks', desc: 'Complexity, smells, bugs, security, duplications', icon: Shield },
    { key: 'performance', label: 'Performance', desc: 'Lazy loading, memoization, caching, N+1 queries', icon: Zap },
    { key: 'security', label: 'Security & Load', desc: 'OWASP, secrets, DoS protection, load readiness', icon: Lock },
];

export default function UploadPage() {
    const navigate = useNavigate();
    const { options, setOptions, setReport, setLoading, setError, isLoading, error } = useStore();
    const [dragging, setDragging] = useState(false);
    const [files, setFiles] = useState<FileList | File[] | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setDragging(false);
        const f = e.dataTransfer.files;
        if (f && f.length > 0) setFiles(f);
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const f = e.target.files;
        if (f && f.length > 0) setFiles(f);
    };

    const handleRun = async () => {
        if (!files) return;
        setLoading(true);
        setError(null);
        try {
            const report = await testService.runTests(files, options);
            setReport(report);
            navigate('/results');
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : 'Failed to run tests');
        } finally {
            setLoading(false);
        }
    };

    const allSelected = Object.values(options).every(Boolean);
    const toggleAll = () => {
        const newVal = !allSelected;
        const all: TestOptions = Object.fromEntries(
            SUITE_OPTIONS.map(o => [o.key, newVal])
        ) as unknown as TestOptions;
        Object.entries(all).forEach(([k, v]) => setOptions({ [k]: v }));
    };

    return (
        <div className="page">
            <div className="hero">
                <div className="heroIcon">
                    <FlaskConical size={32} />
                </div>
                <h1 className="heroTitle">Automated Testing Platform</h1>
                <p className="heroSub">
                    Upload any source code — we'll run comprehensive tests across UI, API, performance, security, and code quality.
                </p>
            </div>

            <div className="content">
                {/* Upload zone */}
                <section className="card">
                    <div className="cardHeader">
                        <FileCode size={18} />
                        <h2>Upload Source Code</h2>
                    </div>
                    <div
                        className={`dropzone ${dragging ? 'dragging' : ''} ${files ? 'hasFile' : ''}`}
                        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                        onDragLeave={() => setDragging(false)}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <input
                            ref={fileInputRef}
                            type="file"
                            hidden
                            multiple
                            {...{ webkitdirectory: "" } as any}
                            // accept=".zip,.tar,.gz,.py,.js,.ts,.jsx,.tsx,.vue,.html,.java,.cs,.go,.rb,.php,.swift,.kt,.rs"
                            onChange={handleFileChange}
                        />
                        {files ? (
                            <div className="fileInfo">
                                <CheckCircle2 size={32} color="#22C55E" />
                                <div>
                                    <div className="fileName">
                                        {files.length === 1 ? files[0].name : `${files.length} files selected`}
                                    </div>
                                    <div className="fileSize">
                                        {(Array.from(files).reduce((acc, f) => acc + f.size, 0) / 1024).toFixed(1)} KB total
                                    </div>
                                </div>
                                <button className="removeBtn" onClick={(e) => { e.stopPropagation(); setFiles(null); }}>
                                    <XCircle size={16} />
                                </button>
                            </div>
                        ) : (
                            <div className="dropContent">
                                <Upload size={36} color="#3B82F6" />
                                <p className="dropMain">Drop your source files here</p>
                                <p className="dropSub">Supports .zip, .tar.gz, or individual files (.py, .js, .ts, .jsx, .tsx, .vue, .java, .go, .rb, .php, ...)</p>
                                <span className="browseBtn">Browse files</span>
                            </div>
                        )}
                    </div>
                </section>

                {/* Test options */}
                <section className="card">
                    <div className="cardHeader">
                        <Shield size={18} />
                        <h2>Test Suites</h2>
                        <button className="toggleAll" onClick={toggleAll}>
                            {allSelected ? 'Deselect all' : 'Select all'}
                        </button>
                    </div>
                    <div className="suiteGrid">
                        {SUITE_OPTIONS.map(({ key, label, desc, icon: Icon }) => (
                            <button
                                key={key}
                                className={`suiteCard ${options[key] ? 'suiteActive' : ''}`}
                                onClick={() => setOptions({ [key]: !options[key] })}
                            >
                                <div className="suiteCheck">
                                    {options[key] ? <CheckCircle2 size={16} color="#22C55E" /> : <div className="suiteUnchecked" />}
                                </div>
                                <Icon size={20} className="suiteIcon" />
                                <div>
                                    <div className="suiteLabel">{label}</div>
                                    <div className="suiteDesc">{desc}</div>
                                </div>
                            </button>
                        ))}
                    </div>
                </section>

                {/* Error */}
                {error && (
                    <div className="errorBox">
                        <AlertTriangle size={16} />
                        <span>{error}</span>
                    </div>
                )}

                {/* Run button */}
                <button
                    className="runBtn"
                    onClick={handleRun}
                    disabled={!files || isLoading || Object.values(options).every(v => !v)}
                >
                    {isLoading ? (
                        <>
                            <Loader2 size={20} className="spin" />
                            Analyzing your code...
                        </>
                    ) : (
                        <>
                            <FlaskConical size={20} />
                            Run Tests
                        </>
                    )}
                </button>

                {isLoading && (
                    <div className="loadingHint">
                        <div className="loadingBar">
                            <div className="loadingFill" />
                        </div>
                        <p>Running all test suites — this may take 15–30 seconds for large codebases</p>
                    </div>
                )}
            </div>
        </div>
    );
}