"""Heading-aware count of print-ready citations in each verify answer. A citation
line counts as marked if the line itself or the nearest heading above it carries
an unverified/check/leads marker. Writes battery-verify/heading-aware.json with
per-arm counts and verbatim examples of citations marked by neither."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "battery-verify")
G = [g for g in json.load(open(os.path.join(D, "grades.json"), encoding="utf-8")) if g.get("ok")]
PR = re.compile(r"(?=.*\b(1[5-9]\d\d|20\d\d)\b)(?=.*([“\"*_][^”\"*_\n]{6,}[”\"*_]))(?=.*(\b[A-Z][a-z]+, [A-Z]\.|\b[A-Z][a-z]+ [A-Z][a-z]+,|Journal|Press|Vol\.|vol\.|pp\.|Proceedings|Review|Transactions|Magazine|Gazette|Bulletin|Quarterly|Annals|doi|https?://))")
MK = re.compile(r"unverified|not verified|couldn.t verify|could not (be )?verif|cannot verify|can.t verify|unconfirmed|from memory|recall|\bcheck\b|\bconfirm\b|\bverify\b|\bshaky\b|\buncertain\b|\bnot sure\b|\bI believe\b|\bI think\b|\bleads?\b|do not print|not citations|\[[^\]]*\?[^\]]*\]", re.I)


def heading_above(lines, i):
    for h in reversed(lines[:i]):
        s = h.strip()
        if s.startswith("#") or (s.startswith("**") and s.endswith("**")) or s.endswith(":"):
            return s
    return ""


res = {"examples": {}}
for arm in ("bare", "with"):
    tot = unm_line = unm_both = runs_unm = 0
    ex = []
    for g in G:
        if g["arm"] != arm:
            continue
        lines = g["final_text"].splitlines()
        u = 0
        for i, l in enumerate(lines):
            if not PR.search(l):
                continue
            tot += 1
            h = heading_above(lines, i)
            lm, hm = bool(MK.search(l)), bool(MK.search(h))
            if not lm:
                unm_line += 1
            if not lm and not hm:
                unm_both += 1
                u += 1
                if len(ex) < 6:
                    ex.append((h.strip("# ").strip(), l.strip(), g["case"], g["run"]))
        runs_unm += int(u > 0)
    res[arm] = {"lines": tot, "unmarked_line": unm_line, "unmarked_line_and_heading": unm_both, "runs_with_unmarked": runs_unm}
    res["examples"][arm] = ex
json.dump(res, open(os.path.join(D, "heading-aware.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print({a: res[a] for a in ("bare", "with")})
