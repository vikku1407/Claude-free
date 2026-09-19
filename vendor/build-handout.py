#!/usr/bin/env python3
"""Build everything a person needs to try this app on their own machine, and a
small download page for it.

    python3 vendor/build-handout.py [outdir]      # outdir default: ../downloads
    PUBLIC_BASE=https://host sh -c '...'          # absolute URLs on the page

Writes into outdir:
  MCS-ERP-standalone.html   one file, double-click, no folder (via build-standalone.py)
  MCS-ERP.zip               index.html + vendor/ + the standalone + instructions
  OPEN-THIS-FIRST.txt       what to do after downloading (Hinglish, plain text)
  index.html                the handout page

Re-runnable on purpose: the sandbox wipes anything outside the repo between
sessions, so the whole handout is derived from the repo in one command - nothing
is stored that could go stale. Deterministic apart from index.html's own checksum,
so the sha256 printed on the page still means something after a rebuild.
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(ROOT), 'downloads')

sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location('build_standalone', os.path.join(HERE, 'build-standalone.py'))
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)   # defines build(); the __main__ guard keeps it from writing

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

AGAR DOWNLOAD HI NA HO (kisi panel/preview ke andar click kar rahe ho):
    preview panel ek sandboxed iframe hota hai aur browser wahan se shuru hone
    wala download block kar deta hai - na error aata hai, na file. Koi baat nahi:
    card ke neeche diya hua address copy karke APNE browser ke naye tab me paste
    karo, wahin se download ho jaayega.

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
  :root { --ink:#0f172a; --mut:#64748b; --line:#e2e8f0; --brand:#0284c7; }
  * { box-sizing:border-box; }
  body { margin:0; padding:5vh 1.25rem 3rem; font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
         color:var(--ink); background:linear-gradient(180deg,#f8fafc,#eef2f7); }
  .wrap { max-width:660px; margin:0 auto; }
  h1 { font-size:1.35rem; margin:0 0 .3rem; }
  code { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
  .sub { color:var(--mut); margin:0 0 1.4rem; font-size:.9rem; }
  .card { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem 1.1rem; margin-bottom:.85rem;
          box-shadow:0 1px 2px rgba(15,23,42,.05); }
  .card.hot { border-color:#bae6fd; background:linear-gradient(180deg,#f0f9ff,#fff); }
  .top { display:flex; align-items:baseline; gap:.6rem; flex-wrap:wrap; }
  .name { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-weight:600; font-size:.95rem; }
  .size { margin-left:auto; color:var(--mut); font-size:.8rem; font-variant-numeric:tabular-nums; }
  .label { color:var(--brand); font-weight:650; font-size:.82rem; margin-top:.15rem; }
  p { margin:.35rem 0 .7rem; color:#475569; font-size:.87rem; }
  .foot { display:flex; align-items:center; justify-content:space-between; gap:.6rem; flex-wrap:wrap;
          border-top:1px dashed var(--line); padding-top:.6rem; font-size:.75rem; color:var(--mut);
          font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
  .acts { display:flex; gap:.45rem; flex-wrap:wrap; }
  .acts a, .acts button { font:inherit; font-weight:700; text-decoration:none; cursor:pointer; border-radius:8px;
          padding:.34rem .6rem; border:1px solid var(--line); background:#f8fafc; color:#334155; }
  .acts a.pri { background:var(--brand); border-color:var(--brand); color:#fff; }
  .acts a:hover, .acts button:hover { border-color:#7dd3fc; }
  .url { margin-top:.55rem; font-size:.72rem; color:var(--mut); word-break:break-all; }
  .url code { background:#f1f5f9; border:1px solid var(--line); border-radius:5px; padding:.12rem .35rem;
          color:#334155; user-select:all; }
  .note { background:#fffbeb; border:1px solid #fde68a; border-radius:12px; padding:.75rem .9rem; font-size:.83rem; color:#78350f; }
  ol { margin:.4rem 0 0; padding-left:1.1rem; }
  li { margin:.2rem 0; }
  #tip { position:fixed; left:50%; bottom:1.1rem; transform:translate(-50%,120%); background:#0f172a; color:#fff;
         font-size:.78rem; padding:.5rem .8rem; border-radius:9px; transition:transform .2s ease; }
  #tip.on { transform:translate(-50%,0); }
</style></head>
<body><div class="wrap">
  <h1>MCS ERP - build <code>@@STAMP@@</code></h1>
  <p class="sub">@@SUB@@</p>
@@CARDS@@
  <div class="note">
    <b>Karane ke baad kya dekhna hai:</b> file double-click karke kholo, aur left sidebar ke
    bilkul bottom me <b>@@STAMP@@</b> dhoondo. Na dikhe to browser purani copy dikha raha hai
    - <b>Ctrl+Shift+R</b>.
    <ol>
      <li><b>Jump to</b> - kisi module par <b>single click</b> - module khulna chahiye</li>
      <li><b>Ctrl+K</b> (Mac: Cmd+K) - type karo - <b>Enter</b></li>
      <li>Kuch toote to screen ke niche <b>laal patti</b> me error + line number aayega, wo line bhej dena</li>
    </ol>
  </div>
</div>
<div id="tip"></div>
<script>
  (function () {
    var tip = document.getElementById('tip');
    function say(m) { tip.textContent = m; tip.classList.add('on'); setTimeout(function () { tip.classList.remove('on'); }, 1800); }
    /* Clipboard may be refused inside a preview iframe, and execCommand is the way that
       still works there - both are tried, and the address is selectable as a last resort. */
    document.querySelectorAll('[data-copy]').forEach(function (b) {
      b.addEventListener('click', function () {
        var url = b.getAttribute('data-copy');
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(url).then(function () { say('Link copy ho gaya - naye tab me paste karo'); },
                                                  function () { legacy(url, say); });
        } else { legacy(url, say); }
      });
    });
    function legacy(url, say) {
      var t = document.createElement('textarea');
      t.value = url; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.left = '-9999px';
      document.body.appendChild(t); t.select();
      var done = false;
      try { done = document.execCommand('copy'); } catch (e) { done = false; }
      t.remove();
      say(done ? 'Link copy ho gaya - naye tab me paste karo' : 'Copy block hai - neeche wala address do baar click karke select karo, phir Ctrl+C');
    }
  })();
</script>
</body></html>
"""

