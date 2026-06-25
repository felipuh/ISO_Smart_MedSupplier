import React, { Suspense, lazy } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import ProtectedRoute, { PublicRoute } from './components/Auth/ProtectedRoute';
import { useI18n } from './context/I18nContext';

const LoginPage = lazy(() => import('./pages/LoginPage'));
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'));
const ResetPasswordPage = lazy(() => import('./pages/ResetPasswordPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const ReportsPage = lazy(() => import('./pages/ReportsPage'));
const SettingsDashboard = lazy(() => import('./components/Settings').then((module) => ({ default: module.SettingsDashboard })));
const MedSupplierShell = lazy(() => import('./features/medsupplier/components/MedSupplierShell'));
const MedSupplierDashboard = lazy(() => import('./features/medsupplier/pages/MedSupplierDashboard'));
const MedSupplierWorkspace = lazy(() => import('./features/medsupplier/pages/MedSupplierWorkspace'));

function App() {
  const { t } = useI18n();

  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center bg-slate-950 text-slate-300">{t('common.messages.loading')}</div>}>
      <Routes>
        <Route
          path="/login"
          element={
            <PublicRoute redirectTo="/medsupplier">
              <LoginPage />
            </PublicRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <PublicRoute redirectTo="/medsupplier">
              <ForgotPasswordPage />
            </PublicRoute>
          }
        />
        <Route
          path="/reset-password"
          element={
            <PublicRoute redirectTo="/medsupplier">
              <ResetPasswordPage />
            </PublicRoute>
          }
        />

        <Route
          element={
            <ProtectedRoute>
              <MedSupplierShell />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/medsupplier" replace />} />
          <Route path="medsupplier" element={<MedSupplierDashboard />} />
          <Route path="medsupplier/:sectionKey" element={<MedSupplierWorkspace />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route
            path="settings"
            element={
              <ProtectedRoute allowedRoles={['org_admin', 'iso_manager']}>
                <SettingsDashboard />
              </ProtectedRoute>
            }
          />
        </Route>

        <Route path="*" element={<Navigate to="/medsupplier" replace />} />
      </Routes>
    </Suspense>
  );
}

export default App;
