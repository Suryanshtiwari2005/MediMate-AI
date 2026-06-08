# 💊 MediMateAI — 7-Day Sprint Build Plan

**Goal**: Build a functional prototype for the Capgemini Exceller Buildathon Grand Final demonstration.

**Stack**: React 18 (Vite) + Tailwind CSS + shadcn/ui | Django 5 + DRF + SQLite | CallMeBot + Twilio + Hugging Face

**Project Root**: `C:\Users\PC\.gemini\antigravity\scratch\medimateai`

---

## Team Roles

| Member | Role | Primary Responsibility |
|--------|------|----------------------|
| **Member A (You)** | Tech Lead / Backend Core | Django setup, database models, auth flow, API architecture, integration oversight |
| **Member B** | Frontend Lead | React + Vite + Tailwind + shadcn/ui, all pages, UI/UX, responsive design |
| **Member C** | Backend Services & Integration | WhatsApp service, AI engine, escalation logic, Twilio, APScheduler |
| **Member D** | Full-Stack Support & Testing | Serializers, helper views, seed data, pytest tests, deployment, demo prep |

> [!IMPORTANT]
> **Parallel workflow**: Members A & C work primarily on `medimateai-backend/`. Member B works on `medimateai-frontend/`. Member D floats between both. Use separate Git branches per member and merge daily.

---

## Open Questions

1. **Team Member Names**: Replace Member A/B/C/D with actual names for your internal tracking.
2. **Google Cloud Project**: Has anyone on the team already created a Google Cloud project with OAuth 2.0 credentials configured? If not, this needs to be done on Day 1 (takes ~15 minutes).
3. **WhatsApp Numbers for Demo**: Have you pre-activated CallMeBot on 2 phone numbers? Each number must send "I allow callmebot to send me messages" to +34644597770 at least 24 hours before demo day.
4. **Hugging Face Token**: Has anyone created a free HF account and generated an API token?

---

## Project Structure Overview

```
medimateai/
├── medimateai-backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   ├── config/                     # Django project config
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── users/                  # Custom User + Google OAuth
│   │   ├── patients/               # PatientProfile + Caretaker
│   │   ├── medicines/              # Medicine + MedicineSchedule + signals
│   │   ├── doses/                  # DoseLog
│   │   ├── whatsapp/               # WhatsAppInteraction + webhook
│   │   ├── ai/                     # Risk score + predictions
│   │   └── escalation/             # EscalationLog
│   ├── services/                   # Business logic layer
│   │   ├── whatsapp_service.py
│   │   ├── ai_message_service.py
│   │   ├── ai_service.py
│   │   ├── escalation_service.py
│   │   ├── call_service.py
│   │   └── dose_generator.py
│   └── scheduler/
│       └── jobs.py
│
└── medimateai-frontend/
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── src/
    │   ├── main.jsx
    │   ├── index.css
    │   ├── App.jsx
    │   ├── store/authStore.js
    │   ├── services/api.js
    │   ├── components/
    │   │   ├── ProtectedRoute.jsx
    │   │   ├── DoseCard.jsx
    │   │   ├── RiskBadge.jsx
    │   │   ├── WeeklyCalendar.jsx
    │   │   ├── AdherenceRing.jsx
    │   │   └── WhatsAppInteractionCard.jsx
    │   └── pages/
    │       ├── Landing.jsx
    │       ├── Login.jsx
    │       ├── Onboarding.jsx
    │       ├── Dashboard.jsx
    │       ├── AddMedicine.jsx
    │       ├── History.jsx
    │       ├── Predictions.jsx
    │       ├── CaretakerDashboard.jsx
    │       ├── Admin.jsx
    │       └── WhatsAppLog.jsx
```

---

# DAY 1 — Foundation: Django Setup + Auth + React Init

## Member A (You) — Django Project + Models

### Tasks
1. Create Django project structure with `django-admin startproject config .`
2. Create all 7 Django apps: `users`, `patients`, `medicines`, `doses`, `whatsapp`, `ai`, `escalation`
3. Write all database models (see below)
4. Configure `settings.py`: INSTALLED_APPS, AUTH_USER_MODEL, CORS, DRF, JWT
5. Run `makemigrations` + `migrate`
6. Create superuser for Django admin

### Files to Create/Edit

#### [NEW] `requirements.txt`
```
django==5.0.6
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.1
social-auth-app-django==5.4.0
django-cors-headers==4.3.1
drf-spectacular==0.27.2
django-apscheduler==0.6.2
httpx==0.27.0
twilio==9.0.5
pywebpush==2.0.0
python-dotenv==1.0.1
gunicorn==22.0.0
Pillow==10.3.0
```

#### [NEW] `apps/users/models.py`
```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('caretaker', 'Caretaker'),
        ('admin', 'Admin'),
    )
    google_id = models.CharField(max_length=128, unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    avatar_url = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    whatsapp_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.role})"
```

#### [NEW] `apps/patients/models.py`
```python
from django.db import models
from django.core.validators import MinValueValidator

class PatientProfile(models.Model):
    GENDER_CHOICES = (('male', 'Male'), ('female', 'Female'), ('other', 'Other'))
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='patient_profile')
    age = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    diseases = models.JSONField(default=list, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    chronic_conditions = models.JSONField(default=list, blank=True)
    emergency_phone = models.CharField(max_length=15, null=True, blank=True)
    adherence_score = models.FloatField(default=100.0)
    risk_level = models.CharField(max_length=10, default='low')
    onboarding_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Caretaker(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='caretaker_profile')
    patients = models.ManyToManyField(PatientProfile, related_name='caretakers', blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    is_primary = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### [NEW] `apps/medicines/models.py`
```python
from django.db import models

class Medicine(models.Model):
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"

class MedicineSchedule(models.Model):
    patient = models.ForeignKey('patients.PatientProfile', on_delete=models.CASCADE, related_name='schedules')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    scheduled_time = models.TimeField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### [NEW] `apps/doses/models.py`
```python
from django.db import models

class DoseLog(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'), ('taken', 'Taken'), ('missed', 'Missed'),
        ('skipped', 'Skipped'), ('rescheduled', 'Rescheduled'),
    )
    schedule = models.ForeignKey('medicines.MedicineSchedule', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.PatientProfile', on_delete=models.CASCADE)
    medicine = models.ForeignKey('medicines.Medicine', on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    taken_at = models.DateTimeField(null=True, blank=True)
    missed_at = models.DateTimeField(null=True, blank=True)
    skip_reason = models.TextField(blank=True)
    reminder_sent = models.BooleanField(default=False)
    escalated = models.BooleanField(default=False)
    call_attempted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('schedule', 'scheduled_date', 'scheduled_time')
```

#### [NEW] `apps/whatsapp/models.py`
```python
from django.db import models

class WhatsAppInteraction(models.Model):
    RESPONSE_CHOICES = (('1', 'Taken'), ('2', 'Reschedule'), ('3', 'Not Taken'))
    STATUS_CHOICES = (
        ('sent', 'Sent'), ('delivered', 'Delivered'),
        ('responded', 'Responded'), ('expired', 'Expired'),
    )
    dose_log = models.ForeignKey('doses.DoseLog', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.PatientProfile', on_delete=models.CASCADE)
    whatsapp_number = models.CharField(max_length=15)
    message_sent = models.TextField()
    ai_variables = models.JSONField(default=dict, blank=True)
    response_received = models.CharField(max_length=1, choices=RESPONSE_CHOICES, null=True, blank=True)
    response_time = models.DateTimeField(null=True, blank=True)
    rescheduled_to = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    sent_at = models.DateTimeField(auto_now_add=True)
```

