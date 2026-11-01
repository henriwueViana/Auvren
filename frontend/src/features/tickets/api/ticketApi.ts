
import { api } from '../../../lib/api'
import type {
  Ticket,
  TicketCreate,
  TicketStatusUpdate,
} from '../../../types/ticket'

export const ticketApi = {
  async list(): Promise<Ticket[]> {
    const response = await api.get<Ticket[]>('/api/v1/tickets')
    return response.data
  },

  async getById(id: number): Promise<Ticket> {
    const response = await api.get<Ticket>(`/api/v1/tickets/${id}`)
    return response.data
  },

  async create(data: TicketCreate): Promise<Ticket> {
    const response = await api.post<Ticket>('/api/v1/tickets', data)
    return response.data
  },

  async updateStatus(
    id: number,
    data: TicketStatusUpdate,
  ): Promise<Ticket> {
    const response = await api.patch<Ticket>(
      `/api/v1/tickets/${id}/status`,
      data,
    )
    return response.data
  },
}
