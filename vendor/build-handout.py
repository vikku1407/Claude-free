#!/usr/bin/env python3
"""Build everything a person needs to try this app on their own machine, and a
small download page for it.

    python3 vendor/build-handout.py [outdir]      # outdir default: ../downloads

Writes into outdir:
  MCS-ERP-standalone.html   one file, double-click, no folder (via build-standalone.py)
  MCS-ERP.zip               index.html + vendor/ + the standalone + instructions
  OPEN-THIS-FIRST.txt       what to do after downloading (Hinglish, plain text)
  index.html                download page (every link has "download", so a click saves)

Re-runnable on purpose: the sandbox wipes anything outside the repo between
sessions, so the whole handout is derived from the repo in one command - nothing
is stored that could go stale.
"""
import hashlib
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(ROOT), 'downloads')

sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location('build_standalone', os.path.join(HERE, 'build-standalone.py'))
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)   # defines build(); __main__ guard keeps it from writing

HOWTO = """MCS ERP - do file, do tarika
==========================================

TARIKA 1 (sabse aasan - ek hi file):
    MCS-ERP-standalone.html  par double-click karo. Bas.
    - koi folder nahi chahiye, internet bhi nahi
    - Excel export isme nahi hai (wo 880 KB ki library folder me rehti hai);
      "Export CSV" aur Print dono kaam karenge
    - data isi browser me save hota hai (auto-save). Browser change kiya to data
      nahi aayega - ye file aise hi bani hai, koi bug nahi

TARIKA 2 (poori features):
    poora "MCS-ERP" folder kahin bhi rakho (Desktop better), phir
    index.html kholo. vendor/ folder isi ke bagal me hona chahiye.
    Excel export, CSV, Print, sab chalega.

TARIKA 3 (server chahiye to):
    cd is-folder-ke-andar
    python3 -m http.server 8000
    phir browser me  http://localhost:8000

Jump / palette:
    header me "Jump to" button, ya Ctrl+K (Mac: Cmd+K), ya tab strip ka "+"
    type karo -> Enter, ya up/neeche arrow se choose karke Enter, ya row par click

Confirm sab theek hai to:
    left sidebar ke BILKUL bottom me "{stamp}" likha hona chahiye.
    wo na dikhe to browser purani copy dikha raha hai -> Ctrl+Shift+R (hard reload)
    koi aur cheez tooti ho to screen ke niche laal patti aayegi uska error + line
    number ke saath - wo line hi problem ka jawab hoti hai.

Data safe rakhna ho:
    kisi bhi table me "Export CSV" -> file bacha lo. (Import UI is file me nahi hai,
    isliye CSV sirf backup/padhne ke liye hai.)
"""

PAGE = """<!doctype html>
<html lang="hi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MCS ERP - download</title>
<style>
  :root {{ --ink:#0f172a; --mut:#64748b; --line:#e2e8f0; --brand:#0284c7; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:6vh 1.25rem 3rem; font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         color:var(--ink); background:linear-gradient(180deg,#f8fafc,#eef2f7); }}
  .wrap {{ max-width:640px; margin:0 auto; }}
  h1 {{ font-size:1.35rem; margin:0 0 .3rem; }}
  code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
  .sub {{ color:var(--mut); margin:0 0 1.5rem; font-size:.9rem; }}
  .card {{ display:block; background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem 1.1rem;
          margin-bottom:.9rem; text-decoration:none; color:inherit; box-shadow:0 1px 2px rgba(15,23,42,.05);
          transition:box-shadow .16s ease, transform .16s ease, border-color .16s ease; }}
  .card:hover {{ border-color:#bfdbfe; box-shadow:0 8px 24px rgba(2,132,199,.12); transform:translateY(-1px); }}
  .top {{ display:flex; align-items:baseline; gap:.6rem; flex-wrap:wrap; }}
  .name {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-weight:600; font-size:.95rem; }}
  .size {{ margin-left:auto; color:var(--mut); font-size:.8rem; font-variant-numeric:tabular-nums; }}
  .label {{ color:var(--brand); font-weight:650; font-size:.82rem; margin-top:.15rem; }}
  p {{ margin:.35rem 0 .7rem; color:#475569; font-size:.87rem; }}
  .foot {{ display:flex; align-items:center; justify-content:space-between; font-size:.75rem; color:var(--mut);
          border-top:1px dashed var(--line); padding-top:.55rem; font-family:ui-monospace,monospace; }}
  .go {{ color:var(--brand); font-weight:700; }}
  .url {{ margin-top:.5rem; font-size:.72rem; color:var(--mut); word-break:break-all; }}
  .url code {{ background:#f1f5f9; border:1px solid var(--line); border-radius:5px; padding:.1rem .3rem; color:#334155; user-select:all; }}
  .note {{ background:#fffbeb; border:1px solid #fde68a; border-radius:12px; padding:.75rem .9rem; font-size:.83rem; color:#78350f; }}
  ol {{ margin:.4rem 0 0; padding-left:1.1rem; }}
  li {{ margin:.2rem 0; }}
</style></head>
<body><div class="wrap">
  <h1>MCS ERP - build <code>{stamp}</code></h1>
  <p class="sub">Dono files same app hain. Kisi bhi ek par click = download hogi (browser save kar dega).</p>
{cards}
  <div class="note">
    <b>Download ke baad:</b> file ko double-click karke kholo. Left sidebar ke bilkul bottom me
    <b>{stamp}</b> likha dikhe to sahi file hai; na dikhe to <b>Ctrl+Shift+R</b> dabao (browser purani
    copy dikha raha hai).
    <ol>
      <li><b>Jump to</b> dabao → kisi module par <b>single click</b> → module khulna chahiye</li>
      <li><b>Ctrl+K</b> (Mac: Cmd+K) → type karo → <b>Enter</b></li>
      <li>Kuch toote to screen ke niche <b>laal patti</b> me error + line number aayega - wo line bhej dena</li>
    </ol>
  </div>
</div></body></html>
"""

