import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Users, AlertTriangle, LayoutDashboard, LogOut, Pill, Bell, Activity } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const PATIENTS = [
  { id: 1, name: 'Priya Sharma', age: 58, condition: 'Type 2 Diabetes', risk: 'medium', score: 42, todayDoses: 5, takenDoses: 3, missedDoses: 1, pendingDoses: 1, medicines: ['Metformin 500mg', 'Lisinopril 10mg'] },
  { id: 2, name: 'Suresh Patel', age: 72, condition: 'Hypertension + Cholesterol', risk: 'high', score: 68, todayDoses: 3, takenDoses: 1, missedDoses: 2, pendingDoses: 0, medicines: ['Atorvastatin 20mg', 'Amlodipine 5mg'] },
  { id: 3, name: 'Meera Iyer', age: 45, condition: 'Thyroid disorder', risk: 'low', score: 15, todayDoses: 2, takenDoses: 2, missedDoses: 0, pendingDoses: 0, medicines: ['Levothyroxine 50mcg'] },
];

const ESCALATIONS = [
  { patient: 'Suresh Patel', medicine: 'Amlodipine 5mg', time: '09:00', missedBy: '45 min', type: 'Caretaker Alert', status: 'pending' },
  { patient: 'Priya Sharma', medicine: 'Metformin 500mg', time: '14:00', missedBy: '30 min', type: 'WhatsApp Sent', status: 'awaiting' },
];

const RISK_CONFIG = {
  low:    { color: 'var(--emerald)', bg: 'rgba(0,255,157,0.1)', label: '🟢 Low' },
  medium: { color: 'var(--amber)',   bg: 'rgba(245,158,11,0.1)', label: '🟡 Medium' },
  high:   { color: '#ef4444',        bg: 'rgba(239,68,68,0.1)', label: '🔴 High' },
};

