export type Commit = {
  sha: string
  who: string
  when: string
  subject: string
  files: string[]
}

export type LocalFile = {
  path: string
  status: string
  modified: string
}

export type Snapshot = {
  commits: Commit[]
  local: LocalFile[]
  ahead: number
  behind: number
  checkedAt: string
  error?: string
}

declare module 'claude-code' {
  interface PluginState {
    'project-updates': { snapshot: Shaped<Snapshot> }
  }
}
