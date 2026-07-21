import api from './client'
import type { LoginPayload, TokenResponse } from '../types'

export const authApi = {
  login: (payload: LoginPayload) =>
    api.post<TokenResponse>('/auth/login', payload),
}
