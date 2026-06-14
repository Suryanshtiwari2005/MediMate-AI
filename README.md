# 💊 MediMate AI — Frontend

> **Biopunk × Clinical Neural Interface** — React + Vite + Tailwind frontend for the MediMate AI medication adherence platform.

---

## 📋 Table of Contents

1. [Tech Stack](#tech-stack)
2. [Project Structure](#project-structure)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Environment Variables](#environment-variables)
6. [Running the Dev Server](#running-the-dev-server)
7. [Building for Production](#building-for-production)
8. [Routes & Navigation](#routes--navigation)
9. [Design System](#design-system)
10. [Connecting to the Backend](#connecting-to-the-backend)
11. [Role-Based Access](#role-based-access)
12. [Pages Overview](#pages-overview)
13. [Troubleshooting](#troubleshooting)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 19 + Vite 8 |
| Styling | Tailwind CSS v4 (`@tailwindcss/vite` plugin) |
| UI Primitives | Radix UI (Dialog, Dropdown, Tabs, Tooltip) |
| Routing | React Router DOM v7 |
| HTTP Client | Axios (with JWT interceptors) |
| Icons | Lucide React |
| Fonts | Syne · Inter · JetBrains Mono (Google Fonts) |
| Class Utils | clsx + tailwind-merge + class-variance-authority |

---

## Project Structure

```
medimate-frontend/
├── index.html                    # App shell (fonts loaded here)
├── vite.config.js                # Vite + Tailwind config, @ alias
├── .env                          # YOUR local env (not committed)
├── .env.example                  # Copy this → .env
├── package.json
└── src/
    ├── main.jsx                  # React root mount
    ├── App.jsx                   # BrowserRouter + all routes
    ├── index.css                 # Design system (CSS vars, glass, animations)
    │
    ├── context/
    │   └── AuthContext.jsx       # JWT auth state + axios interceptor
    │
    ├── components/
    │   ├── layout/
    │   │   ├── Navbar.jsx        # Top nav (Logo, Products, About, Auth CTA)
    │   │   ├── Footer.jsx        # 4-column footer
    │   │   ├── PatientLayout.jsx # Sidebar layout for patient pages
    │   │   └── AdminLayout.jsx   # Sidebar layout for admin pages
    │   └── shared/
    │       ├── AuthModal.jsx     # Sign In / Sign Up modal + Google OAuth
    │       └── ProtectedRoute.jsx# Role-based route guard
    │
    └── pages/
        ├── LandingPage.jsx       # Hero + features + CTA (draiai.com inspired)
        ├── AboutPage.jsx         # Mission, vision, team values
        ├── ContactPage.jsx       # Contact form + info
        ├── patient/
        │   ├── PatientDashboard.jsx  # Today's doses, adherence ring, calendar
        │   ├── DoseHistory.jsx       # Filterable dose history table
        │   ├── AIPredictions.jsx     # Risk score + 7-day forecast
        │   └── WhatsAppLog.jsx       # WhatsApp interaction log + simulator
        ├── admin/
        │   └── AdminDashboard.jsx    # Stats, user table, escalations
        └── caretaker/
            └── CaretakerDashboard.jsx # Patient cards, escalation feed
```

---

## Prerequisites

Make sure these are installed globally before you begin:

```bash
node --version   # >= 18.0.0 required (20+ recommended)
npm --version    # >= 9.0.0
```

---

## Installation & Setup

### Step 1 — Clone / enter the project folder

```bash
cd medimate-frontend
```

### Step 2 — Install dependencies

```bash
npm install
```

> This installs: React, Vite, Tailwind CSS, React Router DOM, Axios, Radix UI, Lucide React, and all utilities.

### Step 3 — Set up environment variables

```bash
cp .env.example .env
```

Then open `.env` and set your backend URL:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Base URL of your Django REST API (no trailing slash) | `http://localhost:8000/api` |

> All `VITE_` prefixed variables are available in the browser via `import.meta.env.VITE_*`.

---

## Running the Dev Server

```bash
npm run dev
```

The app will start at **http://localhost:5173**

Hot Module Replacement (HMR) is enabled — changes reflect instantly without full reload.

---

## Building for Production

```bash
npm run build
```

Output goes to the `dist/` folder. To preview the production build locally:

```bash
npm run preview
```

---

## Routes & Navigation

| Path | Page | Access |
|------|------|--------|
| `/` | Landing Page | Public |
| `/about` | About Us | Public |
| `/contact` | Contact Us | Public |
| `/dashboard` | Patient Dashboard | `patient` role |
| `/dashboard/history` | Dose History | `patient` role |
| `/dashboard/predictions` | AI Predictions | `patient` role |
| `/dashboard/whatsapp` | WhatsApp Log | `patient` role |
| `/dashboard/medicines` | Medicines (→ Dashboard) | `patient` role |
| `/dashboard/settings` | Settings (→ Dashboard) | `patient` role |
| `/admin` | Admin Dashboard | `admin` role |
| `/caretaker` | Caretaker Dashboard | `caretaker` role |
| `*` | Redirects to `/` | — |

---

## Design System

The design system lives in `src/index.css` as CSS custom properties. All components use these variables — never hardcoded colors.

### Color Palette

```css
--bg-primary:    #050d1a   /* Deep navy — main background */
--bg-secondary:  #081425   /* Slightly lighter navy */
--bg-card:       #0a1929   /* Card surfaces */
--bg-glass:      rgba(10, 25, 41, 0.7)  /* Glassmorphic overlays */
--cyan:          #00d4ff   /* Primary accent — interactive elements */
--emerald:       #00ff9d   /* Secondary accent — success / health */
--purple:        #7c3aed   /* Caretaker accent */
--amber:         #f59e0b   /* Warning / pending dose */
--danger:        #ef4444   /* Danger / missed dose */
```

### Typography

```
Syne         — Display / headings (800 weight for hero)
Inter        — Body text / UI
JetBrains Mono — Data / timestamps / codes
```

### Utility Classes

```css
.glass-card     — Glassmorphic card with blur + border
.font-syne      — Apply Syne font
.font-mono      — Apply JetBrains Mono
.dose-taken     — Green pill state
.dose-missed    — Red pill state
.dose-pending   — Amber pill state
.dose-upcoming  — Cyan pill state
.sidebar-item   — Sidebar navigation item
.sidebar-item.active — Active sidebar item
.data-table     — Styled table
.progress-ring  — SVG adherence ring
```

### Animations

```css
fadeInUp     — Entrance from below (hero elements)
pulse-glow   — Cyan glow pulse (risk indicators)
float        — Floating card animation (hero)
ecg-draw     — ECG line drawing animation
```

---

## Connecting to the Backend

All API calls are made via the `apiClient` axios instance in `src/context/AuthContext.jsx`. It automatically attaches JWT tokens to every request.

### Backend API Endpoints Expected

```
POST   /api/auth/login/              { email, password } → { access, refresh, user }
POST   /api/auth/register/           { name, email, password, role } → { access, refresh, user }
POST   /api/auth/logout/             { refresh }
POST   /api/auth/token/refresh/      { refresh } → { access }
GET    /auth/google/login/           → OAuth redirect (social-auth-app-django)

GET    /api/doses/today/             → { summary, medicines }
POST   /api/doses/{id}/take/         → 200 OK
POST   /api/doses/{id}/skip/         { reason } → 200 OK

GET    /api/doses/history/           ?status=&date_from=&date_to= → [doses]
GET    /api/ai/predictions/          → { overall_risk, factors, predictions }
GET    /api/ai/adherence-trend/      → [{ week, rate }]
GET    /api/whatsapp/webhook/        → [interactions]
POST   /api/whatsapp/send-reminder/  { dose_id } → 200 OK

GET    /api/admin/stats/             → { total_patients, ... }
GET    /api/patients/caretaker-dashboard/  → { patients, escalations }
```

### Replacing Mock Data

Every dashboard page has mock data at the top of the file clearly marked with a comment:

```js
// TODO: Replace with API call → GET /api/doses/today/
// const { data } = await apiClient.get('/doses/today/');
```

Simply uncomment the API call and remove the mock object.

---

## Role-Based Access

Authentication flow:

1. User opens the **Sign In** modal from any page
2. On successful login, the server returns `{ access, refresh, user }` where `user.role` is `"patient"`, `"caretaker"`, or `"admin"`
3. The frontend stores tokens in `localStorage` and redirects:
   - `patient` → `/dashboard`
   - `caretaker` → `/caretaker`
   - `admin` → `/admin`
4. `ProtectedRoute` wraps each route and checks `user.role` — wrong role gets redirected to the correct dashboard
5. Axios interceptor auto-refreshes the access token on `401` responses

---

## Pages Overview

### 🏠 Landing Page (`/`)
- Animated ECG hero section (draiai.com-inspired dark navy aesthetic)
- Scroll-animated stat counters (patients served, adherence rate, etc.)
- "Why MediMate" 6-card feature grid
- 6 feature sections with alternating image/text layout (linked from Products nav)
- Bottom CTA band

### 👤 Patient Dashboard (`/dashboard`)
- **Stat row**: Total doses, taken, missed, remaining
- **AdherenceRing**: Animated SVG circular progress
- **MedicineCard** per medicine:
  - Days-active badge — click opens a 30-day calendar modal (non-editable, color-coded by dose status)
  - Dose cards per scheduled time: **Green** = Taken, **Red** = Missed, **Amber** = Pending, **Cyan** = Upcoming
  - "Take" button → marks dose taken, card turns green
  - "Skip" button → opens SkipModal for reason text

### 📋 Dose History (`/dashboard/history`)
- Search bar, date range pickers, status filter buttons
- Sortable color-coded table of all dose records

### 🤖 AI Predictions (`/dashboard/predictions`)
- Overall risk score ring (Low / Medium / High / Critical)
- 5-factor breakdown bars (miss rate, streak, complexity, day pattern, consecutive days)
- 7-day prediction cards with per-dose risk badges

### 💬 WhatsApp Log (`/dashboard/whatsapp`)
- Full log of sent messages, patient replies (1/2/3), and actions taken
- "Simulate Reply" modal for demo/webhook testing without a real WhatsApp number

### 🛡️ Admin Dashboard (`/admin`)
- 4 system stat cards
- Recent users table with role badges and active/inactive status dots
- Today's escalations table

### 👁️ Caretaker Dashboard (`/caretaker`)
- Patient cards showing risk badge, taken/missed/pending counts, adherence bar, medicine tags
- Live escalation feed

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `npm install` fails | Make sure Node.js ≥ 18. Try deleting `node_modules` and `package-lock.json` and re-running |
| Fonts not loading | Check your internet connection — fonts are loaded from Google Fonts CDN |
| API calls return 401 | Confirm `.env` has the correct `VITE_API_BASE_URL` and your Django server is running |
| CORS errors in browser | Add your frontend origin (`http://localhost:5173`) to Django's `CORS_ALLOWED_ORIGINS` |
| Google OAuth redirect fails | Confirm Django's `social-auth-app-django` is configured and `/auth/google/login/` is accessible |
| Build fails | Run `npm run build` and check the error — most common cause is a missing lucide-react icon name |
| White screen on `/dashboard` | You're not logged in — open the Sign In modal on the landing page first |

---

## Quick Start (TL;DR)

```bash
# 1. Install
npm install

# 2. Configure
cp .env.example .env
# Edit .env → set VITE_API_BASE_URL

# 3. Start Django backend (in a separate terminal)
# python manage.py runserver

# 4. Run frontend
npm run dev
# → http://localhost:5173
```

---

*Built for MediMate AI Hackathon · Biopunk × Clinical Neural Interface Design System*
