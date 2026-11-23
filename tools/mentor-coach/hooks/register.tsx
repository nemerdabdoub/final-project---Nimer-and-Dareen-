import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Book, Now, Plan, Playbook } from '../types'

// Mentor coach: a substitute supervisor beside the chat.
// It reads 2_MILESTONES/mentor_playbooks.md (the advice, plain Markdown anyone can edit) and
// 2_MILESTONES/mentor_plan.md (the current milestone's tasks), guesses which process the team is in
// from your messages and Claude's commands / edited files, and shows that playbook.
// It also tells Claude which process it is, so the "Advisor's view" in the chat uses the same playbook.

const PANE = 'mentor-coach'
const PLAYBOOKS = '2_MILESTONES\\mentor_playbooks.md'
const PLAN = '2_MILESTONES\\mentor_plan.md'
const RELOAD_MS = 15_000
const YOU_WIN_MS = 10 * 60_000 // a message of yours outranks Claude's tool calls for 10 minutes

let ROOT = ''
let lastText = ''
let lastPlan = ''

const emptyBook: Book = { principles: [], books: [], loadedAt: '', error: '' }
const book = atom({ plugin: 'mentor-coach', key: 'book' } as const, emptyBook, { shape: 'book-1' })
const startNow: Now = { id: 'lost', reason: 'start of the session', at: 0, pinned: false, source: 'start' }
const now = atom({ plugin: 'mentor-coach', key: 'now' } as const, startNow, { shape: 'now-1' })

// ---------------- reading the files ----------------
function parseBooks(text: string): { principles: string[]; books: Playbook[] } {
  const principles: string[] = []
  const books: Playbook[] = []
  let cur: Playbook | null = null
  let inPrinciples = false
  let list: 'steps' | 'asks' | 'traps' | null = null
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim()
    const h = /^##\s+(.+)$/.exec(line)
    if (h) {
      list = null
      cur = null
      inPrinciples = /^principles$/i.test(h[1].trim())
      if (inPrinciples) continue
      const m = /^([\w-]+)\s*\|\s*(.+)$/.exec(h[1].trim())
      if (!m) continue
      cur = { id: m[1].toLowerCase(), title: m[2].trim(), when: [], why: '', steps: [], asks: [], traps: [], done: '' }
      books.push(cur)
      continue
    }
    if (inPrinciples) {
      const p = /^[-*]\s+(.+)$/.exec(line)
      if (p) principles.push(p[1])
      continue
    }
    if (!cur) continue
    let m: RegExpExecArray | null
    if ((m = /^When:\s*(.*)$/i.exec(line))) {
      cur.when = m[1].split(',').map(s => s.trim().toLowerCase()).filter(Boolean)
      list = null
    } else if ((m = /^Why:\s*(.*)$/i.exec(line))) {
      cur.why = m[1]
      list = null
    } else if (/^Steps:/i.test(line)) list = 'steps'
    else if (/^Gabi asks:/i.test(line)) list = 'asks'
    else if (/^Traps:/i.test(line)) list = 'traps'
    else if ((m = /^Done when:\s*(.*)$/i.exec(line))) {
      cur.done = m[1]
      list = null
    } else if (list && (m = /^(?:[-*]|\d+[.)])\s+(.+)$/.exec(line))) cur[list].push(m[1])
  }
  return { principles, books }
}

