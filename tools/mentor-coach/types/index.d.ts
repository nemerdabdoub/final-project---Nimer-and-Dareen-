export type Playbook = {
  id: string
  title: string
  when: string[]   // trigger words, lower case
  why: string
  steps: string[]
  asks: string[]   // what Gabi will ask
  traps: string[]
  done: string
}

export type Plan = {
  milestone: string
  due: string      // YYYY-MM-DD
  daysLeft: number
  next: string     // first open task
  done: number
  total: number
}

export type Book = {
  principles: string[]
  books: Playbook[]
  plan?: Plan
  loadedAt: string
  error: string
}

export type Now = {
  id: string                          // playbook id
  reason: string                      // what made the guess
  at: number                          // ms since epoch
  pinned: boolean                     // chosen by hand: no automatic switching
  source: 'you' | 'claude' | 'start'  // a message of yours outranks Claude's tool calls for 10 minutes
}

declare module 'claude-code' {
  interface PluginState {
    'mentor-coach': { book: Shaped<Book>; now: Shaped<Now> }
  }
}
