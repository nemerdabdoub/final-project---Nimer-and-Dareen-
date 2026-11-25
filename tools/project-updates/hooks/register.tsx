import { atom, read, update } from 'claude-code'
import type { ProcessRunResult, Register } from 'claude-code'

import type { Activity, Checklist, Commit, FalseAlarm, LabReport, LocalFile, Mentor, Message, Moodle, MoodleEvent, PartnerFile, Snapshot } from '../types'
import { registerImprove, startImprove } from './improve'

const PANE = 'project-updates'
// Found on each laptop at start (see findTools): git, the VS Code launcher, the repo root, its GitHub page.
let REPO = ''
let GIT = 'git'
let CODE = 'code'
let GITHUB = ''
const FIND = [
  "$g = (Get-Command git -ErrorAction SilentlyContinue).Source;",
  "if (-not $g) { $g = Get-ChildItem \"$env:LOCALAPPDATA\\GitHubDesktop\" -Recurse -Filter git.exe -ErrorAction SilentlyContinue |",
  "  Where-Object { $_.FullName -like '*\\cmd\\git.exe' } | Select-Object -First 1 -ExpandProperty FullName };",
  "$c = (Get-Command code.cmd -ErrorAction SilentlyContinue).Source;",
  "if (-not $c) { $c = \"$env:LOCALAPPDATA\\Programs\\Microsoft VS Code\\bin\\code.cmd\" };",
  "\"$g\"; \"$c\"; \"$env:USERPROFILE\"",
].join(' ')
let HOME = ''
const REFRESH_MS = 5_000
const FETCH_EVERY = 24 // full auto pull/push every 24th refresh (2 minutes)
const MSG_FETCH_EVERY = 3 // light fetch for messages every 3rd refresh (15 s)

const empty: Snapshot = { commits: [], local: [], ahead: 0, behind: 0, checkedAt: '', falseAlarms: [] }
const snapshot = atom({ plugin: 'project-updates', key: 'snapshot' } as const, empty, {
  shape: 'snapshot-2',
})

// ---------------- live Claude activity ----------------
const noActivity: Activity = { now: 'idle', since: 0, busy: false, recent: [], tools: 0 }
const activity = atom({ plugin: 'project-updates', key: 'activity' } as const, noActivity, { shape: 'activity-1' })
const RECENT = 8

function clip(s: string, n = 70): string {
  const one = s.replace(/\s+/g, ' ').trim()
  return one.length > n ? one.slice(0, n - 1) + '…' : one
}

function base(p: string): string {
  return p.split(/[\\/]/).pop() || p
}

// One short line saying what a tool call is doing.
function describe(e: any): string {
  const t: string = e.tool ?? 'tool'
  const who = e.agentId ? 'subagent: ' : ''
  const d = (x: string) => who + x
  switch (t) {
    case 'Bash':
    case 'PowerShell':
      return d(`${t === 'Bash' ? 'Running' : 'PowerShell'}: ${clip(e.description || e.command || '', 60)}`)
    case 'Read': return d(`Reading ${base(e.file_path ?? '')}`)
    case 'Write': return d(`Writing ${base(e.file_path ?? '')}`)
    case 'Edit': return d(`Editing ${base(e.file_path ?? '')}`)
    case 'Grep': return d(`Searching for "${clip(e.pattern ?? '', 40)}"`)
    case 'Glob': return d(`Finding files ${clip(e.pattern ?? '', 40)}`)
    case 'Agent': return d(`Started a helper agent: ${clip(e.description ?? '', 50)}`)
    case 'Artifact': return d(`Artifact: ${e.action ?? 'publish'}`)
    case 'AskUserQuestion': return d('Waiting for your answer')
    case 'Skill': return d(`Using skill ${e.skill ?? ''}`)
    default:
      if (t.startsWith('mcp__')) return d(`Connector: ${t.split('__').slice(1).join(' / ')}`)
      return d(t)
  }
}

async function setNow($: any, text: string, busy: boolean, push?: { text: string; done?: boolean; ms?: number }) {
  await update($, activity, a => {
    const recent = push ? [{ at: Date.now(), ...push }, ...a.recent].slice(0, RECENT) : a.recent
    return { ...a, now: text, since: Date.now(), busy, recent, tools: a.tools + (push && !push.done ? 1 : 0) }
  })
}

function ago(ms: number): string {
  const s = Math.max(0, Math.round((Date.now() - ms) / 1000))
  return s < 60 ? `${s} s` : `${Math.floor(s / 60)} min ${s % 60} s`
}

const SET_NAME: Record<string, string> = { '152': 'all 152 frames', '132': 'turban frames (132)', '20': 'no turban (20)' }

// Every Table B CSV under M05_data/results (stand-in PRELIM folders skipped): the newest row per set + method.
async function readFalseAlarms($: any): Promise<FalseAlarm[]> {
  const root = `${REPO}\\M05_data\\results`
  const files: { path: string; mtimeMs: number; dir: string }[] = []
  const walk = async (dir: string, label: string) => {
    let entries: any[] = []
    try { entries = await $.fs.list(dir) } catch { return }
    for (const en of entries) {
      if (en.kind === 'dir' && !/prelim/i.test(en.name)) await walk(`${dir}\\${en.name}`, en.name)
      else if (en.kind === 'file' && /^m05_table_B.*\.csv$/i.test(en.name))
        files.push({ path: `${dir}\\${en.name}`, mtimeMs: en.mtimeMs, dir: label })
    }
  }
  await walk(root, 'results')
  files.sort((a, b) => a.mtimeMs - b.mtimeMs) // newest last, so it wins
  const best = new Map<string, FalseAlarm>()
  for (const f of files) {
    let text = ''
    try { text = await $.fs.read(f.path) } catch { continue }
    for (const line of text.split(/\r?\n/).slice(1)) {
      const c = line.split(',')
      if (c.length < 8) continue
      const [method = '', bright = '', frames = '', withUser = '', , wrong = '', fa = ''] = c
      if (fa.trim() === '-' || fa.trim() === '') continue
      const key = `${frames}|${method}`
      const row = best.get(key) ?? {
        set: SET_NAME[frames] ?? `${frames} frames`, method, fa10: '', fa035: '', wrong10: '',
        noUser: Number(frames) - Number(withUser), from: f.dir,
      }
      if (bright.startsWith('1')) { row.fa10 = fa; row.wrong10 = wrong } else row.fa035 = fa
      row.from = f.dir
      best.set(key, row)
    }
  }
  return [...best.values()]
}

