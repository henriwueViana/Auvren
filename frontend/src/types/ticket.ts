
export type TicketStatus =
  | 'open'
  | 'in_progress'
  | 'resolved'

export type TicketPriority =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical'

export type TicketCategory =
  | 'hardware'
  | 'software'
  | 'network'
  | 'access'
  | 'other'

export interface Ticket {
  id: number
  title: string
  description: string
  status: TicketStatus
  priority: TicketPriority
  category: TicketCategory
  created_at: string
}

export interface TicketCreate {
  title: string
  description: string
  priority?: TicketPriority
  category?: TicketCategory
}

export interface TicketStatusUpdate {
  status: TicketStatus
}
