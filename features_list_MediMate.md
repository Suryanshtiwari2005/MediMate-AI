# 💊 MediMateAI — Complete Features List

> **Total Features: 64** across 10 modules
> Prototype target: Capgemini Exceller Buildathon Grand Final

---

## Module 1 — Authentication & Authorization (6 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 1 | Google OAuth 2.0 Login | One-click "Continue with Google" — full OAuth flow via `social-auth-app-django` | 1 | C |
| 2 | JWT Session Management | Access + Refresh tokens via `djangorestframework-simplejwt`, stored in frontend state | 1 | C |
| 3 | Role-Based Access Control (RBAC) | Three roles: `patient`, `caretaker`, `admin` — each with scoped API permissions | 2 | A |
| 4 | Protected Routes | Frontend `ProtectedRoute` component — redirects unauthenticated users to `/login` | 2 | B |
| 5 | Token Auto-Refresh | Axios interceptor automatically refreshes expired access tokens using refresh token | 2 | B |
| 6 | Secure Logout | Blacklists refresh token on logout, clears frontend state | 1 | C |

---

## Module 2 — Patient Profile & Onboarding (9 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 7 | Multi-Step Onboarding Wizard | 4-step guided setup: Personal → Medical → WhatsApp → Emergency Contact | 2 | B |
| 8 | Patient Profile CRUD | Create, read, update patient profile via `PatientProfileViewSet` | 2 | A |
| 9 | Direct WhatsApp Number Save | Save WhatsApp number directly (no OTP verification) — simplified onboarding | 2 | A |
| 10 | Medical History Capture | JSON fields for diseases, allergies, and chronic conditions | 2 | A |
| 11 | Blood Group & Demographics | Age, gender, blood group stored in patient profile | 2 | B |
| 12 | Emergency Contact | Emergency phone number for fallback escalation | 2 | B |
| 13 | Onboarding Completion Flag | `onboarding_done` flag — dashboard checks this before first load | 2 | A |
| 14 | Avatar from Google | Profile picture auto-populated from Google account | 1 | C |
| 15 | Soft Delete for Users | `is_deleted` flag — clinical records are never hard-deleted | 1 | A |

---

## Module 3 — Medicine & Schedule Management (7 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 16 | Medicine CRUD | Add, edit, delete medicines (name, dosage, instructions) | 2 | C |
| 17 | Medicine Schedule CRUD | Set specific daily times for each medicine with start/end dates | 2 | C |
| 18 | Add Medicine Form (UI) | Frontend form with medicine name, dosage, time picker, date range | 3 | B |
| 19 | Auto Dose Log Generation | Django `post_save` signal auto-creates `DoseLog` entries for 30 days when a schedule is saved | 2 | C |
| 20 | Bulk Log Creation | `bulk_create` with `ignore_conflicts=True` for efficient generation | 2 | C |
| 21 | Schedule Activation Toggle | `is_active` flag to pause/resume a medicine schedule without deleting | 2 | C |
| 22 | Duplicate Prevention | `unique_together` constraint on `(schedule, date, time)` prevents duplicate dose logs | 1 | A |

---

## Module 4 — Dose Tracking & Dashboard (12 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 23 | Today's Doses View | `GET /api/doses/today/` — all doses for today with summary counts | 3 | A |
| 24 | Mark Dose as Taken | `POST /api/doses/{id}/take/` — records `taken_at` timestamp | 3 | A |
| 25 | Skip Dose with Reason | `POST /api/doses/{id}/skip/` — records skip reason text | 3 | A |
| 26 | Duplicate Take Prevention | Returns `409 Conflict` if dose is already marked as taken | 3 | A |
| 27 | Dose History with Filters | `GET /api/doses/history/` — filter by date range and status | 3 | A |
| 28 | Weekly Calendar Grid | `GET /api/doses/weekly/` — 7-day overview with taken/missed counts per day | 3 | A |
| 29 | Missed Doses Report | `GET /api/doses/missed/` — missed doses in last N days | 3 | A |
| 30 | Patient Dashboard (UI) | Full-featured dashboard: today's meds, adherence ring, risk badge, quick actions | 4 | B |
| 31 | Interactive Dose Cards | `DoseCard.jsx` — swipeable/clickable cards with "Take" and "Skip" buttons | 3–4 | B |
| 32 | Adherence Ring | `AdherenceRing.jsx` — animated SVG circular progress showing daily adherence % | 4 | B |
| 33 | Weekly Calendar (UI) | `WeeklyCalendar.jsx` — compact 7-day visual with color-coded dots per day | 4 | B |
| 34 | Loading Skeletons | Shimmer loading placeholders while API data loads | 7 | B |

