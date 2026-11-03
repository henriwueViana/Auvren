
import { api } from '../../../lib/api'

import type {
  TicketTriage,
  TriageReview,
} from '../../../types/triage'

export const triageApi = {
  async create(ticketId: number): Promise<TicketTriage> {
    const response = await api.post<TicketTriage>(
      `/api/v1/tickets/${ticketId}/triage`
    )

    return response.data
  },

  async list(ticketId: number): Promise<TicketTriage[]> {
    const response = await api.get<TicketTriage[]>(
      `/api/v1/tickets/${ticketId}/triages`
    )

    return response.data
  },

  async review(
    ticketId: number,
    triageId: number,
    data: TriageReview
  ): Promise<TicketTriage> {
    const response = await api.patch<TicketTriage>(
      `/api/v1/tickets/${ticketId}/triages/${triageId}/review`,
      data
    )

    return response.data
  },
}
