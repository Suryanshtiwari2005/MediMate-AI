import { useState, useEffect, useCallback } from 'react';
import {
  MessageSquare, Calendar, Loader2, ArrowDownLeft, ArrowUpRight,
  Phone, CheckCheck, Clock, AlertCircle, Inbox, Send
} from 'lucide-react';
import AdminLayout from '@/components/layout/AdminLayout';
import { apiClient } from '@/context/AuthContext';

const DIRECTION_CONFIG = {
  inbound: { label: 'Inbound', color: 'var(--cyan)', bg: 'rgba(0,212,255,0.1)', border: 'rgba(0,212,255,0.2)', icon: ArrowDownLeft },
  outbound: { label: 'Outbound', color: 'var(--emerald)', bg: 'rgba(0,255,157,0.1)', border: 'rgba(0,255,157,0.2)', icon: ArrowUpRight },
};

const STATUS_COLORS = {
  delivered: { color: 'var(--emerald)', icon: CheckCheck },
  sent: { color: 'var(--cyan)', icon: Send },
  read: { color: 'var(--emerald)', icon: CheckCheck },
  failed: { color: '#ef4444', icon: AlertCircle },
  pending: { color: 'var(--amber)', icon: Clock },
  received: { color: 'var(--cyan)', icon: ArrowDownLeft },
};

