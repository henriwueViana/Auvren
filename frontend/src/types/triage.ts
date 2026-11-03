
export type TriageCategory =
  | 'hardware'
  | 'software'
  | 'network'
  | 'access'
  | 'other'

export type TriagePriority =
  | 'low'
  | 'medium'
  | 'high'
  | 'critical'

export type TriageReviewStatus =
  | 'pending'
  | 'accepted'
  | 'rejected'

export interface TicketTriage {
  id: number
  ticket_id: number
  suggested_category: TriageCategory
  suggested_priority: TriagePriority
  justification: string
  model: string
  review_status: TriageReviewStatus
  reviewed_by: number | null
  created_at: string
  reviewed_at: string | null
}

export interface TriageReview {
  review_status: 'accepted' | 'rejected'
}
