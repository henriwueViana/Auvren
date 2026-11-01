
import {
  BrainCircuit,
  LayoutDashboard,
  LogOut,
  Ticket,
  Users,
  Layers3,
} from 'lucide-react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../stores/authStore'

const navigation = [
  { label: 'Visão geral', path: '/dashboard', icon: LayoutDashboard },
  { label: 'Chamados', path: '/tickets', icon: Ticket },
  { label: 'Triagem IA', path: '/triage', icon: BrainCircuit },
  { label: 'Equipe', path: '/users', icon: Users },
]

export function Sidebar() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-slate-800 bg-[#0b1120] p-5 text-slate-200">
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
          <Layers3 size={23} />
        </div>

        <span className="text-xl font-bold tracking-tight">
          Auvren<span className="text-blue-400">.</span>
        </span>
      </div>

      <nav className="flex flex-1 flex-col gap-2">
        {navigation.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                isActive
                  ? 'bg-blue-500/10 text-blue-400'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
              }`
            }
          >
            <Icon size={19} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-slate-800 pt-5">
        <div className="mb-4 px-3">
          <p className="truncate text-sm font-semibold">
            {user?.name}
          </p>
          <p className="truncate text-xs text-slate-500">
            {user?.email}
          </p>
        </div>

        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm text-slate-400 transition hover:bg-red-500/10 hover:text-red-400"
        >
          <LogOut size={19} />
          Sair
        </button>
      </div>
    </aside>
  )
}
