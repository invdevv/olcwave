import api from './client'
import type { User, TrafficInfo, SyncResult } from '../types'

export const usersApi = {
  getAll: () =>
    api.get<User[]>('/users/all', { params: {} }),

  getByShortUuid: (shortUuid: string) =>
    api.get<User>('/users/', { params: { short_uuid: shortUuid } }),

  create: (data: Partial<User> & { short_uuid: string; expires_at: string }) =>
    api.post<User>('/users/', data),

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

  getTraffic: (shortUuid: string) =>
    api.get<TrafficInfo>('/users/traffic', { params: { short_uuid: shortUuid } }),

  setTrafficLimit: (shortUuid: string, trafficLimitBytes: number) =>
    api.patch<TrafficInfo>('/users/traffic', { traffic_limit_bytes: trafficLimitBytes }, {
      params: { short_uuid: shortUuid },
    }),

  resetTraffic: (shortUuid: string) =>
    api.post<TrafficInfo>('/users/traffic/reset', null, {
      params: { short_uuid: shortUuid },
    }),

  syncWithRemnawave: () =>
    api.post<SyncResult>('/users/sync'),
}
