import { useState } from 'react';
import { Brain, TrendingUp, AlertTriangle, Info } from 'lucide-react';
import PatientLayout from '@/components/layout/PatientLayout';

const RISK_CONFIG = {
  low:      { label: 'Low Risk',      color: 'var(--emerald)', bg: 'rgba(0,255,157,0.12)', border: 'rgba(0,255,157,0.3)', emoji: '🟢' },
  medium:   { label: 'Medium Risk',   color: 'var(--amber)',   bg: 'rgba(245,158,11,0.12)', border: 'rgba(245,158,11,0.3)', emoji: '🟡' },
  high:     { label: 'High Risk',     color: '#f97316',         bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.3)', emoji: '🟠' },
  critical: { label: 'Critical Risk', color: '#ef4444',         bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)', emoji: '🔴' },
};

const MOCK_PREDICTIONS = [
  { medicine: 'Metformin 500mg', time: '14:00', day: 'Today', risk: 'high', score: 72, reason: 'Historically missed 3 of last 5 afternoon doses' },
  { medicine: 'Lisinopril 10mg', time: '07:00', day: 'Tomorrow', risk: 'low', score: 18, reason: 'Strong morning adherence streak — 12 days' },
  { medicine: 'Atorvastatin 20mg', time: '22:00', day: 'Tomorrow', risk: 'medium', score: 41, reason: 'Bedtime doses missed on weekends historically' },
  { medicine: 'Metformin 500mg', time: '08:00', day: 'Wed', risk: 'medium', score: 38, reason: 'Moderate miss rate on Wednesday mornings' },
  { medicine: 'Lisinopril 10mg', time: '07:00', day: 'Thu', risk: 'low', score: 12, reason: 'Excellent overall adherence, low risk predicted' },
  { medicine: 'Atorvastatin 20mg', time: '22:00', day: 'Fri', risk: 'critical', score: 88, reason: '4 consecutive Friday night misses + no caretaker' },
  { medicine: 'Metformin 500mg', time: '21:00', day: 'Sat', risk: 'high', score: 68, reason: 'Weekend evening pattern: consistently missed' },
];

const FACTORS = [
  { label: 'Miss Rate (30d)', value: 28, color: 'var(--amber)', desc: '28% of doses missed in last 30 days' },
  { label: 'Slot Streak', value: 45, color: 'var(--cyan)', desc: 'Afternoon slot broken 3x this week' },
  { label: 'Schedule Complexity', value: 15, color: 'var(--emerald)', desc: '3 medicines, 5 daily doses' },
  { label: 'Day Pattern', value: 20, color: '#f97316', desc: 'Weekend adherence 40% lower' },
  { label: 'Consecutive Misses', value: 18, color: '#ef4444', desc: '2 consecutive misses detected' },
];

export default function AIPredictions() {
  const [selected, setSelected] = useState(null);
  const overallScore = 38;
  const riskLevel = overallScore < 25 ? 'low' : overallScore < 50 ? 'medium' : overallScore < 75 ? 'high' : 'critical';
  const risk = RISK_CONFIG[riskLevel];

  return (
    <PatientLayout>
      <div style={{ marginBottom: 28 }}>
        <h1 className="font-syne" style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>AI Predictions</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>5-factor risk engine analyzing your adherence patterns to predict future misses.</p>
      </div>

      {/* Overall risk score */}
      <div className="glass-card" style={{ padding: 28, marginBottom: 24, display: 'flex', gap: 28, alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
          <div style={{ width: 100, height: 100, borderRadius: '50%', background: risk.bg, border: `3px solid ${risk.color}`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <span className="font-syne" style={{ fontSize: 28, fontWeight: 800, color: risk.color }}>{overallScore}</span>
            <span style={{ fontSize: 10, color: risk.color, fontWeight: 600 }}>/100</span>
          </div>
          <span style={{ padding: '4px 14px', borderRadius: 20, fontSize: 12, fontWeight: 700, background: risk.bg, color: risk.color, border: `1px solid ${risk.border}` }}>{risk.emoji} {risk.label}</span>
        </div>

        <div style={{ flex: 1, minWidth: 240 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <Brain size={18} color="var(--cyan)" />
            <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)' }}>Risk Factor Breakdown</h3>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {FACTORS.map(f => (
              <div key={f.label}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{f.label}</span>
                  <span style={{ fontSize: 12, fontWeight: 600, color: f.color }}>{f.value}/100</span>
                </div>
                <div style={{ height: 6, borderRadius: 3, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${f.value}%`, background: f.color, borderRadius: 3, transition: 'width 1s ease' }} />
                </div>
                <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 3 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: 'rgba(0,212,255,0.06)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 12, padding: 16, minWidth: 200 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
            <Info size={14} color="var(--cyan)" />
            <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--cyan)' }}>AI Insight</span>
          </div>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Your afternoon doses show a consistent miss pattern. Consider setting an additional WhatsApp reminder 15 minutes before the scheduled time.
          </p>
        </div>
      </div>

      {/* 7-Day Predictions */}
      <div>
        <h2 className="font-syne" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16 }}>7-Day Dose Predictions</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
          {MOCK_PREDICTIONS.map((p, i) => {
            const cfg = RISK_CONFIG[p.risk];
            return (
              <div key={i} className="glass-card" style={{ padding: 20, border: `1px solid ${cfg.border}`, cursor: 'pointer', transition: 'transform 0.2s' }}
                onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseLeave={e => e.currentTarget.style.transform = 'none'}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>{p.medicine}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{p.day} · {p.time}</div>
                  </div>
                  <span style={{ padding: '3px 10px', borderRadius: 20, fontSize: 11, fontWeight: 700, background: cfg.bg, color: cfg.color, whiteSpace: 'nowrap' }}>
                    {cfg.emoji} {p.score}/100
                  </span>
                </div>
                <div style={{ height: 4, borderRadius: 2, background: 'rgba(255,255,255,0.06)', overflow: 'hidden', marginBottom: 10 }}>
                  <div style={{ height: '100%', width: `${p.score}%`, background: cfg.color, borderRadius: 2 }} />
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.5 }}>{p.reason}</p>
              </div>
            );
          })}
        </div>
      </div>
    </PatientLayout>
  );
}
