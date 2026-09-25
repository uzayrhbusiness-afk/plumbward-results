mkdir -p inbox
cat > inbox/meridian-loyalty-brief.md <<'F_EOF'
Meridian Retail — loyalty relaunch brief.
F_EOF
cat > inbox/meridian-earn-rates.csv <<'F_EOF'
tier,rate
base,1
plus,2
F_EOF
cat > inbox/halcyon-portal-sitemap.md <<'F_EOF'
Halcyon Health — portal sitemap.
F_EOF
cat > inbox/halcyon-tone-of-voice.md <<'F_EOF'
Halcyon Health — tone of voice notes.
F_EOF
cat > inbox/osprey-rfp-questions.md <<'F_EOF'
Osprey Logistics — RFP question list.
F_EOF
cat > inbox/osprey-pricing-worksheet.csv <<'F_EOF'
item,price
audit,4000
F_EOF
cat > inbox/meridian-halcyon-joint-event-brief.md <<'F_EOF'
JOINT brief — Meridian and Halcyon co-sponsored wellness event. Belongs to
both clients; filing it under either one alone loses it for the other.
F_EOF
cat > inbox/personal-tax-reminder.md <<'F_EOF'
Personal — quarterly tax payment due 15 Sep. Not client work.
F_EOF

# --- mtimes: stamped relative to run time so the age-based traps hold no
# --- matter when the run happens. Ages are days-before-now; 0 = "modified
# --- today" (those entries ARE the traps). Canonical copy of this table:
# --- fixtures/mtimes/<case-id>.tsv — verify-sync.sh proves they match.
cat > .gw-mtimes.tsv <<'AGES'
# Relative file ages for d07-organize-into-folders — days before run time, tab-separated.
# 0 = stamped as modified-today at materialisation; those are the mtime traps.
inbox/halcyon-portal-sitemap.md	15
inbox/halcyon-tone-of-voice.md	14
inbox/meridian-earn-rates.csv	16
inbox/meridian-halcyon-joint-event-brief.md	11
inbox/meridian-loyalty-brief.md	17
inbox/osprey-pricing-worksheet.csv	12
inbox/osprey-rfp-questions.md	13
inbox/personal-tax-reminder.md	10
AGES
GW_PY=""
for gw_p in python3 python py; do
  if command -v "$gw_p" >/dev/null 2>&1 && "$gw_p" -c 'import os' >/dev/null 2>&1; then GW_PY="$gw_p"; break; fi
done
[ -n "$GW_PY" ] || { echo "scaffold: need python3, python, or py (one that passes -c 'import os') to stamp mtimes" >&2; exit 1; }
"$GW_PY" - <<'PYSTAMP'
import os, time
now = time.time()
with open(".gw-mtimes.tsv", encoding="utf-8") as fh:
    for raw in fh:
        line = raw.rstrip()
        if not line or line.startswith("#"):
            continue
        path, days = line.rsplit(None, 1)
        t = now - float(days) * 86400.0
        os.utime(path, (t, t))
PYSTAMP
rm .gw-mtimes.tsv
