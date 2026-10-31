// src/api/tickets.ts
import { apiClient } from './client';
import type { Ticket } from '../types/ticket';

interface ListTicketsParams {
  page?: number;
  limit?: number;
  status?: string;
  priority?: string;
  category?: string;
  search?: string;
}

export const getTickets = async (params?: ListTicketsParams): Promise<Ticket[]> => {
  const response = await apiClient.get<Ticket[]>('/tickets', { params });
  return response.data;
};