#### [NEW] `apps/escalation/models.py`
```python
from django.db import models

class EscalationLog(models.Model):
    LEVEL_CHOICES = (
        ('whatsapp_primary', 'WhatsApp Primary Caretaker'),
        ('whatsapp_secondary', 'WhatsApp Secondary Caretaker'),
        ('bot_call', 'Bot Call'),
    )
    dose_log = models.ForeignKey('doses.DoseLog', on_delete=models.CASCADE)
    patient = models.ForeignKey('patients.PatientProfile', on_delete=models.CASCADE)
    escalation_level = models.CharField(max_length=30, choices=LEVEL_CHOICES)
    recipient_phone = models.CharField(max_length=15)
    message_sent = models.TextField()
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### [NEW] `config/settings.py` (key sections)
```python
AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'social_django',
    'drf_spectacular',
    'django_apscheduler',
    # Local apps
    'apps.users',
    'apps.patients',
    'apps.medicines',
    'apps.doses',
    'apps.whatsapp',
    'apps.ai',
    'apps.escalation',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite dev server
]
CORS_ALLOW_CREDENTIALS = True

# Google OAuth via python-social-auth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
```

### ✅ Done When
- `python manage.py migrate` runs without errors
- All 7 tables exist in SQLite
- Django admin accessible at `localhost:8000/admin/`
- Superuser can log in

---

## Member B — React + Vite Frontend Initialization

### Tasks
1. Initialize React project: `npx -y create-vite@latest ./ -- --template react`
2. Install Tailwind CSS, shadcn/ui, React Router, Zustand, Axios, Lucide icons
3. Set up Tailwind config with custom color palette (dark medical theme)
4. Create base CSS design system (`index.css`) with:
   - CSS custom properties for colors, shadows, radii
   - Global typography (Google Font: Inter)
   - Glassmorphic card styles
   - Gradient backgrounds
   - Micro-animation keyframes
5. Create app routing skeleton (`App.jsx`) with React Router
6. Create `Landing.jsx` — stunning product landing page
7. Create `Login.jsx` — Google OAuth login page with "Continue with Google" button

### Files to Create

#### [NEW] `src/index.css` — Design System
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --color-bg-primary: #0a0e1a;
  --color-bg-secondary: #111827;
  --color-bg-card: rgba(17, 24, 39, 0.7);
  --color-accent-blue: #3b82f6;
  --color-accent-emerald: #10b981;
  --color-accent-rose: #f43f5e;
  --color-accent-amber: #f59e0b;
  --color-text-primary: #f1f5f9;
  --color-text-secondary: #94a3b8;
  --color-border: rgba(148, 163, 184, 0.1);
  --color-glass: rgba(255, 255, 255, 0.05);
  --shadow-glow-blue: 0 0 20px rgba(59, 130, 246, 0.3);
  --shadow-glow-emerald: 0 0 20px rgba(16, 185, 129, 0.3);
  --radius-lg: 16px;
  --radius-xl: 24px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Inter', sans-serif;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  min-height: 100vh;
}

/* Glassmorphic Card */
.glass-card {
  background: var(--color-glass);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: transform 0.2s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-glow-blue);
}

/* Gradient backgrounds */
.gradient-hero {
  background: linear-gradient(135deg, #0a0e1a 0%, #1e1b4b 50%, #0a0e1a 100%);
}

/* Animations */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.3); }
  50% { box-shadow: 0 0 25px rgba(59, 130, 246, 0.6); }
}
.animate-fade-in-up { animation: fadeInUp 0.6s ease forwards; }
.animate-pulse-glow { animation: pulse-glow 2s ease-in-out infinite; }
```

#### [NEW] `src/App.jsx` — Routing Skeleton
```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import AddMedicine from './pages/AddMedicine';
import History from './pages/History';
import Predictions from './pages/Predictions';
import CaretakerDashboard from './pages/CaretakerDashboard';
import Admin from './pages/Admin';
import WhatsAppLog from './pages/WhatsAppLog';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/onboarding" element={<ProtectedRoute><Onboarding /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/add-medicine" element={<ProtectedRoute><AddMedicine /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
        <Route path="/predictions" element={<ProtectedRoute><Predictions /></ProtectedRoute>} />
        <Route path="/caretaker" element={<ProtectedRoute><CaretakerDashboard /></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute><Admin /></ProtectedRoute>} />
        <Route path="/whatsapp-log" element={<ProtectedRoute><WhatsAppLog /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}
```

### ✅ Done When
- `npm run dev` starts without errors at `localhost:5173`
- Landing page renders with premium dark-theme design
- Login page shows "Continue with Google" button
- All routes are configured (pages can be placeholder `<h1>` tags for now)

---

## Member C — Google OAuth Backend Implementation

### Tasks
1. Set up Google Cloud Console: Create OAuth 2.0 credentials (Web App type)
   - Authorized redirect URI: `http://localhost:8000/auth/callback`
   - Authorized JS origins: `http://localhost:5173`
2. Implement Google OAuth endpoints using `social-auth-app-django`:
   - `GET /auth/google/login/` → returns Google auth URL
   - `GET /auth/callback/` → exchanges code → creates/gets User → issues JWT
   - `GET /auth/me/` → returns authenticated user
   - `POST /auth/logout/`
   - `POST /auth/token/refresh/`
3. Configure `social-auth-app-django` pipeline in settings
4. Write `.env` file with all environment variable placeholders

### Files to Create

#### [NEW] `apps/users/views.py`
```python
import os
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from social_core.backends.google import GoogleOAuth2
from social_django.utils import psa
import requests

User = get_user_model()

@api_view(['GET'])
@permission_classes([AllowAny])
def google_login(request):
    """Return Google OAuth2 authorization URL."""
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    scope = 'openid email profile'
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return Response({'auth_url': auth_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def google_callback(request):
    """Exchange authorization code for tokens, create/get user, return JWT."""
    code = request.GET.get('code')
    if not code:
        return Response({'error': 'No authorization code provided'}, status=400)

    # Exchange code for tokens
    token_resp = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI'),
        'grant_type': 'authorization_code',
    })
    token_data = token_resp.json()

    if 'error' in token_data:
        return Response({'error': token_data['error']}, status=400)

    # Get user info from Google
    userinfo_resp = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f"Bearer {token_data['access_token']}"}
    )
    userinfo = userinfo_resp.json()

    # Create or get user
    user, created = User.objects.get_or_create(
        google_id=userinfo['id'],
        defaults={
            'username': userinfo['email'].split('@')[0],
            'email': userinfo['email'],
            'full_name': userinfo.get('name', ''),
            'avatar_url': userinfo.get('picture', ''),
        }
    )
    if not created:
        user.full_name = userinfo.get('name', user.full_name)
        user.avatar_url = userinfo.get('picture', user.avatar_url)
        user.save()

    # Issue JWT
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['email'] = user.email

    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    redirect_url = (
        f"{frontend_url}/login"
        f"?access={str(refresh.access_token)}"
        f"&refresh={str(refresh)}"
        f"&user_id={user.id}"
        f"&role={user.role}"
        f"&name={user.full_name}"
    )
    return redirect(redirect_url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_me(request):
    """Return current authenticated user."""
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role,
        'avatar_url': user.avatar_url,
        'whatsapp_number': user.whatsapp_number,
        'has_profile': hasattr(user, 'patient_profile'),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    """Blacklist refresh token."""
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        pass
    return Response({'success': True})
```

