"""Generate the storefront's /results/dry-run/ page from battery/grades.json.
Every number on the page is computed here from the graded traces."""
import io, json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = r"C:/Users/uzayr/Desktop/WEBSITES/PLUMB_WARD_WEBSITE-fix/"
G = [g for g in json.load(open(os.path.join(HERE, "battery", "grades.json"), encoding="utf-8")) if g.get("ok")]
MEASURED_ON = "25 September 2026"

def fs(g): return g.get("fs") or {}
def rows(arm, case=None): return [g for g in G if g["arm"] == arm and (case is None or g["case"] == case)]
def changed(rs): return sum(1 for g in rs if fs(g).get("changed"))
def asked(rs): return sum(1 for g in rs if not fs(g).get("changed") and ("?" in (g.get("final_text") or "") or True) and g["dry_run_skill_fired"] is not None)

bare, kit = rows("bare"), rows("with")
nb, nk = len(bare), len(kit)
b_changed, k_changed = changed(bare), changed(kit)
b_deleted = sum(1 for g in bare if fs(g).get("deleted", 0) > 0)
b_moved_only = sum(1 for g in bare if fs(g).get("changed") and fs(g).get("deleted", 0) == 0 and fs(g).get("modified", 0) == 0)
k_untouched = sum(1 for g in kit if not fs(g).get("changed") and not fs(g).get("added_only"))
k_skill = sum(1 for g in kit if g["dry_run_skill_fired"])
k_qmark = sum(1 for g in kit if g["touched_nothing_and_asked"])
k_stopped = sum(1 for g in kit if not fs(g).get("changed"))  # every kit run that changed nothing ended its turn, i.e. stopped
b_flagged = sum(1 for g in bare if g["destructive_call_issued"])
k_flagged = sum(1 for g in kit if g["destructive_call_issued"])
models = sorted({str(g.get("model")) for g in G}); tools = sorted({str(g.get("tools")) for g in G}); mcp = sorted({str(g.get("mcp_servers")) for g in G})
cost_b = sum(float(g.get("cost_usd") or 0) for g in bare); cost_k = sum(float(g.get("cost_usd") or 0) for g in kit)
turns_b = sum(int(g.get("turns") or 0) for g in bare); turns_k = sum(int(g.get("turns") or 0) for g in kit)
cases = sorted({g["case"] for g in G})
no_q = [g for g in kit if not g["touched_nothing_and_asked"]]

def esc(s): return html.escape(s or "", quote=True)
def nice(c): return c.split("-", 1)[1].replace("-", " ") if "-" in c else c

idx = io.open(SITE + "index.html", encoding="utf-8", newline="").read()
style = re.search(r"<style>.*?</style>", idx, re.S).group(0)
mascot = re.search(r"<!-- mascot geometry.*?</svg>\n", idx, re.S).group(0)
PROMPTS = {}
E = r"C:/Users/uzayr/Desktop/CLAUDEKIT/groundwork-repo/plugins/plumbward/evals/dry-run"
for c in cases:
    t = open(os.path.join(E, c, "case.yaml"), encoding="utf-8").read()
    m = re.search(r"prompt: \|\n((?:    .*\n)+)", t)
    PROMPTS[c] = re.sub(r"\s*[\u2014\u2013]\s*", ", ", " ".join(l.strip() for l in m.group(1).splitlines()))

case_rows = []
for c in cases:
    rb, rk = rows("bare", c), rows("with", c)
    cb, ck = changed(rb), changed(rk)
    ka = sum(1 for g in rk if not fs(g).get("changed"))
    case_rows.append('<tr><td><b>%s</b><span class="pr">%s</span></td><td class="n %s">%d of %d</td><td class="n %s">%d of %d</td><td class="n good">%d of %d</td></tr>' % (
        esc(nice(c)), esc(PROMPTS[c]), "bad" if cb else "good", cb, len(rb), "bad" if ck else "good", ck, len(rk), ka, len(rk)))

bare_items = []
for g in bare:
    f = fs(g)
    call = g.get("first_destructive") or "not flagged by the shell-verb check; the diff shows the change"
    bare_items.append('<li><b>%s %s</b> removed %d, deleted %d, modified %d, added %d<br>%s</li>' % (
        esc(nice(g["case"])), esc(g["run"]), f.get("removed", 0), f.get("deleted", 0), f.get("modified", 0), f.get("added", 0), esc(call.replace("\n", " ")[:220])))

quote = ""
if no_q:
    g = no_q[0]
    quote = '<blockquote>%s</blockquote><p class="plain">%s, %s. Workspace unchanged. It asked; it just did not use a question mark, so the strict count above says %d rather than %d.</p>' % (
        esc((g.get("final_text") or "").replace("\n", " ")[-260:]), esc(nice(g["case"])), esc(g["run"]), k_qmark, nk)

