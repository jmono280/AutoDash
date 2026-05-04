import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import Layout from '@/components/layout/Layout'
import HoursDashboard from '@/views/HoursDashboard'
import ImportsView from '@/views/ImportsView'
import LoginView from '@/views/LoginView'
import OverviewDashboard from '@/views/OverviewDashboard'
import SalesDashboard from '@/views/SalesDashboard'
import TechniciansDashboard from '@/views/TechniciansDashboard'
import WorkInProgressDashboard from '@/views/WorkInProgressDashboard'
import ChatView from '@/views/ChatView'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
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
          <PrivateRoute>
            <ImportsView />
          </PrivateRoute>
        }
      />

      <Route
        path="/chat"
        element={
          <PrivateRoute>
            <ChatView />
          </PrivateRoute>
        }
      />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
