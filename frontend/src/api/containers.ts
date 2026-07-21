import api from './client'
import type { Container, ContainerLogs, ContainerConfig } from '../types'

export const containersApi = {
  getAll: () =>
    api.get<Container[]>('/containers/all'),

  run: (name: string) =>
    api.post<string>('/containers/run', null, { params: { name } }),

  stop: (name: string) =>
    api.post<string>('/containers/stop', null, { params: { name } }),

  restart: (name: string) =>
    api.post<string>('/containers/restart', null, { params: { name } }),

  remove: (name: string) =>
    api.delete('/containers/', { params: { name } }),

  logs: (name: string) =>
    api.get<ContainerLogs>('/containers/logs', { params: { name } }),

  getConfig: (name: string) =>
    api.get<ContainerConfig>('/containers/config', { params: { name } }),
}
