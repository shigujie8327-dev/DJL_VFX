// Plays every hero's skills and variants in headless Chromium and reports page errors.
// Usage: node tools/smoke_test.js   (needs playwright)
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 1000 } });
  const errs = []; p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('file://' + path.resolve(__dirname, '..', 'dist', 'djl-skill-vfx.html')); await p.waitForTimeout(2500);
  let n = 0;
  for (const h of await p.$$eval('.hero', (els) => els.map((e) => e.dataset.id))) {
    await p.click(`.hero[data-id=${h}]`);
    for (const id of await p.$$eval('.skill', (els) => els.map((e) => e.dataset.id))) {
      await p.click(`.skill[data-id=${id}]`); await p.waitForTimeout(150);
      const vars = await p.$$eval('#varSeg button', (els) => els.map((e) => e.dataset.v)).catch(() => []);
      for (const v of vars.length ? vars : [null]) {
        if (v !== null) await p.click(`#varSeg button[data-v="${v}"]`);
        await p.waitForTimeout(2600); n++;
      }
    }
  }
  console.log(`${n} plays, ${errs.length} page errors`); errs.forEach((e) => console.log(' ', e));
  await b.close(); process.exit(errs.length ? 1 : 0);
})();
