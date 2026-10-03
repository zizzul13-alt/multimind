// Shell audit: compare every archetype against the hand-built preview HTML.
//
// The previews are the contract. Each declares its own shell geometry, palette
// and font stack, and the whole point of the DNA is that the shells differ
// radically rather than only in colour. This drives a real login once, then
// walks every archetype and reports what the live shell actually measures.
//
// Usage: node tools/shell-audit.mjs ["Night Train"]
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const { chromium } = await import("playwright");

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const USER = process.env.MM_USER ?? "izzul";
const TRACK = process.argv[2] ?? "Night Train";
const PREVIEW =
  "C:/Users/lepy/AppData/Local/hermes/cache/scratch/mm/fe/preview/lab/music-v0/architecture-swap";

// The contract, read from the HTML rather than transcribed by hand.
function contract() {
  const out = {};
  for (const fn of readdirSync(PREVIEW)) {
    if (!fn.endsWith(".html")) continue;
    const s = readFileSync(join(PREVIEW, fn), "utf8");
    const name = fn
      .replace(/^(re-juliet|you-and-i)-/, "")
      .replace(/-v\d\.html$/, "")
      .replace(/\.html$/, "");
    const root = s.match(/:root\{([^}]+)\}/)?.[1] ?? "";
    const pal = Object.fromEntries(
      [...root.matchAll(/--([a-z0-9]+):\s*([^;]+)/g)].map((m) => [m[1], m[2].trim()]),
    );
    out[name] ??= {};
    out[name].shellCols =
      s.match(/\.app\{[^}]*grid-template-columns:\s*([^;}]+)/)?.[1]?.trim() ?? "";
    out[name].palette = pal;
    out[name].track = fn.startsWith("re-juliet") ? "re-juliet" : "you-and-i";
  }
  return out;
}

function hexToRgb(h) {
  const m = h?.match(/#([0-9a-f]{6})/i);
  if (!m) return null;
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function luminance([r, g, b]) {
  const f = (c) => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}

function contrast(a, b) {
  if (!a || !b) return null;
  const l1 = luminance(a);
  const l2 = luminance(b);
  const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1];
  return (hi + 0.05) / (lo + 0.05);
}

const C = contract();
// The catalog's own keys, which differ from the preview filenames.
const ARCHES = [
  "minimal_saas", "terminal_hacker", "ai_research_lab", "command_center",
  "ai_workspace", "chat_first", "agent_canvas",
];

// preview filename stem -> catalog key
const ALIAS = {
  terminal: "terminal_hacker",
  "terminal-v2": "terminal_hacker",
  "research-lab": "ai_research_lab",
};

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await page.goto(BASE, { waitUntil: "networkidle" });
await page.waitForSelector('input[type="text"]', { timeout: 15000 });
await page.fill('input[type="text"]', USER);
await page.getByRole("button", { name: /login/i }).click();
await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });

await page.locator('button[role="combobox"]').first().click();
await page.getByRole("option", { name: new RegExp(TRACK, "i") }).click();
await page.waitForTimeout(1200);

// Select the architecture combobox by probing: applying a composition
// re-renders the panel and re-orders the comboboxes, so a positional selector
// that is correct on first load points at the skill picker later.
async function findArchBox() {
  const boxes = page.locator('button[role="combobox"]');
  const n = await boxes.count();
  for (let i = 0; i < n; i++) {
    await boxes.nth(i).click();
    await page.waitForTimeout(500);
    const opts = await page.getByRole("option").allInnerTexts();
    await page.keyboard.press("Escape");
    await page.waitForTimeout(200);
    if (opts.some((o) => /minimal_saas|terminal_hacker/.test(o))) return i;
  }
  return 1;
}

const rows = [];

