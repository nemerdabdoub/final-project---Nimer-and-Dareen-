import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

const PANE = 'improvements'
const STORE_KEY = 'improve-done'

type Item = { id: string; text: string; why: string }
type Group = { title: string; items: Item[] }

// What to improve, from the M05 results (22.11) and the plan. Tick an item to mark it done (kept across sessions).
const GROUPS: Group[] = [
  {
    title: 'Now, before Monday 12:00',
    items: [
      { id: 'login', text: 'One-time GitHub token sign-in', why: 'every push fails without it; auto-push in the panel waits for it' },
      { id: 'winner', text: 'Winner call 17:30: propose YOLO11n', why: 'no model reached 90%; YOLO11n is the most accurate (85.4%) and fastest (21 FPS)' },
      { id: 'demo', text: 'Check Dareen\'s demo video: 3 lines (works / fails / why)', why: 'plan, Sun 18:30' },
      { id: 'summary', text: 'One-page summary: Tables A + B, winner, 2 screenshots', why: 'plan, Mon 12:00' },
      { id: 'ailog', text: 'Add your line to the AI log (5_LOGS/Project_logs.xlsx)', why: 'plan, by Mon 12:00' },
      { id: 'm03table', text: 'Fill the M03 moves table from the 12.11 video', why: 'the table in M03_control_from_code.md is still empty' },
    ],
  },
  {
    title: 'Detection: below the 90% target (85%)',
    items: [
      { id: 'conf', text: 'Try a lower confidence (CONF 0.25 → 0.15)', why: 'misses are small or partly hidden people; precision is 94-97%, so there is room' },
      { id: 'imgsz', text: 'Try a bigger image size (imgsz 800) for Table A only', why: 'small far-away people; costs speed' },
      { id: 'yolo11s', text: 'Check YOLO11s (one size up)', why: 'more accurate, still maybe ~10 FPS on the laptop' },
      { id: 'finetune', text: 'Fine-tune YOLO11n on our 152 labelled frames', why: 'learns this hall, the drone angle and the app overlay' },
    ],
  },
  {
    title: 'The SAME person: the hybrid misses 26% of the user frames',
    items: [
      { id: 'head', text: 'Loosen the head check (HEAD_PART 0.35 → 0.45, 3% → 2%)', why: 'misses = frames where the turban is not seen on the head box' },
      { id: 'fallback', text: 'Longer fallback (1 s → 2 s) or a tracker (ByteTrack / BoT-SORT)', why: 'keep the same person when the turban is lost for a moment (M06)' },
      { id: 'hand', text: 'Ignore boxes that are huge or touch the bottom edge', why: 'both hybrid false alarms (7.1%) were a hand in front of the lens' },
      { id: 'reid', text: 'Second characteristic: clothes colours (re-ID) or an ArUco marker', why: 'without the turban the hybrid finds nobody (clip 154124)' },
    ],
  },
  {
    title: 'Tests and data',
    items: [
      { id: 'dark', text: 'A real low-light test (not only x0.35 darkened copies)', why: 'darkened copies are a stand-in; real dark adds noise and blur' },
      { id: 'more', text: 'More frames (the note says ~200; we have 152), more clips without the actor', why: 'false alarm % rests on only 28 frames' },
      { id: 'warmup', text: 'Warm-up frame before timing', why: 'ms/frame spikes (one hybrid run showed 462 ms)' },
      { id: 'latency', text: 'End-to-end delay with detection in the loop (latency_test.py)', why: 'M06 reacts to what it sees; speed alone is not the delay' },
    ],
  },
  {
    title: 'Housekeeping',
    items: [
      { id: 'gitattr', text: 'Add .gitattributes (line endings)', why: 'removes the LF/CRLF warnings on every commit' },
      { id: 'panel', text: 'Dareen installs the Project updates panel', why: '/plugin install project-updates --marketplace nemerdabdoub/final-project---Nimer-and-Dareen-' },
      { id: 'date', text: 'Put the mid-project presentation date in the log', why: 'still blank in 4_DOCUMENTS/mid_project_presentation_log.md' },
    ],
  },
]

const done = atom({ plugin: 'project-updates', key: 'improveDone' } as const, [] as string[], {
  shape: 'improve-1',
})

async function toggle($: any, id: string) {
  await update($, done, list => (list.includes(id) ? list.filter(x => x !== id) : [...list, id]))
  await $.store.set(STORE_KEY, await read($, done))
}

// Called from register.tsx's session.start (one session.start hook per plugin).
export async function startImprove($: any) {
  const saved = await $.store.get(STORE_KEY)
  if (Array.isArray(saved)) await update($, done, () => saved.filter((x): x is string => typeof x === 'string'))
  await $.command.register({ name: 'improve', description: 'Show the list of things to improve (tick them off)' })
  void $.ui.open({ id: PANE, title: 'What to improve' })
}

export const registerImprove: Register = on => {

  on('command.run', { command: 'improve' }, async $ => {
    await $.ui.open({ id: PANE, title: 'What to improve' })

    return { text: 'Improvements list opened.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Text, Button } = $.ui.resolve(e)
    const ticked = await read($, done)
    const total = GROUPS.reduce((n, g) => n + g.items.length, 0)
    const count = GROUPS.reduce((n, g) => n + g.items.filter(i => ticked.includes(i.id)).length, 0)

    return (
      <Box flexDirection="column" gap={1}>
        <Text dimColor>{count}/{total} done · click an item to tick it · /improve reopens this</Text>
        {GROUPS.map(g => (
          <Box key={g.title} flexDirection="column">
            <Text bold>{g.title}</Text>
            {g.items.map(i => {
              const isDone = ticked.includes(i.id)
              return (
                <Box key={i.id} flexDirection="column">
                  <Button key={'imp:' + i.id} onPress={() => toggle($, i.id)}>
                    <Text color={isDone ? 'success' : undefined} strikethrough={isDone}>
                      {isDone ? '☑' : '☐'} {i.text}
                    </Text>
                  </Button>
                  {!isDone && <Text dimColor>   {i.why}</Text>}
                </Box>
              )
            })}
          </Box>
        ))}
      </Box>
    )
  })
}
