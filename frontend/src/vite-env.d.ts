/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  /** Subscription URL template. `{uuid}` is replaced with the user's short UUID. */
  readonly VITE_SUB_URL_TEMPLATE?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
