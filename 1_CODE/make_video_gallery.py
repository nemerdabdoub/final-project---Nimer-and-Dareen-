"""make_video_gallery.py - Project 3760: ONE visual page with every project video on this laptop.

Builds 3_EVIDENCE/ALL_VIDEOS.html (+ 3_EVIDENCE/_thumbs/): thumbnail, date, length, size and category for every .mp4
under 3_EVIDENCE, grouped (first flights, lab clips, field footage, M05 demos, M06 tracking). Click a picture = play.
Nothing is copied and nothing goes into git (3_EVIDENCE is ignored). Re-run after new videos / G:sync.

Use (from 1_CODE):  python make_video_gallery.py      then open ../3_EVIDENCE/ALL_VIDEOS.html
"""
import html, sys, datetime
from pathlib import Path
import cv2

repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent; ev = repo / "3_EVIDENCE"; thumbs = ev / "_thumbs"; thumbs.mkdir(exist_ok=True)

def category(p: Path) -> str:
    s = str(p).lower()
    if "m06_tracking" in s: return "4 · M06 tracking / follow"
    if "m05_user_detection" in s or "demo_" in p.name.lower(): return "3 · M05 detection demos"
    if "2026-11-22" in s: return "2 · Field footage 22.11 (Med Faculty, sessions)"
    if "2026-11-20" in s: return "1 · Lab clips 20.11 (turban actor)"
    if "2026-11-07" in s or "2026-10-20" in s or "2026-11-12" in s: return "0 · First flights (Oct–Nov)"
    return "5 · Other"

items = []
for p in sorted(ev.rglob("*.mp4")):
    if "_thumbs" in p.parts: continue
    c = cv2.VideoCapture(str(p)); n = c.get(7) or 0; fps = c.get(5) or 25
    fourcc = int(c.get(6)).to_bytes(4, "little").decode("latin1", "ignore").strip("\x00")
    c.set(1, int(n * 0.3)); ok, fr = c.read(); c.release()
    t = thumbs / (p.stem + ".jpg")
    if ok:
        h, w = fr.shape[:2]; fr = cv2.resize(fr, (320, int(320 * h / w))); cv2.imwrite(str(t), fr, [cv2.IMWRITE_JPEG_QUALITY, 80])
    secs = n / fps if fps else 0
    items.append(dict(p=p, cat=category(p), t=t if ok else None, secs=secs, mb=p.stat().st_size / 1e6,
                      date=datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%d.%m.%Y %H:%M"), codec=fourcc))

cats = sorted(set(i["cat"] for i in items))
css = """
:root{--bg:#f6f7f9;--card:#fff;--ink:#14233c;--mute:#5b6676;--line:#e3e7ec;--acc:#b01e3c}
@media (prefers-color-scheme:dark){:root{--bg:#0f141b;--card:#18202b;--ink:#e8edf3;--mute:#9aa6b4;--line:#263140}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 'Segoe UI',system-ui,sans-serif}
header{padding:22px 24px 10px}h1{margin:0;font-size:24px}header p{margin:4px 0 0;color:var(--mute)}
nav{position:sticky;top:0;background:var(--bg);padding:8px 24px;border-bottom:1px solid var(--line);display:flex;gap:8px;flex-wrap:wrap;z-index:2}
nav a{color:var(--ink);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:3px 12px;font-size:13px}
h2{margin:22px 24px 10px;font-size:18px;border-left:4px solid var(--acc);padding-left:10px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;padding:0 24px 10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.card a{color:inherit;text-decoration:none}.card img{width:100%;display:block;aspect-ratio:16/9;object-fit:cover;background:#000}
.meta{padding:8px 10px}.name{font-weight:600;font-size:13px;word-break:break-all}.sub{color:var(--mute);font-size:12px;margin-top:3px}
.badge{display:inline-block;font-size:11px;border-radius:4px;padding:0 5px;margin-left:4px;background:var(--line)}
"""
out = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
       f"<title>Project videos</title><style>{css}</style></head><body><header><h1>All project videos</h1>"
       f"<p>{len(items)} videos · {sum(i['mb'] for i in items)/1000:.1f} GB · built {datetime.datetime.now():%d.%m.%Y %H:%M} · click a picture to play it (opens in your video player)</p></header><nav>"]
out += [f"<a href='#c{k}'>{html.escape(c)} ({sum(i['cat']==c for i in items)})</a>" for k, c in enumerate(cats)]
out.append("</nav>")
for k, c in enumerate(cats):
    out.append(f"<h2 id='c{k}'>{html.escape(c)}</h2><div class='grid'>")
    for i in sorted([i for i in items if i["cat"] == c], key=lambda i: i["date"], reverse=True):
        rel = i["p"].relative_to(ev).as_posix(); th = i["t"].relative_to(ev).as_posix() if i["t"] else ""
        m, s = divmod(int(i["secs"]), 60)
        out.append(f"<div class='card'><a href='{html.escape(rel)}'><img src='{html.escape(th)}' alt='' loading='lazy'></a>"
                   f"<div class='meta'><div class='name'>{html.escape(i['p'].name)}</div>"
                   f"<div class='sub'>{i['date']} · {m}:{s:02d} min · {i['mb']:.0f} MB<span class='badge'>{html.escape(i['codec'])}</span></div>"
                   f"<div class='sub'>{html.escape(i['p'].parent.relative_to(ev).as_posix())}</div></div></div>")
    out.append("</div>")
out.append("</body></html>")
(ev / "ALL_VIDEOS.html").write_text("\n".join(out), encoding="utf-8")
print(len(items), "videos ->", ev / "ALL_VIDEOS.html")
for c in cats: print(" ", c, sum(i["cat"] == c for i in items))

