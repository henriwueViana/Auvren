
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from 'react-router-dom'

import { LoginPage } from '../../features/auth/LoginPage'
import { AppLayout } from '../../components/layout/AppLayout'
import { useAuthStore } from '../../stores/authStore'
import { DashboardPage } from '../../features/dashboard/DashboardPage'

function ProtectedRoute() {
  const isAuthenticated = useAuthStore(
    (state) => state.isAuthenticated
  )

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}



function PlaceholderPage({ title }: { title: string }) {
  return (
    <div>
      <h2 className="text-2xl font-bold">{title}</h2>

      <p className="mt-3 text-slate-400">
        Esta funcionalidade será implementada em breve.
      </p>
    </div>
  )
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />

            <Route
              path="/tickets"
              element={<PlaceholderPage title="Chamados" />}
            />

            <Route
              path="/triage"
              element={<PlaceholderPage title="Triagem IA" />}
            />

            <Route
              path="/users"
              element={<PlaceholderPage title="Equipe" />}
            />
          </Route>
        </Route>

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />
      </Routes>
    </BrowserRouter>
  )
}
