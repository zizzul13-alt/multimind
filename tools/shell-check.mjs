// Per-archetype shell check: does each shell actually render its own structure?
//
// shell-audit.mjs reads geometry but relies on .mm-world/.mm-work, which only
// the minimal_saas shell has. This one asks the structural question directly:
// which shell root is present, how many columns it resolves to, whether the
// scene photo and switcher rendered.
import { chromium } from "playwright";

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const TRACK = process.argv[2] ?? "Night Train";
// process.env on Windows may be empty under some shells; treat "1"/"true" as on.
const SHOTS = ["1", "true"].includes(String(process.env.MM_SHOTS ?? "").toLowerCase());
const SHOT_DIR = process.env.MM_SHOT_DIR ?? ".";

const SHELLS = {
  minimal_saas: { root: ".mm-shell-minimal-saas", world: ".mm-world", work: ".mm-work" },
  terminal_hacker: { root: ".mm-shell-terminal-hacker", world: ".mm-side", work: ".mm-term" },
  ai_research_lab: { root: ".mm-shell-ai-research-lab", world: ".mm-viewport-wrap", work: ".mm-lab" },
  ai_workspace: { root: ".mm-shell-ai-workspace", world: ".mm-worldpanel-photo", work: ".mm-workspace-3" },
  chat_first: { root: ".mm-shell-chat-first", world: ".mm-worlds", work: ".mm-messages" },
  agent_canvas: { root: ".mm-shell-agent-canvas", world: ".mm-core", work: ".mm-inspect" },
  command_center: { root: ".mm-shell-command-center", world: ".mm-ground-photo", work: ".mm-board" },
};

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

async function findArchBox() {
  const boxes = page.locator('button[role="combobox"]');
  const n = await boxes.count();
  for (let i = 0; i < n; i++) {
    await boxes.nth(i).click();
    await page.waitForTimeout(450);
    const opts = await page.getByRole("option").allInnerTexts();
    await page.keyboard.press("Escape");
    await page.waitForTimeout(200);
    if (opts.some((o) => /minimal_saas|terminal_hacker/.test(o))) return i;
  }
  return 1;
}

await page.goto(BASE, { waitUntil: "networkidle" });
await page.waitForSelector('button[role="combobox"], input[type="text"]', { timeout: 20000 });
const lb = page.locator('input[type="text"]');
const lbtn = page.getByRole("button", { name: /login/i });
if (await lbtn.count()) { await lb.fill(process.env.MM_USER ?? "izzul"); await lbtn.click(); }
await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });
await page.locator('button[role="combobox"]').first().click();
await page.waitForTimeout(500);
await page.getByRole("option", { name: new RegExp(TRACK, "i") }).first().click();
await page.waitForTimeout(1200);

const rows = [];
for (const [arch, sel] of Object.entries(SHELLS)) {
  // back to the theme panel, since applying switches to the workspace view
  await page.goto(BASE, { waitUntil: "networkidle" });
  const back = page.getByRole("button", { name: /back|theme|ubah|ganti/i }).first();
  if (await back.count()) { await back.click(); await page.waitForTimeout(1000); }
  const lb2 = page.locator('input[type="text"]');
  const lbtn2 = page.getByRole("button", { name: /login/i });
  if (await lbtn2.count()) { await lb2.fill(process.env.MM_USER ?? "izzul"); await lbtn2.click(); }
  await page.waitForSelector('button[role="combobox"], input[type="text"]', { timeout: 20000 });
  if (await page.locator('input[type="text"]').count()) {
    await page.locator('input[type="text"]').fill(USER);
    await page.getByRole("button", { name: /login/i }).click();
    await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });
  }
  await page.locator('button[role="combobox"]').first().click();
  await page.waitForTimeout(450);
  await page.getByRole("option", { name: new RegExp(TRACK, "i") }).first().click();
  await page.waitForTimeout(900);

  const idx = await findArchBox();
  await page.locator('button[role="combobox"]').nth(idx).click();
  await page.waitForTimeout(600);
  const opt = page.getByRole("option", { name: new RegExp(arch.replace(/_/g, "[-_ ]"), "i") }).first();
  if (!(await opt.count())) { await page.keyboard.press("Escape"); rows.push({ arch, missing: true }); continue; }
  await opt.click();
  await page.waitForTimeout(800);
  const apply = page.getByRole("button", { name: /apply composition/i });
  if (await apply.count()) { await apply.click(); await page.waitForTimeout(2000); }

  const m = await page.evaluate((sel) => {
    const root = document.querySelector(sel.root);
    const world = document.querySelector(sel.world);
    const work = document.querySelector(sel.work);
    const cs = (el, p) => (el ? getComputedStyle(el)[p] : null);
    const cols = cs(work || root, "gridTemplateColumns") || "";
    return {
      root: !!root,
      world: !!world,
      work: !!work,
      cols: cols.split(" ").filter(Boolean).length,
      colsRaw: cols.slice(0, 40),
      wpx: world ? Math.round(world.getBoundingClientRect().width) : 0,
      photos: document.querySelectorAll(".mm-world-photo-img, .mm-core img").length,
      buffers: document.querySelectorAll(".mm-buffer").length,
      msgs: document.querySelectorAll(".mm-message").length,
      zones: document.querySelectorAll(".mm-top, .mm-brand, .mm-label").length,
      hpx: root ? Math.round(root.getBoundingClientRect().height) : 0,
    };
  }, sel);

  if (SHOTS) await page.screenshot({ path: `${SHOT_DIR}/shell-${arch}.png`, fullPage: true });
  rows.push({ arch, ...m });
}

await browser.close();

const pad = (s, n) => String(s ?? "").padEnd(n);
console.log(`\nSHELL CHECK — ${TRACK}`);
console.log("=".repeat(96));
console.log(pad("archetype", 17), pad("root", 6), pad("world", 7), pad("work", 6), pad("cols", 5),
            pad("photo", 6), pad("buf", 4), pad("msg", 4), pad("h", 6), "geometry");
console.log("-".repeat(96));
for (const r of rows) {
  if (r.missing) { console.log(pad(r.arch, 17), "NOT IN CATALOG"); continue; }
  console.log(
    pad(r.arch, 17), pad(r.root, 6), pad(r.world, 7), pad(r.work, 6), pad(r.cols, 5),
    pad(r.photos, 6), pad(r.buffers, 4), pad(r.msg, 4), pad(r.hpx, 6), r.colsRaw,
  );
}
const ok = rows.filter((r) => r.root && r.world && r.work).length;
console.log(`\n${ok}/${rows.length} shells render their own structure.`);