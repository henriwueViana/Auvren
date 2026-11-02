
import {
  BrowserRouter,
  Navigate,
  Outlet,
  Route,
  Routes,
} from 'react-router-dom'

import { LoginPage } from '../../features/auth/LoginPage'
import { RegisterPage } from '../../features/auth/RegisterPage'
import { DashboardPage } from '../../features/dashboard/DashboardPage'
import TicketsPage from '../../features/tickets/TicketsPage'
import { AppLayout } from '../../components/layout/AppLayout'
import { useAuthStore } from '../../stores/authStore'
import TicketDetailsPage from '../../features/tickets/TicketDetailsPage'
import UsersPage from '../../features/users/UsersPage'

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
        {/* Rotas públicas */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Rotas protegidas */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />

            <Route path="/tickets" element={<TicketsPage />} />
            <Route
              path="/tickets/:id"
              element={<TicketDetailsPage />}
            />

            <Route
              path="/triage"
              element={<PlaceholderPage title="Triagem IA" />}
            />

            <Route path="/users" element={<UsersPage />} />
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
