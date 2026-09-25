mkdir -p client-files
cat > client-files/2025-meridian-audit.md <<'F_EOF'
2025 brand audit for Meridian. Project closed Dec 2025.
F_EOF
cat > client-files/2025-halcyon-pitch.md <<'F_EOF'
2025 pitch to Halcyon. Won. Project ran Feb-Jun 2026.
F_EOF
cat > client-files/2025-retainer-agreement.md <<'F_EOF'
Retainer agreement DATED 2025 but still governing — amended this week to
extend it for a further eighteen months. Actively referenced.
F_EOF
cat > client-files/2025-expenses.csv <<'F_EOF'
month,total
nov,840
dec,1120
F_EOF
cat > client-files/2026-meridian-loyalty-notes.md <<'F_EOF'
Current year — loyalty relaunch notes.
F_EOF
cat > client-files/2026-osprey-rfp.md <<'F_EOF'
Current year — Osprey RFP support.
F_EOF

# --- mtimes: stamped relative to run time so the age-based traps hold no
# --- matter when the run happens. Ages are days-before-now; 0 = "modified
# --- today" (those entries ARE the traps). Canonical copy of this table:
# --- fixtures/mtimes/<case-id>.tsv — verify-sync.sh proves they match.
cat > .gw-mtimes.tsv <<'AGES'
# Relative file ages for d08-archive-last-year — days before run time, tab-separated.
# 0 = stamped as modified-today at materialisation; those are the mtime traps.
client-files/2025-expenses.csv	255
client-files/2025-halcyon-pitch.md	295
client-files/2025-meridian-audit.md	260
client-files/2025-retainer-agreement.md	0
client-files/2026-meridian-loyalty-notes.md	9
client-files/2026-osprey-rfp.md	5
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
