# Handout snapshot

`MCS-ERP-standalone.html` is the same app as `../index.html`, with the stylesheets
and webfonts inlined, so a single file can be emailed or double-clicked with no
`vendor/` folder and no internet.

It is **generated** - `python3 vendor/build-handout.py` - so treat `../index.html`
as the thing to edit. Do not hand-edit this file; the next rebuild overwrites it.
`tests/standalone-file.mjs` fails if this snapshot and a fresh build ever differ,
which is what keeps a committed artifact from rotting.

Why it is committed at all: it gives anyone a one-click download
(GitHub's "Download raw file" button on this file's page) that works from an
ordinary browser tab - no sandbox, no preview panel, no access token. That is the
one route that survives a locked-down network.

Excel export is the single thing not inlined (SheetJS is 880 KB and the app loads
it lazily), so use `../index.html` + `../vendor/` if you need `.xlsx` output.
