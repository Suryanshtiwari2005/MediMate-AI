import { useState, useEffect } from 'react';
import { Plus, Pill, Clock, Trash2, ToggleLeft, ToggleRight, X, Loader2 } from 'lucide-react';
import PatientLayout from '@/components/layout/PatientLayout';
import { apiClient } from '@/context/AuthContext';

function AddMedicineModal({ onClose, onAdded }) {
  const [form, setForm] = useState({ name: '', dosage: '', instructions: '' });
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));
  const inputStyle = { width: '100%', padding: '10px 14px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, outline: 'none' };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await apiClient.post('/medicines/list/', form);
      onAdded();
      onClose();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add medicine');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div style={{ background: 'var(--bg-card)', borderRadius: 16, border: '1px solid var(--border)', padding: 28, width: '100%', maxWidth: 440, animation: 'fadeInUp 0.2s ease' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 className="font-syne" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>Add Medicine</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>MEDICINE NAME</label>
            <input required value={form.name} onChange={set('name')} placeholder="e.g. Metformin" style={inputStyle} />
          </div>
          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>DOSAGE</label>
            <input required value={form.dosage} onChange={set('dosage')} placeholder="e.g. 500mg" style={inputStyle} />
          </div>
          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>INSTRUCTIONS</label>
            <input value={form.instructions} onChange={set('instructions')} placeholder="e.g. Take with food" style={inputStyle} />
          </div>
          <button type="submit" disabled={loading} className="btn-primary" style={{ width: '100%', marginTop: 8 }}>
            {loading ? 'Adding...' : 'Add Medicine'}
          </button>
        </form>
      </div>
    </div>
  );
}

