import api from './client'

export interface RuntimeSettings {
  sub_name: string
  default_traffic_limit: number
  traffic_collect_interval: number
}

export const settingsApi = {
  get: () =>
    api.get<RuntimeSettings>('/settings/'),

  update: (data: RuntimeSettings) =>
    api.put<RuntimeSettings>('/settings/', data),
}