CARDS = {
    'MCS-ERP-standalone.html': ('Ek file, bas double-click karo',
        'Tailwind + Font Awesome + fonts sab file ke andar inline hain. Excel export nahi (CSV + Print haan). Koi folder nahi chahiye.'),
    'MCS-ERP.zip': ('Poora package (Excel bhi)',
        'index.html + vendor/ folder + standalone + instructions. Excel export isi me hai. Zip nikaal ke index.html kholo.'),
    'OPEN-THIS-FIRST.txt': ('Sirf instructions (Hinglish)',
        'Kya karna hai, kya is file me nahi hai, aur data kaise bachate hain.'),
}


def main():
    html, fonts = bs.build()
    stamp = re.search(r"UX_BUILD = '([^']+)'", html).group(1)

    os.makedirs(OUTDIR, exist_ok=True)
    standalone = os.path.join(OUTDIR, 'MCS-ERP-standalone.html')
    with open(standalone, 'wb') as fh:
        fh.write(html.encode('utf-8'))

    howto = os.path.join(OUTDIR, 'OPEN-THIS-FIRST.txt')
    with open(howto, 'w', encoding='utf-8') as fh:
        fh.write(HOWTO.format(stamp=stamp))

    # zip: the folder shape of the app, plus the one-file build inside it
    stage = os.path.join(OUTDIR, '.handout-stage', 'MCS-ERP')
    shutil.rmtree(os.path.dirname(stage), ignore_errors=True)
    os.makedirs(stage)
    for name in ('index.html', 'README.md'):
        shutil.copy2(os.path.join(ROOT, name), stage)
    shutil.copytree(os.path.join(ROOT, 'vendor'), os.path.join(stage, 'vendor'))
    shutil.copy2(standalone, stage)
    shutil.copy2(howto, stage)
    archive = os.path.join(OUTDIR, 'MCS-ERP.zip')
    # Deterministic on purpose: a stored mtime would give the same app a different
    # sha256 on every rebuild, which makes the checksum on the download page useless.
    members = []
    for base, dirs, files in os.walk(stage):
        dirs.sort()
        for f in sorted(files):
            full = os.path.join(base, f)
            members.append((os.path.relpath(full, os.path.dirname(stage)).replace(os.sep, '/'), full))
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, full in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(full, 'rb') as fh:
                z.writestr(info, fh.read())
    shutil.rmtree(os.path.dirname(stage), ignore_errors=True)

    # download page
    # The preview panel is a sandboxed iframe, and a sandboxed iframe simply is not
    # allowed to start a download (Chrome drops it, nothing appears to happen). So the
    # page also prints the absolute URL as selectable text - paste it in a real tab.
    pub = os.environ.get('PUBLIC_BASE', '').rstrip('/')
    cards = []
    for name, (label, desc) in CARDS.items():
        urlline = ('<div class="url">panel me click dabane par kuch na ho to ye address '
                   'naye tab me paste karo:<br><code>%s/%s</code></div>' % (pub, name)) if pub else ''
        path = os.path.join(OUTDIR, name)
        raw = open(path, 'rb').read()
        cards.append(
            '    <a class="card" href="%s/%s" target="_blank" rel="noopener" download>\n'
            '      <div class="top"><span class="name">%s</span><span class="size">%.2f MB</span></div>\n'
            '      <div class="label">%s</div>\n      <p>%s</p>\n'
            '      <div class="foot"><span>sha256 %s</span><span class="go">Download &#8595;</span></div>\n'
            '      %s\n    </a>' % (pub, name, name, len(raw) / 1048576.0, label, desc,
                                     hashlib.sha256(raw).hexdigest()[:12], urlline))
    with open(os.path.join(OUTDIR, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(PAGE.format(stamp=stamp, cards='\n'.join(cards)))

    print('handout built in %s' % OUTDIR)
    for name in ('MCS-ERP-standalone.html', 'MCS-ERP.zip', 'OPEN-THIS-FIRST.txt', 'index.html'):
        p = os.path.join(OUTDIR, name)
        print('  %-26s %8.2f MB  sha256 %s' % (name, os.path.getsize(p) / 1048576.0,
                                               hashlib.sha256(open(p, 'rb').read()).hexdigest()[:12]))
    print('  webfont faces inlined: %d | build stamp: %s' % (fonts, stamp))
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        print('  zip members: %d | integrity: %s' % (len(z.namelist()), 'OK' if bad is None else 'CORRUPT ' + bad))
        if bad:
            sys.exit(1)


if __name__ == '__main__':
    main()
