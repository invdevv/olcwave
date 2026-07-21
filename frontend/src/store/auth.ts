import { create } from 'zustand'
import type { AuthState, LoginPayload } from '../types'
import { authApi } from '../api/auth'

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (payload: LoginPayload) => {
    const { data } = await authApi.login(payload)
    localStorage.setItem('token', data.access_token)
    set({ token: data.access_token, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ token: null, isAuthenticated: false })
    window.location.href = '/login'
  },

  setToken: (token: string) => {
    localStorage.setItem('token', token)
    set({ token, isAuthenticated: true })
  },
}))
