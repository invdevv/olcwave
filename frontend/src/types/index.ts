export interface LoginPayload {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface User {
  short_uuid: string
  created_at: string
  expires_at: string
}

export interface Profile {
  name: string
  tag: string
  profile: string
}

export interface SubscriptionLocation {
  storage_id: string
  name: string
  endpoint: {
    room_id: string
    key: string
  }
  auth_provider: string
  transport: Record<string, unknown>
}

export interface SubscriptionBundle {
  version: number
  active_location_id: string
  locations: SubscriptionLocation[]
}

export interface Container {
  id: string
  name: string
  user_id: string
  config_tag: string
  status: string
  created: string
  image: string
}

export interface ContainerLogs {
  name: string
  logs: string
}

export interface ContainerConfig {
  name: string
  config: string
}

export interface ApiError {
  detail: string
}

export interface AuthState {
  token: string | null
  isAuthenticated: boolean
  login: (payload: LoginPayload) => Promise<void>
  logout: () => void
  setToken: (token: string) => void
}
