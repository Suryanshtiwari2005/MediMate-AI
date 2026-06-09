import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/shared/ProtectedRoute';

// Public Pages
import LandingPage from './pages/LandingPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';

// Patient Pages
import PatientDashboard from './pages/patient/PatientDashboard';
import DoseHistory from './pages/patient/DoseHistory';
import AIPredictions from './pages/patient/AIPredictions';
import WhatsAppLog from './pages/patient/WhatsAppLog';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';

// Caretaker Pages
import CaretakerDashboard from './pages/caretaker/CaretakerDashboard';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />

          {/* Patient Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute role="patient">
                <PatientDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/history"
            element={
              <ProtectedRoute role="patient">
                <DoseHistory />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/predictions"
            element={
              <ProtectedRoute role="patient">
                <AIPredictions />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/whatsapp"
            element={
              <ProtectedRoute role="patient">
                <WhatsAppLog />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/medicines"
            element={
              <ProtectedRoute role="patient">
                <PatientDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard/settings"
            element={
              <ProtectedRoute role="patient">
                <PatientDashboard />
              </ProtectedRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute role="admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/*"
            element={
              <ProtectedRoute role="admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          {/* Caretaker Routes */}
          <Route
            path="/caretaker"
            element={
              <ProtectedRoute role="caretaker">
                <CaretakerDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/caretaker/*"
            element={
              <ProtectedRoute role="caretaker">
                <CaretakerDashboard />
              </ProtectedRoute>
            }
          />

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
