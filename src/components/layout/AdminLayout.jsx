import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, AlertTriangle, MessageSquare, Settings, LogOut, Pill, Bell, Menu } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const NAV = [
  { label: 'Overview', icon: LayoutDashboard, to: '/admin' },
  { label: 'User Management', icon: Users, to: '/admin/users' },
  { label: 'Escalation Log', icon: AlertTriangle, to: '/admin/escalations' },
  { label: 'WhatsApp Log', icon: MessageSquare, to: '/admin/whatsapp' },
  { label: 'Settings', icon: Settings, to: '/admin/settings' },
];

export default function AdminLayout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [mobile, setMobile] = useState(false);

  const handleLogout = async () => { await logout(); navigate('/'); };

  const Sidebar = () => (
    <div style={{ width: 240, background: 'var(--bg-secondary)', borderRight: '1px solid var(--border)', height: '100vh', display: 'flex', flexDirection: 'column', padding: '0 12px', position: 'sticky', top: 0 }}>
      <div style={{ padding: '20px 12px', borderBottom: '1px solid var(--border)', marginBottom: 8 }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #f472b6, var(--purple-light))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Pill size={16} color="#fff" strokeWidth={2.5} />
          </div>
          <div>
            <div className="font-syne" style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>MediMate <span style={{ color: '#f472b6' }}>Admin</span></div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>System Console</div>
          </div>
        </Link>
      </div>

      <div style={{ padding: '12px 12px', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg, #f472b6, var(--purple-light))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: '#fff' }}>{user?.name?.[0]?.toUpperCase() || 'A'}</span>
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{user?.name || 'Admin'}</div>
            <div style={{ fontSize: 11, color: '#f472b6' }}>Administrator</div>
          </div>
        </div>
      </div>

      <p style={{ color: 'var(--text-muted)', fontSize: 10, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '8px 12px' }}>ADMIN PANEL</p>
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV.map(({ label, icon: Icon, to }) => {
          const active = location.pathname === to;
          return (
            <Link key={to} to={to} className={`sidebar-item ${active ? 'active' : ''}`} style={active ? { borderLeft: '2px solid #f472b6', color: '#f472b6' } : {}}>
              <Icon size={17} /> {label}
            </Link>
          );
        })}
      </nav>

      <div style={{ padding: '12px 0', borderTop: '1px solid var(--border)' }}>
        <button onClick={handleLogout} className="sidebar-item" style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444' }}>
          <LogOut size={17} /> Logout
        </button>
      </div>
    </div>
  );

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <div style={{ flexShrink: 0 }} className="admin-sidebar">
        <Sidebar />
      </div>
      <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
        <div style={{ height: 56, borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', padding: '0 28px', gap: 16, position: 'sticky', top: 0, background: 'rgba(5,13,26,0.9)', backdropFilter: 'blur(12px)', zIndex: 10 }}>
          <div style={{ flex: 1 }}>
            <span style={{ fontSize: 12, color: '#f472b6', fontWeight: 600 }}>ADMIN CONSOLE</span>
          </div>
          <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}><Bell size={18} /></button>
        </div>
        <div style={{ flex: 1, padding: '32px 28px' }}>{children}</div>
      </div>
      <style>{`@media (max-width: 768px) { .admin-sidebar { display: none !important; } }`}</style>
    </div>
  );
}