#### [NEW] `apps/users/urls.py`
```python
from django.urls import path
from . import views

urlpatterns = [
    path('google/login/', views.google_login, name='google-login'),
    path('callback/', views.google_callback, name='google-callback'),
    path('me/', views.auth_me, name='auth-me'),
    path('logout/', views.auth_logout, name='auth-logout'),
]
```

#### [NEW] `.env.example`
```env
DJANGO_SECRET_KEY=change-me-to-a-long-random-string
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
FRONTEND_URL=http://localhost:5173

GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback/

CALLMEBOT_APIKEY=your-callmebot-apikey
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE=+1xxxxxxxxxx

VAPID_PUBLIC_KEY=your-vapid-public-key
VAPID_PRIVATE_KEY=your-vapid-private-key
VAPID_CLAIM_EMAIL=your@email.com
```

### ✅ Done When
- Google OAuth flow works: click login → Google consent → redirect back → JWT returned
- `/auth/me/` returns user data with valid JWT
- `.env` populated with real Google credentials

---

## Member D — Admin Panel + Serializers Scaffold

### Tasks
1. Register all models in Django admin with `list_display`, `search_fields`, `list_filter`
2. Create `serializers.py` for: `User`, `PatientProfile`, `Caretaker`, `Medicine`, `MedicineSchedule`, `DoseLog`
3. Create `config/urls.py` root URL configuration wiring all app URLs
4. Initialize Git repo, `.gitignore`, and make initial commit: `"Day 1: Foundation complete"`
5. Test Django admin: create a test user, patient profile, and medicine via admin panel

### Files to Create

#### [NEW] `apps/users/serializers.py`
```python
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'avatar_url',
                  'whatsapp_number', 'is_active', 'created_at']
        read_only_fields = ['id', 'google_id', 'created_at']
```

#### [NEW] `apps/patients/serializers.py`
```python
from rest_framework import serializers
from .models import PatientProfile, Caretaker
from apps.users.serializers import UserSerializer

class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ['adherence_score', 'risk_level', 'created_at', 'updated_at']

class CaretakerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Caretaker
        fields = '__all__'
```

#### [NEW] `apps/medicines/serializers.py`
```python
from rest_framework import serializers
from .models import Medicine, MedicineSchedule

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class MedicineScheduleSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer(read_only=True)
    medicine_id = serializers.PrimaryKeyRelatedField(
        queryset=Medicine.objects.all(), source='medicine', write_only=True
    )
    class Meta:
        model = MedicineSchedule
        fields = '__all__'
```

#### [NEW] `apps/doses/serializers.py`
```python
from rest_framework import serializers
from .models import DoseLog
from apps.medicines.serializers import MedicineSerializer

class DoseLogSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer(read_only=True)
    class Meta:
        model = DoseLog
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
```

#### [NEW] `config/urls.py`
```python
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.users.urls')),
    path('api/patients/', include('apps.patients.urls')),
    path('api/medicines/', include('apps.medicines.urls')),
    path('api/doses/', include('apps.doses.urls')),
    path('api/whatsapp/', include('apps.whatsapp.urls')),
    path('api/ai/', include('apps.ai.urls')),
    path('api/escalation/', include('apps.escalation.urls')),
    # OpenAPI docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
]
```

### ✅ Done When
- All models appear in Django admin
- Serializers import without error
- Root URLs wire up correctly
- Git initialized with first commit

---

# DAY 2 — Patient Profile + Caretaker + Onboarding UI

## Member A — Patient & Caretaker API Views

### Tasks
1. Build `PatientProfileViewSet` with CRUD operations
2. Build `CaretakerViewSet` with CRUD + patient assignment
3. Build WhatsApp number save endpoint (direct save, no OTP)
4. Implement custom permissions: `IsPatient`, `IsCaretaker`, `IsAdmin`

### Files to Create

#### [NEW] `apps/patients/views.py`
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PatientProfile, Caretaker
from .serializers import PatientProfileSerializer, CaretakerSerializer

class PatientProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return PatientProfile.objects.all()
        elif user.role == 'caretaker':
            return user.caretaker_profile.patients.all()
        return PatientProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def save_whatsapp(self, request):
        """Directly save WhatsApp number without OTP."""
        number = request.data.get('whatsapp_number')
        if not number:
            return Response({'error': 'WhatsApp number required'}, status=400)
        request.user.whatsapp_number = number
        request.user.save()
        return Response({'success': True, 'whatsapp_number': number})

    @action(detail=False, methods=['post'])
    def complete_onboarding(self, request):
        """Mark patient onboarding as done."""
        profile = request.user.patient_profile
        profile.onboarding_done = True
        profile.save()
        return Response({'onboarding_done': True})


class CaretakerViewSet(viewsets.ModelViewSet):
    serializer_class = CaretakerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Caretaker.objects.all()
        return Caretaker.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def assign_patient(self, request, pk=None):
        caretaker = self.get_object()
        patient_id = request.data.get('patient_id')
        try:
            patient = PatientProfile.objects.get(id=patient_id)
            caretaker.patients.add(patient)
            return Response({'success': True})
        except PatientProfile.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=404)
```

#### [NEW] `apps/patients/urls.py`
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientProfileViewSet, CaretakerViewSet

router = DefaultRouter()
router.register(r'profiles', PatientProfileViewSet, basename='patient-profile')
router.register(r'caretakers', CaretakerViewSet, basename='caretaker')

urlpatterns = [
    path('', include(router.urls)),
]
```

### ✅ Done When
- `POST /api/patients/profiles/` creates a patient profile
- `POST /api/patients/profiles/save_whatsapp/` saves number directly
- `GET /api/patients/profiles/` returns only own profile for patients
- Caretaker assignment works

---

## Member B — Onboarding UI + Auth State

### Tasks
1. Create Zustand auth store with token management
2. Create Axios API service with JWT interceptor
3. Build `Login.jsx` — handles Google OAuth redirect and token capture from URL params
4. Build multi-step `Onboarding.jsx`:
   - Step 1: Personal info (name, age, gender, blood group)
   - Step 2: Medical info (diseases, allergies, chronic conditions)
   - Step 3: WhatsApp number entry (direct save)
   - Step 4: Emergency contact
5. Create `ProtectedRoute.jsx` component

### Files to Create

#### [NEW] `src/store/authStore.js`
```javascript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),

      updateUser: (userData) =>
        set((state) => ({ user: { ...state.user, ...userData } })),

      logout: () =>
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false }),
    }),
    { name: 'medimate-auth' }
  )
);
```