---

## Module 5 — WhatsApp Interactive System (10 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 35 | CallMeBot Integration | Send WhatsApp messages via CallMeBot free gateway (HTTP GET) | 3 | C |
| 36 | Interactive Button Template | Message with reply options: `1` = Taken, `2` = Reschedule +15min, `3` = Not Taking | 3 | C |
| 37 | AI-Personalized Messages | Each WhatsApp message includes AI-generated motivational tip + streak info | 3 | C |
| 38 | Manual Reminder Trigger | `POST /api/whatsapp/send-reminder/` — manually send a WhatsApp reminder for any dose | 3 | C |
| 39 | Webhook Reply Handler | `POST /api/whatsapp/webhook/` — receives patient's 1/2/3 reply and routes action | 4 | A |
| 40 | Reschedule on Reply "2" | Creates new `DoseLog` entry +15 minutes, marks original as `rescheduled` | 4 | A |
| 41 | Escalate on Reply "3" | Immediately triggers caretaker WhatsApp alert when patient says "Not Taking" | 4 | A |
| 42 | Stale Message Rejection | Messages older than 2 hours are expired — replies to old messages are rejected | 4 | A |
| 43 | WhatsApp Interaction Log | Full log of all sent messages, AI variables used, responses received, timestamps | 3 | C |
| 44 | Webhook Simulation Page (UI) | `WhatsAppLog.jsx` — frontend tool to simulate incoming WhatsApp replies for demo | 4 | D |

---

## Module 6 — AI Prediction Engine (8 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 45 | Rule-Based Risk Score Engine | 5-factor deterministic scoring: miss rate, slot streak, complexity, day pattern, consecutive days | 5 | A |
| 46 | Risk Level Classification | Scores map to 4 levels: `low` (<25), `medium` (<50), `high` (<75), `critical` (75+) | 5 | A |
| 47 | Risk Factor Breakdown | API returns individual factor contributions (miss rate %, streak count, etc.) | 5 | A |
| 48 | Contextual Insights | Human-readable insight text generated per risk level | 5 | A |
| 49 | 7-Day Predictions | `GET /api/ai/predictions/` — predicts which upcoming doses are at highest risk | 5 | A |
| 50 | Adherence Trend | `GET /api/ai/adherence-trend/` — weekly trend data for charting | 5 | A |
| 51 | Hugging Face AI Tips | GPT-2 via HF free Inference API generates personalized motivational tips | 3 | C |
| 52 | Fallback Tip System | 5 hardcoded motivational tips used when HF API is down or times out | 3 | C |

---

## Module 7 — Escalation Pipeline (7 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 53 | T+30 min Auto-Reminder | APScheduler checks every minute — sends WhatsApp if dose is 30+ minutes late | 5 | C |
| 54 | T+45 min Caretaker Alert | WhatsApp alert sent to primary caretaker after 45 minutes of no response | 5 | C |
| 55 | Secondary Caretaker Alert | If patient has multiple caretakers, secondary is alerted at T+60 min | 4 | C |
| 56 | T+75 min Bot Voice Call | Twilio automated voice call reads alert message to primary caretaker's phone | 6 | A |
| 57 | Emergency Phone Fallback | If no caretaker assigned, alert is sent to patient's emergency phone number | 4 | C |
| 58 | Escalation Logging | Every escalation action (WhatsApp, SMS, call) is logged in `EscalationLog` table | 4 | C |
| 59 | Retroactive Taken Handling | If patient marks "taken" after escalation has fired, pending calls are cancelled | 4 | A |

---

## Module 8 — Caretaker Portal (4 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 60 | Caretaker Dashboard | `CaretakerDashboard.jsx` — see all assigned patients, their risk levels, and today's dose status | 6 | B |
| 61 | Caretaker Patient Assignment | API endpoint to assign/unassign patients to a caretaker | 2 | A |
| 62 | Live Escalation Feed | Real-time list of escalation alerts for the caretaker's assigned patients | 6 | B |
| 63 | Caretaker Dashboard API | `GET /api/patients/caretaker-dashboard/` — aggregated patient data for caretaker view | 6 | C |

