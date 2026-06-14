import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth, apiClient } from '../context/AuthContext';
import { User, Users, Loader2 } from 'lucide-react';

export default function LoginCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser } = useAuth();
  const [showRoleSelect, setShowRoleSelect] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pendingUser, setPendingUser] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const access = params.get('access');
    const refresh = params.get('refresh');
    const userId = params.get('user_id');
    const role = params.get('role');
    const name = params.get('name');
    const avatar = params.get('avatar');
    const isNew = params.get('is_new') === 'true';

    if (access && refresh) {
      // Save tokens to localStorage
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      
      const userData = {
        id: userId,
        role: role,
        full_name: name,
        avatar_url: avatar,
      };

      if (isNew) {
        setPendingUser(userData);
        setShowRoleSelect(true);
      } else {
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        // Redirect based on user role
        if (role === 'admin') {
          navigate('/admin');
        } else if (role === 'caretaker') {
          navigate('/caretaker');
        } else {
          navigate('/dashboard');
        }
      }
    } else {
      // Fallback if no tokens found
      navigate('/');
    }
  }, [location, navigate, setUser]);

  const handleRoleSelect = async (selectedRole) => {
    setLoading(true);
    try {
      // Set token header in apiClient explicitly
      const token = localStorage.getItem('access_token');
      await apiClient.post('/auth/select-role/', { role: selectedRole }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const updatedUser = {
        ...pendingUser,
        role: selectedRole
      };
      
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);

      if (selectedRole === 'caretaker') {
        navigate('/caretaker');
      } else {
        navigate('/onboarding');
      }
    } catch (err) {
      console.error('Failed to select role:', err);
      alert('Failed to save role selection. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (showRoleSelect) {
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        background: 'var(--bg-primary)',
        color: 'var(--text-primary)',
        padding: '24px'
      }}>
        <div style={{ 
          width: '100%', 
          maxWidth: '480px', 
          background: 'var(--bg-card)', 
          borderRadius: '24px', 
          border: '1px solid var(--border)', 
          padding: '40px 32px',
          boxShadow: '0 24px 48px rgba(0,0,0,0.4)',
          textAlign: 'center',
          animation: 'fadeInUp 0.3s ease'
        }}>
          <h2 className="font-syne" style={{ fontSize: '26px', fontWeight: 700, marginBottom: '8px' }}>
            Choose Your Role
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '32px' }}>
            Select how you want to use MediMate AI
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {/* Patient Option */}
            <button 
              onClick={() => !loading && handleRoleSelect('patient')}
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '20px',
                borderRadius: '16px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border)',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s',
                width: '100%',
                color: 'inherit',
                outline: 'none'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'rgba(0,255,157,0.04)';
                e.currentTarget.style.borderColor = 'var(--emerald)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
                e.currentTarget.style.borderColor = 'var(--border)';
              }}
            >
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'rgba(0,255,157,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--emerald)',
                flexShrink: 0
              }}>
                <User size={24} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '4px' }}>I am a Patient</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                  Track your medicines, log daily intakes, view risk alerts, and chat with WhatsApp reminders.
                </p>
              </div>
            </button>

            {/* Caretaker Option */}
            <button 
              onClick={() => !loading && handleRoleSelect('caretaker')}
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '20px',
                borderRadius: '16px',
                background: 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border)',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.2s',
                width: '100%',
                color: 'inherit',
                outline: 'none'
              }}
              onMouseEnter={e => {
                e.currentTarget.style.background = 'rgba(0,212,255,0.04)';
                e.currentTarget.style.borderColor = 'var(--cyan)';
              }}
              onMouseLeave={e => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
                e.currentTarget.style.borderColor = 'var(--border)';
              }}
            >
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'rgba(0,212,255,0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--cyan)',
                flexShrink: 0
              }}>
                <Users size={24} />
              </div>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '4px' }}>I am a Caretaker</h3>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
                  Monitor your family members' adherence rates, manage their medicines, and receive missed dose warnings.
                </p>
              </div>
            </button>
          </div>

          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '24px', gap: '8px', color: 'var(--text-muted)', fontSize: '13px' }}>
              <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
              <span>Saving role setting...</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      background: 'var(--bg-primary)',
      color: 'var(--text-primary)' 
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ 
          width: 40, 
          height: 40, 
          border: '2px solid var(--border)', 
          borderTopColor: 'var(--cyan)', 
          borderRadius: '50%', 
          animation: 'spin 0.8s linear infinite', 
          margin: '0 auto 16px' 
        }} />
        <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Authenticating with Google...</p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
          }
        `}</style>
      </div>
    </div>
  );
}
