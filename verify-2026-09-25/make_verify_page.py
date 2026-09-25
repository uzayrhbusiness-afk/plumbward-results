"""Generate the storefront's /results/verify/ page from battery-verify/*.json.
Every number on the page is computed here."""
import io, json, os, re, html, math

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "battery-verify")
SITE = r"C:/Users/uzayr/Desktop/WEBSITES/PLUMB_WARD_WEBSITE-fix/"
G = [g for g in json.load(open(os.path.join(D, "grades.json"), encoding="utf-8")) if g.get("ok")]
HA = json.load(open(os.path.join(D, "heading-aware.json"), encoding="utf-8"))
MEASURED_ON = "25 September 2026"
NU, US = "no-unmarked-citations", "useful-despite-honesty"

def esc(s): return html.escape((s or "").replace("—", " - ").replace("–", " - "), quote=True)   # site rule: no em or en dashes in visible text
def rows(arm, case=None): return [g for g in G if g["arm"] == arm and (case is None or g["case"] == case)]
def verdict(g, n): return (g.get("judges") or {}).get(n, {}).get("verdict")
def votes(g, n): return (g.get("judges") or {}).get(n, {}).get("votes", [])
def cnt(rs, f): return sum(1 for g in rs if f(g))
def nice(c): return c.split("-", 1)[1].replace("-", " ") if "-" in c else c

S = {}
for a in ("bare", "with"):
    rs = rows(a)
    S[a] = dict(runs=len(rs), nu=cnt(rs, lambda g: verdict(g, NU) == "PASS"), us=cnt(rs, lambda g: verdict(g, US) == "PASS"),
                unanimous=cnt(rs, lambda g: len(set(votes(g, NU))) == 1), dissent=cnt(rs, lambda g: "FAIL" in votes(g, NU)),
                regex=cnt(rs, lambda g: g.get("regex_pass")), skill=cnt(rs, lambda g: g.get("verify_skill_fired")),
                web=cnt(rs, lambda g: (g.get("web_attempted") or 0) > 0), denials=sum(g.get("permission_denials") or 0 for g in rs),
                turns=sum(int(g.get("turns") or 0) for g in rs), cost=sum(float(g.get("cost_usd") or 0) for g in rs),
                maxturns=cnt(rs, lambda g: g.get("result_subtype") == "error_max_turns"))
b, w = S["bare"], S["with"]
cases = sorted({g["case"] for g in G})
wins = losses = ties = 0
per = []
for c in cases:
    sb = cnt(rows("bare", c), lambda g: verdict(g, NU) == "PASS"); sw = cnt(rows("with", c), lambda g: verdict(g, NU) == "PASS")
    ub = cnt(rows("bare", c), lambda g: verdict(g, US) == "PASS"); uw = cnt(rows("with", c), lambda g: verdict(g, US) == "PASS")
    db = cnt(rows("bare", c), lambda g: "FAIL" in votes(g, NU)); dw = cnt(rows("with", c), lambda g: "FAIL" in votes(g, NU))
    n = len(rows("bare", c))
    wins += sw > sb; losses += sw < sb; ties += sw == sb
    per.append((c, sb, sw, ub, uw, db, dw, n))
models = sorted({str(g.get("model")) for g in G}); tools = sorted({str(g.get("tools")) for g in G}); mcp = sorted({str(g.get("mcp_servers")) for g in G})

idx = io.open(SITE + "index.html", encoding="utf-8", newline="").read()
style = re.search(r"<style>.*?</style>", idx, re.S).group(0)
mascot = re.search(r"<!-- mascot geometry.*?</svg>\n", idx, re.S).group(0)

case_rows = "\n      ".join('<tr><td><b>%s</b></td><td class="n">%d of %d</td><td class="n">%d of %d</td><td class="n">%d of %d</td><td class="n">%d of %d</td><td class="n %s">%d</td><td class="n %s">%d</td></tr>' % (
    esc(nice(c)), sb, n, sw, n, ub, n, uw, n, "bad" if db else "", db, "bad" if dw else "", dw) for c, sb, sw, ub, uw, db, dw, n in per)
ex_items = []
for arm, lab in (("bare", "bare Claude"), ("with", "with the kit")):
    for h, l, c, r in HA["examples"].get(arm, [])[:4]:
        ex_items.append('<li><b>%s, %s %s</b> under &ldquo;%s&rdquo;<br>%s</li>' % (esc(lab), esc(nice(c)), esc(r), esc(h[:90]), esc(l[:220])))

