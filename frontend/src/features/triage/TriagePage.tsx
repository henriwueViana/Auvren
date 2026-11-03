
import { useState } from 'react'
import { AxiosError } from 'axios'
import {
  BrainCircuit,
  Check,
  LoaderCircle,
  X,
} from 'lucide-react'

import { useTickets } from '../tickets/hooks/useTickets'
import {
  useTicketTriages,
  useCreateTriage,
  useReviewTriage,
} from './hooks/useTriage'

import type { TicketTriage } from '../../types/triage'

const categoryLabels: Record<string, string> = {
  hardware: 'Hardware',
  software: 'Software',
  network: 'Rede',
  access: 'Acesso',
  other: 'Outros',
}

const priorityLabels: Record<string, string> = {
  low: 'Baixa',
  medium: 'Média',
  high: 'Alta',
  critical: 'Crítica',
}

const reviewLabels: Record<string, string> = {
  pending: 'Pendente',
  accepted: 'Aceita',
  rejected: 'Rejeitada',
}

function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const status = error.response?.status

    if (status === 401) return 'Sua sessão expirou. Faça login novamente.'
    if (status === 403) return 'Você não possui permissão para esta operação.'
    if (status === 404) return 'Chamado ou análise não encontrado.'
    if (status === 409) return 'Esta análise não pode mais ser revisada.'
    if (status === 502) return 'A IA retornou uma resposta inválida.'
    if (status === 503) return 'O serviço de IA está indisponível no momento.'
  }

  return 'Não foi possível concluir a operação. Tente novamente.'
}

function TriageCard({
  triage,
  onReview,
  reviewing,
}: {
  triage: TicketTriage
  onReview: (triageId: number, status: 'accepted' | 'rejected') => void
  reviewing: boolean
}) {
  return (
    <article className="space-y-4 rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="text-xs text-slate-400">
          {new Date(triage.created_at).toLocaleString('pt-BR')}
        </span>

        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
          {reviewLabels[triage.review_status] ?? triage.review_status}
        </span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs text-slate-400">Categoria sugerida</p>
          <p className="mt-1 font-semibold text-white">
            {categoryLabels[triage.suggested_category]}
          </p>
        </div>

        <div>
          <p className="text-xs text-slate-400">Prioridade sugerida</p>
          <p className="mt-1 font-semibold text-white">
            {priorityLabels[triage.suggested_priority]}
          </p>
        </div>
      </div>

      <div>
        <p className="text-xs text-slate-400">Justificativa da IA</p>
        <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-200">
          {triage.justification}
        </p>
      </div>

      <p className="text-xs text-slate-500">
        Modelo: {triage.model}
      </p>

      {triage.review_status === 'pending' && (
        <div className="flex flex-wrap gap-3 border-t border-slate-800 pt-4">
          <button
            type="button"
            disabled={reviewing}
            onClick={() => onReview(triage.id, 'accepted')}
            className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
          >
            <Check size={17} />
            Aceitar sugestão
          </button>

          <button
            type="button"
            disabled={reviewing}
            onClick={() => onReview(triage.id, 'rejected')}
            className="flex items-center gap-2 rounded-lg border border-red-800 px-4 py-2 text-sm text-red-400 hover:bg-red-950/40 disabled:opacity-50"
          >
            <X size={17} />
            Rejeitar
          </button>
        </div>
      )}
    </article>
  )
}

export default function TriagePage() {
  const [ticketId, setTicketId] = useState(0)
  const [message, setMessage] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const ticketsQuery = useTickets()
  const triagesQuery = useTicketTriages(ticketId)
  const createTriage = useCreateTriage(ticketId)
  const reviewTriage = useReviewTriage(ticketId)

  const tickets = ticketsQuery.data ?? []
  const triages = triagesQuery.data ?? []

  async function handleCreate() {
    setMessage('')
    setErrorMessage('')

    try {
      await createTriage.mutateAsync()
      setMessage('Análise gerada com sucesso!')
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
    }
  }

  async function handleReview(
    triageId: number,
    status: 'accepted' | 'rejected'
  ) {
    setMessage('')
    setErrorMessage('')

    try {
      await reviewTriage.mutateAsync({
        triageId,
        data: { review_status: status },
      })

      setMessage(
        status === 'accepted'
          ? 'Sugestão aceita com sucesso!'
          : 'Sugestão rejeitada com sucesso!'
      )
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <BrainCircuit size={28} className="text-indigo-400" />
          <h1 className="text-2xl font-semibold text-white">
            Triagem IA
          </h1>
        </div>

        <p className="mt-2 text-sm text-slate-400">
          Classifique chamados com inteligência artificial e revise as sugestões.
        </p>
      </div>

      <section className="space-y-4 rounded-xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="font-semibold text-white">
          Selecionar chamado
        </h2>

        {ticketsQuery.isLoading ? (
          <p className="text-sm text-slate-400">
            Carregando chamados...
          </p>
        ) : ticketsQuery.isError ? (
          <p role="alert" className="text-sm text-red-400">
            Não foi possível carregar os chamados.
          </p>
        ) : (
          <select
            value={ticketId}
            onChange={(event) => {
              setTicketId(Number(event.target.value))
              setMessage('')
              setErrorMessage('')
            }}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-indigo-500"
          >
            <option value={0}>Selecione um chamado</option>

            {tickets.map((ticket) => (
              <option key={ticket.id} value={ticket.id}>
                #{ticket.id} — {ticket.title}
              </option>
            ))}
          </select>
        )}

        <button
          type="button"
          disabled={ticketId === 0 || createTriage.isPending}
          onClick={() => void handleCreate()}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {createTriage.isPending ? (
            <LoaderCircle size={18} className="animate-spin" />
          ) : (
            <BrainCircuit size={18} />
          )}

          {createTriage.isPending ? 'Analisando...' : 'Analisar com IA'}
        </button>
      </section>

      {message && (
        <p role="status" className="rounded-lg border border-emerald-800 bg-emerald-950/30 p-4 text-sm text-emerald-400">
          {message}
        </p>
      )}

      {errorMessage && (
        <p role="alert" className="rounded-lg border border-red-800 bg-red-950/30 p-4 text-sm text-red-400">
          {errorMessage}
        </p>
      )}

      {ticketId > 0 && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-white">
            Histórico de análises
          </h2>

          {triagesQuery.isLoading ? (
            <p className="text-sm text-slate-400">
              Carregando análises...
            </p>
          ) : triagesQuery.isError ? (
            <p role="alert" className="text-sm text-red-400">
              Não foi possível carregar as análises.
            </p>
          ) : triages.length === 0 ? (
            <p className="rounded-xl border border-slate-800 bg-slate-900 p-6 text-sm text-slate-400">
              Este chamado ainda não possui análises de IA.
            </p>
          ) : (
            triages.map((triage) => (
              <TriageCard
                key={triage.id}
                triage={triage}
                reviewing={reviewTriage.isPending}
                onReview={(id, status) => void handleReview(id, status)}
              />
            ))
          )}
        </section>
      )}
    </div>
  )
}