export default function AdminWhatsAppLog() {
  const [interactions, setInteractions] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [dateFilter, setDateFilter] = useState('');
  const [hoveredCard, setHoveredCard] = useState(null);

  const fetchInteractions = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const params = {};
      if (dateFilter) params.date = dateFilter;
      const { data } = await apiClient.get('/whatsapp/interactions/', { params });
      setInteractions(data.interactions || []);
      setCount(data.count || (data.interactions || []).length);
    } catch (err) {
      console.error('Failed to fetch WhatsApp interactions:', err);
      setInteractions([]);
      setCount(0);
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [dateFilter]);

  useEffect(() => {
    fetchInteractions();
  }, [fetchInteractions]);

  const formatTimestamp = (dateStr) => {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) + ' · ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const getDirectionConfig = (dir) => DIRECTION_CONFIG[dir] || DIRECTION_CONFIG.inbound;

  const getStatusInfo = (status) => {
    const s = (status || '').toLowerCase();
    return STATUS_COLORS[s] || { color: 'var(--text-muted)', icon: Clock };
  };

  const inboundCount = interactions.filter((i) => i.direction === 'inbound').length;
  const outboundCount = interactions.filter((i) => i.direction === 'outbound').length;

  return (
    <AdminLayout>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 4 }}>
          <div style={{ width: 42, height: 42, borderRadius: 12, background: 'rgba(0,255,157,0.1)', border: '1px solid rgba(0,255,157,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <MessageSquare size={20} color="var(--emerald)" />
          </div>
          <div>
            <h1 className="font-syne" style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2 }}>WhatsApp Log</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>View all WhatsApp message interactions</p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14, marginBottom: 24 }}>
        <div className="glass-card" style={{ padding: '18px 20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(167,139,250,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <MessageSquare size={18} color="var(--purple-light)" />
            </div>
            <div>
              <div className="font-syne" style={{ fontSize: 28, fontWeight: 800, color: 'var(--purple-light)' }}>{count}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Total Messages</div>
            </div>
          </div>
        </div>
        <div className="glass-card" style={{ padding: '18px 20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(0,212,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ArrowDownLeft size={18} color="var(--cyan)" />
            </div>
            <div>
              <div className="font-syne" style={{ fontSize: 28, fontWeight: 800, color: 'var(--cyan)' }}>{inboundCount}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Inbound</div>
            </div>
          </div>
        </div>
        <div className="glass-card" style={{ padding: '18px 20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(0,255,157,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ArrowUpRight size={18} color="var(--emerald)" />
            </div>
            <div>
              <div className="font-syne" style={{ fontSize: 28, fontWeight: 800, color: 'var(--emerald)' }}>{outboundCount}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Outbound</div>
            </div>
          </div>
        </div>
      </div>

      {/* Date Filter */}
      <div className="glass-card" style={{ padding: '16px 20px', marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: 10, padding: '10px 14px' }}>
            <Calendar size={16} color="var(--text-muted)" />
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              style={{ background: 'none', border: 'none', outline: 'none', color: 'var(--text-primary)', fontSize: 14, fontFamily: 'inherit', colorScheme: 'dark' }}
            />
          </div>
          {dateFilter && (
            <button
              onClick={() => setDateFilter('')}
              style={{ padding: '10px 16px', borderRadius: 10, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', color: '#ef4444', fontSize: 13, cursor: 'pointer', fontFamily: 'inherit', fontWeight: 500 }}
            >
              Clear Date
            </button>
          )}
          <span style={{ fontSize: 13, color: 'var(--text-muted)', marginLeft: 'auto' }}>
            {count} interaction{count !== 1 ? 's' : ''} recorded
          </span>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="glass-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60, gap: 12 }}>
          <Loader2 size={24} color="var(--emerald)" style={{ animation: 'spin 1s linear infinite' }} />
          <span style={{ color: 'var(--text-muted)', fontSize: 14 }}>Loading WhatsApp interactions...</span>
        </div>
      ) : error || interactions.length === 0 ? (
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '60px 24px', gap: 16 }}>
          <div style={{ width: 72, height: 72, borderRadius: 20, background: 'rgba(0,255,157,0.06)', border: '1px solid rgba(0,255,157,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Inbox size={36} color="var(--text-muted)" strokeWidth={1.2} />
          </div>
          <div style={{ textAlign: 'center' }}>
            <h3 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }}>No WhatsApp interactions recorded yet</h3>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 400, lineHeight: 1.6 }}>
              {error
                ? 'WhatsApp integration may not be fully configured. Please check your Twilio or WhatsApp Business API settings.'
                : 'WhatsApp interactions will appear here once patients start communicating via the WhatsApp channel.'}
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 8, background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.15)' }}>
            <Phone size={14} color="var(--amber)" />
            <span style={{ fontSize: 12, color: 'var(--amber)' }}>WhatsApp channel status: {error ? 'Unavailable' : 'Awaiting data'}</span>
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {interactions.map((msg, idx) => {
            const dirConf = getDirectionConfig(msg.direction);
            const statusInfo = getStatusInfo(msg.status);
            const DirIcon = dirConf.icon;
            const StatusIcon = statusInfo.icon;
            const isHovered = hoveredCard === (msg.id || idx);
            return (
              <div
                key={msg.id || idx}
                className="glass-card"
                onMouseEnter={() => setHoveredCard(msg.id || idx)}
                onMouseLeave={() => setHoveredCard(null)}
                style={{
                  padding: '18px 22px',
                  transition: 'all 0.2s',
                  borderColor: isHovered ? dirConf.border : undefined,
                  transform: isHovered ? 'translateY(-1px)' : 'none',
                }}
              >
                <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                  {/* Direction icon */}
                  <div style={{ width: 40, height: 40, borderRadius: 12, background: dirConf.bg, border: `1px solid ${dirConf.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <DirIcon size={20} color={dirConf.color} />
                  </div>

                  {/* Content */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
                      <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 10px', borderRadius: 6, background: dirConf.bg, color: dirConf.color, display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                        <DirIcon size={10} />
                        {dirConf.label}
                      </span>
                      {msg.patient_name && (
                        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{msg.patient_name}</span>
                      )}
                      <span style={{ fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 6, background: `${statusInfo.color}15`, color: statusInfo.color, display: 'inline-flex', alignItems: 'center', gap: 3, marginLeft: 'auto' }}>
                        <StatusIcon size={10} />
                        {msg.status || 'unknown'}
                      </span>
                    </div>

                    {/* Message body */}
                    <div style={{ padding: '10px 14px', borderRadius: 10, background: msg.direction === 'outbound' ? 'rgba(0,255,157,0.04)' : 'rgba(0,212,255,0.04)', border: `1px solid ${msg.direction === 'outbound' ? 'rgba(0,255,157,0.08)' : 'rgba(0,212,255,0.08)'}`, marginBottom: 8 }}>
                      <p style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0, wordBreak: 'break-word' }}>
                        {msg.message_body || 'No message content'}
                      </p>
                    </div>

                    {/* Timestamp */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <Calendar size={11} color="var(--text-muted)" />
                      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{formatTimestamp(msg.created_at)}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        input[type="date"]::-webkit-calendar-picker-indicator { filter: invert(0.6); cursor: pointer; }
      `}</style>
    </AdminLayout>
  );
}
