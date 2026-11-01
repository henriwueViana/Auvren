
import { api } from '../../../lib/api'
import type { AuthResponse, LoginRequest, RegisterRequest } from '../../../types/auth'

export const authApi = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(
      '/api/v1/auth/login',
      credentials,
    )

    return response.data
  },

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(
      '/api/v1/auth/register',
      data,
    )

    return response.data
  },
}
