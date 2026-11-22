import { atom, read, update } from 'claude-code'
import type { ProcessRunResult, Register } from 'claude-code'

import type { Commit, FalseAlarm, LocalFile, Snapshot } from '../types'

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
  "\"$g\"; \"$c\"",
].join(' ')
const REFRESH_MS = 5_000
const FETCH_EVERY = 24 // fetch from GitHub every 24th refresh (2 minutes)

const empty: Snapshot = { commits: [], local: [], ahead: 0, behind: 0, checkedAt: '', falseAlarms: [] }
const snapshot = atom({ plugin: 'project-updates', key: 'snapshot' } as const, empty, {
  shape: 'snapshot-2',
})

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

async function git($: any, args: string[]): Promise<ProcessRunResult> {
  return $.process.run([GIT, ...args], REPO ? { cwd: REPO, timeoutMs: 60_000 } : { timeoutMs: 60_000 })
}

async function findTools($: any) {
  if (REPO) return
  const found = await $.process.run(['powershell', '-NoProfile', '-Command', FIND], { timeoutMs: 60_000 })
  const [g = '', c = ''] = found.stdout.split(/\r?\n/).map((s: string) => s.trim())
  if (g) GIT = g
  if (c) CODE = c
  const top = await git($, ['rev-parse', '--show-toplevel'])
  REPO = top.stdout.trim().replace(/\//g, '\\')
  const url = await git($, ['remote', 'get-url', 'origin'])
  GITHUB = url.stdout.trim().replace(/\.git$/, '')
}

async function refresh($: any) {
    try {
      await findTools($)
      if (!REPO) throw new Error('This folder is not a git repo: open the project folder in VS Code.')
      if (tick++ % FETCH_EVERY === 0) await git($, ['fetch', '--quiet'])

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

      await update($, snapshot, () => ({
        commits, local, ahead: ahead || 0, behind: behind || 0, falseAlarms,
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

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const started = await next(e)
    await $.command.register({
      name: 'updates',
      description: 'Show the live project updates pane (pushes, changed files)',
    })
    void refresh($)
    $.clock.every(REFRESH_MS, () => refresh($))
    void $.ui.open({ id: PANE, title: 'Project updates' })

    return started
  })

  on('command.run', { command: 'updates' }, async $ => {
    await refresh($)
    await $.ui.open({ id: PANE, title: 'Project updates' })

    return { text: 'Project updates pane opened.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button, Link } = $.ui.resolve(e)
    const s = await read($, snapshot)
    const color = (name: string) => (name === 'Dareen' ? '#d0508a' : name === 'Nimer' ? '#3a8fd6' : undefined)

    return (
      <Box flexDirection="column" gap={1}>
        <Box flexDirection="column">
          <Text dimColor>
            Checked {s.checkedAt || '…'} · refreshes every 5 s
          </Text>
          {s.behind > 0 && <Text color="warning">⬇ {s.behind} new from GitHub, not pulled yet</Text>}
          {s.ahead > 0 && <Text color="warning">⬆ {s.ahead} commit(s) here not pushed yet</Text>}
          {s.ahead === 0 && s.behind === 0 && s.checkedAt !== '' && <Text color="success">In sync with GitHub</Text>}
          {s.error && <Text color="error">{s.error}</Text>}
        </Box>

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
