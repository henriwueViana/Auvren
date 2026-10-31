// src/types/ticket.ts
export type TicketStatus = 'open' | 'in_progress' | 'resolved';
export type TicketPriority = 'low' | 'medium' | 'high' | 'critical';
export type TicketCategory = 'hardware' | 'software' | 'network' | 'access' | 'other';

export interface Ticket {
  id: number;
  title: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  category: TicketCategory;
  organization_id: number;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: 'admin' | 'agent';
  organization_id: number;
}