// Per-shell session wiring check.
//
// Every shell declares a region for the running deliberation in its preview.
// These probes confirm that region exists in the live DOM and is empty before a
// run -- i.e. it is waiting for state rather than hard-coded copy. After a run
// the same regions receive current_critiques / current_participants.
//
// Usage: node tools/session-regions.mjs [track]
import { chromium } from "playwright";

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const USER = process.env.MM_USER ?? "izzul";
const TRACK = process.argv[2] ?? "Re:Juliet";

// region probe per archetype, matching the preview's own class names
const SHELLS = {
  terminal_hacker: {
    pick: /^terminal_hacker$/i,
    regions: {
      transcript: ".mm-line",
      empty_state: ".mm-boot",
      header: ".mm-term-top",
    },
  },
  chat_first: {
    pick: /^chat_first$/i,
    regions: { transcript: ".mm-message", empty_state: ".mm-empty, .mm-messages", rail: ".mm-truth-box" },
  },
  ai_research_lab: {
    pick: /^ai_research_lab$/i,
    regions: { transcript: ".mm-evidence-row", empty_state: ".mm-evidence-set", synthesis: ".mm-synth-label" },
  },
  ai_workspace: {
    pick: /^ai_workspace$/i,
    regions: { transcript: ".mm-thread", empty_state: ".mm-threads", desk: ".mm-desk-title" },
  },
  command_center: {
    pick: /^command_center$/i,
    regions: { transcript: ".mm-state-row", empty_state: ".mm-state-rows", board: ".mm-board-head" },
  },
  agent_canvas: {
    pick: /^agent_canvas$/i,
    regions: { participants: ".mm-cap", core: ".mm-core" },
  },
};

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

async function login() {
  await page.goto(BASE, { waitUntil: "networkidle" });
  await page.waitForSelector('input[type="text"], button[role="combobox"]', { timeout: 20000 });
  const btn = page.getByRole("button", { name: /login/i });
  if (await btn.count()) {
    await page.locator('input[type="text"]').fill(USER);
    await btn.click();
  }
  await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });
}

async function archBox() {
  const boxes = page.locator('button[role="combobox"]');
  for (let i = 0, n = await boxes.count(); i < n; i++) {
    await boxes.nth(i).click();
    await page.waitForTimeout(450);
    const opts = await page.getByRole("option").allInnerTexts();
    await page.keyboard.press("Escape");
    await page.waitForTimeout(180);
    if (opts.some((o) => /minimal_saas|terminal_hacker/.test(o))) return i;
  }
  return 1;
}

const ONLY = process.argv[3] ?? null;
const rows = [];
for (const [name, spec] of Object.entries(SHELLS)) {
  if (ONLY && name !== ONLY) continue;
  await login();
  // Probe for the combobox that actually offers the track list. first() is
  // right on a fresh login but lands on the skill picker once a composition
  // has been applied in an earlier iteration.
  let trackPicked = false;
  const boxes = page.locator('button[role="combobox"]');
  for (let k = 0, n = await boxes.count(); k < n && !trackPicked; k++) {
    await boxes.nth(k).click();
    await page.waitForTimeout(550);
    const t = page.getByRole("option", { name: new RegExp(TRACK, "i") }).first();
    if (await t.count()) { await t.click(); trackPicked = true; }
    else { await page.keyboard.press("Escape"); await page.waitForTimeout(250); }
  }
  if (!trackPicked) { rows.push({ name, missing: true }); continue; }
  await page.waitForTimeout(1200);

  // Back to the theme panel so the architecture selector is reachable again.
  const back = page.getByRole("button", { name: /back|theme|ubah|ganti/i }).first();
  if (await back.count()) { await back.click(); await page.waitForTimeout(1000); }

  const j2 = await archBox();
  await page.locator('button[role="combobox"]').nth(j2).click();
  await page.waitForTimeout(600);
  const opt = page.getByRole("option", { name: spec.pick }).first();
  if (!(await opt.count())) {
    const avail = await page.getByRole("option").allInnerTexts();
    console.error(`[debug] ${name}: offered = ${JSON.stringify(avail.slice(0, 9))}`);
    await page.keyboard.press("Escape");
    rows.push({ name, missing: true });
    continue;
  }
  await opt.click();
  await page.waitForTimeout(800);
  const apply = page.getByRole("button", { name: /apply composition/i });
  if (await apply.count()) { await apply.click(); await page.waitForTimeout(2200); }

const found = await page.evaluate((regions) => {
    const out = {};
    for (const [k, sel] of Object.entries(regions)) {
      out[k] = document.querySelectorAll(sel.split(",")[0].trim()).length;
    }
    out.shell = document.querySelector('[class*="mm-shell-"]')?.className.match(/mm-shell-\S+/)?.[0] ?? "?";
    return out;
  }, spec.regions);

  const err = await page.evaluate(() => {
    const e = document.body.innerText.match(/Error|Traceback|VarTypeError|AttributeError/i);
    return e ? e[0] : null;
  });

  rows.push({ name, ...found, err });
}

await browser.close();

const pad = (s, n) => String(s ?? "").padEnd(n);
console.log("\nSESSION REGIONS");
console.log("=".repeat(84));
console.log(pad("shell", 18), pad("shell class", 30), pad("region", 12), pad("n", 4), "error");
console.log("-".repeat(84));
let bad = 0;
for (const r of rows) {
  if (r.missing) { console.log(pad(r.name, 18), "ARCHETYPE NOT OFFERED"); bad++; continue; }
  const regions = Object.entries(r).filter(([k]) => !["name", "shell", "err"].includes(k));
  const line = regions.map(([k, v]) => `${k}=${v}`).join(" ");
  console.log(pad(r.name, 18), pad(r.shell, 30), pad(line.slice(0, 12), 12), "", r.err ?? "");
  if (r.err) bad++;
}
console.log(`\n${bad === 0 ? "PASS" : "FAIL"}  ${bad === 0 ? "all shells render their session regions without error" : bad + " problems"}`);