for (const arch of ARCHES) {
  // Start each archetype from the theme panel. Applying a composition switches the
  // page to the workspace view, where the architecture selector is gone, so the
  // panel has to be reopened between archetypes (the Back control).
  await page.goto(BASE, { waitUntil: "networkidle" });
  const back = page.getByRole("button", { name: /back|theme|ubah|ganti/i }).first();
  if (await back.count()) {
    await back.click();
    await page.waitForTimeout(1200);
  }
  const loginBox = page.locator('input[type="text"]');
  const loginBtn = page.getByRole("button", { name: /login/i });
  if (await loginBtn.count()) {
    await loginBox.fill(USER);
    await loginBtn.click();
  }
  await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });
  const musicBox = page.locator('button[role="combobox"]').first();
  await musicBox.click();
  await page.waitForTimeout(500);
  const trackOpt = page.getByRole("option", { name: new RegExp(TRACK, "i") }).first();
  if (!(await trackOpt.count())) {
    await page.keyboard.press("Escape");
    console.error(`[debug] track ${TRACK} not offered; skipping run`);
    await browser.close();
    process.exit(2);
  }
  await trackOpt.click();
  await page.waitForTimeout(1000);

  const idx = await findArchBox();
  const cb = page.locator('button[role="combobox"]').nth(idx);
  await cb.click();
  await page.waitForTimeout(700);
  const avail = await page.getByRole("option").allInnerTexts();
  const opt = page.getByRole("option", { name: new RegExp(arch.replace(/_/g, "[-_ ]"), "i") }).first();
  if (!(await opt.count())) {
    console.error(`[debug] ${arch}: not offered. available = ${JSON.stringify(avail)}`);
    await page.keyboard.press("Escape");
    rows.push({ arch, missing: true, avail });
    continue;
  }
  await opt.click();
  await page.waitForTimeout(900);
  const apply = page.getByRole("button", { name: /apply composition/i });
  if (await apply.count()) {
    await apply.click();
    await page.waitForTimeout(1800);
  }

  const m = await page.evaluate(() => {
    const q = (s) => document.querySelector(s);
    const cs = (el, p) => (el ? getComputedStyle(el)[p] : null);
    const world = q(".mm-world");
    const work = q(".mm-work");
    const title = q(".mm-world-title");
    const shell = world?.parentElement ?? world;
    const zones = new Set();
    if (shell) {
      for (const el of shell.querySelectorAll("*")) {
        for (const c of el.classList) {
          const k = c.match(/mm-(zone|panel|row|col|slot)-([a-z0-9]+)/i);
          if (k) zones.add(k[2]);
        }
      }
    }
    // any text whose contrast fails, so readability problems are counted not guessed
    let fails = 0;
    let worst = 99;
    let worstText = "";
    const lum = (s) => {
      const [r, g, b] = s.match(/\d+/g).map(Number).slice(0, 3).map((v) => {
        const x = v / 255;
        return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };
    for (const el of document.querySelectorAll("h1,h2,h3,p,span,button,label,div")) {
      if (el.children.length) continue;
      const t = el.innerText?.trim();
      if (!t || t.length > 160) continue;
      const st = getComputedStyle(el);
      if (st.visibility === "hidden" || st.display === "none" || Number(st.opacity) < 0.05) continue;
      let bgEl = el, bg = null;
      while (bgEl && bgEl !== document.documentElement) {
        const c = getComputedStyle(bgEl).backgroundColor;
        if (c && !/rgba?\([^)]*,\s*0\)/.test(c)) { bg = c; break; }
        bgEl = bgEl.parentElement;
      }
      if (!bg) bg = getComputedStyle(document.body).backgroundColor;
      const l1 = lum(st.color), l2 = lum(bg);
      const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1];
      const ratio = (hi + 0.05) / (lo + 0.05);
      const big = parseFloat(st.fontSize) >= 24 || (parseFloat(st.fontSize) >= 18.66 && Number(st.fontWeight) >= 700);
      const need = big ? 3 : 4.5;
      if (ratio < need) { fails++; if (ratio < worst) { worst = ratio; worstText = t.slice(0, 30); } }
    }
    return {
      worldBg: cs(world, "backgroundColor"),
      workBg: cs(work, "backgroundColor"),
      cols: cs(shell, "gridTemplateColumns"),
      shellClass: shell?.className ?? "",
      titlePx: parseFloat(cs(title, "fontSize") ?? "0") || 0,
      titleFont: (cs(title, "fontFamily") ?? "").split(",")[0],
      titleText: title?.innerText?.trim() ?? "",
      zones: [...zones],
      photos: document.querySelectorAll(".mm-world-photo img").length,
      textures: document.querySelectorAll(".mm-world-texture").length,
      sceneTabs: document.querySelectorAll(".mm-scene-tab").length,
      contrastFails: fails,
      worstContrast: worst === 99 ? null : Number(worst.toFixed(2)),
      worstText,
    };
  });

  rows.push({ arch, ...m });
}

await browser.close();

// --- report ---
const pad = (s, n) => String(s ?? "").padEnd(n);
console.log(`\nSHELL AUDIT — ${TRACK}`);
console.log("=".repeat(104));
console.log(pad("archetype", 16), pad("world", 21), pad("work", 21), pad("cols", 34), "zones");
console.log("-".repeat(104));
for (const r of rows) {
  if (r.missing) { console.log(pad(r.arch, 16), "ARCHETYPE NOT IN CATALOG"); continue; }
  console.log(
    pad(r.arch, 16),
    pad(r.worldBg, 21),
    pad(r.workBg, 21),
    pad((r.cols ?? "").slice(0, 32), 34),
    r.zones.length,
  );
}
console.log("\nDETAIL");
console.log("-".repeat(104));
for (const r of rows) {
  if (r.missing) continue;
  const key = ALIAS[r.arch.replace(/_/g, "-")] ?? r.arch.replace(/_/g, "-");
  const want = C[key] ?? {};
  console.log(`${r.arch}`);
  console.log(`   title    ${r.titlePx}px ${r.titleFont}  "${r.titleText.slice(0, 34)}"`);
  console.log(`   photos   ${r.photos}   textures ${r.textures}   sceneTabs ${r.sceneTabs}`);
  console.log(`   zones    ${r.zones.join(", ") || "(none)"}`);
  console.log(`   html     ${want.shellCols?.slice(0, 46) || "(flex/stack)"}`);
  console.log(`   palette  paper ${want.palette?.paper ?? "?"}  night ${want.palette?.night ?? "?"}  ink ${want.palette?.ink ?? "?"}`);
  const c = contrast(hexToRgb(want.palette?.ink), hexToRgb(want.palette?.paper));
  if (c) console.log(`   html ink-on-paper contrast ${c.toFixed(2)}:1`);
  console.log(`   a11y     ${r.contrastFails} failing  worst ${r.worstContrast} ("${r.worstText}")`);
}
