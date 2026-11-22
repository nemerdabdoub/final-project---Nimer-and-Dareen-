import { atom, read, update } from 'claude-code'
import type { ProcessRunResult, Register } from 'claude-code'

import type { Commit, LocalFile, Snapshot } from '../types'

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
const REFRESH_MS = 15_000
const FETCH_EVERY = 8 // fetch from GitHub every 8th refresh (2 minutes)

const empty: Snapshot = { commits: [], local: [], ahead: 0, behind: 0, checkedAt: '' }
const snapshot = atom({ plugin: 'project-updates', key: 'snapshot' } as const, empty, {
  shape: 'snapshot-1',
})

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

      await update($, snapshot, () => ({
        commits, local, ahead: ahead || 0, behind: behind || 0,
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
            Checked {s.checkedAt || '…'} · refreshes every 15 s
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
