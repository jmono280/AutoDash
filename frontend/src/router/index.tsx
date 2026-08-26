import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { hasRole } from '@/lib/permissions'
import Layout from '@/components/layout/Layout'
import HoursDashboard from '@/views/HoursDashboard'
import ImportsView from '@/views/ImportsView'
import LoginView from '@/views/LoginView'
import OverviewDashboard from '@/views/OverviewDashboard'
import SalesDashboard from '@/views/SalesDashboard'
import TechniciansDashboard from '@/views/TechniciansDashboard'
import WorkInProgressDashboard from '@/views/WorkInProgressDashboard'
import CallAnalyticsDashboard from '@/views/CallAnalyticsDashboard'
import ChatView from '@/views/ChatView'
import PaymentReportDashboard from '@/views/PaymentReportDashboard'
import ProfileView from '@/views/ProfileView'
import IdmsDashboard from '@/views/IdmsDashboard'
import type { UserRole } from '@/types/auth'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  return <RoleRoute>{children}</RoleRoute>
}

function RoleRoute({
  children,
  roles,
}: {
  children: React.ReactNode
  roles?: UserRole[]
}) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!hasRole(user, roles)) {
    return <Navigate to="/" replace />
  }

  return <Layout>{children}</Layout>
}

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginView />} />

      <Route
        path="/"
        element={
          <PrivateRoute>
            <OverviewDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/sales"
        element={
          <PrivateRoute>
            <SalesDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/hours"
        element={
          <PrivateRoute>
            <HoursDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/technicians"
        element={
          <PrivateRoute>
            <TechniciansDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/wip"
        element={
          <PrivateRoute>
            <WorkInProgressDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/imports"
        element={
          <RoleRoute roles={['admin']}>
            <ImportsView />
          </RoleRoute>
        }
      />

      <Route
        path="/calls"
        element={
          <PrivateRoute>
            <CallAnalyticsDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/payment"
        element={
          <RoleRoute roles={['admin']}>
            <PaymentReportDashboard />
          </RoleRoute>
        }
      />
      <Route
        path="/idms-reports"
        element={
          <PrivateRoute>
            <IdmsDashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <RoleRoute roles={['admin']}>
            <ChatView />
          </RoleRoute>
        }
      />
      <Route
        path="/profile"
        element={
          <PrivateRoute>
            <ProfileView />
          </PrivateRoute>
        }
      />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