#### [NEW] `src/services/api.js`
```javascript
import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### ✅ Done When
- Login page redirects to Google, captures JWT tokens from callback URL
- Auth state persists in localStorage via Zustand
- Onboarding wizard completes 4 steps and saves data via API
- Protected routes redirect unauthenticated users to `/login`

---

## Member C — Medicine CRUD API + Dose Log Signal

### Tasks
1. Build `Medicine` CRUD views
2. Build `MedicineSchedule` CRUD views (nested under patient)
3. Implement `post_save` signal: auto-generate `DoseLog` entries for 30 days when a schedule is created
4. Create `services/dose_generator.py` — utility to regenerate daily dose logs

### Files to Create

#### [NEW] `apps/medicines/signals.py`
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta, date
from .models import MedicineSchedule
from apps.doses.models import DoseLog

@receiver(post_save, sender=MedicineSchedule)
def generate_dose_logs(sender, instance, created, **kwargs):
    """Auto-create DoseLog entries for 30 days when a schedule is created."""
    if created and instance.is_active:
        current = instance.start_date or date.today()
        end = instance.end_date or (current + timedelta(days=30))
        logs_to_create = []
        while current <= end:
            logs_to_create.append(DoseLog(
                schedule=instance,
                patient=instance.patient,
                medicine=instance.medicine,
                scheduled_date=current,
                scheduled_time=instance.scheduled_time,
            ))
            current += timedelta(days=1)
        DoseLog.objects.bulk_create(logs_to_create, ignore_conflicts=True)
```

#### [NEW] `apps/medicines/views.py`
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Medicine, MedicineSchedule
from .serializers import MedicineSerializer, MedicineScheduleSerializer

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]

class MedicineScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = MedicineScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return MedicineSchedule.objects.all()
        return MedicineSchedule.objects.filter(patient__user=user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient_profile)