// The first milestone in mentor_plan.md that still has open tasks.
function parsePlan(text: string): Plan | undefined {
  const parts = text.split(/\r?\n(?=##\s)/)
  for (const part of parts) {
    const head = /^##\s+(.+)/.exec(part)
    if (!head) continue
    const open = [...part.matchAll(/^\s*-\s*\[ \]\s*(.+)$/gm)].map(x => x[1].trim())
    const closed = [...part.matchAll(/^\s*-\s*\[x\]/gim)].length
    if (open.length === 0) continue
    const due = /^Due:\s*(\d{4}-\d{2}-\d{2})/m.exec(part)?.[1] ?? ''
    const daysLeft = due ? Math.ceil((Date.parse(due + 'T23:59:59') - Date.now()) / 86_400_000) : 0
    return { milestone: head[1].trim(), due, daysLeft, next: open[0], done: closed, total: closed + open.length }
  }
  return undefined
}

async function readFirst($: any, rel: string): Promise<string> {
  return $.fs.read(`${ROOT}\\${rel}`)
}

async function findRoot($: any) {
  let dir = String(await $.session.root()).replace(/\//g, '\\').replace(/\\+$/, '')
  for (let i = 0; i < 4 && dir; i++) {
    try {
      await $.fs.stat(`${dir}\\${PLAYBOOKS}`)
      ROOT = dir
      return
    } catch { /* go up */ }
    const up = dir.replace(/\\[^\\]+$/, '')
    if (up === dir) break
    dir = up
  }
  ROOT = String(await $.session.root()).replace(/\//g, '\\').replace(/\\+$/, '')
}

async function load($: any) {
  let text = ''
  let planText = ''
  try { text = await readFirst($, PLAYBOOKS) } catch {
    await update($, book, b => ({ ...b, error: `Cannot read ${PLAYBOOKS} under ${ROOT}. Pull from GitHub?` }))
    return
  }
  try { planText = await readFirst($, PLAN) } catch { planText = '' }
  const day = new Date().toDateString() // days left changes at midnight
  if (text === lastText && planText + day === lastPlan) return
  lastText = text
  lastPlan = planText + day
  const parsed = parseBooks(text)
  const plan = planText ? parsePlan(planText) : undefined
  await update($, book, () => ({ ...parsed, plan, loadedAt: new Date().toLocaleTimeString(), error: parsed.books.length ? '' : `No playbooks found in ${PLAYBOOKS}.` }))
}

// ---------------- guessing the process ----------------
function hit(text: string, word: string): boolean {
  if (!/^[a-z0-9]/.test(word)) return text.includes(word)
  const esc = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return new RegExp('[^a-z0-9]' + esc).test(text) // the word must start at a word start: "pid" never matches "rapid"
}

function match(books: Playbook[], text: string): Playbook | undefined {
  const t = ' ' + text.toLowerCase()
  return books.find(b => b.when.some(w => hit(t, w)))
}

function clip(s: string, n = 60): string {
  const one = s.replace(/\s+/g, ' ').trim()
  return one.length > n ? one.slice(0, n - 1) + '…' : one
}

function base(p: string): string {
  return p.split(/[\\/]/).pop() || p
}

// What a tool call tells us; bookkeeping (git, notes, memory) says nothing about the process.
function fromTool(e: any): { text: string; label: string } | undefined {
  const t = e.tool
  if (t === 'Bash' || t === 'PowerShell') {
    const c = String(e.command ?? '')
    if (/(^|&&|;|\|)\s*git\s/.test(c) && !/python|record_video|flight/.test(c)) return undefined
    const desc = e.description ? String(e.description) : c
    return { text: c + ' ' + desc, label: `Claude ran: ${clip(desc, 50)}` }
  }
  if (t === 'Edit' || t === 'Write' || t === 'NotebookEdit') {
    const p = String(e.file_path ?? e.notebook_path ?? '')
    if (/UPDATES\.md|CLAUDE\.md|mid_project_presentation_log|mentor_playbooks|mentor_plan|MEMORY\.md|[\\/]\.claude[\\/]|[\\/]tools[\\/]/i.test(p)) return undefined
    return { text: p, label: `Claude edited ${base(p)}` }
  }
  return undefined
}

async function see($: any, text: string, label: string, source: 'you' | 'claude') {
  const b = await read($, book)
  const n = await read($, now)
  if (n.pinned) return
  if (source === 'claude' && n.source === 'you' && Date.now() - n.at < YOU_WIN_MS) return
  const pb = match(b.books, text)
  if (!pb) return
  if (pb.id === n.id && n.source === source) return // nothing new: no redraw
  await update($, now, () => ({ id: pb.id, reason: label, at: Date.now(), pinned: false, source }))
}

// ---------------- actions ----------------
type Ask = { id: string; label: string; text: (pb: Playbook) => string }
const ASKS: Ask[] = [
  {
    id: 'where',
    label: 'Where are we? What is the ONE next step?',
    text: pb => `Mentor check-in (process: ${pb.title}). Act as our supervisor. In plain words: where are we in the project (use the Status in CLAUDE.md, 2_MILESTONES/mentor_plan.md and the newest UPDATES.md entries), what is the ONE next step for today, who should do it, and how we will know it worked. Keep it short.`,
  },
  {
    id: 'review',
    label: 'Review what we just did, like Gabi would',
    text: pb => `Mentor review (process: ${pb.title}, playbook "${pb.id}" in 2_MILESTONES/mentor_playbooks.md). Review what we did in this session as a strict but kind supervisor: what is solid, what is weak, which of the playbook's traps we fell into, which of "Gabi asks" we cannot answer yet, and what to fix first. Be honest.`,
  },
  {
    id: 'practice',
    label: 'Practice: ask us Gabi’s hardest questions',
    text: pb => `Mentor practice (process: ${pb.title}). Ask us the 3 hardest questions our supervisor Gabi would ask about our current work, ONE at a time. Wait for our answer to each, then tell us how to answer it better (shorter, with numbers and evidence).`,
  },
  {
    id: 'plan',
    label: 'Plan our next 2 hours',
    text: pb => `Mentor planning (process: ${pb.title}). Plan our next 2 hours as small steps, each with a check that says it worked, based on the steps of playbook "${pb.id}" in 2_MILESTONES/mentor_playbooks.md and the first open tasks in 2_MILESTONES/mentor_plan.md. Split the work between Dareen and Nimer if both are working.`,
  },
  {
    id: 'explain',
    label: 'Explain the idea behind this simply',
    text: pb => `Mentor explain (process: ${pb.title}). We are new to this. Explain the main engineering idea behind what we are doing now in simple words, with one example from our own project, and why an engineer does it this way. Then give us one question to check we understood.`,
  },
]

async function ask($: any, a: Ask, pb: Playbook) {
  await update($, now, n => ({ ...n, id: pb.id, source: 'you', at: Date.now(), reason: `you asked: ${a.label}` }))
  await $.prompt.submit({ text: a.text(pb) })
}

async function pin($: any, id: string) {
  await update($, now, () => ({ id, reason: 'chosen by you', at: Date.now(), pinned: true, source: 'you' }))
}

async function unpin($: any) {
  await update($, now, n => ({ ...n, pinned: false, reason: 'automatic again', at: Date.now() }))
}

async function openPlaybooks($: any) {
  const path = `${ROOT}\\${PLAYBOOKS}`
  const r = await $.process.run(['cmd', '/c', 'code', '-r', path], { timeoutMs: 20_000 })
  if (r.exitCode !== 0) await $.process.run(['cmd', '/c', 'start', '""', path], { timeoutMs: 20_000 })
}

function ago(ms: number): string {
  const s = Math.max(0, Math.round((Date.now() - ms) / 1000))
  return s < 60 ? `${s} s` : s < 3600 ? `${Math.floor(s / 60)} min` : `${Math.floor(s / 3600)} h`
}

// ---------------- the hooks ----------------
export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await $.command.register({
      name: 'mentor',
      description: 'Open the Mentor coach pane. "/mentor flight" pins a process, "/mentor auto" follows your work again',
    })
    try { await findRoot($) } catch { /* keep going */ }
    await load($)
    $.clock.every(RELOAD_MS, () => load($))
    void $.ui.open({ id: PANE, title: 'Mentor' })
    return started
  })

  on('command.run', { command: 'mentor' }, async ($, e) => {
    await load($)
    const arg = e.args.trim().toLowerCase()
    const b = await read($, book)
    let text = 'Mentor coach opened.'
    if (arg === 'auto') {
      await unpin($)
      text = 'Mentor coach follows your work again.'
    } else if (arg) {
      const pb = b.books.find(x => x.id === arg) ?? b.books.find(x => x.title.toLowerCase().includes(arg))
      if (pb) {
        await pin($, pb.id)
        text = `Mentor coach pinned to: ${pb.title}. "/mentor auto" to follow your work again.`
      } else text = `No playbook called "${arg}". Try one of: ${b.books.map(x => x.id).join(', ')}.`
    }
    await $.ui.open({ id: PANE, title: 'Mentor' })
    return { text }
  })

  on('prompt.submit', async ($, e, next) => {
    try {
      const origin = (e as any).origin
      if (!origin || origin.kind !== 'plugin') await see($, String(e.text ?? ''), `you wrote: "${clip(String(e.text ?? ''), 45)}"`, 'you')
    } catch { /* never block a message */ }
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    try {
      const t = fromTool(e)
      if (t) await see($, t.text, t.label, 'claude')
    } catch { /* never block a tool */ }
    return next(e)
  })

  // Tell Claude which process the team is in, so the Advisor's view in the chat uses the same playbook.
  on('prompt.compose', async ($, e, next) => {
    const r = await next(e)
    try {
      const n = await read($, now)
      const b = await read($, book)
      const pb = b.books.find(x => x.id === n.id)
      if (!pb) return r
      const text =
        `Mentor coach panel: the team is now in the process "${pb.title}" (playbook "${pb.id}" in ` +
        `2_MILESTONES/mentor_playbooks.md). In your Advisor's view, use that playbook: point out any of its traps you see, ` +
        `say which of its "Gabi asks" questions this step answers or leaves open, and name the next step. ` +
        `If the work has clearly moved to another process, say so in one line.`
      return { ...r, sections: [...r.sections, { id: 'mentor-coach:process', text, scope: 'session' as const }] }
    } catch {
      return r
    }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const b = await read($, book)
    const n = await read($, now)
    const pb = b.books.find(x => x.id === n.id) ?? b.books[0]
    if (!pb) return <Text dimColor>{b.error || 'Loading the mentor playbooks…'}</Text>
    const principle = b.principles.length ? b.principles[Math.floor(Date.now() / 3_600_000) % b.principles.length] : ''
    const p = b.plan

    return (
      <Box flexDirection="column" gap={1}>
        <Box flexDirection="column">
          <Text bold>מנחה · Mentor coach</Text>
          {p && (
            <Text>
              <Text bold>{p.milestone}</Text>
              <Text color={p.daysLeft <= 3 ? 'error' : p.daysLeft <= 7 ? 'warning' : undefined}>
                {'  '}{p.daysLeft} days left
              </Text>
              <Text dimColor>  · {p.done}/{p.total} tasks done</Text>
            </Text>
          )}
          {p && <Text>→ Next task: {p.next}</Text>}
        </Box>

        <Box flexDirection="column">
          <Text>
            Now: <Text bold color="#7a5af5">{pb.title}</Text>
          </Text>
          <Text dimColor>
            {n.pinned ? 'pinned by you · "/mentor auto" to follow your work again' : n.at ? `guessed: ${n.reason} · ${ago(n.at)} ago` : 'a good place to start'}
          </Text>
          {pb.why && <Text>{pb.why}</Text>}
        </Box>

        {pb.steps.length > 0 && (
          <Box flexDirection="column">
            <Text bold>Steps</Text>
            {pb.steps.map((s, i) => (
              <Text key={'s:' + i}>  {i + 1}. {s}</Text>
            ))}
          </Box>
        )}

        {pb.asks.length > 0 && (
          <Box flexDirection="column">
            <Text bold>Gabi will ask</Text>
            {pb.asks.map((s, i) => (
              <Text key={'a:' + i}>  ? {s}</Text>
            ))}
          </Box>
        )}

        {pb.traps.length > 0 && (
          <Box flexDirection="column">
            <Text bold color="warning">Traps</Text>
            {pb.traps.map((s, i) => (
              <Text key={'t:' + i}>  ! {s}</Text>
            ))}
          </Box>
        )}

        {pb.done && (
          <Text>
            <Text bold color="success">Done when: </Text>
            {pb.done}
          </Text>
        )}

        {principle && <Text dimColor>Principle: {principle}</Text>}

        <Box flexDirection="column">
          <Text bold>Ask the mentor <Text dimColor>(sends the question to Claude)</Text></Text>
          {ASKS.map(a => (
            <Button key={'ask:' + a.id} onPress={() => ask($, a, pb)}>
              {a.label}
            </Button>
          ))}
        </Box>

        <Box flexDirection="column">
          <Text bold>Other processes <Text dimColor>(click to pin)</Text></Text>
          {n.pinned && (
            <Button key="auto" onPress={() => unpin($)}>
              ↺ follow my work automatically again
            </Button>
          )}
          {b.books.filter(x => x.id !== pb.id).map(x => (
            <Button key={'pb:' + x.id} onPress={() => pin($, x.id)}>
              {x.title}
            </Button>
          ))}
        </Box>

        <Box flexDirection="column">
          <Button key="open" onPress={() => openPlaybooks($)}>
            open the playbooks (edit the advice)
          </Button>
          {b.error && <Text color="error">{b.error}</Text>}
          <Text dimColor>Read {b.loadedAt || '…'} · reloads every 15 s from 2_MILESTONES/mentor_playbooks.md</Text>
        </Box>
      </Box>
    )
  })
}