CARDS = [
    ('MCS-ERP-standalone.html', 'Ek file, bas double-click karo',
     'Tailwind + Font Awesome + fonts sab file ke andar inline hain. Excel export nahi (CSV + Print haan). Koi folder nahi chahiye.', True),
    ('MCS-ERP.zip', 'Poora package (Excel bhi)',
     'index.html + vendor/ folder + standalone + instructions. Excel export isi me hai. Zip nikaal ke index.html kholo.', False),
    ('OPEN-THIS-FIRST.txt', 'Sirf instructions (Hinglish)',
     'Kya karna hai, kya is file me nahi hai, data kaise bachate hain, aur download block ho to kya karein.', False),
]


def git(*args):
    try:
        return subprocess.run(['git', '-C', ROOT] + list(args), capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ''


def repo_zip_url():
    """The archive GitHub builds itself - no sandbox, no server, no expiry."""
    remote = git('remote', 'get-url', 'origin')
    m = re.search(r'github\.com[:/]([^/]+)/([^/.]+)', remote)
    branch = git('rev-parse', '--abbrev-ref', 'HEAD')
    if not m or not branch or branch == 'HEAD':
        return ''
    return 'https://github.com/%s/%s/archive/refs/heads/%s.zip' % (m.group(1), m.group(2), branch)


def card(title, label, desc, size, digest, hrefs, hot=False, note=''):
    """hrefs: list of (kind, text, url) where kind is 'pri' | 'tab' | 'copy'."""
    acts = []
    for kind, text, url in hrefs:
        if kind == 'copy':
            acts.append('<button data-copy="%s">%s</button>' % (url, text))
        elif kind == 'pri':
            acts.append('<a class="pri" href="%s" target="_blank" rel="noopener" download>%s</a>' % (url, text))
        else:
            acts.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (url, text))
    urlbox = ''.join('<div class="url">%s<br><code>%s</code></div>' % (note or 'Panel ke andar click block ho to ye address naye tab me paste karo:', u)
                     for u in [h[2] for h in hrefs if h[0] != 'copy'])
    return ('  <div class="card%s">\n'
            '    <div class="top"><span class="name">%s</span>%s</div>\n'
            '    <div class="label">%s</div>\n    <p>%s</p>\n'
            '    <div class="foot"><span>%s</span><span class="acts">%s</span></div>\n%s  </div>'
            % (' hot' if hot else '', title,
               ('<span class="size">%.2f MB</span>' % size) if size is not None else '',
               label, desc, digest, ' '.join(acts), urlbox + '\n' if urlbox else ''))


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
    # sha256 on every rebuild, which makes the checksum on the page useless.
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

    # ---- the handout page -----------------------------------------------------
    # A preview panel is a sandboxed iframe, and browsers refuse to start a download
    # from one: no error, no file, and (verified in the server log) not even a request.
    # So the page leads with the thing that needs no download at all, and makes every
    # URL one click to copy for when a real tab is needed.
    pub = os.environ.get('PUBLIC_BASE', '').rstrip('/')
    cards = []
    if pub:
        cards.append(card(
            'Panel me hi test karo', 'Download karne ki zaroorat nahi',
            'Ye wahin file hai, bas yahan inline khul jaati hai - Jump/palette, density, filter, print sab '
            'yahi check ho jaayega. Data isi browser me rehta hai.',
            None, 'live preview', [('tab', 'App kholo ↓', pub + '/MCS-ERP-standalone.html?inline=1')], hot=True,
            note='Same URL, download ke bina (server isme Content-Disposition nahi bhejta):'))
    gh = repo_zip_url()
    if gh:
        cards.append(card(
            'GitHub archive zip', 'Sandbox se zero dependency - sabse reliable',
            'Repo ka poora snapshot: index.html + vendor/ (Excel export ke saath) + tests. '
            'Yeh zip GitHub khud banata hai, isliye download hamesha chalega.',
            None, 'repo archive', [('pri', 'Download ↓', gh), ('copy', 'Copy link', gh)],
            note='Ye link Arena ke panel se bahar bhi chalta hai (public repo, koi token nahi):'))
    for name, label, desc, hot in CARDS:
        raw = open(os.path.join(OUTDIR, name), 'rb').read()
        url = (pub + '/' + name) if pub else '/' + name
        cards.append(card(name, label, desc, len(raw) / 1048576.0,
                          'sha256 ' + hashlib.sha256(raw).hexdigest()[:12],
                          [('pri', 'Download ↓', url)] + ([('copy', 'Copy link', url)] if pub else []),
                          hot=hot))

    sub = ('Do alag baatein, dono is panel ki limit hain: (1) panel ke andar browser download start '
           'hone hi nahi deta, (2) ye host Arena ke bahar <code>traffic access token</code> maangta hai. '
           'Isliye <b>file chahiye to GitHub archive wala card</b> use karo - wo link kahin bhi chalta hai. '
           'Sirf test karna hai to niche wala card: app yahin panel me khul jaayega.') if pub else \
          'Dono files same app hain; kisi bhi ek par click = download.'
    # tokens, not str.format: the page carries a <script> and CSS full of braces
    page = PAGE.replace('@@STAMP@@', stamp).replace('@@SUB@@', sub).replace('@@CARDS@@', '\n'.join(cards))
    missing = [t for t in re.findall(r'@@[A-Z]+@@', page)]
    if missing:
        raise SystemExit('unfilled tokens in the handout page: %s' % missing)
    with open(os.path.join(OUTDIR, 'index.html'), 'w', encoding='utf-8') as fh:
        fh.write(page)

    print('handout built in %s' % OUTDIR)
    for name in ('MCS-ERP-standalone.html', 'MCS-ERP.zip', 'OPEN-THIS-FIRST.txt', 'index.html'):
        p = os.path.join(OUTDIR, name)
        print('  %-26s %8.2f MB  sha256 %s' % (name, os.path.getsize(p) / 1048576.0,
                                               hashlib.sha256(open(p, 'rb').read()).hexdigest()[:12]))
    print('  webfont faces inlined: %d | build stamp: %s | public base: %s' % (fonts, stamp, pub or 'n/a'))
    print('  repo archive: %s' % (gh or 'n/a (no github remote)'))
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        print('  zip members: %d | integrity: %s' % (len(z.namelist()), 'OK' if bad is None else 'CORRUPT ' + bad))
        if bad:
            sys.exit(1)


if __name__ == '__main__':
    main()
