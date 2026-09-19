/* "Jump to shows up but clicking a row does nothing" - the bug, the fix, and a
   control that proves the test would still catch it.   node tests/palette-click.mjs */
import fs from 'fs';
import path from 'path';
import { ROOT, suite, clickAndNavigate, withoutTheFix } from './lib.mjs';

const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const s = suite();

const a = await clickAndNavigate(html, { label: 'index.html' });
s.ok(a.opened, 'Jump to opens the palette');
s.ok(a.foundRow, 'a "Dispatch Entry" row is listed');
s.ok(a.rowSurvivesHover, 'hover does not rebuild the list, so the row survives under the cursor');
s.ok(a.hoverHighlights, 'hover moves the highlight onto that row');
s.ok(a.paletteClosed, 'click closes the palette');
s.ok(a.navigated, 'click opens the Dispatch Entry pane');
s.ok(a.activeTab === 'dispatch', 'app state followed: activeTabKey = ' + a.activeTab);
s.ok(!a.beacon, 'no error beacon from a normal click' + (a.beacon ? ': ' + a.beacon.slice(0, 90) : ''));
s.ok(a.errs.length === 0, 'no script errors on the click path' + (a.errs[0] ? ': ' + a.errs[0] : ''));

const b = await clickAndNavigate(withoutTheFix(html), { label: 'mutant' });
s.ok(b.opened, '[control] the pre-fix build opens the palette just the same (so "it opens" proves nothing)');
s.ok(!b.rowSurvivesHover, '[control] [pre-fix] hover destroyed the row node - exactly the reported symptom');
s.ok(!(b.navigated && b.paletteClosed), '[control] [pre-fix] and the click genuinely did nothing');

process.exit(s.report('palette click') ? 1 : 0);
