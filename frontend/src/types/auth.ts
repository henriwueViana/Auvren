
export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  organization_name: string
  name: string
  email: string
  password: string
}

export interface User {
  id: number
  organization_id: number
  name: string
  email: string
  role: string
  is_active: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}
