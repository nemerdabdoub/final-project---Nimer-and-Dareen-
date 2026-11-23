import { atom, read, update } from 'claude-code'
import type { ProcessRunResult, Register } from 'claude-code'

import type { Activity, Commit, FalseAlarm, LabReport, LocalFile, PartnerFile, Snapshot } from '../types'
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
const FETCH_EVERY = 24 // fetch from GitHub every 24th refresh (2 minutes)

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
      if (tick++ % FETCH_EVERY === 0) await autoSync($)

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
        commits, local, ahead: ahead || 0, behind: behind || 0, falseAlarms, syncNote, dareenFiles, labs,
        checkedAt: stamp(Date.now()),
      }))
    } catch (err) {
      await update($, snapshot, s => ({ ...s, error: String(err), checkedAt: stamp(Date.now()) }))
    }
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

  on('command.run', { command: 'updates' }, async $ => {
    await refresh($)
    await $.ui.open({ id: PANE, title: 'Project updates' })

    return { text: 'Project updates pane opened.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Link } = $.ui.resolve(e)
    const s = await read($, snapshot)
    const act = await read($, activity)
    const color = (name: string) => (name === 'Dareen' ? '#d0508a' : name === 'Nimer' ? '#3a8fd6' : undefined)

    return (
      <Box flexDirection="column" gap={1}>
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
