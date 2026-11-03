
import { useState, type FormEvent } from 'react'
import { AxiosError } from 'axios'
import { Plus, X } from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'

import { useCreateTicket, useTickets } from './hooks/useTickets'
import type {
  TicketCategory,
  TicketCreate,
  TicketPriority,
  TicketStatus,
} from '../../types/ticket'

const statusLabels: Record<TicketStatus, string> = {
  open: 'Aberto',
  in_progress: 'Em andamento',
  resolved: 'Resolvido',
}

const priorityLabels: Record<TicketPriority, string> = {
  low: 'Baixa',
  medium: 'Média',
  high: 'Alta',
  critical: 'Crítica',
}

const categoryLabels: Record<TicketCategory, string> = {
  hardware: 'Hardware',
  software: 'Software',
  network: 'Rede',
  access: 'Acesso',
  other: 'Outros',
}

const initialForm: TicketCreate = {
  title: '',
  description: '',
  priority: 'medium',
  category: 'other',
}

export default function TicketsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { data: tickets = [], isLoading, isError, refetch } = useTickets()
  const createTicket = useCreateTicket()

  const [showForm, setShowForm] = useState(
  () => searchParams.get('new') === '1'
)
  const [form, setForm] = useState<TicketCreate>({ ...initialForm })
  const [formError, setFormError] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError('')

    try {
      await createTicket.mutateAsync(form)
      setForm({ ...initialForm })
      setShowForm(false)
      if (searchParams.has('new')) {
  setSearchParams(
    (previous) => {
      const next = new URLSearchParams(previous)
      next.delete('new')
      return next
    },
    { replace: true }
  )
}
    } catch (error) {
      if (error instanceof AxiosError) {
        if (error.response?.status === 422) {
          setFormError('Verifique os dados informados.')
        } else if (error.response?.status === 401) {
          setFormError('Sua sessão não é válida. Faça login novamente.')
        } else {
          setFormError('Não foi possível criar o chamado.')
        }
      } else {
        setFormError('Ocorreu um erro inesperado.')
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            Chamados
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Gerencie os chamados de suporte da sua organização.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setFormError('')
            setShowForm((previous) => !previous)
          }}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
        >
          {showForm ? <X size={18} /> : <Plus size={18} />}
          {showForm ? 'Cancelar' : 'Novo chamado'}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={(event) => void handleSubmit(event)}
          className="space-y-5 rounded-xl border border-slate-800 bg-slate-900 p-6"
        >
          <div>
            <h2 className="text-lg font-semibold text-white">
              Criar chamado
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Descreva o problema para registrar um novo ticket.
            </p>
          </div>

          <div>
            <label htmlFor="ticket-title" className="mb-2 block text-sm text-slate-300">
              Título
            </label>
            <input
              id="ticket-title"
              type="text"
              required
              minLength={5}
              maxLength={200}
              value={form.title}
              onChange={(event) =>
                setForm({ ...form, title: event.target.value })
              }
              placeholder="Ex.: Não consigo acessar o sistema"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="ticket-description" className="mb-2 block text-sm text-slate-300">
              Descrição
            </label>
            <textarea
              id="ticket-description"
              required
              minLength={10}
              rows={4}
              value={form.description}
              onChange={(event) =>
                setForm({ ...form, description: event.target.value })
              }
              placeholder="Descreva o problema com detalhes..."
              className="w-full resize-y rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="ticket-priority" className="mb-2 block text-sm text-slate-300">
                Prioridade
              </label>
              <select
                id="ticket-priority"
                value={form.priority}
                onChange={(event) =>
                  setForm({
                    ...form,
                    priority: event.target.value as TicketPriority,
                  })
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-indigo-500"
              >
                {Object.entries(priorityLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="ticket-category" className="mb-2 block text-sm text-slate-300">
                Categoria
              </label>
              <select
                id="ticket-category"
                value={form.category}
                onChange={(event) =>
                  setForm({
                    ...form,
                    category: event.target.value as TicketCategory,
                  })
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-indigo-500"
              >
                {Object.entries(categoryLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
          </div>

          {formError && (
            <p role="alert" className="text-sm text-red-400">
              {formError}
            </p>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={createTicket.isPending}
              className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {createTicket.isPending ? 'Criando...' : 'Criar chamado'}
            </button>
          </div>
        </form>
      )}

      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
        {isLoading ? (
          <p className="p-6 text-slate-400">
            Carregando chamados...
          </p>
        ) : isError ? (
          <div className="space-y-3 p-6">
            <p className="text-red-400">
              Não foi possível carregar os chamados.
            </p>
            <button
              type="button"
              onClick={() => void refetch()}
              className="rounded-lg bg-slate-700 px-4 py-2 text-sm text-white hover:bg-slate-600"
            >
              Tentar novamente
            </button>
          </div>
        ) : tickets.length === 0 ? (
          <div className="p-10 text-center">
            <p className="font-medium text-white">
              Nenhum chamado encontrado
            </p>
            <p className="mt-2 text-sm text-slate-400">
              Clique em Novo chamado para registrar o primeiro ticket.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-800 bg-slate-950/50 text-slate-400">
                <tr>
                  <th className="px-5 py-4 font-medium">Chamado</th>
                  <th className="px-5 py-4 font-medium">Categoria</th>
                  <th className="px-5 py-4 font-medium">Prioridade</th>
                  <th className="px-5 py-4 font-medium">Status</th>
                  <th className="px-5 py-4 font-medium">Criado em</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {tickets.map((ticket) => (
                  <tr
                    key={ticket.id}
                    className="transition-colors hover:bg-slate-800/50"
                  >
                    <td className="px-5 py-4">
                      <Link
                        to={`/tickets/${ticket.id}`}
                        className="font-medium text-white transition-colors hover:text-indigo-400"
                      >
                        {ticket.title}
                      </Link>
                      <p className="mt-1 text-xs text-slate-500">
                        #{ticket.id}
                      </p>
                    </td>

                    <td className="px-5 py-4 text-slate-300">
                      {categoryLabels[ticket.category]}
                    </td>

                    <td className="px-5 py-4">
                      <span className={
                        ticket.priority === 'critical'
                          ? 'text-red-400'
                          : ticket.priority === 'high'
                            ? 'text-orange-400'
                            : ticket.priority === 'medium'
                              ? 'text-amber-400'
                              : 'text-emerald-400'
                      }>
                        {priorityLabels[ticket.priority]}
                      </span>
                    </td>

                    <td className="px-5 py-4">
                      <span className={
                        ticket.status === 'resolved'
                          ? 'text-emerald-400'
                          : ticket.status === 'in_progress'
                            ? 'text-blue-400'
                            : 'text-amber-400'
                      }>
                        {statusLabels[ticket.status]}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-slate-400">
                      {new Date(ticket.created_at).toLocaleDateString('pt-BR')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
