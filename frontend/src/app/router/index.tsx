
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
import TicketDetailsPage from '../../features/tickets/TicketDetailsPage'
import UsersPage from '../../features/users/UsersPage'
import TriagePage from '../../features/triage/TriagePage'

import { AppLayout } from '../../components/layout/AppLayout'
import { useAuthStore } from '../../stores/authStore'

type UserRole = 'admin' | 'agent' | 'requester'

function ProtectedRoute() {
  const isAuthenticated = useAuthStore(
    (state) => state.isAuthenticated
  )
  const user = useAuthStore((state) => state.user)

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

function RoleRoute({
  allowedRoles,
}: {
  allowedRoles: UserRole[]
}) {
  const user = useAuthStore((state) => state.user)

  if (!user || !allowedRoles.includes(user.role as UserRole)) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route
              path="/dashboard"
              element={<DashboardPage />}
            />

            <Route
              path="/tickets"
              element={<TicketsPage />}
            />

            <Route
              path="/tickets/:id"
              element={<TicketDetailsPage />}
            />

            {/* Administradores e agentes */}
            <Route
              element={
                <RoleRoute
                  allowedRoles={['admin', 'agent']}
                />
              }
            >
              <Route
                path="/triage"
                element={<TriagePage />}
              />
            </Route>

            {/* Apenas administradores */}
            <Route
              element={
                <RoleRoute allowedRoles={['admin']} />
              }
            >
              <Route
                path="/users"
                element={<UsersPage />}
              />
            </Route>
          </Route>
        </Route>

        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />
      </Routes>
    </BrowserRouter>
  )
}
