// Terminal session check: does the session render as the screen content?
//
// The preview puts the running deliberation in .term > .screen -- a boot line,
// the active world, one article per turn, and a composer pinned to the foot of
// the viewport. What used to be missing is that the session lived in a separate
// card below the shell. This reads the live terminal and reports where each
// piece actually is.
import { chromium } from "playwright";

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const USER = process.env.MM_USER ?? "izzul";
const TRACK = process.argv[2] ?? "Re:Juliet";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await page.goto(BASE, { waitUntil: "networkidle" });
await page.waitForSelector('input[type="text"], button[role="combobox"]', { timeout: 20000 });
const login = page.getByRole("button", { name: /login/i });
if (await login.count()) {
  await page.locator('input[type="text"]').fill(USER);
  await login.click();
}
await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });

await page.locator('button[role="combobox"]').first().click();
await page.waitForTimeout(500);
await page.getByRole("option", { name: new RegExp(TRACK, "i") }).first().click();
await page.waitForTimeout(1200);

await page.locator('button[role="combobox"]').nth(1).click();
await page.waitForTimeout(500);
await page.getByRole("option", { name: /terminal/i }).first().click();
await page.waitForTimeout(700);
const apply = page.getByRole("button", { name: /apply composition/i });
if (await apply.count()) { await apply.click(); await page.waitForTimeout(2500); }

const m = await page.evaluate(() => {
  const box = (s) => document.querySelector(s);
  const rect = (s) => { const e = box(s); return e ? e.getBoundingClientRect() : null; };
  const screen = box(".mm-screen");
  const comp = box(".mm-composer");
  const zones = [...document.querySelectorAll(".mm-zone")].map((z) => ({
    cls: z.className.match(/mm-zone-\w+/)?.[0] ?? "?",
    top: Math.round(z.getBoundingClientRect().top),
    h: Math.round(z.getBoundingClientRect().height),
  }));
  return {
    viewportH: window.innerHeight,
    screenH: screen ? Math.round(screen.getBoundingClientRect().height) : 0,
    screenScroll: screen ? getComputedStyle(screen).overflowY : "-",
    screenTop: screen ? Math.round(screen.getBoundingClientRect().top) : 0,
    boot: box(".mm-boot")?.innerText?.trim().slice(0, 54) ?? "-",
    sessionId: box(".mm-top-b")?.innerText?.trim() ?? "-",
    activeBuffer: box(".mm-term-name")?.innerText?.trim() ?? "-",
    turns: document.querySelectorAll(".mm-line").length,
    composerTop: comp ? Math.round(comp.getBoundingClientRect().top) : 0,
    composerH: comp ? Math.round(comp.getBoundingClientRect().height) : 0,
    composerText: box(".mm-prompt-input")?.getAttribute("placeholder")?.slice(0, 44) ?? "-",
    runLabel: box(".mm-run")?.innerText?.trim() ?? "-",
    zones,
    // the question: does any zone still own the lower half of the viewport?
    screenBottom: screen ? Math.round(screen.getBoundingClientRect().bottom) : 0,
  };
});

console.log("\nTERMINAL SESSION");
console.log("=".repeat(72));
for (const [k, v] of Object.entries(m)) {
  if (Array.isArray(v)) {
    console.log(`${k}: ${JSON.stringify(v)}`);
  } else {
    console.log(`${k}: ${v}`);
  }
}
const bigZoneBelow = m.zones.filter((z) => z.top >= m.screenBottom && z.h > 200);
const occupiesLowerHalf = bigZoneBelow.length > 0;
console.log(
  `\n${occupiesLowerHalf ? "FAIL" : "PASS"}  ` +
    (occupiesLowerHalf
      ? "a zone still takes the lower half of the viewport"
      : "the session owns the screen; no generic panel below it"),
);

await browser.close();