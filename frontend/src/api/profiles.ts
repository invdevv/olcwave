import api from './client'
import type { Profile } from '../types'

export const profilesApi = {
  create: (profile: Omit<Profile, 'id'>) =>
    api.post<string>('/profiles/', profile),

  getByTag: (tag: string) =>
    api.get<Profile>('/profiles/', { params: { tag } }),

  update: (tag: string, name: string, profile: string) =>
    api.put('/profiles/', null, { params: { tag, name, profile } }),

  delete: (tag: string) =>
    api.delete('/profiles/', { params: { tag } }),
}
