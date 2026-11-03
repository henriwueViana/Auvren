
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import { triageApi } from '../api/triageApi'
import type { TriageReview } from '../../../types/triage'

export function useTicketTriages(ticketId: number) {
  return useQuery({
    queryKey: ['triages', ticketId],
    queryFn: () => triageApi.list(ticketId),
    enabled: ticketId > 0,
    staleTime: 30_000,
    retry: 1,
  })
}

export function useCreateTriage(ticketId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => triageApi.create(ticketId),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['triages', ticketId],
      })

      await queryClient.invalidateQueries({
        queryKey: ['tickets'],
      })
    },
  })
}

interface ReviewTriageVariables {
  triageId: number
  data: TriageReview
}

export function useReviewTriage(ticketId: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ triageId, data }: ReviewTriageVariables) =>
      triageApi.review(ticketId, triageId, data),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['triages', ticketId],
      })

      await queryClient.invalidateQueries({
        queryKey: ['tickets'],
      })
    },
  })
}
