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

export type PartnerFile = {
  path: string
  when: string
  count?: number
}

export type LabReport = {
  lab: string
  status: string
  next?: string
  pdf?: string // full path
  pdfTime?: string
}

export type ActivityItem = {
  at: number   // ms since epoch
  text: string
  done?: boolean
  ms?: number  // how long it took
}

export type Activity = {
  now: string          // what Claude is doing right now
  since: number        // when "now" started (ms)
  busy: boolean
  recent: ActivityItem[] // newest first
  tools: number        // tool calls this session
}

export type Snapshot = {
  labs?: LabReport[]
  commits: Commit[]
  local: LocalFile[]
  falseAlarms: FalseAlarm[]
  dareenFiles?: PartnerFile[]
  syncNote?: string
  ahead: number
  behind: number
  checkedAt: string
  error?: string
}

declare module 'claude-code' {
  interface PluginState {
    'project-updates': { snapshot: Shaped<Snapshot>; improveDone: Shaped<string[]>; activity: Shaped<Activity> }
  }
}
