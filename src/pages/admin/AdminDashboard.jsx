import { Users, Activity, AlertTriangle, MessageSquare, TrendingUp, CheckCircle } from 'lucide-react';
import AdminLayout from '@/components/layout/AdminLayout';

const STATS = [
  { label: 'Total Patients', value: 248, sub: '+12 this week', color: 'var(--cyan)', icon: Users },
  { label: 'Active Schedules', value: 516, sub: 'Across all patients', color: 'var(--emerald)', icon: Activity },
  { label: 'Doses Today', value: 1432, sub: '87% taken so far', color: '#a78bfa', icon: CheckCircle },
  { label: 'Escalations Today', value: 14, sub: '3 still pending', color: '#ef4444', icon: AlertTriangle },
];

const RECENT_USERS = [
  { name: 'Priya Sharma', email: 'priya@example.com', role: 'patient', status: 'active', joined: '2025-03-12' },
  { name: 'Rahul Mehta', email: 'rahul@example.com', role: 'caretaker', status: 'active', joined: '2025-03-10' },
  { name: 'Aisha Khan', email: 'aisha@example.com', role: 'patient', status: 'inactive', joined: '2025-02-28' },
  { name: 'Suresh Patel', email: 'suresh@example.com', role: 'patient', status: 'active', joined: '2025-02-15' },
  { name: 'Meera Iyer', email: 'meera@example.com', role: 'caretaker', status: 'active', joined: '2025-02-01' },
];

const RECENT_ESCALATIONS = [
  { patient: 'Priya Sharma', medicine: 'Metformin 500mg', time: '14:30', type: 'WhatsApp', status: 'resolved' },
  { patient: 'Suresh Patel', medicine: 'Lisinopril 10mg', time: '09:15', type: 'Caretaker Alert', status: 'pending' },
  { patient: 'Aisha Khan', medicine: 'Atorvastatin 20mg', time: '22:00', type: 'Voice Call', status: 'resolved' },
];

export default function AdminDashboard() {
  return (
    <AdminLayout>
      <div style={{ marginBottom: 28 }}>
        <h1 className="font-syne" style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>System Overview</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Platform-wide statistics and health monitoring.</p>
      </div>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
        {STATS.map(({ label, value, sub, color, icon: Icon }) => (
          <div key={label} className="glass-card" style={{ padding: '22px 24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: `${color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={20} color={color} />
              </div>
              <TrendingUp size={14} color="var(--text-muted)" />
            </div>
            <div className="font-syne" style={{ fontSize: 32, fontWeight: 800, color }}>{value.toLocaleString()}</div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>{label}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{sub}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24 }}>
        {/* Recent users */}
        <div className="glass-card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>Recent Users</h2>
            <span style={{ fontSize: 12, color: 'var(--cyan)', cursor: 'pointer' }}>View all →</span>
          </div>
          <table className="data-table">
            <thead><tr><th>Name</th><th>Role</th><th>Status</th></tr></thead>
            <tbody>
              {RECENT_USERS.map(u => (
                <tr key={u.email}>
                  <td>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{u.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{u.email}</div>
                  </td>
                  <td>
                    <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 6, background: u.role === 'admin' ? 'rgba(244,114,182,0.12)' : u.role === 'caretaker' ? 'rgba(167,139,250,0.12)' : 'rgba(0,212,255,0.1)', color: u.role === 'admin' ? '#f472b6' : u.role === 'caretaker' ? 'var(--purple-light)' : 'var(--cyan)' }}>{u.role}</span>
                  </td>
                  <td>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: u.status === 'active' ? 'var(--emerald)' : 'var(--text-muted)', display: 'inline-block', marginRight: 6 }} />
                    <span style={{ fontSize: 12, color: u.status === 'active' ? 'var(--emerald)' : 'var(--text-muted)' }}>{u.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Recent escalations */}
        <div className="glass-card" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>Escalations Today</h2>
            <span style={{ fontSize: 12, color: 'var(--cyan)', cursor: 'pointer' }}>View all →</span>
          </div>
          <table className="data-table">
            <thead><tr><th>Patient</th><th>Type</th><th>Status</th></tr></thead>
            <tbody>
              {RECENT_ESCALATIONS.map((e, i) => (
                <tr key={i}>
                  <td>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{e.patient}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{e.medicine} · {e.time}</div>
                  </td>
                  <td><span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{e.type}</span></td>
                  <td>
                    <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 6, background: e.status === 'resolved' ? 'rgba(0,255,157,0.1)' : 'rgba(239,68,68,0.1)', color: e.status === 'resolved' ? 'var(--emerald)' : '#ef4444' }}>{e.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AdminLayout>
  );
}
