import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, MessageSquare, Search, ArrowLeft } from 'lucide-react';
import CaretakerLayout from '@/components/layout/CaretakerLayout';
import { apiClient, useAuth } from '@/context/AuthContext';

export default function CaretakerChat() {
  const { user } = useAuth();
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [chatLoading, setChatLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [search, setSearch] = useState('');
  const bottomRef = useRef(null);
  const pollRef = useRef(null);

  // Load assigned patients
  useEffect(() => {
    apiClient.get('/patients/caretaker-patients/')
      .then(({ data }) => {
        setPatients(data.patients || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const fetchMessages = async (patientId, silent = false) => {
    if (!patientId) return;
    if (!silent) setChatLoading(true);
    try {
      const { data } = await apiClient.get(`/chat/messages/?patient_id=${patientId}`);
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to load messages:', err);
    } finally {
      if (!silent) setChatLoading(false);
    }
  };

  useEffect(() => {
    if (selectedPatient) {
      fetchMessages(selectedPatient.id);
      pollRef.current = setInterval(() => fetchMessages(selectedPatient.id, true), 5000);
    }
    return () => clearInterval(pollRef.current);
  }, [selectedPatient]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending || !selectedPatient) return;

    setSending(true);
    setInput('');

    // Optimistic add
    const tempMsg = {
      id: `temp-${Date.now()}`,
      sender: user?.id,
      sender_name: user?.name || 'You',
      message: text,
      is_ai_nudge: false,
      is_reminder: false,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, tempMsg]);

    try {
      await apiClient.post('/chat/send/', {
        patient_id: selectedPatient.id,
        message: text
      });
      setTimeout(() => fetchMessages(selectedPatient.id, true), 500);
    } catch (err) {
      console.error('Failed to send:', err);
    } finally {
      setSending(false);
    }
  };

  const formatTime = (ts) => {
    if (!ts) return '';
    return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (ts) => {
    if (!ts) return '';
    const d = new Date(ts);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    if (d.toDateString() === today.toDateString()) return 'Today';
    if (d.toDateString() === yesterday.toDateString()) return 'Yesterday';
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Group messages by date
  const groupedMessages = [];
  let lastDate = '';
  messages.forEach(msg => {
    const dateKey = formatDate(msg.created_at);
    if (dateKey !== lastDate) {
      groupedMessages.push({ type: 'date', date: dateKey });
      lastDate = dateKey;
    }
    groupedMessages.push({ type: 'message', ...msg });
  });

  const isOwnMessage = (msg) => msg.sender === user?.id;
  const isAIMessage = (msg) => msg.is_ai_nudge || msg.is_reminder || !msg.sender;

  const filteredPatients = patients.filter(p =>
    (p.user_name || p.name || '').toLowerCase().includes(search.toLowerCase())
  );

  if (loading) {
    return (
      <CaretakerLayout>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
          <Loader2 size={32} color="#a78bfa" style={{ animation: 'spin 1s linear infinite' }} />
        </div>
      </CaretakerLayout>
    );
  }

  return (
    <CaretakerLayout>
      <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 152px)' }}>
        {/* Header */}
        <div style={{ marginBottom: 16 }}>
          <h1 className="font-syne" style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
            <MessageSquare size={24} color="#a78bfa" />
            Patient Chat
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            Communicate with your assigned patients. View AI nudges and medication reminders.
          </p>
        </div>

        {/* Chat container */}
        <div className="glass-card" style={{ flex: 1, display: 'flex', overflow: 'hidden', padding: 0 }}>
          {/* Patient list sidebar */}
          <div style={{
            width: 280, borderRight: '1px solid var(--border)',
            display: 'flex', flexDirection: 'column',
            background: 'rgba(255,255,255,0.01)',
          }}>
            {/* Search */}
            <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)' }}>
                <Search size={14} color="var(--text-muted)" />
                <input
                  value={search} onChange={e => setSearch(e.target.value)}
                  placeholder="Search patients..."
                  style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--text-primary)', fontSize: 12, outline: 'none' }}
                />
              </div>
            </div>

            {/* Patient list */}
            <div style={{ flex: 1, overflowY: 'auto' }}>
              {filteredPatients.length === 0 ? (
                <div style={{ padding: 20, textAlign: 'center', color: 'var(--text-muted)', fontSize: 12 }}>No patients found</div>
              ) : (
                filteredPatients.map(p => {
                  const isActive = selectedPatient?.id === p.id;
                  return (
                    <div
                      key={p.id}
                      onClick={() => setSelectedPatient(p)}
                      style={{
                        padding: '12px 14px', cursor: 'pointer',
                        borderBottom: '1px solid var(--border)',
                        background: isActive ? 'rgba(167,139,250,0.08)' : 'transparent',
                        borderLeft: isActive ? '3px solid #a78bfa' : '3px solid transparent',
                        transition: 'all 0.15s',
                      }}
                      onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = 'rgba(167,139,250,0.04)'; }}
                      onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = 'transparent'; }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <div style={{
                          width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
                          background: isActive ? 'linear-gradient(135deg, #a78bfa, var(--cyan))' : 'rgba(167,139,250,0.15)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}>
                          <span style={{ fontSize: 12, fontWeight: 700, color: isActive ? '#fff' : '#a78bfa' }}>
                            {(p.user_name || p.name || 'P')[0].toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{p.user_name || p.name || `Patient #${p.id}`}</div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{p.condition || 'Patient'}</div>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Chat area */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            {!selectedPatient ? (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, opacity: 0.4 }}>
                <MessageSquare size={48} color="#a78bfa" strokeWidth={1} />
                <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Select a patient to start chatting</p>
              </div>
            ) : (
              <>
                {/* Chat header */}
                <div style={{ padding: '12px 20px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 10, background: 'rgba(255,255,255,0.02)' }}>
                  <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg, #a78bfa, var(--cyan))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <span style={{ fontSize: 13, fontWeight: 700, color: '#fff' }}>{(selectedPatient.user_name || selectedPatient.name || 'P')[0].toUpperCase()}</span>
                  </div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>{selectedPatient.user_name || selectedPatient.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{selectedPatient.condition || 'Patient'}</div>
                  </div>
                </div>

                {/* Messages */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {chatLoading ? (
                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Loader2 size={24} color="#a78bfa" style={{ animation: 'spin 1s linear infinite' }} />
                    </div>
                  ) : messages.length === 0 ? (
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, opacity: 0.4 }}>
                      <Bot size={40} color="#a78bfa" strokeWidth={1} />
                      <p style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center' }}>No messages yet. Send a message to {selectedPatient.user_name || selectedPatient.name}.</p>
                    </div>
                  ) : (
                    groupedMessages.map((item, i) => {
                      if (item.type === 'date') {
                        return (
                          <div key={`date-${i}`} style={{ display: 'flex', justifyContent: 'center', padding: '12px 0' }}>
                            <span style={{ fontSize: 11, color: 'var(--text-muted)', background: 'rgba(255,255,255,0.04)', padding: '4px 14px', borderRadius: 12, fontWeight: 600 }}>{item.date}</span>
                          </div>
                        );
                      }

                      const own = isOwnMessage(item);
                      const ai = isAIMessage(item);

                      return (
                        <div key={item.id} style={{ display: 'flex', justifyContent: own ? 'flex-end' : 'flex-start', marginBottom: 4 }}>
                          <div style={{ maxWidth: '75%', display: 'flex', gap: 8, flexDirection: own ? 'row-reverse' : 'row', alignItems: 'flex-end' }}>
                            {!own && (
                              <div style={{
                                width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                                background: ai ? 'linear-gradient(135deg, var(--cyan), var(--emerald))' : 'rgba(167,139,250,0.15)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                              }}>
                                {ai ? <Bot size={13} color="#050d1a" /> : <span style={{ fontSize: 10, fontWeight: 700, color: '#a78bfa' }}>{(item.sender_name || 'P')[0]}</span>}
                              </div>
                            )}
                            <div style={{
                              padding: '10px 14px',
                              borderRadius: own ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                              background: own
                                ? 'linear-gradient(135deg, rgba(167,139,250,0.15), rgba(0,212,255,0.08))'
                                : ai
                                  ? item.is_reminder
                                    ? 'linear-gradient(135deg, rgba(245,158,11,0.12), rgba(239,68,68,0.08))'
                                    : 'linear-gradient(135deg, rgba(0,255,157,0.08), rgba(0,212,255,0.06))'
                                  : 'rgba(255,255,255,0.04)',
                              border: own
                                ? '1px solid rgba(167,139,250,0.2)'
                                : ai
                                  ? item.is_reminder
                                    ? '1px solid rgba(245,158,11,0.2)'
                                    : '1px solid rgba(0,255,157,0.15)'
                                  : '1px solid var(--border)',
                            }}>
                              {!own && (
                                <div style={{ fontSize: 10, fontWeight: 700, marginBottom: 4, color: ai ? 'var(--emerald)' : '#a78bfa', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                  {ai ? (item.is_reminder ? '💊 Reminder' : '🤖 AI Nudge') : item.sender_name || 'Patient'}
                                </div>
                              )}
                              <div style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>{item.message}</div>
                              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, textAlign: own ? 'right' : 'left' }}>{formatTime(item.created_at)}</div>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                  <div ref={bottomRef} />
                </div>

                {/* Input */}
                <form onSubmit={handleSend} style={{
                  padding: '12px 16px', borderTop: '1px solid var(--border)',
                  display: 'flex', gap: 10, alignItems: 'center',
                  background: 'rgba(255,255,255,0.02)',
                }}>
                  <input
                    value={input} onChange={e => setInput(e.target.value)}
                    placeholder={`Message ${selectedPatient.user_name || selectedPatient.name}...`}
                    style={{
                      flex: 1, padding: '12px 16px', borderRadius: 12,
                      background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)',
                      color: 'var(--text-primary)', fontSize: 13, outline: 'none',
                      fontFamily: 'Inter, sans-serif', transition: 'border-color 0.2s',
                    }}
                    onFocus={e => e.target.style.borderColor = 'rgba(167,139,250,0.4)'}
                    onBlur={e => e.target.style.borderColor = 'var(--border)'}
                  />
                  <button
                    type="submit" disabled={!input.trim() || sending}
                    style={{
                      width: 44, height: 44, borderRadius: 12, border: 'none',
                      background: input.trim() ? 'linear-gradient(135deg, #a78bfa, var(--cyan))' : 'rgba(255,255,255,0.06)',
                      color: input.trim() ? '#fff' : 'var(--text-muted)',
                      cursor: input.trim() ? 'pointer' : 'not-allowed',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      transition: 'all 0.2s', flexShrink: 0,
                    }}
                  >
                    {sending ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} /> : <Send size={18} />}
                  </button>
                </form>
              </>
            )}
          </div>
        </div>
      </div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </CaretakerLayout>
  );
}
