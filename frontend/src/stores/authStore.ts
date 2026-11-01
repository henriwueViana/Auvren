
import { create } from 'zustand'
import type { User } from '../types/auth'

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean

  setSession: (user: User, accessToken: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,

  setSession: (user, accessToken) =>
    set({
      user,
      accessToken,
      isAuthenticated: true,
    }),

  logout: () =>
    set({
      user: null,
      accessToken: null,
      isAuthenticated: false,
    }),
}))
