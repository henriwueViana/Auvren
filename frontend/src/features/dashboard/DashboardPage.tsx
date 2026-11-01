
import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  Ticket,
} from 'lucide-react'

import { useTickets } from '../tickets/hooks/useTickets'
import { useAuthStore } from '../../stores/authStore'

export function DashboardPage() {
  const user = useAuthStore((state) => state.user)
  const { data: tickets = [], isPending, isError, refetch } = useTickets()

  const total = tickets.length
  const open = tickets.filter((ticket) => ticket.status === 'open').length
  const inProgress = tickets.filter(
    (ticket) => ticket.status === 'in_progress'
  ).length
  const resolved = tickets.filter(
    (ticket) => ticket.status === 'resolved'
  ).length

  const stats = [
    { label: 'Total de chamados', value: total, icon: Ticket },
    { label: 'Abertos', value: open, icon: AlertCircle },
    { label: 'Em andamento', value: inProgress, icon: Clock3 },
    { label: 'Resolvidos', value: resolved, icon: CheckCircle2 },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">
          Visão geral
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Bem-vindo ao Auvren, {user?.name}. Acompanhe seus chamados.
        </p>
      </div>

      {isPending ? (
        <p className="text-slate-400">Carregando indicadores...</p>
      ) : isError ? (
        <div
          role="alert"
          className="rounded-xl border border-red-500/20 bg-red-500/10 p-5"
        >
          <p className="text-sm text-red-300">
            Não foi possível carregar os chamados.
          </p>
          <button
            type="button"
            onClick={() => void refetch()}
            className="mt-3 text-sm font-medium text-blue-400 hover:text-blue-300"
          >
            Tentar novamente
          </button>
        </div>
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map(({ label, value, icon: Icon }) => (
            <div
              key={label}
              className="rounded-2xl border border-slate-800 bg-[#101a2e] p-6"
            >
              <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
                <Icon size={21} />
              </div>

              <p className="text-sm text-slate-400">{label}</p>
              <p className="mt-2 text-3xl font-bold tracking-tight">
                {value}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
