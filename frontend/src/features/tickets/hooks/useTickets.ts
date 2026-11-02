
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import { ticketApi } from '../api/ticketApi'

export function useTickets() {
  return useQuery({
    queryKey: ['tickets'],
    queryFn: ticketApi.list,
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
