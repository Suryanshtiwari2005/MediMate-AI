import { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Phone, MessageSquare, Loader2 } from 'lucide-react';
import PatientLayout from '@/components/layout/PatientLayout';
import { apiClient } from '@/context/AuthContext';

export default function EscalationLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const { data } = await apiClient.get('/escalation/logs/');
        setLogs(data.logs || []);
      } catch (err) {
        console.error('Escalation fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  const typeIcon = (type) => {
    if (type?.toLowerCase().includes('call')) return Phone;
    if (type?.toLowerCase().includes('whatsapp')) return MessageSquare;
    return AlertTriangle;
  };

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
      <div style={{ marginBottom: 28 }}>
        <h1 className="font-syne" style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>Escalation Logs</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Track all escalation events — missed dose alerts, caretaker notifications, and voice calls.</p>
      </div>

      {logs.length === 0 ? (
        <div className="glass-card" style={{ padding: 40, textAlign: 'center' }}>
          <CheckCircle size={32} color="var(--emerald)" style={{ marginBottom: 12 }} />
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>No escalations! You're keeping up with your medications perfectly.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {logs.map((log, i) => {
            const Icon = typeIcon(log.escalation_type);
            const isResolved = log.resolved;
            return (
              <div key={log.id || i} className="glass-card" style={{ padding: 22, border: `1px solid ${isResolved ? 'rgba(0,255,157,0.15)' : 'rgba(239,68,68,0.25)'}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
                  <div style={{ width: 40, height: 40, borderRadius: 10, background: isResolved ? 'rgba(0,255,157,0.1)' : 'rgba(239,68,68,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    {isResolved ? <CheckCircle size={20} color="var(--emerald)" /> : <Icon size={20} color="#ef4444" />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                      <span style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{log.escalation_type || 'Escalation'}</span>
                      <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 6, background: isResolved ? 'rgba(0,255,157,0.1)' : 'rgba(239,68,68,0.1)', color: isResolved ? 'var(--emerald)' : '#ef4444' }}>
                        {isResolved ? 'Resolved' : 'Pending'}
                      </span>
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      {log.medicine_name && `Medicine: ${log.medicine_name} · `}
                      {log.created_at && new Date(log.created_at).toLocaleString()}
                    </div>
                    {log.message && <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 8 }}>{log.message}</p>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </PatientLayout>
  );
}