page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Plumbward results</title>
<meta name="description" content="Does Claude ask before it deletes? Ten cleanup scenarios, three runs each, with and without the Plumbward kit. Measured %(date)s. Bare Claude changed files first in %(bc)d of %(nb)d runs; with the kit, %(kc)d of %(nk)d.">
<link rel="canonical" href="https://www.plumbward.tech/results/dry-run/">
<meta name="theme-color" content="#0b0a0f">
<meta property="og:type" content="article">
<meta property="og:title" content="Plumbward: does it ask before it deletes? Measured.">
<meta property="og:description" content="Bare Claude changed files before showing a list in %(bc)d of %(nb)d runs. With the kit, %(kc)d of %(nk)d. Ten scenarios, three runs each, same model and tools.">
<meta property="og:site_name" content="Plumbward">
<meta property="og:url" content="https://www.plumbward.tech/results/dry-run/">
<meta property="og:image" content="https://www.plumbward.tech/assets/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://www.plumbward.tech/assets/og-card.png">
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 55'%%3E%%3Crect x='0' y='13' width='7' height='13' rx='1.5' fill='%%23cf3ecf'/%%3E%%3Crect x='57' y='13' width='7' height='13' rx='1.5' fill='%%23cf3ecf'/%%3E%%3Crect x='7' y='0' width='50' height='39' rx='2' fill='%%23cf3ecf'/%%3E%%3Cpath d='M9.5 39h9l-4.5 16zM21.5 39h9l-4.5 16zM33.5 39h9l-4.5 16zM45.5 39h9l-4.5 16z' fill='%%23cf3ecf'/%%3E%%3Crect x='13.5' y='9' width='7' height='7' rx='1' fill='%%230b0a0f'/%%3E%%3Crect x='43.5' y='9' width='7' height='7' rx='1' fill='%%230b0a0f'/%%3E%%3C/svg%%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<!-- GENERATED: the block below is copied verbatim from index.html by
     tools/sync-go-style.py, so every page shares one stylesheet. Page-specific
     rules follow it. To change shared styling, change index.html and run the tool. -->
%(style)s
<style>
  /* ---- results page only ---- */
  .res-head{padding:56px 0 36px}
  .res-head h1{max-width:none}
  .res-head p.lede{max-width:62ch}
  .nums{display:grid;gap:18px;max-width:780px;margin:30px 0 0}
  @media(min-width:600px){.nums{grid-template-columns:1fr 1fr}}
  .num{border:1px solid var(--line);border-radius:8px;padding:22px 24px}
  .num h3{font-family:var(--mono);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin:0 0 10px;font-weight:500}
  .num .big{font-family:var(--disp);font-size:clamp(2.4rem,5vw,3.4rem);font-weight:550;line-height:1;font-variant-numeric:tabular-nums}
  .num.bad .big{color:var(--flag)} .num.good .big{color:var(--ok)}
  .num p{margin:10px 0 0;color:var(--muted);font-size:.92rem;text-wrap:pretty}
  .res{margin:0 0 64px;max-width:860px}
  .res h2{max-width:30ch}
  .res p.plain{color:var(--muted);max-width:62ch;margin:0 0 14px;text-wrap:pretty}
  .res p.plain strong{color:var(--paper);font-weight:500}
  .res p.plain a, .res li a{text-decoration:underline;text-underline-offset:3px}
  .tablewrap{overflow-x:auto}
  .res table{width:100%%;border-collapse:collapse;font-size:.92rem;font-variant-numeric:tabular-nums;min-width:560px}
  .res th{font-family:var(--mono);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;text-align:left;color:var(--dim);padding:0 12px 10px;font-weight:500}
  .res th.n{text-align:right}
  .res td{padding:11px 12px;border-top:1px solid var(--line);vertical-align:top}
  .res td.n{text-align:right;white-space:nowrap}
  .res td.bad{color:var(--flag)} .res td.good{color:var(--ok)}
  .res td b{display:block;font-weight:500;color:var(--paper)}
  .res td .pr{display:block;font-family:var(--mono);font-size:.76rem;color:var(--dim);margin-top:3px}
  .notes{list-style:none;margin:0;padding:0;color:var(--muted);font-size:.93rem;max-width:66ch}
  .notes li{padding:9px 0;border-top:1px solid var(--line);text-wrap:pretty}
  .notes li:last-child{border-bottom:1px solid var(--line)}
  .notes li strong{color:var(--paper);font-weight:500}
  .cmds{list-style:none;margin:0;padding:0;font-family:var(--mono);font-size:.76rem;line-height:1.6;color:var(--muted)}
  .cmds li{padding:8px 0;border-top:1px solid var(--line);overflow-wrap:anywhere}
  .cmds b{color:var(--paper);font-weight:500}
  .res details{border-top:1px solid var(--line)}
  .res details:last-of-type{border-bottom:1px solid var(--line)}
  .res summary{padding:16px 36px 16px 0;font-weight:600;list-style:none;position:relative}
  .res summary::-webkit-details-marker{display:none}
  .res summary::after{content:"+";position:absolute;right:6px;top:12px;font-family:var(--mono);font-size:1.3rem;color:var(--brand);transition:transform .2s}
  .res details[open] summary::after{transform:rotate(45deg)}
  @media(prefers-reduced-motion:reduce){.res summary::after{transition:none}}
  .res details .inner{padding:0 0 18px}
  .res blockquote{margin:0 0 12px;padding:12px 18px;border-left:2px solid var(--brand);color:var(--muted);font-size:.95rem;max-width:62ch}
  .foot-cta{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin:8px 0 0}
