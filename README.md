# MCS — Dispatch & Sales Summary Report ERP

Single-file ERP for **Mining Chemical Suppliers (Tyre-Lub Division)**: dispatch, inward and
stock-transfer entries, customer/item masters, stock statements and the dispatch report.
No server, no build step, no database — one `index.html`.

## Run it

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000     # → http://localhost:8000
```

Log in with the seeded admin (`Admin User` / `admin123`) or switch role from the header.

## Data

| What | Where |
| --- | --- |
| Entries you create (dispatch / inward / transfer / new masters / users) | this browser's `localStorage`, key `mcs-erp-v1`, written on every change |
| Item & customer master shipped in the file | hardcoded in `index.html`, re-merged on load (new records in the file still arrive) |
| Backups | Export CSV, or Export to Excel (SheetJS) |

Header shows `Saved HH:MM` — that is auto-save confirming the write actually happened.

## Assets are local now

Everything the page needs ships in `vendor/` — Tailwind (pre-compiled), Font Awesome,
Inter + JetBrains Mono, SheetJS. No CDN, so a blocked or slow network cannot break the layout.

```bash
sh vendor/build.sh      # regenerate vendor/tailwind.css after adding/changing classes
```

Tailwind's build scans `index.html` for class names, so any class that is *composed at
runtime* (`'bg-' + x`) would be missed and must go into `safelist` in
`vendor/tailwind.config.js`. The file currently composes none (verified).
SheetJS (861 KB) is not loaded on page open — it is injected the first time
**Export to Excel** is clicked, by `uxEnsureXlsx()`.

## Handing it to someone as one file

`python3 vendor/build-standalone.py [outdir]` derives `MCS-ERP-standalone.html`
from `index.html`: the three vendored stylesheets get inlined and every webfont
becomes a data URI, so a single file can be emailed or dropped on a Desktop and
double-clicked - no folder, no server, no internet. It refuses to write if any
`src`/`href`/`url()` would still point outside the file, so the output cannot
silently regress into something that needs `vendor/`.

`index.html` stays the source of truth (edit that, then rebuild). Excel export is
the one thing not inlined - SheetJS is 880 KB and the app deliberately loads it on
demand - so the standalone tells the user to use Export CSV, which needs no
library. The zip used for handouts is built the same way: `index.html` + `vendor/`
+ the standalone file + a short instructions text file.

## "A button appears but does nothing" — how to tell what broke

Everything lives in one file, so a single script error can unwire half the page in
silence. Two things make that visible, both added for that reason:

* the sidebar footer prints a build stamp (`ux2.2 (2026-09-19)`) — no stamp, or an
  older one, means the browser is showing a cached copy: hard-reload (Ctrl+Shift+R)
* if the app's own script throws, a red bar slides up from the bottom of the screen
  naming the error and its line number — that line is the whole diagnosis. The
  console also logs `[ux] …` on load, which proves the UX layer installed.

Two bugs of this class were found and fixed that way, both invisible to a naive test:

1. the UX layer used to be wired at the end of the app's 9.5k-line script, so any
   earlier throw silently unwired every button → the layer now lives in its own
   `<script id="ux-layers">` after the app, is wired by event delegation, and runs
   each boot step in its own `try/catch`
2. the command palette rebuilt its row list on `mouseenter`, so the node the mouse
   went down on no longer existed at mouseup and the browser aimed the `click` at
   the `<ul>` instead of the row → clicking a module did nothing while Ctrl+K +
   Enter worked. Rows are now indexed (`data-i`) with one delegated handler on the
   list, and hover only moves the highlight (a CSS `:hover` does the look) instead
   of re-rendering.

Worth remembering when editing this file: dispatching `click()` on an element in
jsdom bypasses hit testing, so it cannot catch a "rebuilt under the cursor" bug.
The palette test drives mouseover → mousedown → mouseup → click on a captured node
reference, asserts that node is still in the DOM, and runs the same sequence against
a mutant built by reverting the fix — so the check is known to have teeth.

## Notes for whoever maintains this

- `index.html` is ~8.6k lines: markup, the `<style>` block, and all app logic in one file. Edit in place; the UI/UX polish layer at the end of the `<style>` block is separated and commented so it can be deleted wholesale.
- **Single file no more:** `index.html` must stay next to its `vendor/` folder. Copying just the HTML gives a plain, unstyled page (the app detects that and says exactly why).
- **Auth is cosmetic.** `handleLogin()` only sets a JS variable, so anyone with the file can read it in a text editor. Treat it as a role switch for one trusted operator, not as access control. Real security needs a backend.
- `localStorage` is per-browser and per-machine: entries do not sync between the store PC and your laptop, and clearing browser data clears them. Move to a small server + SQLite/Postgres if more than one person must see the same numbers.
- The dispatch table defaults to **today only** — older entries are hidden, never deleted. Use the `Today only` toggle in the preview card header.
