// Visual check for the MusicDNA workspace.
//
// Drives a real login, selects a track and an archetype, applies the
// composition, then reads back the computed geometry and colour of the world
// rail and the work column. The point is to compare the numbers against the
// hand-built preview rather than eyeballing a screenshot: a target
// dark-left / light-right split has an objective signature.
//
// Usage:
//   node tools/visual-check.mjs                    # default: ti01 / minimal_saas
//   node tools/visual-check.mjs ti01 command_center
const { chromium } = await import("playwright");

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const USER = process.env.MM_USER ?? "izzul";
const TRACK = process.argv[2] ?? "Night Train";
const ARCHETYPE = process.argv[3] ?? "minimal_saas";
const SHOT = process.env.MM_SHOT ?? null;

// Mirrors what the previews specify. A pass means the two-tone split is real.
const EXPECT = {
  worldDark: true,   // left plate must be dark
  workLight: true,   // right plate must be light
  minContrast: 0.3,  // relative luminance gap; 0-1 scale, not 0-21
  minTitlePx: 40,    // editorial title scale
};

function luminance([r, g, b]) {
  const f = (c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

try {
  await page.goto(BASE, { waitUntil: "networkidle" });
  await page.waitForSelector('input[type="text"]', { timeout: 15000 });
  await page.fill('input[type="text"]', USER);
  await page.getByRole("button", { name: /login/i }).click();
  await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });

  // MusicDNA track
  await page.locator('button[role="combobox"]').first().click();
  await page.getByRole("option", { name: new RegExp(TRACK, "i") }).click();
  await page.waitForTimeout(1500);

  // Architecture
  await page.locator('button[role="combobox"]').nth(1).click();
  await page.getByRole("option", { name: new RegExp(ARCHETYPE, "i") }).click();
  await page.waitForTimeout(1500);

  await page.getByRole("button", { name: /apply composition/i }).click();
  await page.waitForTimeout(2500);

  const m = await page.evaluate(() => {
    const px = (el, p) => (el ? getComputedStyle(el)[p] : null);
    const box = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { w: Math.round(r.width), h: Math.round(r.height) };
    };
    const title = document.querySelector(".mm-world-title");
    const tex = document.querySelector(".mm-world-texture");
    return {
      worldBg: px(document.querySelector(".mm-world"), "backgroundColor"),
      workBg: px(document.querySelector(".mm-work"), "backgroundColor"),
      titleText: title?.innerText?.trim() ?? "",
      titlePx: parseFloat(px(title, "fontSize") ?? "0"),
      titleFamily: px(title, "fontFamily"),
      worldBox: box(".mm-world"),
      workBox: box(".mm-work"),
      textureWidth: tex?.naturalWidth ?? 0,
      sceneTabs: document.querySelectorAll(".mm-scene-tab").length,
      shell: (document.querySelector("[class*='mm-shell-']")?.className ?? "")
        .split(" ").filter((c) => c.startsWith("mm-shell-"))[0] ?? null,
      hasRail: Boolean(document.querySelector(".mm-world")),
      hasWorkColumn: Boolean(document.querySelector(".mm-work")),
    };
  });

  const toRgb = (s) => (s ?? "").match(/\d+/g)?.slice(0, 3).map(Number) ?? null;
  const wL = toRgb(m.worldBg) ? luminance(toRgb(m.worldBg)) : null;
  const kL = toRgb(m.workBg) ? luminance(toRgb(m.workBg)) : null;
  const contrast = wL !== null && kL !== null ? Math.abs(wL - kL) : 0;

  const checks = [
    ["world rail present", Boolean(m.worldBox), m.worldBox],
    ["work column present", Boolean(m.workBox), m.workBox],
    ["title not empty", m.titleText.length > 0, m.titleText.slice(0, 40)],
    [`title >= ${EXPECT.minTitlePx}px`, m.titlePx >= EXPECT.minTitlePx, m.titlePx],
    ["texture loaded", m.textureWidth > 0, m.textureWidth],
    ["scene tabs == 3", m.sceneTabs === 3, m.sceneTabs],
    ["plate contrast >= 0.3", contrast >= EXPECT.minContrast, contrast.toFixed(3)],
    ["world is the darker plate", wL !== null && kL !== null && wL < kL, { worldL: wL, workL: kL }],
  ];

  console.log(`\ntrack=${TRACK} archetype=${ARCHETYPE}\n`);
  let failed = 0;
  for (const [label, ok, detail] of checks) {
    if (!ok) failed += 1;
    console.log(`  ${ok ? "PASS" : "FAIL"}  ${label}  ${JSON.stringify(detail)}`);
  }
  console.log(`\n  worldBg=${m.worldBg}  workBg=${m.workBg}`);
  console.log(`  titleFamily=${(m.titleFamily ?? "").slice(0, 60)}`);
  console.log(`  shell=${m.shell}  rail=${m.hasRail}  workColumn=${m.hasWorkColumn}`);
  if (m.shell && !m.hasRail) {
    console.log(
      "  -> this archetype has its own shell but still renders the generic zones;\n" +
        "     the replicated world rail + work column are minimal_saas only so far."
    );
  }
  console.log("");

  if (SHOT) {
    await page.screenshot({ path: SHOT, fullPage: false });
    console.log(`  screenshot -> ${SHOT}`);
  }

  await browser.close();
  console.log(failed === 0 ? "ALL CHECKS PASSED" : `${failed} CHECK(S) FAILED`);
  process.exit(failed === 0 ? 0 : 1);
} catch (err) {
  console.error("visual-check failed:", err.message);
  await browser.close();
  process.exit(2);
}
