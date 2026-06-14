import { useState, useEffect } from 'react';
import { MessageSquare, Send, CheckCheck, Clock, AlertTriangle, Loader2 } from 'lucide-react';
import PatientLayout from '@/components/layout/PatientLayout';
import { apiClient } from '@/context/AuthContext';

const STATUS_CONFIG = {
  sent:        { label: 'Sent',         color: 'var(--cyan)',    bg: 'rgba(0,212,255,0.1)', icon: Send },
  responded:   { label: 'Responded',    color: 'var(--emerald)', bg: 'rgba(0,255,157,0.1)', icon: CheckCheck },
  escalated:   { label: 'Escalated',    color: '#ef4444',        bg: 'rgba(239,68,68,0.1)', icon: AlertTriangle },
  rescheduled: { label: 'Rescheduled',  color: 'var(--cyan)',    bg: 'rgba(0,212,255,0.1)', icon: Clock },
  expired:     { label: 'Expired',      color: 'var(--text-muted)', bg: 'rgba(255,255,255,0.04)', icon: Clock },
};

function SimulateModal({ onClose }) {
  const [doseId, setDoseId] = useState('');
  const [reply, setReply] = useState('1');
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);

  const handleSend = async () => {
    if (!doseId) return;
    setSending(true);
    try {
      const { data } = await apiClient.post('/whatsapp/webhook/', {
        Body: reply,
        From: '+0000000000', // Simulated
        dose_id: doseId,
      });
      setResult(data);
    } catch (err) {
      setResult({ error: err.response?.data?.error || 'Webhook failed' });
    } finally {
      setSending(false);
    }
  };

  const inputStyle = { width: '100%', padding: '10px 14px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, outline: 'none' };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div style={{ background: 'var(--bg-card)', borderRadius: 16, border: '1px solid var(--border)', padding: 28, width: '100%', maxWidth: 400, animation: 'fadeInUp 0.2s ease' }}>
        <h3 className="font-syne" style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>Simulate WhatsApp Reply</h3>
        <p style={{ color: 'var(--text-muted)', fontSize: 13, marginBottom: 20 }}>Test the webhook handler with a simulated patient reply.</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>DOSE ID</label>
            <input value={doseId} onChange={e => setDoseId(e.target.value)} placeholder="e.g. 101" style={inputStyle} />
          </div>
          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, letterSpacing: '0.05em', display: 'block', marginBottom: 6 }}>REPLY</label>
            <select value={reply} onChange={e => setReply(e.target.value)} style={inputStyle}>
              <option value="1">1 — Taken</option>
              <option value="2">2 — Reschedule +15 min</option>
              <option value="3">3 — Not Taking (escalate)</option>
            </select>
          </div>
          {result && (
            <div style={{ background: result.error ? 'rgba(239,68,68,0.1)' : 'rgba(0,255,157,0.1)', border: `1px solid ${result.error ? 'rgba(239,68,68,0.3)' : 'rgba(0,255,157,0.3)'}`, borderRadius: 8, padding: '10px 14px' }}>
              <p style={{ color: result.error ? '#ef4444' : 'var(--emerald)', fontSize: 13 }}>{result.error || result.reply}</p>
            </div>
          )}
          <button onClick={handleSend} disabled={sending || !doseId} className="btn-primary" style={{ width: '100%' }}>
            {sending ? 'Sending...' : 'Send Simulation'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function WhatsAppLog() {
  const [simOpen, setSimOpen] = useState(false);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const { data } = await apiClient.get('/whatsapp/interactions/');
        setLogs(data.interactions || []);
      } catch (err) {
        console.error('Error fetching WhatsApp logs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  if (loading) {
    return (
      <PatientLayout>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
          <Loader2 size={32} color="var(--cyan)" style={{ animation: 'spin 1s linear infinite' }} />
        </div>
      </PatientLayout>
    );
  }

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

      {logs.length === 0 ? (
        <div className="glass-card" style={{ padding: 40, textAlign: 'center' }}>
          <MessageSquare size={32} color="var(--text-muted)" style={{ marginBottom: 12 }} />
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>No WhatsApp interactions yet. Reminders will appear here when sent.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {logs.map(log => {
            const cfg = STATUS_CONFIG[log.status] || STATUS_CONFIG.sent;
            const Icon = cfg?.icon || MessageSquare;
            return (
              <div key={log.id} className="glass-card" style={{ padding: 22, border: `1px solid ${cfg?.color}25` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12, flexWrap: 'wrap', gap: 8 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 36, height: 36, borderRadius: 10, background: '#25D36620', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <MessageSquare size={18} color="#25D366" />
                    </div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{log.medicine_name || `Dose #${log.dose_log}`}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Sent: {log.sent_at ? new Date(log.sent_at).toLocaleString() : '—'}</div>
                    </div>
                  </div>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 700, background: cfg?.bg, color: cfg?.color }}>
                    <Icon size={12} /> {cfg?.label}
                  </span>
                </div>

                {log.message_body && (
                  <div style={{ background: 'rgba(37,211,102,0.06)', border: '1px solid rgba(37,211,102,0.15)', borderRadius: 10, padding: '12px 14px', marginBottom: 12 }}>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{log.message_body}</p>
                  </div>
                )}

                <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                  {log.response_received ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>Reply:</span>
                      <span style={{ fontSize: 12, fontWeight: 700, color: cfg?.color, background: cfg?.bg, padding: '2px 8px', borderRadius: 6 }}>{log.response_received}</span>
                      {log.response_time && <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>at {new Date(log.response_time).toLocaleTimeString()}</span>}
                    </div>
                  ) : (
                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>No response received</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {simOpen && <SimulateModal onClose={() => setSimOpen(false)} />}
    </PatientLayout>
  );
}
