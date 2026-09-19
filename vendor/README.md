# vendor/ — everything this app needs, locally

The page used to pull Tailwind (Play CDN), Font Awesome, SheetJS and Inter from CDNs.
That meant: block or throttle the network and the app rendered as unstyled HTML, and the
Play CDN re-compiled every class in the browser on each load. All of it is local now.

| File | Where it came from | Notes |
| --- | --- | --- |
| `tailwind.css` | built from `../index.html` by `tailwindcss@3.4.14` | 22 KB, purge-scoped to exactly the classes this file uses |
| `fontawesome/` | npm `@fortawesome/fontawesome-free@6.4.0` | CSS + 4 woff2 files (woff2 only; no ttf/svg) |
| `fonts/` | npm `@fontsource/inter@5`, `@fontsource/jetbrains-mono@5` | Inter 400-800 + JetBrains Mono 400/500, latin |
| `xlsx.full.min.js` | npm `xlsx@0.18.5` | **loaded on demand** by `uxEnsureXlsx()` when Export-to-Excel is clicked, not on page load |

## After changing any class in index.html

Tailwind has to be rebuilt, because unlike the CDN it does not compile in the browser:

```bash
sh vendor/build.sh      # needs node; writes vendor/tailwind.css
```

If you add a class only inside a string built at runtime (`'bg-' + color`), the scanner
cannot see it - list it in `safelist` inside `tailwind.config.js` instead. Nothing in this
app does that today (checked: no composed class names).