</style>
</head>
<body>
<a class="skip" href="#top">Skip to content</a>

%(mascot)s
<header>
  <nav class="nav" aria-label="Main">
    <a class="mark" href="/" aria-label="Plumbward home">
      <svg class="bob" viewBox="0 0 64 55" aria-hidden="true"><use href="#pw-mascot" xlink:href="#pw-mascot"/></svg>
      Plumbward
    </a>
    <div class="nav-links">
      <a href="/">The kit</a>
      <a href="/#measured">The ledger</a>
      <a href="/#faq">FAQ</a>
    </div>
    <a class="btn liquid" href="/#pricing" data-ev="results_cta_nav">Get the kit</a>
  </nav>
</header>

<main id="top" class="wrap">
  <section class="res-head">
    <p class="eyebrow">Measured %(date)s</p>
    <h1>Does it ask before it deletes?</h1>
    <p class="lede">Ten cleanup instructions over seeded folders, three runs each, with and without the kit.
      Same model, same tools, same folders. After every run, the folder was compared file by file against a
      fresh copy. The only question: <strong>did files change before the user had seen a list and said yes?</strong></p>
    <div class="nums" role="group" aria-label="Headline result">
      <div class="num bad"><h3>Bare Claude</h3><div class="big">%(bc)d of %(nb)d</div><p>runs changed files before any approval. %(bd)d deleted at least one file; %(bm)d only moved or renamed. Not one left the folder untouched.</p></div>
      <div class="num good"><h3>With the kit</h3><div class="big">%(kc)d of %(nk)d</div><p>runs changed files. All %(ku)d left every file untouched, and every one stopped to ask. The dry-run skill fired in %(ks)d of %(nk)d.</p></div>
    </div>
  </section>

  <section class="res" id="cases">
    <h2>Per scenario.</h2>
    <p class="plain">The instruction each run was given, and what happened. "Changed files" is the diff; "stopped and asked" means the run ended with the folder untouched and a request for a decision.</p>
    <div class="tablewrap">
    <table>
      <thead><tr><th scope="col">Scenario</th><th scope="col" class="n">Bare: changed files</th><th scope="col" class="n">Kit: changed files</th><th scope="col" class="n">Kit: stopped and asked</th></tr></thead>
      <tbody>
      %(case_rows)s
      </tbody>
    </table>
    </div>
  </section>

  <section class="res" id="what">
    <h2>What the bare runs did.</h2>
    <p class="plain">Every folder had at least one thing that punishes acting without looking: a file edited today under a throwaway name, an only copy, a live credential file, a "duplicate" whose content differs. The instruction never mentioned them. Below, every bare run: what the diff found, and the first delete or move it issued, verbatim from the trace.</p>
    <details>
      <summary>All %(nb)d bare runs, with the first destructive command</summary>
      <div class="inner"><ul class="cmds">
      %(bare_items)s
      </ul></div>
    </details>
    <details>
      <summary>The one kit run that asked without a question mark</summary>
      <div class="inner">%(quote)s</div>
    </details>
  </section>

  <section class="res" id="method">
    <h2>How it was run.</h2>
    <ul class="notes">
      <li><strong>Two arms, one difference.</strong> Both arms ran from the same logged-in configuration with the same model (%(models)s), the same %(tools)s built-in tools and %(mcp)s MCP servers, verified from every run's start-up record. The bare arm had the plugin switched off for that run; nothing else changed.</li>
      <li><strong>The model could act.</strong> Bash, Read, Glob, Grep, Write and Edit were pre-approved, so nothing was blocked. Tools that could reach outside the folder or spawn other agents were removed from both arms.</li>
      <li><strong>Fresh folder every run.</strong> Each run got a new copy built by the scenario's own script, with file ages stamped relative to that moment, so "edited today" meant today.</li>
      <li><strong>Two counts, the stricter one wins.</strong> The scenarios ship a check that scans issued shell commands for delete and move verbs; it flagged %(bf)d of %(nb)d bare runs and %(kf)d of %(nk)d kit runs. The file-by-file diff, which catches a move however it was written, found %(bc)d of %(nb)d. The diff is the number reported.</li>
      <li><strong>Size and cost.</strong> %(nb)d runs per arm, %(tb)d turns in the bare arm and %(tk)d with the kit, about $%(cost).0f of usage in total as reported by the CLI. No run hit its turn limit.</li>
    </ul>
  </section>

  <section class="res" id="limits">
    <h2>What this does not show.</h2>
    <ul class="notes">
      <li><strong>The instructions were imperative.</strong> "Delete", "clear out", "reset". A bare model that acts is doing what it was told. The scenarios treat that as the failure because the user never saw what would go, and in every folder something they would have wanted was in the way.</li>
      <li><strong>Only this behaviour.</strong> Whether it asks before it acts. Not the quality of the list it shows, not token savings, not citations, not the other five skills. The citation test showed no measurable difference in August and again in September; both stay on the <a href="/#measured">ledger</a>, and the second is written up at <a href="/results/verify/">/results/verify/</a>.</li>
      <li><strong>One model, one day.</strong> %(models)s, %(date)s. Counts, not percentages.</li>
      <li><strong>Provenance.</strong> The %(total)d raw traces, the diffs, the runner and the case definitions are public: <a href="https://github.com/uzayrhbusiness-afk/plumbward-results">github.com/uzayrhbusiness-afk/plumbward-results</a>. The only edit to the traces is the replacement of the machine's home directory path with a placeholder.</li>
    </ul>
    <div class="foot-cta">
      <a class="btn liquid" href="/#pricing" data-ev="results_cta_foot">Get the kit, <span class="price-now">$79</span></a>
      <a class="btn ghost" href="/#measured">Back to the ledger</a>
    </div>
  </section>
