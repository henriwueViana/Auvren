
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import { ticketApi } from '../api/ticketApi'
import type { TicketStatusUpdate } from '../../../types/ticket'

export function useTickets() {
  return useQuery({
    queryKey: ['tickets'],
    queryFn: ticketApi.list,
    staleTime: 60_000,
    retry: 1,
  })
}

export function useAllTickets() {
  return useQuery({
    queryKey: ['tickets', 'all'],
    queryFn: ticketApi.listAll,
    staleTime: 60_000,
    retry: 1,
  })
}

export function useCreateTicket() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ticketApi.create,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['tickets'],
      })
    },
  })
}


export function useUpdateTicketStatus(ticketId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: TicketStatusUpdate) =>
      ticketApi.updateStatus(ticketId, data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['tickets'],
      })
    },
  })
}


export function useTicketHistory(ticketId: number) {
  return useQuery({
    queryKey: ['tickets', ticketId, 'history'],
    queryFn: () => ticketApi.getHistory(ticketId),
    enabled: Number.isInteger(ticketId) && ticketId > 0,
    staleTime: 30_000,
    retry: 1,
  })
}
