"""Recompute priority_words in a keyword file from its `terms` (lower rank = more searched).
Usage: python rebuild_priority.py glass-kundan-bangles.json"""
import json, re, sys
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
stop = {"for", "women", "set", "of", "and", "the", "ki"}
best = {}
for t, r in d["terms"].items():
    for w in re.findall(r"[a-z]+", t):
        if w in stop:
            continue
        if w not in best or r < best[w][0]:
            best[w] = (r, t)
d["priority_words"] = [{"word": w, "best_rank": r, "from": t} for w, (r, t) in sorted(best.items(), key=lambda x: x[1][0])]
json.dump(d, open(p, "w", encoding="utf-8"), indent=1)
print(len(d["priority_words"]), "words")
