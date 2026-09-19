/* Shared bits for the tests. jsdom only - no browser, no server needed:
     npm i jsdom@24 && node tests/palette-click.mjs
   (see tests/run.sh, which installs it into /tmp if the sandbox wiped it) */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { JSDOM, VirtualConsole } from 'jsdom';

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const wait = (ms) => new Promise((r) => setTimeout(r, ms));

export function boot(html, { url = 'http://localhost/', seed = null } = {}) {
  const errs = [];
  const vc = new VirtualConsole();
  // "Could not load" = jsdom refusing to fetch the vendored <link>s from disk,
  // which every browser does fine; anything else is a real script error.
  vc.on('jsdomError', (e) => { const m = String(e && e.message || e); if (!/Could not load|Not implemented: navigation/.test(m)) errs.push(m); });
  vc.on('error', (...a) => errs.push('console.error ' + a.join(' ')));
  const dom = new JSDOM(html, {
    runScripts: 'dangerously',
    pretendToBeVisual: true,
    url,
    virtualConsole: vc,
    beforeParse(w) { if (seed && w.localStorage) w.localStorage.setItem('mcs-erp-v1', seed); }
  });
  return { dom, w: dom.window, d: dom.window.document, errs };
}

export function suite() {
  const res = [];
  return {
    ok: (cond, info) => res.push([!!cond, info]),
    report(title) {
      console.log(res.map(([c, i]) => (c ? ' ok  ' : 'FAIL ') + i).join('\n'));
      const bad = res.filter(([c]) => !c).length;
      console.log('\n' + (bad ? bad + ' FAILURE' + (bad > 1 ? 'S' : '') : 'all green') + ' - ' + title + ' (' + res.length + ' checks)');
      return bad;
    }
  };
}

/* The regression that matters in a one-file app whose palette re-renders rows:
   a real pointer click is mouseover -> mousedown -> mouseup -> click, and if the
   row node is replaced in between, the browser aims the click at the <ul> and the
   user sees a menu that "does nothing". jsdom's .click() bypasses hit testing, so
   this drives the whole sequence on a captured node reference instead. */
export async function clickAndNavigate(html, { url = 'http://localhost/', label = 'index.html', find = /Dispatch Entry/ } = {}) {
  const { w, d, errs } = boot(html, { url });
  await wait(350);
  const mouse = (el, type) => el && el.dispatchEvent(new w.MouseEvent(type, { bubbles: true, cancelable: true, view: w }));
  const out = { label, errs };

  mouse(d.getElementById('paletteBtn'), 'click');
  await wait(40);
  const box = d.querySelector('.ux-palette');
  out.opened = !!box;
  if (!box) return out;

  const list = box.querySelector('ul');
  const li = [...list.querySelectorAll('li[data-i]')].find((x) => find.test(x.textContent));
  out.foundRow = !!li;
  if (!li) return out;

  mouse(li, 'mouseover');      // a real pointer sends both (jsdom does not synthesize
  mouse(li, 'mouseenter');     // mouseenter from mouseover, so dispatch it ourselves)
  await wait(25);
  out.rowSurvivesHover = list.contains(li);          // no innerHTML rebuild under the cursor
  out.hoverHighlights = li.dataset.on === '1';

  const icon = li.querySelector('.ico') || li;       // real clicks land on a child
  mouse(icon, 'mousedown'); mouse(icon, 'mouseup'); mouse(icon, 'click');
  await wait(80);
  out.paletteClosed = !d.querySelector('.ux-palette');
  const pane = d.getElementById('pane-dispatch');
  out.navigated = !!pane && !pane.classList.contains('hidden');
  out.activeTab = w.eval('typeof activeTabKey !== "undefined" ? activeTabKey : "?"');
  out.beacon = (d.querySelector('.ux-beacon') || {}).textContent || '';
  return out;
}

/* The same file before the fix: hover rebuilt the list, so the click died. Used to
   prove these assertions actually have teeth rather than merely blessing new code. */
export function withoutTheFix(html) {
  const mutant = html
    .replace("li.dataset.i = i;", "li.dataset.i = i;\n                    li.addEventListener('mouseenter', function () { sel = i; paint(); });")
    .replace(/\n\s*list\.addEventListener\('click', function \(e\) \{[\s\S]*?\n\s*\}\);/, '');
  if (mutant === html) throw new Error('could not build the "before the fix" mutant - palette code moved, update tests/lib.mjs');
  return mutant;
}
