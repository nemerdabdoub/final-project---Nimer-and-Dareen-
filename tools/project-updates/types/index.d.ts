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

export type FalseAlarm = {
  set: string
  method: string
  fa10: string
  fa035: string
  wrong10: string
  noUser: number
  from: string
}

export type Snapshot = {
  commits: Commit[]
  local: LocalFile[]
  falseAlarms: FalseAlarm[]
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
