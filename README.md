# Claude-free

> A free, open repo for all users — no sign-up, no paywall, no tracking.

<p align="left">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <img alt="No build step" src="https://img.shields.io/badge/build-none%20needed-brightgreen">
  <img alt="Zero dependencies" src="https://img.shields.io/badge/dependencies-0-informational">
  <img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-9cf">
</p>

Plain HTML/CSS/JS landing page + a home for free prompts, guides and tiny tools.
Clone it, fork it, ship it on GitHub Pages in a minute.

---

## Contents

```
Claude-free/
├── index.html          # the landing page
├── assets/
│   ├── styles.css      # design tokens, dark + light theme, responsive layout
│   └── app.js          # theme toggle, scroll spy, copy buttons, filters (all optional)
├── README.md
└── LICENSE
```

## Quick start

No install step. Pick whichever is easier:

```bash
# 1) open it directly — works offline, works on a phone
open index.html            # macOS
xdg-open index.html        # Linux

# 2) or serve it locally
python3 -m http.server 8000   # → http://localhost:8000
```

## Publishing on GitHub Pages

1. Push this folder to a branch (e.g. `main`).
2. Repo **Settings → Pages → Build and deployment → Source: Deploy from a branch**.
3. Branch `main`, folder `/ (root)` → **Save**.
4. Visit `https://<your-username>.github.io/<repo-name>/`.

## Design notes

The page is built so that it degrades politely rather than breaking:

| Decision | Why |
| --- | --- |
| Zero dependencies, no bundler | Nothing to audit, nothing to `npm install`, nothing to rot |
| Dark theme by default, light theme on toggle | Both meet WCAG AA contrast; system preference is respected |
| Semantic landmarks + `<details>` for the FAQ | Works with a screen reader and with a keyboard, no custom widget to maintain |
| All JS is progressive enhancement | Content is visible with JavaScript disabled |
| `prefers-reduced-motion` honoured | Animations switch themselves off |
| Fluid `clamp()` type scale | 320 px phone → ultrawide without horizontal scroll |

## Contributing

1. Open an issue first so we don't duplicate work.
2. Branch off `main`, one focused change per pull request.
3. Keep files small and dependency-free — if it can't be read in one sitting, it doesn't belong here.
4. Include one line describing the problem the change solves.

## Disclaimer

This is an unofficial, community-run project. It is **not affiliated with, sponsored by, or
endorsed by Anthropic**. "Claude" is a trademark of its respective owner, used here descriptively
to mean "free things for people who use Claude".

## License

Released under the [MIT License](LICENSE). Do what you want with it, attribution appreciated.