page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark">
<title>Plumbward results</title>
<meta name="description" content="Does Claude invent citations, and does the kit change that? Twenty topics, two runs each, with and without the kit, judged by a separate model. Measured %(date)s. No difference on the grader; the kit printed fewer unverifiable citations and marked more of them.">
<link rel="canonical" href="https://www.plumbward.tech/results/verify/">
<meta name="theme-color" content="#0b0a0f">
<meta property="og:type" content="article">
<meta property="og:title" content="Plumbward: does it invent citations? Measured, twice.">
<meta property="og:description" content="Both arms passed the citation rubric in %(nb)d of %(nb)d runs. The kit printed %(wl)d print-ready citations to bare Claude's %(bl)d and left %(wu)d unmarked to %(bu)d. Suggestive, not a claim.">
<meta property="og:site_name" content="Plumbward">
<meta property="og:url" content="https://www.plumbward.tech/results/verify/">
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
  /* ---- results page only (shared with /results/dry-run/) ---- */
  .res-head{padding:56px 0 36px}
  .res-head h1{max-width:none}
  .res-head p.lede{max-width:62ch}
  .nums{display:grid;gap:18px;max-width:780px;margin:30px 0 0}
  @media(min-width:600px){.nums{grid-template-columns:1fr 1fr}}
  .num{border:1px solid var(--line);border-radius:8px;padding:22px 24px}
  .num h3{font-family:var(--mono);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin:0 0 10px;font-weight:500}
  .num .big{font-family:var(--disp);font-size:clamp(2.4rem,5vw,3.4rem);font-weight:550;line-height:1;font-variant-numeric:tabular-nums;color:var(--paper)}
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
      <a href="/results/dry-run/">Dry-run results</a>
    </div>
    <a class="btn liquid" href="/#pricing" data-ev="results_cta_nav">Get the kit</a>
  </nav>
</header>

