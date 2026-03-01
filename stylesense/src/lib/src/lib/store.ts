import { create } from 'zustand'
import { User } from './types'

interface AuthStore {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
  setAuth: (user: User, token: string) => void
  clearAuth: () => void
  setError: (error: string | null) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isLoading: false,
  error: null,
  setAuth: (user, token) => {
    localStorage.setItem('token', token)
    set({ user, token, error: null })
  },
  clearAuth: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null })
  },
  setError: (error) => set({ error }),
  setLoading: (loading) => set({ isLoading: loading }),
}))