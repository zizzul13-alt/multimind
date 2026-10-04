// Screenshot the terminal shell header so the two controls can be eyeballed
// against the preview's `model / GPT-5.6 SOL · memory / ON` line.
import { chromium } from "playwright";

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const OUT = process.argv[2] ?? "shots/terminal-header.png";
const TRACK = process.argv[3] ?? "Re:Juliet";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await page.goto(BASE, { waitUntil: "networkidle" });
await page.waitForSelector('input[type="text"], button[role="combobox"]', { timeout: 20000 });
const login = page.getByRole("button", { name: /login/i });
if (await login.count()) {
  await page.locator('input[type="text"]').fill(process.env.MM_USER ?? "izzul");
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

const header = page.locator(".mm-term-top");
await header.screenshot({ path: OUT });
console.log("header ->", OUT);

// and open the model picker so the options are visible in the record
const combo = page.locator('.mm-term-top [role="combobox"]').first();
await combo.click();
await page.waitForTimeout(700);
const items = await page.getByRole("option").allInnerTexts();
console.log("model options:", JSON.stringify(items));
await page.screenshot({ path: OUT.replace(".png", "-open.png") });
console.log("open   ->", OUT.replace(".png", "-open.png"));

await browser.close();