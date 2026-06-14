import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, Pill, ArrowLeft } from 'lucide-react';
import PatientLayout from '@/components/layout/PatientLayout';
import { apiClient, useAuth } from '@/context/AuthContext';

export default function ChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);
  const pollRef = useRef(null);

  const fetchMessages = async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const { data } = await apiClient.get('/chat/messages/');
      setMessages(data.messages || []);
    } catch (err) {
      console.error('Failed to load messages:', err);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    fetchMessages();
    // Poll for new messages every 5 seconds
    pollRef.current = setInterval(() => fetchMessages(true), 5000);
    return () => clearInterval(pollRef.current);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

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
      await apiClient.post('/chat/send/', { message: text });
      // Re-fetch to get AI replies
      setTimeout(() => fetchMessages(true), 1000);
    } catch (err) {
      console.error('Failed to send:', err);
    } finally {
      setSending(false);
    }
  };

  const formatTime = (ts) => {
    if (!ts) return '';
    const d = new Date(ts);
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
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

  if (loading) {
    return (
      <PatientLayout>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
          <Loader2 size={32} color="var(--cyan)" style={{ animation: 'spin 1s linear infinite' }} />
        </div>
      </PatientLayout>
    );
  }

  return (
    <PatientLayout>
      <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 152px)', maxHeight: 'calc(100vh - 152px)' }}>
        {/* Header */}
        <div style={{ marginBottom: 16 }}>
          <h1 className="font-syne" style={{ fontSize: 24, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Bot size={24} color="var(--cyan)" />
            MediMate Chat
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            Your AI health assistant & caretaker communication hub. Respond to reminders and get personalized health nudges.
          </p>
        </div>

        {/* Chat area */}
        <div className="glass-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', padding: 0 }}>
          {/* Messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: 8 }}>
            {messages.length === 0 && (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12, opacity: 0.5 }}>
                <Bot size={48} color="var(--cyan)" strokeWidth={1} />
                <p style={{ color: 'var(--text-muted)', fontSize: 14, textAlign: 'center' }}>
                  No messages yet. Your medication reminders and AI nudges will appear here.
                </p>
              </div>
            )}

            {groupedMessages.map((item, i) => {
              if (item.type === 'date') {
                return (
                  <div key={`date-${i}`} style={{ display: 'flex', justifyContent: 'center', padding: '12px 0' }}>
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', background: 'rgba(255,255,255,0.04)', padding: '4px 14px', borderRadius: 12, fontWeight: 600 }}>
                      {item.date}
                    </span>
                  </div>
                );
              }

              const own = isOwnMessage(item);
              const ai = isAIMessage(item);

              return (
                <div key={item.id} style={{ display: 'flex', justifyContent: own ? 'flex-end' : 'flex-start', marginBottom: 4 }}>
                  <div style={{ maxWidth: '75%', display: 'flex', gap: 8, flexDirection: own ? 'row-reverse' : 'row', alignItems: 'flex-end' }}>
                    {/* Avatar */}
                    {!own && (
                      <div style={{
                        width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                        background: ai
                          ? 'linear-gradient(135deg, var(--cyan), var(--emerald))'
                          : 'linear-gradient(135deg, #a78bfa, var(--cyan))',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                      }}>
                        {ai
                          ? <Bot size={14} color="#050d1a" />
                          : <span style={{ fontSize: 11, fontWeight: 700, color: '#050d1a' }}>{(item.sender_name || 'C')[0]}</span>
                        }
                      </div>
                    )}

                    {/* Bubble */}
                    <div style={{
                      padding: '10px 14px',
                      borderRadius: own ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                      background: own
                        ? 'linear-gradient(135deg, rgba(0,212,255,0.15), rgba(0,255,157,0.1))'
                        : ai
                          ? item.is_reminder
                            ? 'linear-gradient(135deg, rgba(245,158,11,0.12), rgba(239,68,68,0.08))'
                            : 'linear-gradient(135deg, rgba(0,255,157,0.08), rgba(0,212,255,0.06))'
                          : 'rgba(167,139,250,0.1)',
                      border: own
                        ? '1px solid rgba(0,212,255,0.2)'
                        : ai
                          ? item.is_reminder
                            ? '1px solid rgba(245,158,11,0.2)'
                            : '1px solid rgba(0,255,157,0.15)'
                          : '1px solid rgba(167,139,250,0.2)',
                    }}>
                      {/* Sender label */}
                      {!own && (
                        <div style={{ fontSize: 10, fontWeight: 700, marginBottom: 4, color: ai ? 'var(--emerald)' : '#a78bfa', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                          {ai ? (item.is_reminder ? '💊 Medication Reminder' : '🤖 MediMate AI') : item.sender_name || 'Caretaker'}
                        </div>
                      )}
                      <div style={{ fontSize: 13, color: 'var(--text-primary)', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
                        {item.message}
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4, textAlign: own ? 'right' : 'left' }}>
                        {formatTime(item.created_at)}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={bottomRef} />
          </div>

          {/* Input bar */}
          <form onSubmit={handleSend} style={{
            padding: '12px 16px', borderTop: '1px solid var(--border)',
            display: 'flex', gap: 10, alignItems: 'center',
            background: 'rgba(255,255,255,0.02)',
          }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Type your reply... (1=Taken, 2=Snooze, 3=Skip)"
              style={{
                flex: 1, padding: '12px 16px', borderRadius: 12,
                background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)',
                color: 'var(--text-primary)', fontSize: 13, outline: 'none',
                fontFamily: 'Inter, sans-serif',
                transition: 'border-color 0.2s',
              }}
              onFocus={e => e.target.style.borderColor = 'rgba(0,212,255,0.4)'}
              onBlur={e => e.target.style.borderColor = 'var(--border)'}
            />
            <button
              type="submit"
              disabled={!input.trim() || sending}
              style={{
                width: 44, height: 44, borderRadius: 12, border: 'none',
                background: input.trim() ? 'linear-gradient(135deg, var(--cyan), var(--emerald))' : 'rgba(255,255,255,0.06)',
                color: input.trim() ? '#050d1a' : 'var(--text-muted)',
                cursor: input.trim() ? 'pointer' : 'not-allowed',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.2s', flexShrink: 0,
              }}
            >
              {sending
                ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                : <Send size={18} />
              }
            </button>
          </form>
        </div>
      </div>

      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </PatientLayout>
  );
}
