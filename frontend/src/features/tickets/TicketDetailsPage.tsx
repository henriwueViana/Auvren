
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AxiosError } from 'axios'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, CalendarDays, Tag, History } from 'lucide-react'

import { ticketApi } from './api/ticketApi'
import {
  useTicketHistory,
  useUpdateTicketStatus,
} from './hooks/useTickets'

import type {
  TicketCategory,
  TicketPriority,
  TicketStatus,
  TicketStatusUpdate,
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

const statusColors: Record<TicketStatus, string> = {
  open: 'text-amber-400',
  in_progress: 'text-blue-400',
  resolved: 'text-emerald-400',
}

export default function TicketDetailsPage() {
  const { id } = useParams()

  const ticketId = Number(id)
  const validId = Number.isInteger(ticketId) && ticketId > 0

  const [statusError, setStatusError] = useState('')
  const [statusSuccess, setStatusSuccess] = useState('')

  const updateStatus = useUpdateTicketStatus(ticketId)

  const {
    data: ticket,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ['tickets', ticketId],
    queryFn: () => ticketApi.getById(ticketId),
    enabled: validId,
    retry: 1,
  })

  const {
    data: history = [],
    isLoading: historyLoading,
    isError: historyError,
    refetch: refetchHistory,
  } = useTicketHistory(ticketId)

  async function handleStatusChange(
    status: TicketStatusUpdate['status']
  ) {
    setStatusError('')
    setStatusSuccess('')

    if (!ticket || status === ticket.status) {
      return
    }

    try {
      await updateStatus.mutateAsync({ status })

      setStatusSuccess('Status atualizado com sucesso!')
    } catch (error) {
      if (error instanceof AxiosError) {
        if (error.response?.status === 403) {
          setStatusError(
            'Você não tem permissão para alterar este chamado.'
          )
        } else if (error.response?.status === 401) {
          setStatusError(
            'Sua sessão expirou. Faça login novamente.'
          )
        } else {
          setStatusError(
            'Não foi possível atualizar o status.'
          )
        }
      } else {
        setStatusError(
          'Ocorreu um erro inesperado ao atualizar o status.'
        )
      }
    }
  }

  if (!validId) {
    return (
      <div className="space-y-4">
        <p className="text-red-400">
          Identificador de chamado inválido.
        </p>

        <Link
          to="/tickets"
          className="text-sm text-indigo-400 hover:text-indigo-300"
        >
          Voltar aos chamados
        </Link>
      </div>
    )
  }

  if (isLoading) {
    return (
      <p className="text-slate-400">
        Carregando detalhes do chamado...
      </p>
    )
  }

  if (isError || !ticket) {
    return (
      <div className="space-y-4">
        <p className="text-red-400">
          Não foi possível carregar o chamado.
        </p>

        <button
          type="button"
          onClick={() => void refetch()}
          className="rounded-lg bg-slate-700 px-4 py-2 text-sm text-white hover:bg-slate-600"
        >
          Tentar novamente
        </button>

        <Link
          to="/tickets"
          className="block text-sm text-indigo-400 hover:text-indigo-300"
        >
          Voltar aos chamados
        </Link>
      </div>
    )
  }

  const sortedHistory = [...history].sort(
    (a, b) =>
      new Date(b.changed_at).getTime() -
      new Date(a.changed_at).getTime()
  )

  return (
    <div className="space-y-6">
      {/* Navegação */}
      <Link
        to="/tickets"
        className="inline-flex items-center gap-2 text-sm text-slate-400 transition-colors hover:text-white"
      >
        <ArrowLeft size={16} />
        Voltar aos chamados
      </Link>

      {/* Cabeçalho */}
      <div>
        <p className="text-sm font-medium text-indigo-400">
          Chamado #{ticket.id}
        </p>

        <h1 className="mt-2 text-2xl font-semibold text-white">
          {ticket.title}
        </h1>
      </div>

      {/* Informações principais */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Descrição */}
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-white">
            Descrição do problema
          </h2>

          <p className="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-300">
            {ticket.description}
          </p>
        </section>

        {/* Informações do chamado */}
        <section className="space-y-5 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-lg font-semibold text-white">
            Informações
          </h2>

          {/* Status */}
          <div>
            <label
              htmlFor="ticket-status"
              className="mb-2 block text-xs text-slate-500"
            >
              Status
            </label>

            <select
              id="ticket-status"
              value={ticket.status}
              disabled={updateStatus.isPending}
              onChange={(event) => {
                void handleStatusChange(
                  event.target.value as TicketStatus
                )
              }}
              className={`w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm font-medium outline-none focus:border-indigo-500 disabled:cursor-not-allowed disabled:opacity-50 ${statusColors[ticket.status]}`}
            >
              {Object.entries(statusLabels).map(
                ([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                )
              )}
            </select>

            {updateStatus.isPending && (
              <p className="mt-2 text-xs text-slate-400">
                Atualizando status...
              </p>
            )}

            {statusError && (
              <p
                role="alert"
                className="mt-2 text-xs text-red-400"
              >
                {statusError}
              </p>
            )}

            {statusSuccess && (
              <p
                role="status"
                className="mt-2 text-xs text-emerald-400"
              >
                {statusSuccess}
              </p>
            )}
          </div>

          {/* Prioridade */}
          <div>
            <p className="text-xs text-slate-500">
              Prioridade
            </p>

            <p className="mt-1 text-sm font-medium text-white">
              {priorityLabels[ticket.priority]}
            </p>
          </div>

          {/* Categoria */}
          <div>
            <p className="flex items-center gap-2 text-xs text-slate-500">
              <Tag size={14} />
              Categoria
            </p>

            <p className="mt-1 text-sm font-medium text-white">
              {categoryLabels[ticket.category]}
            </p>
          </div>

          {/* Data de criação */}
          <div>
            <p className="flex items-center gap-2 text-xs text-slate-500">
              <CalendarDays size={14} />
              Criado em
            </p>

            <p className="mt-1 text-sm font-medium text-white">
              {new Date(ticket.created_at).toLocaleString(
                'pt-BR'
              )}
            </p>
          </div>
        </section>
      </div>

      {/* Histórico de alterações */}
      <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
        <div className="mb-6 flex items-start gap-3">
          <div className="rounded-lg bg-indigo-500/10 p-2.5">
            <History
              size={20}
              className="text-indigo-400"
            />
          </div>

          <div>
            <h2 className="text-lg font-semibold text-white">
              Histórico de alterações
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Acompanhe as mudanças de status deste chamado.
            </p>
          </div>
        </div>

        {historyLoading ? (
          <p className="text-sm text-slate-400">
            Carregando histórico...
          </p>
        ) : historyError ? (
          <div className="space-y-3">
            <p className="text-sm text-red-400">
              Não foi possível carregar o histórico.
            </p>

            <button
              type="button"
              onClick={() => void refetchHistory()}
              className="rounded-lg bg-slate-700 px-4 py-2 text-sm text-white hover:bg-slate-600"
            >
              Tentar novamente
            </button>
          </div>
        ) : sortedHistory.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-700 p-6 text-center">
            <History
              size={24}
              className="mx-auto text-slate-500"
            />

            <p className="mt-3 text-sm text-slate-400">
              Nenhuma alteração de status registrada.
            </p>
          </div>
        ) : (
          <ol className="relative ml-2 border-l border-slate-700">
            {sortedHistory.map((entry) => (
              <li
                key={entry.id}
                className="relative mb-7 ml-6 last:mb-0"
              >
                {/* Indicador da linha do tempo */}
                <span className="absolute -left-[31px] top-1 flex h-3 w-3 rounded-full border-2 border-slate-900 bg-indigo-500" />

                <p className="text-sm font-medium text-white">
                  Status alterado
                </p>

                <div className="mt-2 flex flex-wrap items-center gap-2 text-sm">
                  <span
                    className={
                      statusColors[entry.previous_status] ??
                      'text-slate-300'
                    }
                  >
                    {statusLabels[entry.previous_status] ??
                      entry.previous_status}
                  </span>

                  <span className="text-slate-500">
                    →
                  </span>

                  <span
                    className={
                      statusColors[entry.new_status] ??
                      'text-slate-300'
                    }
                  >
                    {statusLabels[entry.new_status] ??
                      entry.new_status}
                  </span>
                </div>

                <time
                  dateTime={entry.changed_at}
                  className="mt-2 block text-xs text-slate-500"
                >
                  {new Date(
                    entry.changed_at
                  ).toLocaleString('pt-BR')}
                </time>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  )
}