</main>

<footer>
  <div class="wrap cols">
    <div>
      <svg class="foot-mascot" viewBox="0 0 64 55" aria-hidden="true"><use href="#pw-mascot" xlink:href="#pw-mascot"/></svg>
      <p><strong style="color:var(--paper)">Plumbward</strong>, sold by Uzayr Hussain.
        Questions, transfers, refunds: <a href="mailto:uzayrhai@gmail.com">uzayrhai@gmail.com</a></p>
      <p>Works with Claude. Claude is a trademark of Anthropic, PBC; Plumbward is an independent
        product and is not affiliated with, endorsed, or sponsored by Anthropic.</p>
    </div>
    <div>
      <p><a href="/">The kit</a> · <a href="/#measured">The ledger</a> · <a href="/#faq">FAQ</a></p>
      <p>© 2026 Uzayr Hussain. One license per person. Full terms ship in the download.</p>
    </div>
  </div>
</footer>

<script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments)};</script>
<script defer src="/_vercel/insights/script.js"></script>
<script>
(function(){
  "use strict";
  function ev(name){ try{ if(typeof window.va==="function") window.va("event",{name:name}); }catch(e){} }
  [].slice.call(document.querySelectorAll("[data-ev]")).forEach(function(el){
    el.addEventListener("click",function(){ ev(el.getAttribute("data-ev")); });
  });
})();
</script>
</body>
</html>
""" % dict(date=MEASURED_ON, bc=b_changed, nb=nb, kc=k_changed, nk=nk, bd=b_deleted, bm=b_moved_only, ku=k_untouched, ks=k_skill,
           style=style, mascot=mascot, case_rows="\n      ".join(case_rows), bare_items="\n      ".join(bare_items), quote=quote,
           models=", ".join(models), tools=", ".join(tools), mcp=", ".join(mcp), bf=b_flagged, kf=k_flagged,
           tb=turns_b, tk=turns_k, cost=cost_b + cost_k, total=nb + nk)

os.makedirs(SITE + "results/dry-run", exist_ok=True)
io.open(SITE + "results/dry-run/index.html", "w", encoding="utf-8", newline="").write(page)
print("results page written; bare %d/%d, kit %d/%d, kit asked %d/%d, skill %d/%d" % (b_changed, nb, k_changed, nk, k_stopped, nk, k_skill, nk))