function AddScheduleModal({ medicines, onClose, onAdded }) {
  const [form, setForm] = useState({ medicine_id: '', time: '08:00', start_date: new Date().toISOString().split('T')[0], end_date: '' });
  const [loading, setLoading] = useState(false);
  const [conflicts, setConflicts] = useState(null);
  const [conflictLoading, setConflictLoading] = useState(false);
  const [bypassConfirmed, setBypassConfirmed] = useState(false);
  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));
  const inputStyle = { width: '100%', padding: '10px 14px', borderRadius: 8, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, outline: 'none' };

  // Check for conflicts when medicine is selected
  const handleMedicineChange = async (e) => {
    const medId = e.target.value;
    setForm(f => ({ ...f, medicine_id: medId }));
    setConflicts(null);
    setBypassConfirmed(false);

    if (!medId) return;

    setConflictLoading(true);
    try {
      const { data } = await apiClient.post('/chat/check-conflict/', { medicine_id: parseInt(medId) });
      if (data && !data.safe && data.warnings?.length > 0) {
        setConflicts(data);
      }
    } catch (err) {
      console.error('Conflict check failed:', err);
      // Don't block the user if the check fails
    } finally {
      setConflictLoading(false);
    }
  };

  const hasMajorConflict = conflicts?.warnings?.some(w => w.severity === 'major');
  const canSubmit = !loading && !conflictLoading && (!conflicts || (!hasMajorConflict && bypassConfirmed) || (!conflicts));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (hasMajorConflict) return;
    if (conflicts && !bypassConfirmed) return;

    setLoading(true);
    try {
      await apiClient.post('/medicines/schedules/', {
        medicine_id: parseInt(form.medicine_id),
        scheduled_time: form.time,
        start_date: form.start_date,
        end_date: form.end_date || null,
      });
      onAdded();
      onClose();
    } catch (err) {
      alert(err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Failed to add schedule');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div style={{ background: 'var(--bg-card)', borderRadius: 16, border: '1px solid var(--border)', padding: 28, width: '100%', maxWidth: 440, animation: 'fadeInUp 0.2s ease' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 className="font-syne" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>Add Schedule</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={18} /></button>
        </div>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>MEDICINE</label>
            <select required value={form.medicine_id} onChange={handleMedicineChange} style={{ ...inputStyle, cursor: 'pointer' }}>
              <option value="">Select medicine...</option>
              {medicines.map(m => <option key={m.id} value={m.id}>{m.name} ({m.dosage})</option>)}
            </select>
          </div>

          {/* Conflict Loading */}
          {conflictLoading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '10px 14px', borderRadius: 10, background: 'rgba(0,212,255,0.06)', border: '1px solid rgba(0,212,255,0.15)' }}>
              <Loader2 size={14} color="var(--cyan)" style={{ animation: 'spin 1s linear infinite' }} />
              <span style={{ fontSize: 12, color: 'var(--cyan)', fontWeight: 500 }}>Checking for medicine interactions with AI...</span>
            </div>
          )}

          {/* Conflict Warnings */}
          {conflicts && conflicts.warnings?.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {conflicts.warnings.map((w, i) => (
                <div key={i} style={{
                  padding: '10px 14px', borderRadius: 10,
                  background: w.severity === 'major' ? 'rgba(239,68,68,0.08)' : 'rgba(245,158,11,0.08)',
                  border: `1px solid ${w.severity === 'major' ? 'rgba(239,68,68,0.25)' : 'rgba(245,158,11,0.25)'}`,
                }}>
                  <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', marginBottom: 4, color: w.severity === 'major' ? '#ef4444' : 'var(--amber)' }}>
                    {w.severity === 'major' ? '🚫 Major Conflict' : w.severity === 'moderate' ? '⚠️ Moderate Warning' : '💡 Minor Note'}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{w.message}</div>
                </div>
              ))}

              {hasMajorConflict && (
                <div style={{ fontSize: 12, color: '#ef4444', fontWeight: 600, textAlign: 'center', padding: '6px 0' }}>
                  This medicine cannot be scheduled due to a major conflict. Please consult your doctor.
                </div>
              )}

              {!hasMajorConflict && (
                <label style={{ display: 'flex', alignItems: 'flex-start', gap: 8, cursor: 'pointer', padding: '6px 0' }}>
                  <input
                    type="checkbox"
                    checked={bypassConfirmed}
                    onChange={e => setBypassConfirmed(e.target.checked)}
                    style={{ marginTop: 2, accentColor: 'var(--amber)' }}
                  />
                  <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                    I have consulted my doctor and wish to schedule this medicine anyway.
                  </span>
                </label>
              )}
            </div>
          )}

          <div>
            <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>TIME</label>
            <input required type="time" value={form.time} onChange={set('time')} style={inputStyle} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>START DATE</label>
              <input required type="date" value={form.start_date} onChange={set('start_date')} style={inputStyle} />
            </div>
            <div>
              <label style={{ color: 'var(--text-secondary)', fontSize: 12, fontWeight: 600, display: 'block', marginBottom: 6 }}>END DATE (optional)</label>
              <input type="date" value={form.end_date} onChange={set('end_date')} style={inputStyle} />
            </div>
          </div>
          <button
            type="submit"
            disabled={loading || hasMajorConflict || (conflicts && !hasMajorConflict && !bypassConfirmed)}
            className="btn-primary"
            style={{ width: '100%', marginTop: 8, opacity: (hasMajorConflict || (conflicts && !bypassConfirmed)) ? 0.5 : 1 }}
          >
            {loading ? 'Adding...' : 'Add Schedule'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function MedicinesPage() {
  const [medicines, setMedicines] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddMed, setShowAddMed] = useState(false);
  const [showAddSched, setShowAddSched] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [medRes, schedRes] = await Promise.all([
        apiClient.get('/medicines/list/').catch(() => ({ data: { results: [] } })),
        apiClient.get('/medicines/schedules/').catch(() => ({ data: { results: [] } })),
      ]);
      setMedicines(medRes.data.results || medRes.data || []);
      setSchedules(schedRes.data.results || schedRes.data || []);
    } catch (err) {
      console.error('Medicines fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleDeleteMed = async (id) => {
    if (!confirm('Delete this medicine?')) return;
    try {
      await apiClient.delete(`/medicines/list/${id}/`);
      fetchData();
    } catch (err) {
      alert('Failed to delete');
    }
  };

  const handleToggleSchedule = async (id) => {
    try {
      await apiClient.post(`/medicines/schedules/${id}/toggle_active/`);
      fetchData();
    } catch (err) {
      alert('Failed to toggle');
    }
  };

  const handleDeleteSchedule = async (id) => {
    if (!confirm('Delete this schedule?')) return;
    try {
      await apiClient.delete(`/medicines/schedules/${id}/`);
      fetchData();
    } catch (err) {
      alert('Failed to delete');
    }
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
        <h1 className="font-syne" style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>My Medicines</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>Manage your medications and daily schedules.</p>
      </div>

      {/* Medicines Section */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 className="font-syne" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>Medicines</h2>
        <button onClick={() => setShowAddMed(true)} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(0,212,255,0.1)', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 8, padding: '7px 14px', color: 'var(--cyan)', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}>
          <Plus size={14} /> Add Medicine
        </button>
      </div>

      {medicines.length === 0 ? (
        <div className="glass-card" style={{ padding: 40, textAlign: 'center', marginBottom: 32 }}>
          <Pill size={28} color="var(--text-muted)" style={{ marginBottom: 10 }} />
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>No medicines added yet. Click "Add Medicine" to start.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 14, marginBottom: 32 }}>
          {medicines.map(med => (
            <div key={med.id} className="glass-card" style={{ padding: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 40, height: 40, borderRadius: 10, background: 'linear-gradient(135deg, rgba(0,212,255,0.2), rgba(0,255,157,0.2))', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <span style={{ fontSize: 18 }}>💊</span>
                  </div>
                  <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{med.name}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{med.dosage}</div>
                  </div>
                </div>
                <button onClick={() => handleDeleteMed(med.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                  <Trash2 size={14} />
                </button>
              </div>
              {med.instructions && <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 10 }}>{med.instructions}</p>}
            </div>
          ))}
        </div>
      )}

      {/* Schedules Section */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 className="font-syne" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>Schedules</h2>
        <button onClick={() => setShowAddSched(true)} disabled={medicines.length === 0} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'rgba(0,255,157,0.1)', border: '1px solid rgba(0,255,157,0.2)', borderRadius: 8, padding: '7px 14px', color: 'var(--emerald)', fontSize: 13, fontWeight: 600, cursor: medicines.length === 0 ? 'not-allowed' : 'pointer', opacity: medicines.length === 0 ? 0.5 : 1 }}>
          <Clock size={14} /> Add Schedule
        </button>
      </div>

      {schedules.length === 0 ? (
        <div className="glass-card" style={{ padding: 40, textAlign: 'center' }}>
          <Clock size={28} color="var(--text-muted)" style={{ marginBottom: 10 }} />
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>No schedules set. Add a schedule to start getting reminders.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {schedules.map(sched => (
            <div key={sched.id} className="glass-card" style={{ padding: '16px 22px', display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', opacity: sched.is_active ? 1 : 0.5 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(0,255,157,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Clock size={18} color="var(--emerald)" />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{sched.medicine?.name || `Medicine #${sched.medicine}`}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  Time: {(sched.scheduled_time || sched.time)?.slice(0, 5)} · From: {sched.start_date} {sched.end_date ? `→ ${sched.end_date}` : '(ongoing)'}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <button onClick={() => handleToggleSchedule(sched.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: sched.is_active ? 'var(--emerald)' : 'var(--text-muted)' }}>
                  {sched.is_active ? <ToggleRight size={22} /> : <ToggleLeft size={22} />}
                </button>
                <button onClick={() => handleDeleteSchedule(sched.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showAddMed && <AddMedicineModal onClose={() => setShowAddMed(false)} onAdded={fetchData} />}
      {showAddSched && <AddScheduleModal medicines={medicines} onClose={() => setShowAddSched(false)} onAdded={fetchData} />}
    </PatientLayout>
  );
}
