// Probe: which combobox is the architecture selector?
// nth() is unreliable because the workspace re-orders its comboboxes as it
// renders, so find the one that actually offers archetype options.
import { chromium } from "playwright";

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await page.goto(BASE, { waitUntil: "networkidle" });
await page.waitForSelector('input[type="text"]', { timeout: 15000 });
await page.fill('input[type="text"]', process.env.MM_USER ?? "izzul");
await page.getByRole("button", { name: /login/i }).click();
await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });

const boxes = page.locator('button[role="combobox"]');
const n = await boxes.count();
console.log(`${n} comboboxes\n`);

for (let i = 0; i < n; i++) {
  const label = (await boxes.nth(i).innerText().catch(() => "")).replace(/\n/g, " ").slice(0, 40);
  await boxes.nth(i).click();
  await page.waitForTimeout(600);
  const opts = (await page.getByRole("option").allInnerTexts()).filter(Boolean);
  await page.keyboard.press("Escape");
  await page.waitForTimeout(200);
  const isArch = opts.some((o) => /minimal_saas|terminal_hacker|command_center|chat_first|agent_canvas/.test(o));
  console.log(`[${i}] "${label}"  n=${opts.length}  ARCH=${isArch ? "YES" : "no"}`);
  console.log(`      ${opts.slice(0, 8).join(" | ").slice(0, 96)}`);
}
await browser.close();
