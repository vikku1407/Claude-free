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

## Notes for whoever maintains this

- `index.html` is ~8.6k lines: markup, the `<style>` block, and all app logic in one file. Edit in place; the UI/UX polish layer at the end of the `<style>` block is separated and commented so it can be deleted wholesale.
- **Single file no more:** `index.html` must stay next to its `vendor/` folder. Copying just the HTML gives a plain, unstyled page (the app detects that and says exactly why).
- **Auth is cosmetic.** `handleLogin()` only sets a JS variable, so anyone with the file can read it in a text editor. Treat it as a role switch for one trusted operator, not as access control. Real security needs a backend.
- `localStorage` is per-browser and per-machine: entries do not sync between the store PC and your laptop, and clearing browser data clears them. Move to a small server + SQLite/Postgres if more than one person must see the same numbers.
- The dispatch table defaults to **today only** — older entries are hidden, never deleted. Use the `Today only` toggle in the preview card header.
