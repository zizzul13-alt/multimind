// Do different tracks actually look different?
//
// The whole point of the previews is that each track is its own world. This walks
// the catalog and reports the ground, the scene names and the photo each track
// resolves to, so two tracks sharing a world is visible as a number rather than
// as a feeling.
import { chromium } from "playwright";

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const USER = process.env.MM_USER ?? "izzul";

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

async function trackOptions() {
  const boxes = page.locator('button[role="combobox"]');
  for (let i = 0, n = await boxes.count(); i < n; i++) {
    await boxes.nth(i).click();
    await page.waitForTimeout(450);
    const opts = await page.getByRole("option").allInnerTexts();
    await page.keyboard.press("Escape");
    await page.waitForTimeout(180);
    if (opts.length > 8) return opts;
  }
  return [];
}

const tracks = await trackOptions();
console.log(`\nTRACK WORLDS  (${tracks.length} tracks)`);
console.log("=".repeat(78));

const seen = new Map();
for (const label of tracks) {
  // Applying a composition switches to the workspace view, where the music
  // selector no longer exists, so return to the theme panel before each pick.
  await page.goto(BASE, { waitUntil: "networkidle" });
  const back = page.getByRole("button", { name: /back|theme studio|ubah|ganti/i }).first();
  if (await back.count()) { await back.click(); await page.waitForTimeout(1200); }
  const lb = page.locator('input[type="text"]');
  const lbtn = page.getByRole("button", { name: /login/i });
  if (await lbtn.count()) { await lb.fill(USER); await lbtn.click(); await page.waitForTimeout(2500); }

  let picked = false;
  const boxes = page.locator('button[role="combobox"]');
  for (let i = 0, n = await boxes.count(); i < n && !picked; i++) {
    await boxes.nth(i).click();
    await page.waitForTimeout(450);
    const t = page.getByRole("option", { name: label }).first();
    if (await t.count()) { await t.click(); picked = true; }
    else { await page.keyboard.press("Escape"); await page.waitForTimeout(200); }
  }
  if (!picked) { console.log(`${label.slice(0, 22).padEnd(24)} (not selectable)`); continue; }
  await page.waitForTimeout(900);

  // keep the archetype fixed so only the track changes
  const arch = page.locator('button[role="combobox"]').filter({ hasText: /_/ }).first();
  if (await arch.count()) {
    await arch.click();
    await page.waitForTimeout(450);
    const a = page.getByRole("option", { name: /^minimal_saas$/i }).first();
    if (await a.count()) { await a.click(); await page.waitForTimeout(600); }
    else { await page.keyboard.press("Escape"); }
  }
  const apply = page.getByRole("button", { name: /apply composition/i });
  if (await apply.count()) { await apply.click(); await page.waitForTimeout(2000); }

  const m = await page.evaluate(() => {
    const world = document.querySelector(".mm-world");
    const photo = document.querySelector(".mm-world-photo-img, .mm-world img");
    const title = document.querySelector(".mm-world-title");
    const scenes = [...document.querySelectorAll(".mm-scene-tab, .mm-buffer")].map((b) =>
      b.innerText.replace(/\n/g, "/").trim());
    return {
      ground: world ? getComputedStyle(world).backgroundColor : null,
      photo: photo ? (photo.src || "").split("/").pop() : null,
      loaded: photo ? photo.naturalWidth : 0,
      title: title?.innerText?.replace(/\n/g, " ").slice(0, 26) ?? "",
      scenes: scenes.slice(0, 3).join(" "),
    };
  });

  const key = `${m.ground}|${m.photo}`;
  const dupe = seen.has(key) ? `  SAME AS ${seen.get(key)}` : "";
  if (!dupe) seen.set(key, label.slice(0, 18));
  console.log(
    `${label.slice(0, 22).padEnd(24)} ${String(m.ground).padEnd(20)} ${String(m.photo || "-").padEnd(20)} ${m.title}${dupe}`,
  );
}

await browser.close();
console.log(`\n${seen.size} distinct world combinations across ${tracks.length} tracks`);