```

### ✅ Done When
- Creating a medicine schedule via API auto-generates 30 DoseLog records
- Medicines CRUD works via Swagger/Postman
- Signal tested: verify DoseLog count after creating one schedule

---

## Member D — Admin Panel Registration + Frontend Component Stubs

### Tasks
1. Register all models in Django admin with proper `list_display`, `list_filter`, `search_fields`
2. Create frontend component stubs: `DoseCard.jsx`, `RiskBadge.jsx`, `AdherenceRing.jsx`
3. Test full Day 1 + Day 2 flow end-to-end: Login → Profile → Save WhatsApp
4. Git commit: `"Day 2: Profiles + Auth complete"`

### ✅ Done When
- All models visible and searchable in Django admin
- Frontend component stubs render placeholder UI
- End-to-end flow tested manually

---

# DAY 3 — Medicines UI + WhatsApp Interactive System

## Member A — Dose Tracking API

### Tasks
1. Build dose tracking endpoints:
   - `GET /api/doses/today/` — today's doses for logged-in patient
   - `GET /api/doses/history/` — filtered historical view
   - `GET /api/doses/weekly/` — 7-day grid view
   - `POST /api/doses/{id}/take/` — mark taken
   - `POST /api/doses/{id}/skip/` — mark skipped with reason
   - `GET /api/doses/missed/` — missed doses for last N days
2. Add duplicate-take protection (409 Conflict)

#### [NEW] `apps/doses/views.py`
```python
from datetime import date, timedelta, datetime
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import DoseLog
from .serializers import DoseLogSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_doses(request):
    doses = DoseLog.objects.filter(
        patient__user=request.user,
        scheduled_date=date.today()
    ).select_related('medicine').order_by('scheduled_time')
    serializer = DoseLogSerializer(doses, many=True)
    summary = {
        'total': doses.count(),
        'taken': doses.filter(status='taken').count(),
        'pending': doses.filter(status='pending').count(),
        'missed': doses.filter(status='missed').count(),
    }
    return Response({'doses': serializer.data, 'summary': summary})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def take_dose(request, pk):
    try:
        dose = DoseLog.objects.get(pk=pk, patient__user=request.user)
    except DoseLog.DoesNotExist:
        return Response({'error': 'Dose not found'}, status=404)
    if dose.status == 'taken':
        return Response({'error': 'Already marked as taken'}, status=409)
    dose.status = 'taken'
    dose.taken_at = timezone.now()
    dose.save()
    return Response({'status': 'taken', 'taken_at': dose.taken_at})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def skip_dose(request, pk):
    try:
        dose = DoseLog.objects.get(pk=pk, patient__user=request.user)
    except DoseLog.DoesNotExist:
        return Response({'error': 'Dose not found'}, status=404)
    dose.status = 'skipped'
    dose.skip_reason = request.data.get('reason', '')
    dose.save()
    return Response({'status': 'skipped'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dose_history(request):
    from_date = request.GET.get('from', (date.today() - timedelta(days=30)).isoformat())
    to_date = request.GET.get('to', date.today().isoformat())
    status_filter = request.GET.get('status')
    qs = DoseLog.objects.filter(
        patient__user=request.user,
        scheduled_date__gte=from_date,
        scheduled_date__lte=to_date,
    ).select_related('medicine').order_by('-scheduled_date', '-scheduled_time')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return Response({'doses': DoseLogSerializer(qs, many=True).data, 'total': qs.count()})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_doses(request):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    week_grid = []
    for i in range(7):
        day = start + timedelta(days=i)
        doses = DoseLog.objects.filter(patient__user=request.user, scheduled_date=day)
        week_grid.append({
            'date': day.isoformat(),
            'day_name': day.strftime('%A'),
            'total': doses.count(),
            'taken': doses.filter(status='taken').count(),
            'missed': doses.filter(status='missed').count(),
        })
    return Response({'week_grid': week_grid})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def missed_doses(request):
    days = int(request.GET.get('days', 7))
    cutoff = date.today() - timedelta(days=days)
    missed = DoseLog.objects.filter(
        patient__user=request.user, status='missed', scheduled_date__gte=cutoff
    ).select_related('medicine')
    return Response({'missed': DoseLogSerializer(missed, many=True).data, 'count': missed.count()})
```

### ✅ Done When
- All dose endpoints return correct data via Postman
- Duplicate take returns 409

---

## Member B — Add Medicine Form + Dashboard Layout

### Tasks
1. Build `AddMedicine.jsx` — form to add medicine + schedule (name, dosage, time, start/end date)
2. Build `Dashboard.jsx` skeleton:
   - Header with user avatar, greeting, risk badge
   - Today's medication cards (from `/api/doses/today`)
   - Adherence ring (circular progress)
   - Quick action buttons
3. Build `DoseCard.jsx` component — interactive card with "Take" / "Skip" buttons
4. Build `AdherenceRing.jsx` — animated SVG circular progress

### ✅ Done When
- Can add a medicine via the frontend form
- Dashboard shows today's doses fetched from API
- Take/Skip buttons update dose status via API call

---

## Member C — WhatsApp Service + AI Message Generation

### Tasks
1. Build `services/whatsapp_service.py` — CallMeBot integration with template filling
2. Build `services/ai_message_service.py` — Hugging Face API + fallback tips
3. Build `apps/whatsapp/views.py`:
   - `POST /api/whatsapp/send-reminder/` — manually trigger a reminder
   - `GET /api/whatsapp/interactions/` — list all interactions
4. Test: send a real WhatsApp message via CallMeBot to a pre-activated number

#### [NEW] `services/whatsapp_service.py`
```python
import httpx
import urllib.parse
import os
import logging

logger = logging.getLogger(__name__)

CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

REMINDER_TEMPLATE = """💊 MediMate Reminder — {patient_name}

It's time for your {medicine_name} ({dosage}).
Scheduled: {scheduled_time}

{ai_personalized_tip}

Reply with:
  *1* — ✅ Taken
  *2* — ⏰ Remind me in 15 minutes
  *3* — ❌ Not taking today"""


def send_whatsapp_message(phone: str, message: str) -> bool:
    """Send a WhatsApp message via CallMeBot."""
    apikey = os.environ.get('CALLMEBOT_APIKEY', '')
    if not apikey:
        logger.warning("CALLMEBOT_APIKEY not set — skipping WhatsApp send")
        return False

    params = {
        'phone': phone,
        'text': urllib.parse.quote(message),
        'apikey': apikey,
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(CALLMEBOT_URL, params=params)
            resp.raise_for_status()
            logger.info(f"WhatsApp sent to {phone}: {resp.status_code}")
            return True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            logger.warning("CallMeBot rate limited (429). Will retry in 60s.")
        else:
            logger.error(f"WhatsApp send error: {e}")
        return False
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False


def send_reminder(dose_log, patient, ai_variables: dict) -> bool:
    """Build and send interactive reminder."""
    message = REMINDER_TEMPLATE.format(**ai_variables)
    phone = patient.user.whatsapp_number
    if not phone:
        logger.warning(f"No WhatsApp number for patient {patient.id}")
        return False
    success = send_whatsapp_message(phone, message)

    # Log the interaction
    from apps.whatsapp.models import WhatsAppInteraction
    WhatsAppInteraction.objects.create(
        dose_log=dose_log,
        patient=patient,
        whatsapp_number=phone,
        message_sent=message,
        ai_variables=ai_variables,
        status='sent' if success else 'failed',
    )
    return success
```

#### [NEW] `services/ai_message_service.py`
```python
import requests
import os
import random
import logging

logger = logging.getLogger(__name__)

HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"

FALLBACK_TIPS = [
    "Consistency is key — your health depends on it! 💪",
    "Taking your medicine at the same time every day helps it work better. ⏰",
    "You're doing great — keep up the streak! 🔥",
    "Small steps today lead to big health wins tomorrow! 🌟",
    "Your future self will thank you for staying on track! 🎯",
]

def generate_ai_variables(patient, dose_log) -> dict:
    """Build the full variable dict for a WhatsApp message."""
    from services.ai_service import calculate_risk_score
    from apps.doses.models import DoseLog
    from datetime import date, timedelta

    # Calculate risk
    risk = calculate_risk_score(patient.id)

    # Calculate streak
    streak = _get_streak(patient.id)

    # Generate AI tip
    ai_tip = _call_huggingface(
        patient.user.full_name,
        dose_log.medicine.name,
        risk['score']
    )

    return {
        "patient_name": patient.user.full_name,
        "medicine_name": dose_log.medicine.name,
        "dosage": dose_log.medicine.dosage,
        "scheduled_time": dose_log.scheduled_time.strftime("%I:%M %p"),
        "ai_personalized_tip": ai_tip,
        "risk_insight": risk.get("insight", ""),
        "streak": f"{streak}-day streak 🔥" if streak > 1 else "Start your streak today!",
    }

def _get_streak(patient_id: int) -> int:
    from apps.doses.models import DoseLog
    from datetime import date, timedelta
    streak = 0
    check_date = date.today() - timedelta(days=1)
    while True:
        day_doses = DoseLog.objects.filter(
            patient_id=patient_id, scheduled_date=check_date
        )
        if not day_doses.exists():
            break
        if day_doses.exclude(status='taken').exists():
            break
        streak += 1
        check_date -= timedelta(days=1)
    return streak

def _call_huggingface(name: str, medicine: str, risk_score: float) -> str:
    hf_token = os.environ.get('HF_API_TOKEN', '')
    if not hf_token:
        return random.choice(FALLBACK_TIPS)

    prompt = f"{name} should take {medicine}. Risk score: {risk_score}. Motivational health tip:"
    try:
        resp = requests.post(
            HF_API_URL,
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": prompt, "parameters": {"max_new_tokens": 50}},
            timeout=5,
        )
        resp.raise_for_status()
        result = resp.json()
        generated = result[0]["generated_text"].replace(prompt, "").strip()
        return generated[:200] if generated else random.choice(FALLBACK_TIPS)
    except Exception as e:
        logger.warning(f"HF API failed, using fallback: {e}")
        return random.choice(FALLBACK_TIPS)
```

### ✅ Done When
- WhatsApp message sends to a pre-activated test number
- AI tip generates from HF (or falls back gracefully)
- Interaction logged in database

---

## Member D — Medicines URLs + WhatsApp URLs + Integration Test

### Tasks
1. Wire up `apps/medicines/urls.py` and `apps/doses/urls.py`
2. Wire up `apps/whatsapp/urls.py`
3. Write manual integration test script: create user → profile → medicine → schedule → verify dose logs auto-generated
4. Git commit: `"Day 3: Medicines + WhatsApp service complete"`

### ✅ Done When
- All Day 3 URLs accessible via Swagger
- End-to-end: add medicine → dose logs appear → trigger WhatsApp reminder
- Git committed

---

# DAY 4 — Webhook + Dashboard Completion

## Member A — WhatsApp Webhook Endpoint

### Tasks
1. Build `/api/whatsapp/webhook/` — receives reply body (1/2/3) and routes:
   - `1` → mark taken, send confirmation
   - `2` → mark rescheduled, create new DoseLog +15min, queue followup
   - `3` → mark missed, trigger caretaker escalation
2. Implement stale message rejection (expire after 2 hours)
3. Handle edge cases: invalid reply, no active interaction, duplicate replies

#### [NEW] `apps/whatsapp/views.py`
```python
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import WhatsAppInteraction
from .serializers import WhatsAppInteractionSerializer
from apps.doses.models import DoseLog
from services.whatsapp_service import send_whatsapp_message

@api_view(['POST'])
@permission_classes([AllowAny])  # Webhook — no JWT
def whatsapp_webhook(request):
    """Receive reply from patient (1, 2, or 3)."""
    sender_phone = request.data.get('From', '').replace('+', '').strip()
    body = request.data.get('Body', '').strip()

    # Find latest pending (non-expired) interaction for this phone
    two_hours_ago = timezone.now() - timedelta(hours=2)
    interaction = WhatsAppInteraction.objects.filter(
        whatsapp_number__endswith=sender_phone[-10:],  # match last 10 digits
        status='sent',
        sent_at__gte=two_hours_ago,
    ).order_by('-sent_at').first()

    if not interaction:
        return Response({'error': 'No active interaction found'}, status=404)

    dose_log = interaction.dose_log

    if body == '1':  # Taken
        dose_log.status = 'taken'
        dose_log.taken_at = timezone.now()
        dose_log.save()
        reply = "✅ Great! Dose marked as taken. Keep it up!"

    elif body == '2':  # Reschedule +15 min
        new_time = timezone.now() + timedelta(minutes=15)
        dose_log.status = 'rescheduled'
        dose_log.save()
        interaction.rescheduled_to = new_time

        # Create a new DoseLog for the rescheduled time
        DoseLog.objects.create(
            schedule=dose_log.schedule,
            patient=dose_log.patient,
            medicine=dose_log.medicine,
            scheduled_date=dose_log.scheduled_date,
            scheduled_time=new_time.time(),
            status='pending',
        )
        reply = f"⏰ Got it! We'll remind you again at {new_time.strftime('%I:%M %p')}."

    elif body == '3':  # Not Taking
        dose_log.status = 'missed'
        dose_log.missed_at = timezone.now()
        dose_log.save()
        # Trigger escalation
        from services.escalation_service import trigger_caretaker_alert
        trigger_caretaker_alert(dose_log)
        reply = "❌ Noted. Your caretaker has been notified. Please take care!"

    else:
        reply = "❓ Please reply with 1 (Taken), 2 (Remind in 15 min), or 3 (Not taking)."
        return Response({'processed': False, 'reply': reply})

    interaction.response_received = body
    interaction.response_time = timezone.now()
    interaction.status = 'responded'
    interaction.save()

    # Send confirmation
    send_whatsapp_message(interaction.whatsapp_number, reply)
    return Response({'processed': True, 'reply': reply})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_interactions(request):
    """List WhatsApp interactions for authenticated user."""
    interactions = WhatsAppInteraction.objects.filter(
        patient__user=request.user
    ).order_by('-sent_at')
    date_filter = request.GET.get('date')
    if date_filter:
        interactions = interactions.filter(sent_at__date=date_filter)
    return Response({'interactions': WhatsAppInteractionSerializer(interactions, many=True).data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_reminder_manual(request):
    """Manually trigger a WhatsApp reminder for a dose."""
    dose_log_id = request.data.get('dose_log_id')
    try:
        dose_log = DoseLog.objects.get(id=dose_log_id, patient__user=request.user)
    except DoseLog.DoesNotExist:
        return Response({'error': 'Dose not found'}, status=404)

    from services.ai_message_service import generate_ai_variables
    from services.whatsapp_service import send_reminder
    variables = generate_ai_variables(dose_log.patient, dose_log)
    success = send_reminder(dose_log, dose_log.patient, variables)
    dose_log.reminder_sent = True
    dose_log.save()
    return Response({'success': success, 'message_id': dose_log.id})
```

### ✅ Done When
- Webhook handles 1, 2, 3, and invalid replies
- Reply "2" creates a new DoseLog
- Reply "3" triggers escalation
- Stale messages (>2h) rejected

---

## Member B — Complete Dashboard UI

### Tasks
1. Finish `Dashboard.jsx` — full feature:
   - Live today's doses from API
   - Adherence ring (SVG animated)
   - Risk badge (color-coded: green/yellow/orange/red)
   - "Mark Taken" / "Skip" action buttons on each DoseCard
2. Build `WeeklyCalendar.jsx` — compact 7-day view with dots/pills showing status
3. Build `RiskBadge.jsx` — dynamic badge showing risk level with glow effects
4. Add loading skeletons + error toast notifications

### ✅ Done When
- Dashboard renders real data from backend
- Take/Skip buttons trigger API and update UI
- Weekly calendar shows 7-day view
- Loading and error states handled

---

## Member C — Escalation Service

### Tasks
1. Build `services/escalation_service.py`:
   - `trigger_caretaker_alert(dose_log)` — WhatsApp to primary caretaker
   - Logic to find assigned caretakers for a patient
   - Log escalation in `EscalationLog`
2. Build `apps/escalation/views.py`:
   - `GET /api/escalation/logs/` — list escalation logs
3. Wire up escalation URLs

#### [NEW] `services/escalation_service.py`
```python
import logging
from services.whatsapp_service import send_whatsapp_message
from apps.escalation.models import EscalationLog

logger = logging.getLogger(__name__)

CARETAKER_ALERT_TEMPLATE = """🚨 MediMate ALERT

Patient: {patient_name}
Missed: {medicine_name} ({dosage})
Scheduled: {scheduled_time}

The patient has indicated they are not taking this dose.
Please check on them immediately.

— MediMateAI Escalation System"""


def trigger_caretaker_alert(dose_log):
    """Send WhatsApp alert to assigned caretakers."""
    patient = dose_log.patient
    caretakers = patient.caretakers.all()

    if not caretakers.exists():
        # Fallback: send to patient's emergency phone
        emergency = patient.emergency_phone
        if emergency:
            msg = _build_alert_message(dose_log)
            send_whatsapp_message(emergency, msg)
            _log_escalation(dose_log, patient, 'whatsapp_primary', emergency, msg, True)
        else:
            logger.warning(f"No caretaker or emergency contact for patient {patient.id}")
        return

    for caretaker in caretakers:
        phone = caretaker.user.whatsapp_number or caretaker.phone
        if phone:
            msg = _build_alert_message(dose_log)
            success = send_whatsapp_message(phone, msg)
            level = 'whatsapp_primary' if caretaker.is_primary else 'whatsapp_secondary'
            _log_escalation(dose_log, patient, level, phone, msg, success)

    dose_log.escalated = True
    dose_log.save()


def _build_alert_message(dose_log) -> str:
    return CARETAKER_ALERT_TEMPLATE.format(
        patient_name=dose_log.patient.user.full_name,
        medicine_name=dose_log.medicine.name,
        dosage=dose_log.medicine.dosage,
        scheduled_time=dose_log.scheduled_time.strftime("%I:%M %p"),
    )


def _log_escalation(dose_log, patient, level, phone, message, success):
    EscalationLog.objects.create(
        dose_log=dose_log,
        patient=patient,
        escalation_level=level,
        recipient_phone=phone,
        message_sent=message,
        success=success,
    )
```

### ✅ Done When
- Reply "3" on webhook → caretaker receives WhatsApp alert
- EscalationLog created in database
- Edge case: no caretaker → emergency phone fallback

---

## Member D — WhatsApp Webhook Simulation Page + Testing

### Tasks
1. Build `WhatsAppLog.jsx` — frontend page showing:
   - List of all WhatsApp interactions
   - A "Simulate Reply" form: select a pending interaction, enter 1/2/3, POST to webhook
   - Real-time status updates
2. Test full end-to-end flow: Create patient → Add medicine → Trigger reminder → Simulate reply → Verify status
3. Git commit: `"Day 4: Webhook + Dashboard complete"`

### ✅ Done When
- Simulation page sends POST to webhook and shows result
- Full flow works end-to-end in browser
- Git committed

---

# DAY 5 — AI Prediction Engine + Background Scheduler

## Member A — Rule-Based Risk Score Engine

### Tasks
1. Build `services/ai_service.py` — full risk calculation with 5 factors
2. Build `apps/ai/views.py`:
   - `GET /api/ai/risk-score/` — current risk for logged-in patient
   - `GET /api/ai/predictions/` — next 7 days predictions
   - `GET /api/ai/adherence-trend/` — weekly trend data
3. Wire up `apps/ai/urls.py`

#### [NEW] `services/ai_service.py`
```python
from datetime import date, timedelta
from django.db.models import Count, Q
from apps.doses.models import DoseLog

def calculate_risk_score(patient_id: int) -> dict:
    """Deterministic risk engine using 5 factors."""
    today = date.today()
    week_ago = today - timedelta(days=7)
    base_score = 0

    # Factor 1: Recent miss rate (last 7 days) — up to 50 points
    recent = DoseLog.objects.filter(
        patient_id=patient_id,
        scheduled_date__gte=week_ago,
        scheduled_date__lte=today,
    )
    total_7d = recent.count()
    missed_7d = recent.filter(status__in=['missed', 'skipped']).count()
    miss_rate = missed_7d / total_7d if total_7d > 0 else 0
    base_score += miss_rate * 50

    # Factor 2: Consecutive missed slots — up to 20 points
    recent_ordered = recent.order_by('-scheduled_date', '-scheduled_time')
    streak = 0
    for dose in recent_ordered:
        if dose.status in ('missed', 'skipped'):
            streak += 1
        else:
            break
    if streak >= 3:
        base_score += 20

    # Factor 3: Medicine complexity — up to 10 points
    from apps.medicines.models import MedicineSchedule
    active_schedules = MedicineSchedule.objects.filter(
        patient_id=patient_id, is_active=True
    ).count()
    if active_schedules >= 4:
        base_score += 10

    # Factor 4: Day-of-week pattern — up to 10 points
    day_misses = DoseLog.objects.filter(
        patient_id=patient_id, status='missed'
    ).values('scheduled_date__week_day').annotate(
        count=Count('id')
    ).order_by('-count').first()
    if day_misses:
        # Django week_day: 1=Sunday, 2=Monday, etc.
        today_weekday = today.isoweekday() % 7 + 1
        if day_misses['scheduled_date__week_day'] == today_weekday:
            base_score += 10

    # Factor 5: Consecutive missed DAYS — up to 10 points
    consec_days = 0
    check = today - timedelta(days=1)
    for _ in range(7):
        day_doses = DoseLog.objects.filter(patient_id=patient_id, scheduled_date=check)
        if day_doses.exists() and not day_doses.filter(status='taken').exists():
            consec_days += 1
            check -= timedelta(days=1)
        else:
            break
    if consec_days >= 2:
        base_score += 10

    risk_score = min(round(base_score), 100)
    thresholds = [(25, 'low'), (50, 'medium'), (75, 'high'), (101, 'critical')]
    level = next(lbl for t, lbl in thresholds if risk_score < t)

    insights = {
        'low': "You're doing great! Keep up the consistency. 💚",
        'medium': "Some doses were missed recently. Let's get back on track! 💛",
        'high': "Multiple missed doses detected. Your health needs attention! 🧡",
        'critical': "Urgent: High risk of medication non-adherence. Please take action! ❤️",
    }

    return {
        'score': risk_score,
        'level': level,
        'insight': insights[level],
        'factors': {
            'miss_rate_7d': round(miss_rate * 100, 1),
            'slot_streak': streak,
            'active_medicines': active_schedules,
            'consecutive_missed_days': consec_days,
        },
    }
```

### ✅ Done When
- `/api/ai/risk-score/` returns correct score for test patient
- Score changes when dose statuses are modified

---

## Member B — Predictions Page + History Page

### Tasks
1. Build `Predictions.jsx` — AI risk analytics page:
   - Large risk score circle with color
   - Factor breakdown cards
   - 7-day prediction cards
   - Insight text with icon
2. Build `History.jsx` — medication adherence history page:
   - Date range filter
   - Status filter (taken/missed/skipped)
   - Table or timeline view of past doses
3. Polish Dashboard: connect live risk score to dashboard header

### ✅ Done When
- Predictions page shows real risk data from API
- History page loads and filters dose history
- Dashboard risk badge shows live score

---

## Member C — APScheduler Background Jobs

### Tasks
1. Set up `django-apscheduler` in settings
2. Build `scheduler/jobs.py`:
   - **Every 1 minute**: check pending doses > 30min late → send WhatsApp
   - **Every 1 minute**: check doses > 45min late or response=3 → escalate
   - **Every 6 hours**: recalculate risk scores for all patients
3. Register jobs on Django startup (via `AppConfig.ready()`)

#### [NEW] `scheduler/jobs.py`
```python
from datetime import timedelta
from django.utils import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
import logging

logger = logging.getLogger(__name__)

def check_pending_reminders():
    """Send WhatsApp reminder for doses > 30 min late."""
    from apps.doses.models import DoseLog
    from services.ai_message_service import generate_ai_variables
    from services.whatsapp_service import send_reminder
    from datetime import date, datetime

    now = timezone.now()
    cutoff_time = (now - timedelta(minutes=30)).time()
    today = date.today()

    overdue = DoseLog.objects.filter(
        scheduled_date=today,
        status='pending',
        reminder_sent=False,
        scheduled_time__lte=cutoff_time,
    ).select_related('patient', 'patient__user', 'medicine')

    for dose in overdue:
        try:
            variables = generate_ai_variables(dose.patient, dose)
            send_reminder(dose, dose.patient, variables)
            dose.reminder_sent = True
            dose.save()
            logger.info(f"Reminder sent for dose {dose.id}")
        except Exception as e:
            logger.error(f"Reminder failed for dose {dose.id}: {e}")


def check_escalations():
    """Escalate doses > 45min late or with response=3."""
    from apps.doses.models import DoseLog
    from services.escalation_service import trigger_caretaker_alert
    from datetime import date

    now = timezone.now()
    cutoff_time = (now - timedelta(minutes=45)).time()
    today = date.today()

    needs_escalation = DoseLog.objects.filter(
        scheduled_date=today,
        status__in=['pending', 'missed'],
        escalated=False,
        scheduled_time__lte=cutoff_time,
    ).select_related('patient', 'medicine')

    for dose in needs_escalation:
        try:
            trigger_caretaker_alert(dose)
            logger.info(f"Escalated dose {dose.id}")
        except Exception as e:
            logger.error(f"Escalation failed for dose {dose.id}: {e}")


def recalculate_risk_scores():
    """Recalculate risk scores for all active patients."""
    from apps.patients.models import PatientProfile
    from services.ai_service import calculate_risk_score

    for patient in PatientProfile.objects.filter(user__is_active=True):
        try:
            result = calculate_risk_score(patient.id)
            patient.risk_level = result['level']
            patient.save()
        except Exception as e:
            logger.error(f"Risk recalc failed for patient {patient.id}: {e}")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(check_pending_reminders, 'interval', minutes=1, id='check_reminders',
                      replace_existing=True)
    scheduler.add_job(check_escalations, 'interval', minutes=1, id='check_escalations',
                      replace_existing=True)
    scheduler.add_job(recalculate_risk_scores, 'interval', hours=6, id='recalc_risk',
                      replace_existing=True)

    scheduler.start()
    logger.info("APScheduler started with 3 jobs")
```

### ✅ Done When
- Scheduler starts when Django starts
- Overdue doses get WhatsApp reminders automatically
- Risk scores recalculate every 6 hours

---

## Member D — AI Generate Message Endpoint + Testing

### Tasks
1. Build `POST /api/ai/generate-message/` endpoint
2. Test scheduler: create a dose 31 minutes ago → verify reminder fires within 1 minute
3. Test escalation: create a dose 46 minutes ago → verify caretaker alerted
4. Git commit: `"Day 5: AI Engine + Scheduler complete"`

### ✅ Done When
- Generate-message endpoint returns AI tip
- Scheduler automatically sends reminders for overdue doses
- All tests pass

---

# DAY 6 — Bot Call + Caretaker Dashboard + Admin Panel

## Member A — Twilio Bot Call Service

### Tasks
1. Build `services/call_service.py` — Twilio voice call with TwiML
2. Add bot call to escalation timeline: at T+75 min, trigger voice call
3. Update `scheduler/jobs.py`: add bot call check

#### [NEW] `services/call_service.py`
```python
import os
import logging
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from apps.escalation.models import EscalationLog

logger = logging.getLogger(__name__)

def make_bot_call(dose_log):
    """Make automated voice call to caretaker."""
    patient = dose_log.patient
    caretaker = patient.caretakers.filter(is_primary=True).first()
    if not caretaker:
        logger.warning(f"No primary caretaker for patient {patient.id}")
        return False

    phone = caretaker.user.whatsapp_number or caretaker.phone
    if not phone:
        return False

    sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
    token = os.environ.get('TWILIO_AUTH_TOKEN', '')
    from_phone = os.environ.get('TWILIO_PHONE', '')

    if not all([sid, token, from_phone]):
        logger.warning("Twilio credentials not set — skipping bot call")
        # Log as attempted even if simulated
        dose_log.call_attempted = True
        dose_log.save()
        _log_call(dose_log, patient, phone, "SIMULATED — Twilio not configured", False)
        return False

    twiml = VoiceResponse()
    twiml.say(
        f"Alert from MediMate. Patient {patient.user.full_name} has missed their "
        f"{dose_log.medicine.name} medication scheduled for "
        f"{dose_log.scheduled_time.strftime('%I:%M %p')}. "
        f"Please contact them immediately. This is an automated alert.",
        voice='alice',
    )

    try:
        client = Client(sid, token)
        call = client.calls.create(
            twiml=str(twiml),
            to=phone,
            from_=from_phone,
        )
        dose_log.call_attempted = True
        dose_log.save()
        _log_call(dose_log, patient, phone, f"Call SID: {call.sid}", True)
        return True
    except Exception as e:
        logger.error(f"Bot call failed: {e}")
        _log_call(dose_log, patient, phone, str(e), False)
        dose_log.call_attempted = True
        dose_log.save()
        return False


def _log_call(dose_log, patient, phone, message, success):
    EscalationLog.objects.create(
        dose_log=dose_log,
        patient=patient,
        escalation_level='bot_call',
        recipient_phone=phone,
        message_sent=message,
        success=success,
    )
```

### ✅ Done When
- Bot call fires (or simulates) after 75 min
- EscalationLog records the call attempt
- Graceful handling when Twilio not configured

---

## Member B — Caretaker Dashboard + Admin Panel UI

### Tasks
1. Build `CaretakerDashboard.jsx`:
   - Patient list with risk badges
   - Per-patient dose status (today)
   - Escalation alert feed
   - Real-time status indicators
2. Build `Admin.jsx`:
   - System stats cards (total patients, active schedules, doses today, escalations)
   - User management table
   - Escalation log viewer
   - WhatsApp interaction log viewer

### ✅ Done When
- Caretaker can see assigned patients and their dose statuses
- Admin can see system-wide stats and all logs
- Both pages are responsive and polished

---

## Member C — Push Notifications + Caretaker API

### Tasks
1. Build caretaker dashboard API:
   - `GET /api/patients/caretaker-dashboard/` — all assigned patients with today's dose status
2. Build admin dashboard API:
   - `GET /api/admin/stats/` — system-wide statistics
   - `GET /api/admin/users/` — all users (admin only)
3. Set up VAPID push notifications (optional stretch goal)

### ✅ Done When
- Caretaker API returns patient data correctly
- Admin API returns system stats

---

## Member D — Django Admin Polish + WhatsApp Log Page

### Tasks
1. Customize Django admin: add `WhatsAppInteraction` inline, `EscalationLog` list view
2. Build `WhatsAppLog.jsx` — full interaction history page with simulation panel
3. Add "Simulate Bot Call" button (logs a simulated call for demo purposes)
4. Git commit: `"Day 6: Full platform features complete"`

### ✅ Done When
- Django admin shows all logs beautifully
- WhatsApp Log page lists all interactions with status badges
- Simulation controls work

---

# DAY 7 — Testing + Polish + Demo Prep

## Member A — Test Suite + Seed Data

### Tasks
1. Write pytest tests:
   - `test_webhook_reply_1_marks_taken()`
   - `test_webhook_reply_2_reschedules()`
   - `test_webhook_reply_3_triggers_escalation()`
   - `test_ai_variable_generation()`
   - `test_risk_score_formula()`
   - `test_dose_log_auto_generated()`
   - `test_duplicate_taken_rejected()`
2. Create seed data management command:
   - 2 patients, 1 caretaker, 1 admin
   - 5 medicines across both patients
   - 7 days of historical dose logs (mix of taken/missed)
3. Run full test suite and fix any failures

### ✅ Done When
- All tests pass
- Seed data creates realistic demo scenario

---

## Member B — UI Polish + Landing Page

### Tasks
1. Polish `Landing.jsx`:
   - Hero section with animated gradient background
   - Feature cards with hover effects
   - Testimonials section
   - CTA button → Login
2. Add loading skeletons to all pages
3. Add toast notifications for success/error states
4. Responsive design tweaks for mobile
5. Final visual review of all pages

### ✅ Done When
- Landing page looks production-grade
- All pages responsive on mobile
- Smooth loading transitions everywhere

---

## Member C — End-to-End Demo Script + Deploy Backend

### Tasks
1. Write the 5-minute demo script (exact clicks, exact flow)
2. Deploy backend to Render:
   - Connect GitHub repo
   - Set environment variables
   - Verify API accessible at Render URL
3. Pre-register 2 WhatsApp numbers with CallMeBot (should have been done 24h earlier)
4. Test WhatsApp send from deployed backend

### Demo Script (5 minutes):
```
0:00 — Landing page showcase (wow factor)
0:30 — Google OAuth login
1:00 — Patient onboarding (profile + WhatsApp + medicine)
1:30 — Dashboard: show today's doses, adherence ring
2:00 — Mark a dose as taken (manual)
2:15 — Show WhatsApp reminder received on phone (pre-triggered)
2:30 — Reply "3" on WhatsApp → show escalation alert
3:00 — Caretaker dashboard: see patient status + alert
3:30 — AI Predictions page: risk score + factors
4:00 — Admin panel: system stats + escalation log
4:30 — Show bot call simulation log
4:45 — Wrap up: key differentiators
```

### ✅ Done When
- Backend deployed and accessible
- WhatsApp sends from production URL
- Demo rehearsed once end-to-end

---

## Member D — Deploy Frontend + Final Testing

### Tasks
1. Deploy frontend to Vercel:
   - Connect GitHub repo
   - Set `VITE_API_URL` env var to Render backend URL
   - Verify all pages load on Vercel URL
2. Run full test suite one last time
3. Test deployed app end-to-end (Vercel → Render → WhatsApp)
4. Create backup demo data in case of deployment issues
5. Final Git commit: `"Day 7: Testing + Deployment complete"`

### ✅ Done When
- App accessible at Vercel URL
- All API calls work between Vercel frontend and Render backend
- Demo data seeded in production database
- All tests pass
- Git tagged as `v1.0-demo`

---

## Verification Plan

### Automated Tests
```bash
cd medimateai-backend
pytest apps/ -v --tb=short
```

### Manual Verification
1. Complete Google OAuth login flow
2. Create patient profile + add medicine
3. Verify dose logs auto-generated
4. Trigger and verify WhatsApp reminder
5. Simulate webhook replies (1, 2, 3)
6. Verify escalation to caretaker
7. Check AI risk score calculation
8. Test caretaker and admin dashboards
9. Verify responsive design on mobile
10. Run 5-minute demo script end-to-end
