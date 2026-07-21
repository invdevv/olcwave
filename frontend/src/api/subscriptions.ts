import api from './client'
import type { SubscriptionBundle } from '../types'

export const subscriptionsApi = {
  getBundle: (shortUuid: string) =>
    api.get<SubscriptionBundle>(`/sub/${shortUuid}`),
}
