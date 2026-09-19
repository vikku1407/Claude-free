/* Runs the single-file handout the way a user will: built from the repo, opened
   from a file:// path, with localStorage unavailable (what Safari does there).
   node tests/standalone-file.mjs                                                   */
import fs from 'fs';
import os from 'os';
import path from 'path';
import { execFileSync } from 'child_process';
import { ROOT, suite, boot, wait, clickAndNavigate } from './lib.mjs';

const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'erp-handout-'));
const file = path.join(outDir, 'MCS-ERP-standalone.html');
execFileSync('python3', [path.join(ROOT, 'vendor', 'build-standalone.py'), outDir], { stdio: 'pipe' });
if (!fs.existsSync(file)) { console.log('FAIL the builder wrote no ' + file); process.exit(1); }
const html = fs.readFileSync(file, 'utf8');
const s = suite();

s.ok(!/<link[^>]+vendor/.test(html), 'no <link> points at the missing vendor/ folder');
s.ok(!/<script[^>]+src=/.test(html), 'no <script src> at all (everything is inline)');
s.ok((html.match(/url\(data:font\/woff2;base64,/g) || []).length >= 15,
     'webfonts inlined as data URIs: ' + (html.match(/url\(data:font/g) || []).length + ' faces');
s.ok(/\.text-xs\s*\{/.test(html) && /fa-truck-fast/.test(html), 'the Tailwind build and the FA glyphs came along');
s.ok(html.includes('Excel needs the vendor/ folder'), 'Excel fallback text is in the built file');

const r = await clickAndNavigate(html, { url: 'file://' + file, label: 'standalone' });
s.ok(r.errs.length === 0, 'boots from a file:// path without script errors' + (r.errs[0] ? ': ' + r.errs[0] : ''));
s.ok(r.opened, 'Jump to opens, from a double-clicked file');
s.ok(r.rowSurvivesHover, 'hover keeps the row node');
s.ok(r.navigated && r.activeTab === 'dispatch', 'click on a module opens it (activeTabKey = ' + r.activeTab + ')');
s.ok(!r.beacon, 'no error beacon' + (r.beacon ? ': ' + r.beacon.slice(0, 80) : ''));

/* locked-down storage is the file:// case a browser really hits */
const { w, d, errs } = boot(html, { url: 'file://' + file });
await wait(350);
const mouse = (el) => el && el.dispatchEvent(new w.MouseEvent('click', { bubbles: true, view: w }));
s.ok(w.eval('typeof localStorage') === 'undefined', 'this origin has no localStorage at all (the hard case)');
const badge = d.querySelector('#savedBadge');
s.ok(badge && /Auto-save off/i.test(badge.textContent), 'badge admits it instead of claiming a save: "' + (badge ? badge.textContent.trim() : 'no badge') + '"');
w.eval('erpSave()'); w.eval('erpLoad()');
await wait(25);
s.ok(errs.length === 0, 'save/load with no storage is a silent no-op, not a throw');
s.ok(!d.querySelector('.ux-beacon'), 'blocked storage raised no beacon');

mouse(d.querySelector('#densityBtn'));
await wait(25);
s.ok(d.body.dataset.density === 'compact', 'density toggle works with no vendor/ and no storage');
w.eval('exportStyledExcelReport()');
await wait(60);
s.ok(errs.length === 0, 'clicking Export-to-Excel without vendor/ throws nothing');
s.ok(/ux\d+\.\d+ \(/.test((d.querySelector('.ux-build') || {}).textContent || ''), 'build stamp printed even in the single-file build: ' + (d.querySelector('.ux-build') || {}).textContent.trim());

process.exit(s.report('single-file handout') ? 1 : 0);