function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const NAV = [
    { label: 'Dashboard', icon: LayoutDashboard, to: '/caretaker' },
    { label: 'Patients', icon: Users, to: '/caretaker/patients' },
    { label: 'Escalations', icon: AlertTriangle, to: '/caretaker/escalations' },
  ];
  return (
    <div style={{ width: 240, background: 'var(--bg-secondary)', borderRight: '1px solid var(--border)', height: '100vh', display: 'flex', flexDirection: 'column', padding: '0 12px', position: 'sticky', top: 0 }}>
      <div style={{ padding: '20px 12px', borderBottom: '1px solid var(--border)', marginBottom: 8 }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <div style={{ width: 32, height: 32, borderRadius: 8, background: 'linear-gradient(135deg, #a78bfa, var(--cyan))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Pill size={16} color="#fff" strokeWidth={2.5} />
          </div>
          <div>
            <div className="font-syne" style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>MediMate <span style={{ color: '#a78bfa' }}>Care</span></div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>Caretaker Portal</div>
          </div>
        </Link>
      </div>
      <div style={{ padding: '12px 12px', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg, #a78bfa, var(--cyan))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: '#fff' }}>{user?.name?.[0]?.toUpperCase() || 'C'}</span>
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{user?.name || 'Caretaker'}</div>
            <div style={{ fontSize: 11, color: '#a78bfa' }}>Caretaker</div>
          </div>
        </div>
      </div>
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {NAV.map(({ label, icon: Icon, to }) => {
          const active = location.pathname === to;
          return (
            <Link key={to} to={to} className={`sidebar-item ${active ? 'active' : ''}`} style={active ? { borderLeft: '2px solid #a78bfa', color: '#a78bfa' } : {}}>
              <Icon size={17} /> {label}
            </Link>
          );
        })}
      </nav>
      <div style={{ padding: '12px 0', borderTop: '1px solid var(--border)' }}>
        <button onClick={async () => { await logout(); navigate('/'); }} className="sidebar-item" style={{ width: '100%', background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444' }}>
          <LogOut size={17} /> Logout
        </button>
      </div>
    </div>
  );
}

export default function CaretakerDashboard() {
  const { user } = useAuth();

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <div style={{ flexShrink: 0 }}><Sidebar /></div>
      <div style={{ flex: 1, overflow: 'auto' }}>
        <div style={{ height: 56, borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', padding: '0 28px', position: 'sticky', top: 0, background: 'rgba(5,13,26,0.9)', backdropFilter: 'blur(12px)', zIndex: 10 }}>
          <div style={{ flex: 1 }}><span style={{ fontSize: 12, color: '#a78bfa', fontWeight: 600 }}>CARETAKER PORTAL</span></div>
          <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}><Bell size={18} /></button>
        </div>

        <div style={{ padding: '32px 28px' }}>
          <div style={{ marginBottom: 28 }}>
            <h1 className="font-syne" style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>Patient Monitor</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>All your assigned patients in one view.</p>
          </div>

          {/* Summary stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16, marginBottom: 32 }}>
            {[
              { label: 'Total Patients', value: PATIENTS.length, color: '#a78bfa', icon: Users },
              { label: 'At Risk', value: PATIENTS.filter(p => p.risk !== 'low').length, color: 'var(--amber)', icon: AlertTriangle },
              { label: 'All Good', value: PATIENTS.filter(p => p.risk === 'low').length, color: 'var(--emerald)', icon: Activity },
              { label: 'Escalations', value: ESCALATIONS.length, color: '#ef4444', icon: AlertTriangle },
            ].map(s => (
              <div key={s.label} className="glass-card" style={{ padding: '20px 22px', display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{ width: 38, height: 38, borderRadius: 10, background: `${s.color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <s.icon size={18} color={s.color} />
                </div>
                <div>
                  <div className="font-syne" style={{ fontSize: 24, fontWeight: 800, color: s.color }}>{s.value}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>{s.label}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Patient cards */}
          <h2 className="font-syne" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16 }}>Assigned Patients</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 16, marginBottom: 32 }}>
            {PATIENTS.map(p => {
              const risk = RISK_CONFIG[p.risk];
              const adherence = Math.round((p.takenDoses / p.todayDoses) * 100);
              return (
                <div key={p.id} className="glass-card" style={{ padding: 22, border: `1px solid ${risk.color}20`, transition: 'transform 0.2s' }}
                  onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
                  onMouseLeave={e => e.currentTarget.style.transform = 'none'}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{ width: 40, height: 40, borderRadius: '50%', background: `${risk.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <span style={{ fontSize: 16, fontWeight: 700, color: risk.color }}>{p.name[0]}</span>
                      </div>
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{p.name}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Age {p.age} · {p.condition}</div>
                      </div>
                    </div>
                    <span style={{ fontSize: 12, fontWeight: 700, padding: '3px 10px', borderRadius: 20, background: risk.bg, color: risk.color }}>{risk.label}</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                    {[['Taken', p.takenDoses, 'var(--emerald)'], ['Missed', p.missedDoses, '#ef4444'], ['Pending', p.pendingDoses, 'var(--amber)']].map(([l, v, c]) => (
                      <div key={l} style={{ textAlign: 'center' }}>
                        <div className="font-syne" style={{ fontSize: 20, fontWeight: 800, color: c }}>{v}</div>
                        <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{l}</div>
                      </div>
                    ))}
                  </div>

                  <div style={{ marginBottom: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Today's adherence</span>
                      <span style={{ fontSize: 11, fontWeight: 600, color: risk.color }}>{adherence}%</span>
                    </div>
                    <div style={{ height: 6, borderRadius: 3, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${adherence}%`, background: risk.color, borderRadius: 3 }} />
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>Active medicines:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {p.medicines.map(m => (
                        <span key={m} style={{ fontSize: 11, background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', borderRadius: 6, padding: '2px 8px', color: 'var(--text-secondary)' }}>{m}</span>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Escalations */}
          <h2 className="font-syne" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16 }}>Live Escalation Feed</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {ESCALATIONS.map((e, i) => (
              <div key={i} className="glass-card" style={{ padding: '18px 22px', border: '1px solid rgba(239,68,68,0.25)', display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(239,68,68,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <AlertTriangle size={18} color="#ef4444" />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{e.patient}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{e.medicine} · Scheduled {e.time} · Missed by {e.missedBy}</div>
                </div>
                <div style={{ display: 'flex', align: 'center', gap: 10 }}>
                  <span style={{ fontSize: 12, color: '#f97316' }}>{e.type}</span>
                  <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 20, background: e.status === 'pending' ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)', color: e.status === 'pending' ? '#ef4444' : 'var(--amber)' }}>{e.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
