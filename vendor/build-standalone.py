#!/usr/bin/env python3
"""Build a single self-contained HTML from index.html, for people who just want
to double-click a file (email attachment, USB stick, office PC with no folder).

index.html stays the source of truth and keeps its lazy vendor/ assets; this
derives MCS-ERP-standalone.html from it by inlining the three stylesheets, and
turning every font url() into a data URI. Nothing else changes, so both files
run the same scripts and the same UX layers.

    python3 vendor/build-standalone.py [outdir]

Excel export is the one thing that cannot be inlined cheaply (SheetJS is 880 KB,
which is exactly why the app loads it on demand), so the standalone file tells
the user to use Export CSV - which needs no library at all.
"""
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else ROOT

MIME = {'.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf',
        '.otf': 'font/otf', '.eot': 'application/vnd.ms-fontobject',
        '.svg': 'image/svg+xml'}

LINKS = ['vendor/tailwind.css', 'vendor/fonts/fonts.css', 'vendor/fontawesome/css/all.min.css']
ENTRY = re.compile(r'url\(\s*([\'"]?)([^)\'"]+)\1\s*\)\s*format\(\s*[\'"]([^\'"]+)[\'"]\s*\)')


def data_uri(path):
    raw = open(path, 'rb').read()
    mime = MIME.get(os.path.splitext(path)[1], 'application/octet-stream')
    return 'url(data:%s;base64,%s)' % (mime, base64.b64encode(raw).decode('ascii'))


def font_faces(css, seen, needed=None):
    """Drop @font-face blocks that are duplicates, or that the app never selects.

    all.min.css alone declares ten faces (FA6 solid/regular/brands, the FA5 aliases and
    the v4-compat ones). Only the ones a font-family in use can actually resolve to are
    worth 200 KB of base64 each, so everything else goes - that is roughly half the
    size of the old single-file build.
    """
    kept, dropped = [], 0
    for block in re.findall(r'@font-face\s*\{[^}]*\}', css):
        fam = re.search(r'font-family:\s*([\'"]?)([^\'";]+)\1', block)
        wt = re.search(r'font-weight:\s*([0-9]+|normal|bold)', block)
        key = ((fam.group(2) if fam else '?').strip(), (wt.group(1) if wt else 'normal'))
        if key in seen or (needed is not None and key not in needed):
            dropped += 1
            css = css.replace(block, '', 1)
            continue
        seen.add(key)
        kept.append(key)
    return css, kept, dropped


def inline_css(rel, seen=None, needed=None):
    path = os.path.join(ROOT, rel)
    css = open(path, encoding='utf-8').read()
    dropped = 0
    if seen is not None:
        css, _, dropped = font_faces(css, seen, needed)
    base = os.path.dirname(path)
    state = {'n': 0}

    def fix_src(block):
        out = []
        for entry in block.split(','):
            em = ENTRY.search(entry)
            if not em:
                out.append(entry)
                continue
            target = os.path.normpath(os.path.join(base, em.group(2).strip()))
            if os.path.exists(target):
                out.append(data_uri(target))
                state['n'] += 1
            # a missing fallback format (we ship woff2 only) is dropped, not 404ed
        return ','.join(out) if out else block

    # minified css ends a src list with '}' rather than ';', so stop at either
    css = re.sub(r'src:\s*([^;}]+)', lambda m: 'src:' + fix_src(m.group(1)), css)
    # leftovers only - a data: uri we just made must survive this pass
    css = re.sub(r'url\(\s*[\'"]?(?!data:)[^)\'"]*[\'"]?\s*\)', '', css)
    return css, state['n'], dropped


def build():
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()

    # 2. be honest about the one thing that stayed outside
    old = "showToast('vendor/xlsx.full.min.js is missing - use Export CSV.', 'error')"
    new = "showToast('Excel needs the vendor/ folder - Export CSV works on its own.', 'error')"
    assert old in html or new in html, 'xlsx fallback text moved - update this builder'
    html = html.replace(old, new)   # a no-op once index.html already says it

    head = html[:html.find('</head>')]

    # 1. swap the three <link> tags for one inlined <style>
    links = ''.join('    <link rel="stylesheet" href="%s">\n' % l for l in LINKS)
    assert links in head, 'the <link> block in index.html changed - update this builder'
    # which icons the app actually paints decides which faces are loadable
    uses = lambda *names: any(n in html for n in names)
    fa_needed = set()
    if uses('fa-solid', 'fas'):
        fa_needed.add(('Font Awesome 6 Free', '900'))
    if uses('fa-regular', 'far'):
        fa_needed.add(('Font Awesome 6 Free', '400'))
    if uses('fa-brands', 'fab'):
        fa_needed.add(('Font Awesome 6 Brands', '400'))
    seen = set()
    blocks, total, dropped = [], 0, 0
    for rel in LINKS:
        css, n, drop = inline_css(rel, seen, fa_needed if 'fontawesome' in rel else None)
        total += n
        dropped += drop
        blocks.append('    /* ---- inlined from %s ---- */\n    <style>\n%s\n    </style>' % (rel, css.strip()))
    head = head.replace(links, '\n'.join(blocks) + '\n', 1)

    note = ('<!-- SINGLE-FILE BUILD - generated by vendor/build-standalone.py, do not edit.\n'
            '     Stylesheets and fonts are inlined; edit index.html instead and rebuild. -->\n')
    head = note + head.replace('<head>', '<head>\n    <meta name="ux-standalone" content="1">', 1)
    # the app script lives in <body>, so patch the toast text there too
    body = html[html.find('</head>'):]

    out = head + '</head>' + body
    return out, total, dropped


def write(outdir=None):
    out, fonts, dropped = build()
    path = os.path.join(outdir or OUTDIR, 'MCS-ERP-standalone.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(out.encode('utf-8'))
    return path, len(out), fonts, dropped


if __name__ == '__main__':
    out, fonts, dropped = build()

    # nothing may point outside the file
    stray = re.findall(r'(?:src|href)="(?!#)([^"]+)"', out)
    stray = [s for s in stray if not s.startswith('data:') and not s.startswith('vendor/xlsx')]
    leftover = re.findall(r'url\((?!data:)[\'"]?[^)\'"]*[\'"]?\)', out)
    # licences in CSS comments mention their home page; that is not a request.
    code = re.sub(r'/\*.*?\*/', '', out, flags=re.S)
    external = sorted({u for u in re.findall(r'https?://[^\s"\'`)<>]+', code) if 'w3.org' not in u})

    name = 'MCS-ERP-standalone.html'
    path = os.path.join(OUTDIR, name)
    open(path, 'wb').write(out.encode('utf-8'))

    print('wrote %s' % path)
    print('  size            : %.1f MB (%d bytes)' % (len(out) / 1048576.0, len(out)))
    print('  fonts inlined   : %d (dropped %d redundant/unused @font-face blocks)' % (fonts, dropped))
    print('  external src/href: %s' % (', '.join(stray) or 'none'))
    print('  non-data url()  : %d' % len(leftover))
    print('  external URLs   : %s' % (', '.join(external) or 'none'))
    print('  inline scripts  : %d' % len(re.findall(r'<script\b', out)))
    if stray or leftover or external:
        print('\nWARNING: the standalone file still reaches outside itself')
        sys.exit(1)
