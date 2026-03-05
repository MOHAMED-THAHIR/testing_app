import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { FlaskConical, LayoutDashboard, Upload, Github } from 'lucide-react';
import { useStore } from '../../store/index';
import './Layout.css';

const navItems = [
    { icon: Upload, label: 'Upload', path: '/' },
    { icon: LayoutDashboard, label: 'Results', path: '/results' },
];

export default function Layout() {
    const navigate = useNavigate();
    const location = useLocation();
    const { report } = useStore();

    return (
        <div className="root">
            <aside className="sidebar">
                <div className="logo">
                    <FlaskConical size={22} color="#3B82F6" />
                    <span>Testa</span>
                </div>
                <nav className="nav">
                    {navItems.map(({ icon: Icon, label, path }) => {
                        const active = location.pathname === path;
                        const disabled = path === '/results' && !report;
                        return (
                            <button
                                key={path}
                                className={`navItem ${active ? 'active' : ''} ${disabled ? 'disabled' : ''}`}
                                onClick={() => !disabled && navigate(path)}
                                title={disabled ? 'Run tests first' : label}
                            >
                                <Icon size={18} />
                                <span>{label}</span>
                                {path === '/results' && report && (
                                    <span className="badge">
                                        {report.summary.total}
                                    </span>
                                )}
                            </button>
                        );
                    })}
                </nav>
                <div className="sidebarFooter">
                    <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="footerLink">
                        <Github size={16} />
                        <span>View on GitHub</span>
                    </a>
                    <div className="version">v1.0.0</div>
                </div>
            </aside>
            <main className="main">
                <Outlet />
            </main>
        </div>
    );
}