// ---------------- Moodle deadlines (personal) ----------------
// Reads the Moodle calendar export link from %USERPROFILE%\.claude\moodle_calendar_url.txt (never in git) and
// downloads the iCal feed every 15 minutes. The section appears only on a laptop that has that file.
const MOODLE_EVERY = 180 // refresh ticks of 5 s = 15 min
let moodleCache: Moodle | undefined

function icalTime(v: string): number {
  const m = v.match(/(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})(Z?))?/)
  if (!m) return 0
  const [, y = '0', mo = '1', d = '1', h = '23', mi = '59', s = '0', z] = m
  return z ? Date.UTC(+y, +mo - 1, +d, +h, +mi, +s) : new Date(+y, +mo - 1, +d, +h, +mi, +s).getTime()
}

function parseIcal(text: string): MoodleEvent[] {
  const unfolded = text.replace(/\r?\n[ \t]/g, '')
  const events: MoodleEvent[] = []
  for (const block of unfolded.split('BEGIN:VEVENT').slice(1)) {
    const get = (k: string) => (block.match(new RegExp('\\n' + k + '[^:\\n]*:([^\\r\\n]*)')) ?? [])[1] ?? ''
    const due = icalTime(get('DTEND') || get('DTSTART'))
    const title = get('SUMMARY').replace(/\\,/g, ',').replace(/\\n/g, ' ').replace(/\\;/g, ';')
    const course = get('CATEGORIES').replace(/\\,/g, ',')
    if (title && due) events.push({ title, course, due })
  }
  return events.sort((a, b) => a.due - b.due)
}

