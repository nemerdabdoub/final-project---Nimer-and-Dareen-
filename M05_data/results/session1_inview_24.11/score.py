# Score session 1: Claude's by-eye in-view labels vs the detector decision (detector.csv).
# Y = user in view with her head visible; P = partly (sleeve/hand close-up, or head cut at the frame edge); N = not in view.
import csv, math, sys
from pathlib import Path

d = Path(sys.argv[1])
def rng(spec):
    s = set()
    for part in spec.split(","):
        a, _, b = part.partition("-"); s.update(range(int(a), int(b or a) + 1))
    return s
Y = rng("0-19,23-25,38-58,71-78,107-119,146-147,185-186,194-203,211-212,286-301")
P = rng("79-82,88-97,105-106,150-152,155,173,182-184,187,285")

rows = list(csv.DictReader(open(d / "detector.csv")))
for r in rows:
    i = int(r["idx"]); r["in_view"] = "Y" if i in Y else "P" if i in P else "N"
with open(d / "session1_inview_labels.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; c = (p + z*z/(2*n)) / (1 + z*z/n); h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
    return (100*(c-h), 100*(c+h))

for lab in "YPN":
    g = [r for r in rows if r["in_view"] == lab]
    k = sum(r["detector"] != "none" for r in g)
    lo, hi = wilson(k, len(g))
    print(f"{lab}: n={len(g):3d}  user picked {k:3d} ({100*k/max(1,len(g)):.1f}%, 95% CI {lo:.1f}-{hi:.1f})  "
          f"colour={sum(r['detector']=='colour' for r in g)} kept={sum(r['detector']=='kept' for r in g)}")
print("picks on N frames (possible wrong person):", [r["idx"] for r in rows if r["in_view"] == "N" and r["detector"] != "none"])
print("misses on Y frames:", [r["idx"] for r in rows if r["in_view"] == "Y" and r["detector"] == "none"])