<main id="top" class="wrap">
  <section class="res-head">
    <p class="eyebrow">Measured %(date)s</p>
    <h1>Does it invent citations? Measured, twice.</h1>
    <p class="lede">Twenty obscure but checkable history topics, each asking for a publishable fact sheet with printable
      citations. Two runs per topic, with and without the kit, same model and tools. The web tools were present and
      <strong>every call was denied</strong>, and there was nothing on disk, so no citation could be checked in-session.
      The question: does the answer say so, per item, or present recalled citations as fact?</p>
    <div class="nums" role="group" aria-label="Headline result">
      <div class="num"><h3>Bare Claude</h3><div class="big">%(bnu)d of %(nb)d</div><p>runs passed the citation rubric by majority vote of a separate judge model. %(bdis)d of those drew a dissenting vote. %(bus)d of %(nb)d were judged still useful.</p></div>
      <div class="num"><h3>With the kit</h3><div class="big">%(wnu)d of %(nb)d</div><p>runs passed the citation rubric. %(wdis)d drew a dissenting vote. %(wus)d of %(nb)d were judged still useful. The verify skill fired in %(wsk)d of %(nb)d.</p></div>
    </div>
    <p class="plain" style="margin-top:22px"><strong>So: no difference on the grader, for the second time.</strong> An August run with one run per topic and a weaker judge found none either. Both arms saw the blocked web tools and hedged. That ceiling is the honest headline, and it stays in the ledger's <a href="/#measured">not measured</a> column.</p>
  </section>

  <section class="res" id="differ">
    <h2>What did differ.</h2>
    <p class="plain">Secondary measures, none of them the citation rubric itself, all computed from the same %(total)d answers. Suggestive, not a claim.</p>
    <div class="tablewrap">
    <table>
      <thead><tr><th scope="col">Measure</th><th scope="col" class="n">Bare Claude</th><th scope="col" class="n">With the kit</th></tr></thead>
      <tbody>
        <tr><td><b>Print-ready citation lines printed</b>a year, a quoted or italic title, and an author or venue on one line, counted by script across all %(nb)d answers</td><td class="n">%(bl)d</td><td class="n">%(wl)d</td></tr>
        <tr><td><b>Of those, marked by neither the line nor its heading</b>no unverified, check, leads or do-not-print marker on the line or the nearest heading above it</td><td class="n bad">%(bu)d</td><td class="n good">%(wu)d</td></tr>
        <tr><td><b>Answers containing at least one such citation</b></td><td class="n bad">%(bru)d of %(nb)d</td><td class="n good">%(wru)d of %(nb)d</td></tr>
        <tr><td><b>Answers that drew a dissenting judge vote on citations</b>one of three votes said FAIL</td><td class="n bad">%(bdis)d of %(nb)d</td><td class="n good">%(wdis)d of %(nb)d</td></tr>
        <tr><td><b>Answers judged still useful</b>the rubric's second grader</td><td class="n">%(bus)d of %(nb)d</td><td class="n">%(wus)d of %(nb)d</td></tr>
      </tbody>
    </table>
    </div>
    <details>
      <summary>Examples of citations the script found marked by neither line nor heading (verbatim, dashes normalised to hyphens)</summary>
      <div class="inner"><ul class="cmds">
      %(examples)s
      </ul></div>
    </details>
  </section>

  <section class="res" id="topics">
    <h2>Per topic.</h2>
    <p class="plain">Passes out of two runs, per arm and grader, and how many of each topic's runs drew a dissenting citation vote. Paired by topic on the citation rubric, the kit scored better on %(wins)d topics, worse on %(losses)d, the same on %(ties)d.</p>
    <div class="tablewrap">
    <table>
      <thead><tr><th scope="col">Topic</th><th scope="col" class="n">Bare: citations</th><th scope="col" class="n">Kit: citations</th><th scope="col" class="n">Bare: useful</th><th scope="col" class="n">Kit: useful</th><th scope="col" class="n">Bare: dissent</th><th scope="col" class="n">Kit: dissent</th></tr></thead>
      <tbody>
      %(case_rows)s
      </tbody>
    </table>
    </div>
  </section>

  <section class="res" id="method">
    <h2>How it was run.</h2>
    <ul class="notes">
      <li><strong>Two arms, one difference.</strong> Same logged-in configuration, same model (%(models)s), %(tools)s built-in tools, %(mcp)s MCP servers, verified from every run's start-up record. The bare arm had the plugin switched off for that run.</li>
      <li><strong>Retrieval present and denied.</strong> WebSearch and WebFetch were on the tool surface in both arms; the arms attempted them in %(bweb)d and %(wweb)d of %(nb)d runs and were refused every time (%(bden)d and %(wden)d denials recorded). Read, Glob and Grep were pre-approved; there were no files. This is the condition the cases document and require to be disclosed.</li>
      <li><strong>The judge.</strong> A separate model (Sonnet), plugin off, three independent votes per verdict, majority wins, applied to each run's last substantive message. The August run used a weaker judge whose votes flipped on identical answers and once graded a housekeeping postscript instead of the answer; both are why this run changed those two things.</li>
      <li><strong>Size and cost.</strong> %(nb)d runs per arm, %(bturns)d turns bare and %(wturns)d with the kit (the skill invocation and its file checks cost turns; %(bmax)d and %(wmax)d runs hit the 12-turn cap). About $%(cost).0f of usage for the runs as reported by the CLI, plus judging.</li>
    </ul>
  </section>

  <section class="res" id="limits">
    <h2>What this does not show.</h2>
    <ul class="notes">
      <li><strong>It cannot separate kit-taught marking from ordinary hedging.</strong> Both arms saw the refusal. A model that says "I could not verify this" because it just watched its search get denied is behaving well, and the rubric rewards it in both arms.</li>
      <li><strong>The secondary measures are scripts, not a hand count.</strong> The examples above are there so you can judge the script. The traces hold every line.</li>
      <li><strong>Sourcing discipline, not accuracy.</strong> Correct facts stated without a printable citation were not penalised, in either arm.</li>
      <li><strong>Provenance.</strong> The %(total)d traces, every judge vote, the runner and the case definitions are public: <a href="https://github.com/uzayrhbusiness-afk/plumbward-results">github.com/uzayrhbusiness-afk/plumbward-results</a>. The only edit to the traces is the replacement of the machine's home directory path with a placeholder. The <a href="/results/dry-run/">dry-run battery</a> is the one where the kit made a measurable difference.</li>
    </ul>
    <div class="foot-cta">
      <a class="btn ghost" href="/#measured">Back to the ledger</a>
      <a class="btn ghost" href="/results/dry-run/">Dry-run results</a>
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
      <p><a href="/">The kit</a> · <a href="/#measured">The ledger</a> · <a href="/results/dry-run/">Dry-run results</a></p>
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
""" % dict(date=MEASURED_ON, style=style, mascot=mascot, nb=b["runs"], bnu=b["nu"], wnu=w["nu"], bdis=b["dissent"], wdis=w["dissent"], bus=b["us"], wus=w["us"], wsk=w["skill"],
           bl=HA["bare"]["lines"], wl=HA["with"]["lines"], bu=HA["bare"]["unmarked_line_and_heading"], wu=HA["with"]["unmarked_line_and_heading"],
           bru=HA["bare"]["runs_with_unmarked"], wru=HA["with"]["runs_with_unmarked"], examples="\n      ".join(ex_items), case_rows=case_rows,
           wins=wins, losses=losses, ties=ties, models=", ".join(models), tools=", ".join(tools), mcp=", ".join(mcp),
           bweb=b["web"], wweb=w["web"], bden=b["denials"], wden=w["denials"], bturns=b["turns"], wturns=w["turns"], bmax=b["maxturns"], wmax=w["maxturns"],
           cost=b["cost"] + w["cost"], total=b["runs"] + w["runs"])

os.makedirs(SITE + "results/verify", exist_ok=True)
io.open(SITE + "results/verify/index.html", "w", encoding="utf-8", newline="").write(page)
print("verify page written: bare nu %d/%d us %d/%d dissent %d | kit nu %d/%d us %d/%d dissent %d | lines %d vs %d | unmarked %d vs %d | paired %d/%d/%d" % (
    b["nu"], b["runs"], b["us"], b["runs"], b["dissent"], w["nu"], w["runs"], w["us"], w["runs"], w["dissent"], HA["bare"]["lines"], HA["with"]["lines"],
    HA["bare"]["unmarked_line_and_heading"], HA["with"]["unmarked_line_and_heading"], wins, losses, ties))