async function readMoodle($: any): Promise<Moodle | undefined> {
  if (!HOME) return undefined
  const cfg = `${HOME}\\.claude\\moodle_calendar_url.txt`
  let url = ''
  try { url = (await $.fs.read(cfg)).split(/\r?\n/).map((l: string) => l.trim()).find((l: string) => /^https?:\/\//.test(l)) ?? '' }
  catch { return undefined }                                  // no file -> no section
  if (!url) return { configured: false, events: [], fetchedAt: '' }
  if (moodleCache && tick % MOODLE_EVERY !== 1) return moodleCache
  const ps = `$ProgressPreference='SilentlyContinue'; (Invoke-WebRequest -UseBasicParsing -TimeoutSec 30 -Uri $env:MOODLE_URL).Content`
  const r = await $.process.run(['powershell', '-NoProfile', '-Command', ps], { timeoutMs: 45_000, env: { MOODLE_URL: url } })
  if (r.exitCode !== 0 || !/BEGIN:VCALENDAR/.test(r.stdout)) {
    moodleCache = { configured: true, events: moodleCache?.events ?? [], fetchedAt: moodleCache?.fetchedAt ?? '',
      error: 'Could not download the Moodle calendar (check the link or the internet).' }
    return moodleCache
  }
  const now = Date.now()
  moodleCache = { configured: true, events: parseIcal(r.stdout).filter(e => e.due > now - 3_600_000).slice(0, 10),
    fetchedAt: stamp(now) }
  return moodleCache
}

function daysLeft(ms: number): string {
  const h = (ms - Date.now()) / 3_600_000
  if (h < 0) return 'now'
  if (h < 24) return `${Math.round(h)} h`
  return `${Math.floor(h / 24)} d`
}

// ---------------- mentor (מנחה) ----------------
// Reads 2_MILESTONES/mentor_plan.md: the FIRST milestone that still has open tasks is the current one.
async function readMentor($: any): Promise<Mentor | undefined> {
  let text = ''
  try { text = await $.fs.read(`${REPO}\\2_MILESTONES\\mentor_plan.md`) } catch { return undefined }
  const blocks = text.split(/\r?\n(?=## )/).filter(b => b.startsWith('## '))
  for (const b of blocks) {
    const lines = b.split(/\r?\n/)
    const tasks = lines.filter(l => /^- \[( |x|X)\]/.test(l.trim()))
    const open = tasks.filter(l => /^- \[ \]/.test(l.trim())).map(l => l.trim().slice(6))
    if (tasks.length === 0 || open.length === 0) continue
    const get = (k: string) => (lines.find(l => l.startsWith(k + ':')) ?? '').slice(k.length + 1).trim()
    const due = get('Due')
    const daysLeft = due ? Math.ceil((new Date(due + 'T23:59:00').getTime() - Date.now()) / 86_400_000) : 0
    return {
      milestone: lines[0].replace(/^##\s*/, ''), due, daysLeft, question: get('Question'), metric: get('Metric'),
      asks: get('Ask').split('|').map(s => s.trim()).filter(Boolean),
      done: tasks.length - open.length, total: tasks.length, next: open.slice(0, 3),
    }
  }
  return undefined
}

const PRINCIPLES = [
  'Know your current question, its metric and its pass line before you run anything.',
  'Fix the weakest link: tracking, the controller and the command delay - not detection.',
  'Change one thing at a time, re-measure, then decide in one line with the number.',
  'Never tune on the test set. Keep a hold-out set and report that as the real result.',
  'Always give the denominator: "3 of 164", not only "1.8%".',
  'When unsure, hold. Never chase a guess.',
  'Get an ugly end-to-end version working early, then improve the worst stage.',
  'Bring Gabi decisions with evidence: "we chose X because of Y - do you agree?"',
  'Write one page per milestone now; the final report will be 70% done.',
  'Test offline before you fly: recorded video, ground test, hover, slow follow.',
]

// One piece of advice that fits what is happening right now.
function mentorTip(s: Snapshot, a: Activity): { text: string; level: 'error' | 'warning' | 'success' | undefined } {
  const m = s.mentor
  const now = a.now.toLowerCase()
  if (m && m.daysLeft <= 3 && m.done / Math.max(1, m.total) < 0.7)
    return { text: `${m.daysLeft} day(s) left and ${m.total - m.done} tasks open: cut scope now, agree with Gabi what is "done".`, level: 'error' }
  if (s.behind > 0) return { text: 'Your partner pushed new work: pull and read UPDATES.md before you change anything.', level: 'warning' }
  if (/flight|takeoff|take off|land|hover|drone_interface|moves/.test(now))
    return { text: 'Flight: phone in hand, Manual Control, open space, battery > 40%, Ctrl+C = stop. Log the flight.', level: 'error' }
  if (/editing|writing/.test(now)) return { text: 'Changing code: one change at a time, then re-run the same test and compare.', level: undefined }
  if (/running|powershell/.test(now)) return { text: 'Running an experiment: save the result CSV with date and parameters; never overwrite.', level: undefined }
  if (s.local.length > 8) return { text: `${s.local.length} files changed and not committed: commit small, clear steps so your partner can follow.`, level: 'warning' }
  if (m && m.daysLeft <= 7) return { text: `${m.daysLeft} days to ${m.milestone}: start the one-page summary and the questions for Gabi now.`, level: 'warning' }
  return { text: PRINCIPLES[Math.floor(Date.now() / 60_000) % PRINCIPLES.length], level: 'success' }
}

// Personal lab reports (not project work): read from a status file outside the repo, so this section only
// appears on a laptop that has LAB 2\lab_status.json. Nothing about it is committed or sent anywhere.
async function readLabs($: any): Promise<LabReport[]> {
  if (!HOME) return []
  const dir = `${HOME}\\OneDrive\\Desktop\\Documents\\LAB 2`
  let raw: any[] = []
  try { raw = JSON.parse(await $.fs.read(`${dir}\\lab_status.json`)) } catch { return [] }
  const labs: LabReport[] = []
  for (const r of Array.isArray(raw) ? raw : []) {
    const lab: LabReport = { lab: String(r.lab ?? ''), status: String(r.status ?? ''), next: r.next ? String(r.next) : undefined }
    if (r.pdf) {
      lab.pdf = `${dir}\\${String(r.pdf).replace(/\//g, '\\')}`
      try { lab.pdfTime = stamp((await $.fs.stat(lab.pdf)).mtimeMs) } catch { lab.pdfTime = 'missing' }
    }
    labs.push(lab)
  }
  return labs
}

function openPdf($: any, full: string) {
  return $.process.run(['powershell', '-NoProfile', '-Command', `Start-Process -FilePath '${full.replace(/'/g, "''")}'`], {
    timeoutMs: 20_000,
  })
}

function who(name: string): string {
  const n = name.toLowerCase()
  if (n.includes('dareen')) return 'Dareen'
  if (n.includes('nimer') || n.includes('nemer')) return 'Nimer'
  return name
}

function two(n: number): string {
  return n < 10 ? '0' + n : String(n)
}

function stamp(ms: number): string {
  const d = new Date(ms)
  return `${two(d.getDate())}.${two(d.getMonth() + 1)} ${two(d.getHours())}:${two(d.getMinutes())}`
}

const statusWord: Record<string, string> = {
  M: 'changed', A: 'added', D: 'deleted', R: 'renamed', '?': 'new',
}

let tick = 0

// No prompts or sign-in windows from the background: a push without a saved login just fails and says so.
const QUIET = { GIT_TERMINAL_PROMPT: '0', GCM_INTERACTIVE: 'never' }

async function git($: any, args: string[]): Promise<ProcessRunResult> {
  return $.process.run([GIT, ...args], REPO ? { cwd: REPO, timeoutMs: 60_000, env: QUIET } : { timeoutMs: 60_000, env: QUIET })
}

let syncNote = ''

// Auto pull + push, every 2 minutes. Never stashes, never force-pushes, never commits: it only moves commits that exist.
async function autoSync($: any) {
  const inMerge = await git($, ['rev-parse', '-q', '--verify', 'MERGE_HEAD'])
  if (inMerge.exitCode === 0) { syncNote = 'Auto-sync paused: a merge is in progress. Finish it first.'; return }
  await git($, ['fetch', '--quiet'])
  const counts = await git($, ['rev-list', '--left-right', '--count', 'HEAD...origin/main'])
  const [ahead = 0, behind = 0] = counts.stdout.trim().split(/\s+/).map(Number)
  if (behind > 0) {
    const pull = ahead === 0
      ? await git($, ['merge', '--ff-only', 'origin/main'])            // only new commits from GitHub: fast-forward
      : await git($, ['merge', '--no-edit', 'origin/main'])            // both sides have commits: a normal merge
    if (pull.exitCode !== 0) {
      await git($, ['merge', '--abort'])                              // conflict: undo the attempt, keep everything
      const why = /overwritten|local changes/i.test(pull.stderr + pull.stdout)
        ? 'your unsaved changes touch the same files. Commit or finish them first (nothing is stashed).'
        : 'a conflict needs a person. Ask Claude to merge it.'
      syncNote = `Auto-pull stopped: ${why}`
      return
    }
    syncNote = `Auto-pulled ${behind} commit(s) at ${stamp(Date.now())}`
  }
  const now = await git($, ['rev-list', '--count', 'origin/main..HEAD'])
  if (Number(now.stdout.trim()) > 0) {
    const push = await git($, ['push', 'origin', 'HEAD:main'])
    syncNote = push.exitCode === 0
      ? `Auto-pushed ${now.stdout.trim()} commit(s) at ${stamp(Date.now())}`
      : 'Auto-push needs a GitHub login once (token sign-in), or click Push origin in GitHub Desktop.'
  }
}

// ---------------- push pop-ups (Windows notification) ----------------
// Every new commit that reaches GitHub (origin/main) gives one pop-up on this laptop:
//   your own push  -> "Sent to <partner>: ..."   ·   the partner's push -> "New from <partner>: ..."
// The last seen commit is kept in %USERPROFILE%\.claude\project_updates_seen.txt, so pushes made while the
// laptop was off still pop up once at the next start. The very first run only sets the baseline (no pop-up).
const TOAST = [
  '[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;',
  '$t = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);',
  '$x = $t.GetElementsByTagName("text");',
  '$x.Item(0).AppendChild($t.CreateTextNode($env:TOAST_TITLE)) > $null;',
  '$x.Item(1).AppendChild($t.CreateTextNode($env:TOAST_BODY)) > $null;',
  '$app = "{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe";',
  '[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show([Windows.UI.Notifications.ToastNotification]::new($t))',
].join(' ')
let ME = ''
let lastSeen: string | undefined // undefined = not loaded yet
let popNote = ''

function toast($: any, title: string, body: string) {
  // Text goes in through environment variables, so quotes or $ in commit messages can't break the command.
  return $.process.run(['powershell', '-NoProfile', '-Command', TOAST], {
    timeoutMs: 20_000, env: { TOAST_TITLE: clip(title, 60), TOAST_BODY: clip(body, 220) },
  })
}

async function notifyPushes($: any) {
  const seenFile = HOME ? `${HOME}\\.claude\\project_updates_seen.txt` : ''
  if (!ME) ME = who((await git($, ['config', 'user.name'])).stdout.trim())
  const head = (await git($, ['rev-parse', 'origin/main'])).stdout.trim()
  if (!head) return
  if (lastSeen === undefined) {
    try { lastSeen = seenFile ? String(await $.fs.read(seenFile)).trim() : '' } catch { lastSeen = '' }
  }
  if (lastSeen === head) return
  const save = async () => {
    lastSeen = head
    if (seenFile) try { await $.fs.write(seenFile, head) } catch { /* pop-ups still work this session */ }
  }
  if (!lastSeen) { await save(); return } // first run: baseline only
  const r = await git($, ['log', `${lastSeen}..${head}`, '--format=%an%x1f%s', '-30'])
  if (r.exitCode !== 0) { await save(); return } // old commit no longer known: start fresh
  const rows = r.stdout.split('\n').filter((l: string) => l.trim()).map((l: string) => {
    const [a = '', s = ''] = l.split('\x1f'); return { who: who(a), subject: s.trim() }
  })
  const partner = ME === 'Dareen' ? 'Nimer' : 'Dareen'
  const mine = rows.filter(c => c.who === ME)
  const theirs = rows.filter(c => c.who !== ME)
  const list = (cs: { subject: string }[]) =>
    cs.slice(0, 3).map(c => '• ' + clip(c.subject, 70)).join('\n') + (cs.length > 3 ? `\n+${cs.length - 3} more` : '')
  if (theirs.length) {
    const from = theirs[0].who === ME ? partner : theirs[0].who
    const isMsg = theirs.every(c => c.subject.startsWith('💬'))
    await toast($, isMsg ? `💬 Message from ${from}` : `New from ${from} (${theirs.length} push${theirs.length > 1 ? 'es' : ''})`,
      list(theirs) + '\nPulled automatically - read UPDATES.md.')
  }
  if (mine.length) await toast($, `Sent to ${partner} ✓ (${mine.length})`, list(mine))
  popNote = `Pop-up ${stamp(Date.now())}: ${theirs.length} new from ${partner}, ${mine.length} sent`
  await save()
}

// ---------------- messages to the partner ----------------
// One small file per message in messages/ (never two people editing one file -> no merge conflicts).
// Sending commits ONLY that file and pushes; the partner's panel pops it up ("New from ...") within 2 min.
let msgNote = ''

async function sendMessage($: any, text: string) {
  const t = text.trim()
  if (!t || !REPO) return
  if (!ME) ME = who((await git($, ['config', 'user.name'])).stdout.trim())
  const d = new Date()
  const id = `${d.getFullYear()}${two(d.getMonth() + 1)}${two(d.getDate())}_${two(d.getHours())}${two(d.getMinutes())}${two(d.getSeconds())}`
  const rel = `messages/${id}_${ME}.txt`
  try {
    await $.fs.write(`${REPO}\\${rel.replace('/', '\\')}`, `${ME} ${stamp(d.getTime())}\n${t}\n`)
    await git($, ['add', '--', rel])
    const c = await git($, ['commit', '-m', `💬 ${ME}: ${clip(t.replace(/\s+/g, ' '), 90)}`, '--', rel])
    if (c.exitCode !== 0) throw new Error(c.stderr || c.stdout)
    await autoSync($)                                    // pull if needed, then push now (not in 2 min)
    msgNote = /needs|stopped|paused/.test(syncNote) ? `Saved, not pushed yet: ${syncNote}` : `Sent ✓ ${stamp(Date.now()).slice(6)}`
  } catch (err) {
    msgNote = `Not sent: ${clip(String(err), 120)}`
  }
  await refresh($)
}

// ---------------- live checklist (tick boxes of the current plan file) ----------------
// Reads the first file that exists, every refresh (5 s): tick "- [ ]" -> "- [x]" in VS Code, save, the panel follows.
const CHECKLISTS = ['2_MILESTONES/M06_field_day_manual.md', '2_MILESTONES/M06_plan_together_step_by_step.md']

async function readChecklist($: any): Promise<Checklist | undefined> {
  if (!REPO) return undefined
  for (const rel of CHECKLISTS) {
    let text = ''
    try { text = String(await $.fs.read(`${REPO}\\${rel.replace(/\//g, '\\')}`)) } catch { continue }
    const lines = text.split(/\r?\n/)
    const title = (lines.find(l => /^\s*A?#\s/.test(l)) ?? rel).replace(/^\s*A?#\s*/, '').split('—')[0]!.trim()
    const blocks: { name: string; done: number; total: number }[] = []
    const next: string[] = []
    let block = { name: 'Start', done: 0, total: 0 }
    for (const l of lines) {
      const h = l.match(/^##\s+(.+)/)
      if (h) { if (block.total) blocks.push(block); block = { name: clip(h[1]!.replace(/\s*[—·-].*$/, '').trim(), 40), done: 0, total: 0 }; continue }
      const m = l.match(/^\s*-\s\[( |x|X)\]\s+(.*)/)
      if (!m) continue
      block.total++
      if (m[1] !== ' ') block.done++
      else if (next.length < 5) next.push(clip(m[2]!.replace(/\*\*/g, '').replace(/`/g, ''), 95))
    }
    if (block.total) blocks.push(block)
    const done = blocks.reduce((n, b) => n + b.done, 0)
    const total = blocks.reduce((n, b) => n + b.total, 0)
    if (total) return { file: rel, title, done, total, blocks, next }
  }
  return undefined
}

// Messages come from GitHub's copy (origin/main) AND the local folder (own messages not pushed yet), so they show
// even when the local pull is blocked. Each file is read once and cached.
const msgCache = new Map<string, Message>()

function parseMsg(text: string): Message {
  const [head = '', ...rest] = text.split(/\r?\n/)
  const sp = head.indexOf(' ')
  return { who: head.slice(0, sp), when: head.slice(sp + 1), text: rest.join(' ').trim() }
}

async function readMessages($: any): Promise<Message[]> {
  if (!REPO) return []
  const names = new Set<string>()
  try {
    const t = await git($, ['ls-tree', '--name-only', 'origin/main', 'messages/'])
    for (const p of t.stdout.split(/\r?\n/)) if (p.endsWith('.txt')) names.add(p.replace(/^messages\//, ''))
  } catch { /* no remote copy */ }
  try {
    const all = (await $.fs.list(`${REPO}\\messages`)) as { name: string }[]
    for (const e of all) if (e.name.endsWith('.txt')) names.add(e.name)
  } catch { /* no local folder */ }
  const newest = [...names].sort().reverse().slice(0, 6)
  const out: Message[] = []
  for (const n of newest) {
    let m = msgCache.get(n)
    if (!m) {
      let text = ''
      try { text = String(await $.fs.read(`${REPO}\\messages\\${n}`)) }
      catch { text = (await git($, ['show', `origin/main:messages/${n}`])).stdout }
      if (!text.trim()) continue
      m = parseMsg(text)
      msgCache.set(n, m)
    }
    out.push(m)
  }
  return out
}

async function findTools($: any) {
  if (REPO) return
  const found = await $.process.run(['powershell', '-NoProfile', '-Command', FIND], { timeoutMs: 60_000 })
  const [g = '', c = '', h = ''] = found.stdout.split(/\r?\n/).map((s: string) => s.trim())
  if (g) GIT = g
  if (c) CODE = c
  if (h) HOME = h
  const top = await git($, ['rev-parse', '--show-toplevel'])
  REPO = top.stdout.trim().replace(/\//g, '\\')
  const url = await git($, ['remote', 'get-url', 'origin'])
  GITHUB = url.stdout.trim().replace(/\.git$/, '')
}

async function refresh($: any) {
    try {
      await findTools($)
      if (!REPO) throw new Error('This folder is not a git repo: open the project folder in VS Code.')
      if (tick % FETCH_EVERY === 0) await autoSync($)
      // Messages fast lane: a light fetch every 15 s (3 refreshes) so a partner's message pops up within ~15 s.
      // Faster is not safe: one fetch takes 1-2 s and GitHub rate-limits clients that ask many times a second.
      else if (tick % MSG_FETCH_EVERY === 0) await git($, ['fetch', '--quiet', 'origin', 'main'])
      tick++
      // Pop-ups: checks every 5 s (local, cheap), so a push made from this laptop pops up at once,
      // the partner's within 2 min (next fetch). A failed pop-up never breaks the panel.
      try { await notifyPushes($) } catch { /* ignore */ }
      try { await writeDareenLog($) } catch { /* ignore */ }

      const log = await git($, [
        'log', 'origin/main', '-20', '--name-only',
        '--format=%x1e%h%x1f%an%x1f%ad%x1f%s', '--date=format:%d.%m %H:%M',
      ])
      const commits: Commit[] = log.stdout
        .split('\x1e')
        .filter(block => block.trim() !== '')
        .map(block => {
          const [head = '', ...rest] = block.split('\n')
          const [sha = '', author = '', when = '', subject = ''] = head.split('\x1f')
          return {
            sha, who: who(author), when, subject,
            files: rest.map(f => f.trim()).filter(f => f !== ''),
          }
        })

      const counts = await git($, ['rev-list', '--left-right', '--count', 'HEAD...origin/main'])
      const [ahead, behind] = counts.stdout.trim().split(/\s+/).map(Number)

      const status = await git($, ['status', '--porcelain=v1', '-uall'])
      const local: LocalFile[] = []
      for (const line of status.stdout.split('\n')) {
        if (line.trim() === '') continue
        const code = line.slice(0, 2).trim().charAt(0)
        const path = line.slice(3).replace(/^"|"$/g, '').split(' -> ').pop() as string
        let modified = ''
        try {
          modified = stamp((await $.fs.stat(`${REPO}\\${path.replace(/\//g, '\\')}`)).mtimeMs)
        } catch {
          modified = ''
        }
        local.push({ path, status: statusWord[code] ?? code, modified })
      }
      local.sort((a, b) => (a.modified < b.modified ? 1 : -1))

      const falseAlarms = await readFalseAlarms($)
      const labs = await readLabs($)
      const mentor = await readMentor($)
      const moodle = await readMoodle($)
      const messages = await readMessages($)
      const checklist = await readChecklist($)

      // Files Dareen changed: every file in her pushed commits of the last 2 days, newest first.
      // Only pushed work is visible: unsaved or uncommitted files on her laptop never reach this one.
      const dl = await git($, ['log', 'origin/main', '--author=Dareen', '--since=2 days ago', '--name-only',
        '--format=%x1e%ad', '--date=format:%d.%m %H:%M'])
      const seen = new Map<string, string>()
      for (const block of dl.stdout.split('\x1e')) {
        const [when = '', ...files] = block.split('\n').map((x: string) => x.trim())
        for (const f of files) if (f && !seen.has(f)) seen.set(f, when)
      }
      // A folder with many changed files (frames, labels) becomes one row, so her code and notes stay visible.
      const byDir = new Map<string, string[]>()
      for (const path of seen.keys()) {
        const dir = path.includes('/') ? path.slice(0, path.lastIndexOf('/') + 1) : ''
        byDir.set(dir, [...(byDir.get(dir) ?? []), path])
      }
      const dareenFiles: PartnerFile[] = []
      const grouped = new Set<string>()
      for (const [path, when] of seen) {
        const dir = path.includes('/') ? path.slice(0, path.lastIndexOf('/') + 1) : ''
        const inDir = byDir.get(dir) ?? []
        if (dir && (inDir.length > 10 || (dir.startsWith('M05_data/') && inDir.length > 3))) {
          if (!grouped.has(dir)) {
            grouped.add(dir)
            dareenFiles.push({ path: dir, when, count: inDir.length })
          }
        } else dareenFiles.push({ path, when })
      }

      await update($, snapshot, () => ({
        commits, local, ahead: ahead || 0, behind: behind || 0, falseAlarms, syncNote: [syncNote, popNote].filter(Boolean).join(' · '), dareenFiles, labs, mentor, moodle, messages, checklist,
        checkedAt: stamp(Date.now()),
      }))
    } catch (err) {
      await update($, snapshot, s => ({ ...s, error: String(err), checkedAt: stamp(Date.now()) }))
    }
  }

// ---------------- /updfd: live chronological log of Dareen's pushes (Markdown, outside the repo) ----------------
// %USERPROFILE%\.claude\dareen_updates_log.md, rewritten whenever GitHub has a new commit (checked every 5 s,
// fetched every 2 min). Newest first, grouped by day, with the files each push changed and GitHub links.
let logHead = ''
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function logPath() { return HOME ? `${HOME}\\.claude\\dareen_updates_log.md` : '' }

async function writeDareenLog($: any, force = false) {
  const out = logPath()
  if (!out || !REPO) return
  const head = (await git($, ['rev-parse', 'origin/main'])).stdout.trim()
  if (!force && head && head === logHead) return
  const r = await git($, ['log', 'origin/main', '--author=Dareen', '-n', '300', '--name-only',
    '--format=%x1e%h%x1f%at%x1f%s%x1f%b'])
  const lines: string[] = [
    '# Dareen – live updates log',
    '',
    `_Regenerated ${stamp(Date.now())} · newest first · from GitHub (origin/main) · open with /updfd · auto-updates on every new push_`,
    '',
  ]
  let day = ''
  let count = 0
  for (const block of r.stdout.split('\x1e')) {
    if (!block.trim()) continue
    const [head2 = '', ...rest] = block.split('\n')
    const [sha = '', at = '0', subject = '', body = ''] = head2.split('\x1f')
    const d = new Date(Number(at) * 1000)
    const dKey = `${two(d.getDate())}.${two(d.getMonth() + 1)}.${d.getFullYear()} (${DAYS[d.getDay()]})`
    if (dKey !== day) { day = dKey; lines.push('', `## ${dKey}`, '') }
    const link = GITHUB ? ` · [${sha}](${GITHUB}/commit/${sha})` : ` · ${sha}`
    lines.push(`- **${two(d.getHours())}:${two(d.getMinutes())}** ${subject}${link}`)
    if (body.trim()) lines.push(`  - ${clip(body.trim().replace(/\s+/g, ' '), 300)}`)
    const files = rest.map(f => f.trim()).filter(Boolean)
    if (files.length) {
      const shown = files.slice(0, 8).map(f => (GITHUB ? `[${f}](${GITHUB}/blob/main/${encodeURI(f)})` : `\`${f}\``))
      lines.push(`  - files: ${shown.join(', ')}${files.length > 8 ? ` … +${files.length - 8} more` : ''}`)
    }
    count++
  }
  if (count === 0) lines.push('_No pushes by Dareen found on GitHub._')
  await $.fs.write(out, lines.join('\n') + '\n')
  logHead = head
}

function openFile($: any, path: string) {
  return $.process.run(['cmd', '/c', CODE, '-r', `${REPO}\\${path.replace(/\//g, '\\')}`], {
    timeoutMs: 20_000,
  })
}

export const register: Register = (on, options) => {
  registerImprove(on, options)

  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await $.command.register({
      name: 'updates',
      description: 'Show the live project updates pane (pushes, changed files)',
    })
    await $.command.register({
      name: 'updfd',
      description: "Open Dareen's live updates log (.md, chronological, rewrites itself on every push)",
    })
    void refresh($)
    $.clock.every(REFRESH_MS, () => refresh($))
    void $.ui.open({ id: PANE, title: 'Project updates' })
    await startImprove($)

    return started
  })

  // Live activity: every tool call, and when a turn starts / ends.
  on('tool.call', async ($, e, next) => {
    const text = describe(e)
    const t0 = Date.now()
    try { await setNow($, text, true, { text }) } catch { /* never block the tool */ }
    const result = await next(e)
    try {
      await update($, activity, a => ({
        ...a,
        recent: a.recent.map((r, i) => (i === a.recent.findIndex(x => x.text === text && !x.done) ? { ...r, done: true, ms: Date.now() - t0 } : r)),
      }))
    } catch { /* ignore */ }
    return result
  })

  on('turn.start', async ($, e, next) => {
    if (!(e as any).agentId) { try { await setNow($, 'Thinking about your message…', true) } catch { /* ignore */ } }
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const r = await next(e)
    if (!(e as any).agentId) { try { await setNow($, 'Finished – waiting for you', false) } catch { /* ignore */ } }
    return r
  })

  on('command.run', { command: 'updfd' }, async $ => {
    await findTools($)
    await git($, ['fetch', '--quiet'])
    await writeDareenLog($, true)
    const p = logPath()
    if (!p) return { text: 'Could not find your user folder for the log.' }
    await $.process.run(['cmd', '/c', CODE, '-r', p], { timeoutMs: 20_000 })
    return { text: `Dareen's live log opened: ${p} (newest first; rewrites itself on every new push).` }
  })

  on('command.run', { command: 'updates' }, async $ => {
    await refresh($)
    await $.ui.open({ id: PANE, title: 'Project updates' })

    return { text: 'Project updates pane opened.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Link, Input } = $.ui.resolve(e)
    const s = await read($, snapshot)
    const act = await read($, activity)
    const color = (name: string) => (name === 'Dareen' ? '#d0508a' : name === 'Nimer' ? '#3a8fd6' : undefined)

    return (
      <Box flexDirection="column" gap={1}>
        {s.checklist && (() => {
          const c = s.checklist!
          const pct = Math.round((100 * c.done) / c.total)
          const bar = '█'.repeat(Math.round(pct / 5)) + '░'.repeat(20 - Math.round(pct / 5))
          return (
            <Box flexDirection="column">
              <Text bold>✅ Checklist <Text dimColor>· {c.title}</Text></Text>
              <Text color={pct === 100 ? 'success' : undefined}>{bar} {c.done}/{c.total} ({pct}%)</Text>
              {c.blocks.map((b, i) => (
                <Text key={'cb:' + i} dimColor={b.done === b.total}>
                  {b.done === b.total ? '✓' : b.done > 0 ? '◐' : '○'} {b.name} <Text dimColor>{b.done}/{b.total}</Text>
                </Text>
              ))}
              {c.next.length > 0 && <Text>Next:</Text>}
              {c.next.map((t, i) => <Text key={'cn:' + i}>  {i === 0 ? '→' : '·'} {t}</Text>)}
              <Button key="checklist-open" onPress={() => openFile($, c.file)}>open the checklist (tick boxes there, save)</Button>
            </Box>
          )
        })()}

        {(() => {
          // Sent & received: the last pushes on GitHub, yours = sent to the partner (pop-up on their laptop),
          // theirs = received (pop-up here). Same list both laptops see, from origin/main.
          const me = ME || 'Nimer'
          const partner = me === 'Dareen' ? 'Nimer' : 'Dareen'
          return (
            <Box flexDirection="column">
              <Text bold>💬 Message {partner}</Text>
              <Input
                key="msg-partner"
                placeholder={`type a message to ${partner}, Enter = send (pops up on her/his laptop)`}
                submitLabel="send"
                onSubmit={(v: string) => { void sendMessage($, v) }}
              />
              {msgNote !== '' && <Text color={msgNote.startsWith('Sent') ? 'success' : 'warning'}>{msgNote}</Text>}
              {(s.messages ?? []).map((m, i) => (
                <Text key={'msg:' + i}>
                  <Text color={color(m.who)}>{m.who === me ? '→ ' : '← '}{m.who}</Text>
                  <Text dimColor> {m.when}  </Text>{m.text}
                </Text>
              ))}
              <Text> </Text>
              <Text bold>Sent & received <Text dimColor>(every push pops up on the other laptop)</Text></Text>
              {s.commits.slice(0, 8).map(c => (
                <Text key={'sr:' + c.sha}>
                  {c.who === me
                    ? <Text color="success">⬆ sent to {partner}  </Text>
                    : <Text color={color(c.who) ?? 'warning'}>⬇ from {c.who}  </Text>}
                  <Text dimColor>{c.when}  </Text>{clip(c.subject, 80)}
                </Text>
              ))}
              {s.commits.length === 0 && <Text dimColor>Loading pushes…</Text>}
              {popNote !== '' && <Text dimColor>Last pop-up: {popNote.replace(/^Pop-up /, '')}</Text>}
            </Box>
          )
        })()}

        <Box flexDirection="column">
          <Text bold>Claude right now</Text>
          <Text color={act.busy ? 'warning' : 'success'}>
            {act.busy ? '● ' : '○ '}{act.now}
            {act.since > 0 && <Text dimColor>  ({ago(act.since)})</Text>}
          </Text>
          {act.recent.slice(0, RECENT).map((r, i) => (
            <Text key={'act:' + r.at + ':' + i} dimColor={r.done}>
              {stamp(r.at).slice(6)} {r.done ? '✓' : '…'} {r.text}
              {r.ms !== undefined && <Text dimColor>  {r.ms < 1000 ? `${r.ms} ms` : `${Math.round(r.ms / 1000)} s`}</Text>}
            </Text>
          ))}
          <Text dimColor>{act.tools} tool calls this session · updates live</Text>
        </Box>

        {(() => {
          const m = s.mentor
          const tip = mentorTip(s, act)
          return (
            <Box flexDirection="column">
              <Text bold>מנחה · Mentor <Text dimColor>(live advice)</Text></Text>
              <Text color={tip.level}>» {tip.text}</Text>
              {m ? (
                <Box flexDirection="column">
                  <Text>
                    <Text bold>{m.milestone}</Text>
                    <Text color={m.daysLeft <= 3 ? 'error' : m.daysLeft <= 7 ? 'warning' : undefined}>
                      {'  '}{m.daysLeft} days left (due {m.due})
                    </Text>
                    <Text dimColor>  · {m.done}/{m.total} done</Text>
                  </Text>
                  {m.question && <Text dimColor>Question: {m.question}</Text>}
                  {m.metric && <Text dimColor>Pass line: {m.metric}</Text>}
                  <Text>Next:</Text>
                  {m.next.map((t, i) => (
                    <Text key={'mn:' + i}>  {i === 0 ? '→' : '·'} {t}</Text>
                  ))}
                  {m.asks.length > 0 && <Text dimColor>Gabi will ask: {m.asks.join(' · ')}</Text>}
                  <Button key="mentor-plan" onPress={() => openFile($, '2_MILESTONES/mentor_plan.md')}>
                    open the plan (tick tasks there)
                  </Button>
                </Box>
              ) : (
                <Text dimColor>No open milestone in 2_MILESTONES/mentor_plan.md.</Text>
              )}
            </Box>
          )
        })()}

        <Box flexDirection="column">
          <Text dimColor>
            Checked {s.checkedAt || '…'} · refreshes every 5 s
          </Text>
          {s.behind > 0 && <Text color="warning">⬇ {s.behind} new from GitHub, not pulled yet</Text>}
          {s.ahead > 0 && <Text color="warning">⬆ {s.ahead} commit(s) here not pushed yet</Text>}
          {s.ahead === 0 && s.behind === 0 && s.checkedAt !== '' && <Text color="success">In sync with GitHub</Text>}
          {s.syncNote && (
            <Text color={/stopped|paused|needs/.test(s.syncNote) ? 'warning' : 'success'}>{s.syncNote}</Text>
          )}
          <Text dimColor>Auto pull + push every 2 min · never stashes · never force-pushes</Text>
          {s.error && <Text color="error">{s.error}</Text>}
        </Box>

        {s.moodle && (
          <Box flexDirection="column">
            <Text bold>Moodle – upcoming <Text dimColor>(this laptop only)</Text></Text>
            {!s.moodle.configured && (
              <Text dimColor>
                Paste your Moodle calendar export link (Calendar → Export calendar → All courses → Get calendar URL)
                into .claude\moodle_calendar_url.txt
              </Text>
            )}
            {s.moodle.error && <Text color="warning">{s.moodle.error}</Text>}
            {s.moodle.configured && s.moodle.events.length === 0 && !s.moodle.error && (
              <Text dimColor>Nothing due soon.</Text>
            )}
            {s.moodle.events.map((ev, i) => {
              const h = (ev.due - Date.now()) / 3_600_000
              return (
                <Text key={'md:' + i + ':' + ev.due}>
                  <Text color={h < 24 ? 'error' : h < 72 ? 'warning' : undefined} bold>{daysLeft(ev.due).padStart(4)}</Text>
                  {'  '}{ev.title}
                  <Text dimColor>  {ev.course} · {stamp(ev.due)}</Text>
                </Text>
              )
            })}
            {s.moodle.fetchedAt && <Text dimColor>updated {s.moodle.fetchedAt} · every 15 min</Text>}
          </Box>
        )}

        {(s.labs ?? []).length > 0 && (
          <Box flexDirection="column">
            <Text bold>Lab reports <Text dimColor>(this laptop only, not in git)</Text></Text>
            {(s.labs ?? []).map(l => (
              <Box key={'lab:' + l.lab} flexDirection="column">
                <Text>
                  <Text bold>{l.lab}</Text>{'  '}
                  <Text color={/done|submitted/i.test(l.status) ? 'success' : /not/i.test(l.status) ? 'warning' : undefined}>
                    {l.status}
                  </Text>
                </Text>
                {l.next && <Text dimColor>next: {l.next}</Text>}
                {l.pdf && l.pdfTime !== 'missing' && (
                  <Button key={'labpdf:' + l.lab} onPress={() => openPdf($, l.pdf as string)}>
                    open PDF <Text dimColor>updated {l.pdfTime}</Text>
                  </Button>
                )}
                {l.pdf && l.pdfTime === 'missing' && <Text color="warning">PDF not found</Text>}
              </Box>
            ))}
          </Box>
        )}

        <Box flexDirection="column">
          <Text bold>Files changed on this laptop ({s.local.length})</Text>
          {s.local.length === 0 && <Text dimColor>None. Everything is committed.</Text>}
          {s.local.slice(0, 15).map(f => (
            <Button key={'local:' + f.path} onPress={() => openFile($, f.path)}>
              {f.path} <Text dimColor>{f.status} {f.modified}</Text>
            </Button>
          ))}
        </Box>

        <Box flexDirection="column">
          <Text bold>
            <Text color="#d0508a">Files Dareen changed</Text> (
            {(s.dareenFiles ?? []).reduce((n, f) => n + (f.count ?? 1), 0)}, pushed in the last 2 days)
          </Text>
          <Text dimColor>newest first · click to open · only what she pushed is visible</Text>
          {(s.dareenFiles ?? []).length === 0 && <Text dimColor>Nothing pushed by Dareen in the last 2 days.</Text>}
          {(s.dareenFiles ?? []).slice(0, 25).map(f =>
            f.count ? (
              <Text key={'dareen:' + f.path}>
                {f.path} <Text dimColor>({f.count} files) {f.when}</Text>
              </Text>
            ) : (
              <Button key={'dareen:' + f.path} onPress={() => openFile($, f.path)}>
                {f.path} <Text dimColor>{f.when}</Text>
              </Button>
            ),
          )}
          {(s.dareenFiles ?? []).length > 25 && (
            <Text dimColor>+{(s.dareenFiles ?? []).length - 25} more (older)</Text>
          )}
        </Box>

        <Box flexDirection="column">
          <Text bold>False alarms, M05 (frames without the user)</Text>
          <Text dimColor>method · false alarm % at 1.0 / 0.35 · wrong person % at 1.0</Text>
          {(s.falseAlarms ?? []).length === 0 && <Text dimColor>No result tables in M05_data/results yet.</Text>}
          {[...new Set((s.falseAlarms ?? []).map(f => f.set))].map(set => (
            <Box key={'fa:' + set} flexDirection="column">
              <Text dimColor>
                {set} · {(s.falseAlarms ?? []).find(f => f.set === set)?.noUser ?? 0} frames without the user
              </Text>
              {(s.falseAlarms ?? []).filter(f => f.set === set).map(f => (
                <Text key={'fa:' + set + ':' + f.method}>
                  <Text color={Number(f.fa10) <= 10 ? 'success' : Number(f.fa10) >= 50 ? 'error' : 'warning'}>
                    {f.fa10 || '?'}% / {f.fa035 || '?'}%
                  </Text>
                  {'  '}{f.method}<Text dimColor>  wrong {f.wrong10 || '?'}%</Text>
                </Text>
              ))}
            </Box>
          ))}
        </Box>

        <Box flexDirection="column" gap={1}>
          <Text bold>Pushed updates (newest first)</Text>
          {s.commits.length === 0 && <Text dimColor>Loading…</Text>}
          {s.commits.map(c => (
            <Box key={c.sha} flexDirection="column">
              <Text>
                <Text color={color(c.who)} bold>{c.who}</Text>
                <Text dimColor> {c.when} </Text>
                {GITHUB.startsWith('https://') ? <Link href={`${GITHUB}/commit/${c.sha}`} label={c.sha} /> : <Text dimColor>{c.sha}</Text>}
              </Text>
              <Text>{c.subject}</Text>
              {c.files.slice(0, 8).map(f => (
                <Button key={c.sha + ':' + f} onPress={() => openFile($, f)}>
                  {f}
                </Button>
              ))}
              {c.files.length > 8 && <Text dimColor>+{c.files.length - 8} more files</Text>}
            </Box>
          ))}
        </Box>
      </Box>
    )
  })
}
