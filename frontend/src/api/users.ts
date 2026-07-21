import api from './client'
import type { User } from '../types'

export const usersApi = {
  getAll: () =>
    api.get<User[]>('/users/all', { params: { tag: '' } }),

  getByShortUuid: (shortUuid: string) =>
    api.get<User>('/users/', { params: { short_uuid: shortUuid } }),

  update: (shortUuid: string, expiresAt: string) =>
    api<boolean>('/users/', {
      params: { short_uuid: shortUuid, expires_at: expiresAt },
      method: 'PUT',
    }),

  delete: (shortUuid: string) =>
    api<boolean>('/users/', {
      params: { short_uuid: shortUuid },
      method: 'DELETE',
    }),
}
