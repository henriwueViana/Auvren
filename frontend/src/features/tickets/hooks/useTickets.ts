
import { useQuery } from '@tanstack/react-query'
import { ticketApi } from '../api/ticketApi'

export function useTickets() {
  return useQuery({
    queryKey: ['tickets'],
    queryFn: ticketApi.list,
    staleTime: 60_000,
    retry: 1,
  })
}
