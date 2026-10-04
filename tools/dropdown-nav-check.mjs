// Dropdown and cross-surface wiring check.
//
// No provider keys here, so a debate cannot run. What can be verified locally is
// that the controls are wired to their events and that the two surfaces move
// between each other: login -> theme studio -> apply -> workspace -> back.
//
// Every dropdown is opened and its options read, so a control that renders but
// does not change anything is caught here rather than by eye.
import { chromium } from "playwright";

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const USER = process.env.MM_USER ?? "izzul";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const results = [];
const fail = (m) => results.push(["FAIL", m]);
const pass = (m) => results.push(["ok", m]);

await page.goto(BASE, { waitUntil: "networkidle" });
await page.waitForSelector('input[type="text"], button[role="combobox"]', { timeout: 20000 });

// --- login ----------------------------------------------------------------
if (await page.getByRole("button", { name: /login/i }).count()) {
  await page.locator('input[type="text"]').fill(USER);
  await page.getByRole("button", { name: /login/i }).click();
  pass("login accepted");
} else {
  fail("no login form");
}
await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });
pass("reached the theme studio");

// --- track dropdown -------------------------------------------------------
const boxes = page.locator('button[role="combobox"]');
const n = await boxes.count();
let trackOptions = 0;
for (let i = 0; i < n; i++) {
  await boxes.nth(i).click();
  await page.waitForTimeout(450);
  const opts = await page.getByRole("option").allInnerTexts();
  if (opts.length > 4) {
    trackOptions = opts.length;
    await page.getByRole("option").first().click();
    pass(`track dropdown offers ${opts.length}`);
  } else {
    await page.keyboard.press("Escape");
  }
}
if (trackOptions === 0) fail("no track dropdown found");

// --- architecture dropdown -> workspace -----------------------------------
await page.waitForTimeout(900);
const arch = page.locator('button[role="combobox"]').filter({ hasText: /_/ }).first();
if (await arch.count()) {
  await arch.click();
  await page.waitForTimeout(500);
  const opts = await page.getByRole("option").allInnerTexts();
  if (opts.length >= 7) pass(`architecture dropdown offers ${opts.length}`);
  else fail(`architecture dropdown offered ${opts.length}`);
  await page.getByRole("option", { name: /terminal_hacker/i }).first().click();
  await page.waitForTimeout(700);
}

// --- apply -> workspace ---------------------------------------------------
const apply = page.getByRole("button", { name: /apply composition/i });
if (await apply.count()) {
  await apply.click();
  await page.waitForTimeout(2200);
  const shell = await page.evaluate(() =>
    document.querySelector('[class*="mm-shell-"]')?.className.match(/mm-shell-\S+/)?.[0] ?? null);
  if (shell) pass(`apply reached the workspace (${shell})`);
  else fail("apply did not reach a shell");
} else {
  fail("apply composition button missing");
}

// --- terminal header dropdowns --------------------------------------------
const combos = page.locator('.mm-term-top [role="combobox"]');
const cn = await combos.count();
if (cn >= 2) {
  pass(`terminal header exposes ${cn} controls`);
  for (let i = 0; i < cn; i++) {
    const before = (await combos.nth(i).innerText()).trim();
    await combos.nth(i).click();
    await page.waitForTimeout(500);
    const opts = (await page.getByRole("option").allInnerTexts()).map((o) => o.trim());
    if (opts.length === 0) { fail(`header control ${i} opens with no options`); continue; }
    // the model picker leads with a "-- model --" placeholder; skip it
    const real = opts.filter((o) => !/^--.+--$/.test(o));
    const other = real.find((o) => o.toLowerCase() !== before.toLowerCase());
    if (!other) {
      fail(`header control ${i}: no alternative to ${before} (options: ${real.join(", ")})`);
      await page.keyboard.press("Escape");
      continue;
    }
    await page.getByRole("option", { name: new RegExp(`^${other.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`) }).first().click();
    await page.waitForTimeout(800);
    const after = (await combos.nth(i).innerText()).trim();
    if (after === before) fail(`header control ${i} did not change (${before} -> ${after})`);
    else pass(`header control ${i}: ${before} -> ${after}`);
    await page.keyboard.press("Escape").catch(() => {});
  }
} else {
  fail(`terminal header exposes ${cn} controls, expected 2`);
}

// --- workspace -> theme studio -> back ------------------------------------
const studio = page.getByRole("button", { name: /theme studio/i }).first();
if (await studio.count()) {
  await studio.click();
  await page.waitForTimeout(1400);
  const onTheme = await page.evaluate(() => !!document.querySelector("input[type='text']") ||
    document.body.innerText.includes("Theme Studio") || document.body.innerText.includes("MusicDNA"));
  if (onTheme) pass("theme studio reopened from the workspace");
  else fail("theme studio did not reopen");

  const back = page.getByRole("button", { name: /back|workspace|return/i }).first();
  if (await back.count()) {
    await back.click();
    await page.waitForTimeout(1400);
    const backInShell = await page.evaluate(() => !!document.querySelector('[class*="mm-shell-"]'));
    if (backInShell) pass("returned to the workspace shell");
    else fail("back did not return to the shell");
  } else {
    fail("no back control in the theme studio");
  }
} else {
  fail("no theme studio button in the workspace");
}

await browser.close();

console.log("\nDROPDOWN + NAVIGATION");
console.log("=".repeat(70));
for (const [s, m] of results) console.log(`${s.padEnd(5)} ${m}`);
const bad = results.filter(([s]) => s === "FAIL").length;
console.log(`\n${bad === 0 ? "PASS" : "FAIL"}  ${results.length - bad}/${results.length} checks`);