---

## Module 9 — Admin Panel (6 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 64 | System Stats Dashboard | `Admin.jsx` — total patients, active schedules, doses today, escalations count | 6 | B |
| 65 | User Management Table | View all users, filter by role, see active/inactive status | 6 | B |
| 66 | Escalation Log Viewer | Searchable table of all escalation events across the platform | 6 | B |
| 67 | WhatsApp Interaction Log (Admin) | Admin view of all WhatsApp interactions across all patients | 6 | D |
| 68 | Django Admin Panel | Auto-configured Django admin with `list_display`, `search_fields`, `list_filter` for all models | 1 | D |
| 69 | Admin Stats API | `GET /api/admin/stats/` — system-wide statistics endpoint (admin only) | 6 | C |

---

## Module 10 — Infrastructure & Deployment (5 Features)

| # | Feature | Description | Day | Owner |
|---|---------|-------------|-----|-------|
| 70 | APScheduler Background Jobs | 3 recurring jobs: reminder check (1min), escalation check (1min), risk recalc (6h) | 5 | C |
| 71 | OpenAPI Documentation | `drf-spectacular` auto-generates Swagger UI at `/api/docs/` | 1 | D |
| 72 | Seed Data Command | Management command to populate 2 patients, 5 medicines, 7 days of history for demo | 7 | A |
| 73 | Vercel Frontend Deployment | React app deployed to Vercel free tier with auto-deploy from GitHub | 7 | D |
| 74 | Render Backend Deployment | Django app deployed to Render free tier (750h/month) | 7 | C |

---

## Feature Summary by Module

| Module | Features | Core / Nice-to-Have |
|--------|----------|-------------------|
| 🔐 Authentication & Authorization | 6 | Core |
| 👤 Patient Profile & Onboarding | 9 | Core |
| 💊 Medicine & Schedule Management | 7 | Core |
| 📊 Dose Tracking & Dashboard | 12 | Core |
| 📱 WhatsApp Interactive System | 10 | Core (Key Differentiator) |
| 🤖 AI Prediction Engine | 8 | Core (Key Differentiator) |
| 🚨 Escalation Pipeline | 7 | Core |
| 🩺 Caretaker Portal | 4 | Core |
| ⚙️ Admin Panel | 6 | Supporting |
| 🚀 Infrastructure & Deployment | 5 | Supporting |
| **TOTAL** | **74** | |

---

## Feature Distribution by Team Member

| Member | Total Features Owned | Key Areas |
|--------|---------------------|-----------|
| **Member A (You)** | ~20 | Models, dose tracking, webhook, AI engine, Twilio, tests |
| **Member B** | ~18 | All UI pages, components, responsive design, polish |
| **Member C** | ~20 | OAuth, WhatsApp service, AI messages, scheduler, escalation, deploy backend |
| **Member D** | ~16 | Serializers, admin panel, simulation page, testing, deploy frontend |

---

## Feature Distribution by Day

| Day | Features Built | Cumulative |
|-----|---------------|------------|
| Day 1 | 12 | 12 |
| Day 2 | 16 | 28 |
| Day 3 | 14 | 42 |
| Day 4 | 12 | 54 |
| Day 5 | 8 | 62 |
| Day 6 | 10 | 72 |
| Day 7 | 2 + testing + polish + deploy | **74** |

---

## 🌟 Key Differentiators (Highlight for Judges)

1. **AI-Personalized WhatsApp Reminders** — Every message includes a Hugging Face-generated motivational tip tailored to the patient's name, medicine, and risk score
2. **Interactive 1/2/3 Reply System** — Patients reply directly on WhatsApp; the system reacts instantly (mark taken, reschedule, or escalate)
3. **5-Factor Risk Prediction Engine** — Deterministic AI that predicts which patients are most likely to miss their next dose
4. **3-Tier Escalation Pipeline** — WhatsApp → WhatsApp (caretaker) → Automated Bot Voice Call — no missed dose goes unnoticed
5. **Real-Time Caretaker Dashboard** — Caretakers monitor multiple patients with live dose status and risk badges
