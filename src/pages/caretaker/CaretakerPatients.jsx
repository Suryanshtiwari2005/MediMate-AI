import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, AlertTriangle, Activity, Search, Loader2, Phone, Heart, Shield, Plus, X } from 'lucide-react';
import { apiClient } from '@/context/AuthContext';
import CaretakerLayout from '@/components/layout/CaretakerLayout';

const RISK_CONFIG = {
  low:      { color: 'var(--emerald)', bg: 'rgba(0,255,157,0.1)',  label: '🟢 Low' },
  medium:   { color: 'var(--amber)',   bg: 'rgba(245,158,11,0.1)', label: '🟡 Medium' },
  high:     { color: '#ef4444',        bg: 'rgba(239,68,68,0.1)',  label: '🔴 High' },
  critical: { color: '#ef4444',        bg: 'rgba(239,68,68,0.15)', label: '🔴 Critical' },
};

export default function CaretakerPatients() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  // Link Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('existing'); // 'existing' | 'new'
  const [email, setEmail] = useState('');
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState('');
  const [modalSuccess, setModalSuccess] = useState('');

  // Create New Patient Form States
  const [newForm, setNewForm] = useState({
    name: '',
    email: '',
    age: '',
    gender: 'male',
    blood_group: '',
    diseases: '',
    allergies: '',
    chronic_conditions: '',
    whatsapp_number: '',
    emergency_phone: '',
  });

  useEffect(() => {
    apiClient.get('/patients/')
      .then(res => setPatients(Array.isArray(res.data) ? res.data : []))
      .catch(() => setPatients([]))
      .finally(() => setLoading(false));
  }, []);

  const handleLinkPatient = async () => {
    setModalLoading(true);
    setModalError('');
    setModalSuccess('');
    try {
      const res = await apiClient.post('/patients/caretakers/link_patient/', { email });
      const newPatient = res.data.patient;
      
      // Update local state list
      setPatients(prev => [...prev, newPatient]);
      setModalSuccess('Patient linked successfully!');
      
      // Close modal after a short delay
      setTimeout(() => {
        setIsModalOpen(false);
      }, 1500);
    } catch (err) {
      console.error('Link patient error:', err);
      const msg = err.response?.data?.error || err.response?.data?.detail || 'Failed to link patient. Ensure the email is correct and they have onboarded.';
      setModalError(msg);
    } finally {
      setModalLoading(false);
    }
  };

  const handleCreateAndLinkPatient = async () => {
    setModalLoading(true);
    setModalError('');
    setModalSuccess('');
    try {
      const payload = {
        name: newForm.name,
        email: newForm.email,
        age: parseInt(newForm.age) || null,
        gender: newForm.gender,
        blood_group: newForm.blood_group || null,
        diseases: newForm.diseases,
        allergies: newForm.allergies,
        chronic_conditions: newForm.chronic_conditions,
        whatsapp_number: newForm.whatsapp_number || null,
        emergency_phone: newForm.emergency_phone || null,
      };

      const res = await apiClient.post('/patients/caretakers/create_and_link_patient/', payload);
      const newPatient = res.data.patient;

      // Update local state list
      setPatients(prev => [...prev, newPatient]);
      setModalSuccess('Patient created and linked successfully!');

      // Reset form
      setNewForm({
        name: '',
        email: '',
        age: '',
        gender: 'male',
        blood_group: '',
        diseases: '',
        allergies: '',
        chronic_conditions: '',
        whatsapp_number: '',
        emergency_phone: '',
      });

      // Close modal after a short delay
      setTimeout(() => {
        setIsModalOpen(false);
      }, 1500);
    } catch (err) {
      console.error('Create and link patient error:', err);
      const msg = err.response?.data?.error || err.response?.data?.detail || 'Failed to create patient. Verify your inputs.';
      setModalError(msg);
    } finally {
      setModalLoading(false);
    }
  };

  const filtered = useMemo(() => {
    if (!search.trim()) return patients;
    const q = search.toLowerCase();
    return patients.filter(p => {
      const name = (p.user_name || p.user?.full_name || '').toLowerCase();
      return name.includes(q);
    });
  }, [patients, search]);

  const atRisk = patients.filter(p => p.risk_level && p.risk_level !== 'low').length;
  const allGood = patients.filter(p => !p.risk_level || p.risk_level === 'low').length;

  // Custom Input Style
  const inputStyle = {
    width: '100%',
    padding: '12px 14px',
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid var(--border)',
    borderRadius: 10,
    color: 'var(--text-primary)',
    fontSize: 13,
    outline: 'none',
    boxSizing: 'border-box'
  };

  const labelStyle = { 
    fontSize: 11, 
    fontWeight: 600, 
    color: 'var(--text-secondary)',
    letterSpacing: '0.02em',
    marginBottom: 4,
    display: 'block'
  };

  if (loading) {
    return (
      <CaretakerLayout>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
          <Loader2 size={32} color="var(--cyan)" style={{ animation: 'spin 1s linear infinite' }} />
        </div>
      </CaretakerLayout>
    );
  }

  return (
    <CaretakerLayout>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
        <div>
          <h1 className="font-syne" style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>My Patients</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>View and manage all your assigned patients.</p>
        </div>
        <button 
          onClick={() => {
            setIsModalOpen(true);
            setActiveTab('existing');
            setEmail('');
            setModalError('');
            setModalSuccess('');
          }}
          className="btn-primary" 
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 8, 
            padding: '12px 20px', 
            borderRadius: 10,
            background: 'linear-gradient(135deg, #a78bfa, var(--cyan))',
            border: 'none',
            color: '#fff',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          <Plus size={16} /> Link Patient
        </button>
      </div>

      {/* Summary stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16, marginBottom: 28 }}>
        {[
          { label: 'Total Patients', value: patients.length, color: '#a78bfa', icon: Users },
          { label: 'At Risk', value: atRisk, color: 'var(--amber)', icon: AlertTriangle },
          { label: 'All Good', value: allGood, color: 'var(--emerald)', icon: Activity },
        ].map(s => (
          <div key={s.label} className="glass-card" style={{ padding: '18px 22px', display: 'flex', alignItems: 'center', gap: 14 }}>
            <div style={{ width: 38, height: 38, borderRadius: 10, background: `${s.color}18`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <s.icon size={18} color={s.color} />
            </div>
            <div>
              <div className="font-syne" style={{ fontSize: 22, fontWeight: 800, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 1 }}>{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Search bar */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ position: 'relative', maxWidth: 420 }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            placeholder="Search patients by name..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              width: '100%',
              padding: '10px 14px 10px 40px',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border)',
              borderRadius: 10,
              color: 'var(--text-primary)',
              fontSize: 13,
              outline: 'none',
              transition: 'border-color 0.2s',
            }}
            onFocus={e => e.target.style.borderColor = '#a78bfa'}
            onBlur={e => e.target.style.borderColor = 'var(--border)'}
          />
        </div>
      </div>

      {/* Patient Grid */}
      {filtered.length === 0 ? (
        <div className="glass-card" style={{ padding: 48, textAlign: 'center' }}>
          <Users size={36} color="var(--text-muted)" style={{ marginBottom: 12, opacity: 0.5 }} />
          <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>{search ? 'No patients match your search.' : 'No patients assigned yet.'}</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 16 }}>
          {filtered.map(p => {
            const riskLevel = p.risk_level || 'low';
            const risk = RISK_CONFIG[riskLevel] || RISK_CONFIG.low;
            const patientName = p.user_name || p.user?.full_name || `Patient #${p.id}`;
            const conditions = [p.diseases, p.chronic_conditions].filter(Boolean).join(', ') || p.conditions || p.medical_conditions || '';
            const allergies = p.allergies || '';
            const whatsapp = p.user?.whatsapp_number || p.whatsapp_number || '';

            return (
              <div key={p.id} className="glass-card" style={{ padding: 22, border: `1px solid ${risk.color}20`, transition: 'transform 0.2s, box-shadow 0.2s', cursor: 'pointer' }}
                onClick={() => navigate(`/caretaker/patient/${p.id}`)}
                onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 8px 30px rgba(167,139,250,0.12)'; }}
                onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = 'none'; }}>
                {/* Header row */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{ width: 42, height: 42, borderRadius: '50%', background: `${risk.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <span style={{ fontSize: 16, fontWeight: 700, color: risk.color }}>{patientName[0]}</span>
                    </div>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>{patientName}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                        {p.age ? `Age ${p.age}` : ''}{p.age && p.gender ? ' · ' : ''}{p.gender || ''}{p.blood_group ? ` · ${p.blood_group}` : ''}
                      </div>
                    </div>
                  </div>
                  <span style={{ fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 20, background: risk.bg, color: risk.color, whiteSpace: 'nowrap' }}>{risk.label}</span>
                </div>

                {/* Details */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 14 }}>
                  {conditions && (
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                      <Heart size={13} color="var(--text-muted)" style={{ marginTop: 2, flexShrink: 0 }} />
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>{conditions}</span>
                    </div>
                  )}
                  {allergies && (
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
                      <Shield size={13} color="var(--amber)" style={{ marginTop: 2, flexShrink: 0 }} />
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.4 }}>Allergies: {allergies}</span>
                    </div>
                  )}
                  {whatsapp && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <Phone size={13} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{whatsapp}</span>
                    </div>
                  )}
                </div>

                {/* Bottom stats */}
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0 0', borderTop: '1px solid var(--border)' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div className="font-syne" style={{ fontSize: 15, fontWeight: 800, color: 'var(--emerald)' }}>{p.adherence_score != null ? `${p.adherence_score}%` : '—'}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Adherence</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div className="font-syne" style={{ fontSize: 15, fontWeight: 800, color: risk.color }}>{p.risk_score || '—'}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Risk Score</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div className="font-syne" style={{ fontSize: 15, fontWeight: 800, color: p.onboarding_done ? 'var(--cyan)' : 'var(--text-muted)' }}>{p.onboarding_done ? '✓' : '✗'}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Onboarded</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Link Patient Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setIsModalOpen(false)} style={{ zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(8px)' }}>
          <div style={{ 
            background: 'var(--bg-card)', 
            borderRadius: 18, 
            border: '1px solid var(--border)', 
            padding: 28, 
            width: '100%', 
            maxWidth: 440, 
            maxHeight: '90vh',
            overflowY: 'auto',
            animation: 'fadeInUp 0.2s ease',
            position: 'relative',
            boxSizing: 'border-box'
          }}>
            <button 
              onClick={() => setIsModalOpen(false)}
              style={{ position: 'absolute', right: 20, top: 20, background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', zIndex: 10 }}
            >
              <X size={18} />
            </button>

            <h3 className="font-syne" style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 16 }}>Link Patient</h3>

            {/* Modal Tabs */}
            <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: 20 }}>
              <button 
                onClick={() => { setActiveTab('existing'); setModalError(''); setModalSuccess(''); }}
                style={{ flex: 1, padding: '10px 0', background: 'none', border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: activeTab === 'existing' ? '#a78bfa' : 'var(--text-muted)', borderBottom: activeTab === 'existing' ? '2px solid #a78bfa' : '2px solid transparent', outline: 'none' }}
              >
                Existing Patient
              </button>
              <button 
                onClick={() => { setActiveTab('new'); setModalError(''); setModalSuccess(''); }}
                style={{ flex: 1, padding: '10px 0', background: 'none', border: 'none', cursor: 'pointer', fontSize: 13, fontWeight: 600, color: activeTab === 'new' ? '#a78bfa' : 'var(--text-muted)', borderBottom: activeTab === 'new' ? '2px solid #a78bfa' : '2px solid transparent', outline: 'none' }}
              >
                Create New Patient
              </button>
            </div>

            {modalError && (
              <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, padding: '10px 14px', marginBottom: 16 }}>
                <p style={{ color: '#ef4444', fontSize: 12, margin: 0 }}>{modalError}</p>
              </div>
            )}

            {modalSuccess && (
              <div style={{ background: 'rgba(0,255,157,0.1)', border: '1px solid rgba(0,255,157,0.3)', borderRadius: 8, padding: '10px 14px', marginBottom: 16 }}>
                <p style={{ color: 'var(--emerald)', fontSize: 12, margin: 0 }}>{modalSuccess}</p>
              </div>
            )}

            {activeTab === 'existing' ? (
              /* Link Existing Patient View */
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <p style={{ color: 'var(--text-muted)', fontSize: 13, margin: 0 }}>Enter the patient's registered email address to link them to your monitoring panel.</p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={labelStyle}>PATIENT EMAIL</label>
                  <input 
                    type="email" 
                    placeholder="e.g. raj@example.com" 
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    style={inputStyle}
                  />
                </div>

                <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
                  <button 
                    onClick={() => setIsModalOpen(false)}
                    className="btn-outline" 
                    style={{ flex: 1, padding: '11px', borderRadius: 10, border: '1px solid var(--border)', background: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontWeight: 600 }}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleLinkPatient}
                    disabled={modalLoading || !email.trim()}
                    className="btn-primary" 
                    style={{ 
                      flex: 1, 
                      padding: '11px', 
                      borderRadius: 10,
                      background: 'linear-gradient(135deg, #a78bfa, var(--cyan))',
                      border: 'none',
                      color: '#fff',
                      fontWeight: 600,
                      cursor: (modalLoading || !email.trim()) ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 6
                    }}
                  >
                    {modalLoading && <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />}
                    {modalLoading ? 'Linking...' : 'Add Patient'}
                  </button>
                </div>
              </div>
            ) : (
              /* Create New Patient Form View */
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <p style={{ color: 'var(--text-muted)', fontSize: 13, margin: 0 }}>Fill in the medical and account details below. This will register the patient and link them to your panel.</p>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={labelStyle}>FULL NAME</label>
                  <input type="text" placeholder="Rajesh Kumar" value={newForm.name} onChange={e => setNewForm(f => ({ ...f, name: e.target.value }))} style={inputStyle} />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={labelStyle}>EMAIL ADDRESS (For Google Sign-In)</label>
                  <input type="email" placeholder="rajesh@gmail.com" value={newForm.email} onChange={e => setNewForm(f => ({ ...f, email: e.target.value }))} style={inputStyle} />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <label style={labelStyle}>AGE</label>
                    <input type="number" placeholder="45" value={newForm.age} onChange={e => setNewForm(f => ({ ...f, age: e.target.value }))} style={inputStyle} />
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <label style={labelStyle}>GENDER</label>
                    <select value={newForm.gender} onChange={e => setNewForm(f => ({ ...f, gender: e.target.value }))} style={{ ...inputStyle, cursor: 'pointer' }}>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={labelStyle}>BLOOD GROUP</label>
                  <select value={newForm.blood_group} onChange={e => setNewForm(f => ({ ...f, blood_group: e.target.value }))} style={{ ...inputStyle, cursor: 'pointer' }}>
                    <option value="">Select blood group...</option>
                    {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(bg => <option key={bg} value={bg}>{bg}</option>)}
                  </select>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={labelStyle}>DISEASES (Comma-separated)</label>
                  <input type="text" placeholder="e.g. Hypertension, Asthma" value={newForm.diseases} onChange={e => setNewForm(f => ({ ...f, diseases: e.target.value }))} style={inputStyle} />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={labelStyle}>ALLERGIES (Comma-separated)</label>
                  <input type="text" placeholder="e.g. Penicillin" value={newForm.allergies} onChange={e => setNewForm(f => ({ ...f, allergies: e.target.value }))} style={inputStyle} />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <label style={labelStyle}>CHRONIC CONDITIONS (Comma-separated)</label>
                  <input type="text" placeholder="e.g. Diabetes" value={newForm.chronic_conditions} onChange={e => setNewForm(f => ({ ...f, chronic_conditions: e.target.value }))} style={inputStyle} />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <label style={labelStyle}>WHATSAPP NUMBER</label>
                    <input type="text" placeholder="+91930..." value={newForm.whatsapp_number} onChange={e => setNewForm(f => ({ ...f, whatsapp_number: e.target.value }))} style={inputStyle} />
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <label style={labelStyle}>EMERGENCY PHONE</label>
                    <input type="text" placeholder="+91987..." value={newForm.emergency_phone} onChange={e => setNewForm(f => ({ ...f, emergency_phone: e.target.value }))} style={inputStyle} />
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 10, marginTop: 12 }}>
                  <button 
                    onClick={() => setIsModalOpen(false)}
                    className="btn-outline" 
                    style={{ flex: 1, padding: '11px', borderRadius: 10, border: '1px solid var(--border)', background: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontWeight: 600 }}
                  >
                    Cancel
                  </button>
                  <button 
                    onClick={handleCreateAndLinkPatient}
                    disabled={modalLoading || !newForm.name.trim() || !newForm.email.trim() || !newForm.age.trim()}
                    className="btn-primary" 
                    style={{ 
                      flex: 1, 
                      padding: '11px', 
                      borderRadius: 10,
                      background: 'linear-gradient(135deg, #a78bfa, var(--cyan))',
                      border: 'none',
                      color: '#fff',
                      fontWeight: 600,
                      cursor: (modalLoading || !newForm.name.trim() || !newForm.email.trim() || !newForm.age.trim()) ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: 6
                    }}
                  >
                    {modalLoading && <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />}
                    {modalLoading ? 'Creating...' : 'Create & Link'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </CaretakerLayout>
  );
}
