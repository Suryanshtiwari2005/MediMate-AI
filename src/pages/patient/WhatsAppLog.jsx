import { useState } from 'react';
import { MessageSquare, Send, CheckCheck, Clock, AlertTriangle } from 'lucide-react';
import PatientLayout from '@/components/layout/PatientLayout';

const MOCK_LOGS = [
  { id: 1, medicine: 'Metformin 500mg', time: '14:00', sent_at: '14:00:03', message: 'Time to take Metformin 500mg! Your 8-day streak is impressive 🔥 Reply: 1=Taken, 2=Reschedule +15min, 3=Not Taking', response: '1', response_at: '14:04:22', action: 'Marked as taken', status: 'responded' },
  { id: 2, medicine: 'Atorvastatin 20mg', time: '22:00', sent_at: '22:00:01', message: "Don't forget your Atorvastatin 20mg! Taking medications consistently helps your long-term health. Reply: 1=Taken, 2=Reschedule +15min, 3=Not Taking", response: null, response_at: null, action: 'Escalated to caretaker at 22:45', status: 'escalated' },
  { id: 3, medicine: 'Lisinopril 10mg', time: '07:00', sent_at: '07:00:02', message: 'Good morning! Time for Lisinopril 10mg 🌅 Stay consistent — you\'re doing great! Reply: 1=Taken, 2=Reschedule +15min, 3=Not Taking', response: '2', response_at: '07:08:15', action: 'Rescheduled to 07:15', status: 'rescheduled' },
  { id: 4, medicine: 'Metformin 500mg', time: '08:00', sent_at: '08:00:01', message: 'Morning dose reminder: Metformin 500mg. Keep up your streak! Reply: 1=Taken, 2=Reschedule, 3=Not Taking', response: '1', response_at: '08:02:44', action: 'Marked as taken', status: 'responded' },
  { id: 5, medicine: 'Metformin 500mg', time: '21:00', sent_at: '21:00:04', message: 'Evening Metformin 500mg reminder. Almost done for the day! Reply: 1=Taken, 2=Reschedule, 3=Not Taking', response: '3', response_at: '21:15:30', action: 'Caretaker alert sent immediately', status: 'not_taking' },
];

const STATUS_CONFIG = {
  responded:   { label: 'Taken',        color: 'var(--emerald)', bg: 'rgba(0,255,157,0.1)', icon: CheckCheck },
  escalated:   { label: 'Escalated',    color: '#ef4444',        bg: 'rgba(239,68,68,0.1)', icon: AlertTriangle },
  rescheduled: { label: 'Rescheduled',  color: 'var(--cyan)',    bg: 'rgba(0,212,255,0.1)', icon: Clock },
  not_taking:  { label: 'Not Taking',   color: 'var(--amber)',   bg: 'rgba(245,158,11,0.1)', icon: AlertTriangle },
};

function SimulateModal({ onClose }) {
  const [dose, setDose] = useState('');
  const [reply, setReply] = useState('1');

  const inputStyle = { width: '100%', padding: '10px 14px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, outline: 'none' };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div style={{ background: 'var(--bg-card)', borderRadius: 16, border: '1px solid var(--border)', padding: 28, width: '100%', maxWidth: 400, animation: 'fadeInUp 0.2s ease' }}>
        <h3 className="font-syne" style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>Simulate WhatsApp Reply</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 20 }}>Test the webhook handler with a simulated patient reply.</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>DOSE ID</label>
            <input value={dose} onChange={e => setDose(e.target.value)} placeholder="e.g. 101" style={inputStyle} />
          </div>
          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>REPLY</label>
            <select value={reply} onChange={e => setReply(e.target.value)} style={inputStyle}>
              <option value="1">1 — Taken</option>
              <option value="2">2 — Reschedule +15 min</option>
              <option value="3">3 — Not Taking (escalate)</option>
            </select>
          </div>
          <button onClick={() => { alert(`Webhook simulated: Dose ${dose}, Reply ${reply}`); onClose(); }} className="btn-primary" style={{ width: '100%' }}>Send Simulation</button>
        </div>
      </div>
    </div>
  );
}

export default function WhatsAppLog() {
  const [simOpen, setSimOpen] = useState(false);

  return (
    <PatientLayout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h1 className="font-syne" style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>WhatsApp Log</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>All sent reminders, patient replies, and automated actions.</p>
        </div>
        <button onClick={() => setSimOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'rgba(37,211,102,0.1)', border: '1px solid rgba(37,211,102,0.3)', borderRadius: 8, padding: '9px 16px', color: '#25D366', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
          <Send size={14} /> Simulate Reply
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        {MOCK_LOGS.map(log => {
          const cfg = STATUS_CONFIG[log.status];
          const Icon = cfg?.icon || MessageSquare;
          return (
            <div key={log.id} className="glass-card" style={{ padding: 22, border: `1px solid ${cfg?.color}25` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: '#25D36620', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <MessageSquare size={18} color="#25D366" />
                  </div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{log.medicine}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Scheduled: {log.time} · Sent: {log.sent_at}</div>
                  </div>
                </div>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 700, background: cfg?.bg, color: cfg?.color }}>
                  <Icon size={12} /> {cfg?.label}
                </span>
              </div>

              {/* Message bubble */}
              <div style={{ background: 'rgba(37,211,102,0.06)', border: '1px solid rgba(37,211,102,0.15)', borderRadius: 10, padding: '12px 14px', marginBottom: 12 }}>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{log.message}</p>
              </div>

              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                {log.response ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Reply:</span>
                    <span style={{ fontSize: 12, fontWeight: 700, color: cfg?.color, background: cfg?.bg, padding: '2px 8px', borderRadius: 6 }}>{log.response}</span>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>at {log.response_at}</span>
                  </div>
                ) : (
                  <span style={{ fontSize: 12, color: '#ef4444' }}>No response received</span>
                )}
                {log.action && (
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>→ {log.action}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {simOpen && <SimulateModal onClose={() => setSimOpen(false)} />}
    </PatientLayout>
  );
}
