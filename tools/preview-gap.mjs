// Gap audit: what the preview declares versus what Reflex renders.
//
// The previews are the contract, so this reads them directly and compares each
// declared property against the live shell. Nothing here is transcribed by
// hand -- if a value is missing from the HTML, it is reported as absent rather
// than assumed.
//
// Usage: node tools/preview-gap.mjs [track] [archetype]
import { readFileSync, existsSync, writeFileSync } from "node:fs";
import { chromium } from "playwright";

const BASE = process.env.MM_BASE ?? "http://localhost:3000";
const USER = process.env.MM_USER ?? "izzul";
const TRACK = process.argv[2] ?? "Night Train";
const ONLY = process.argv[3] ?? null;
const PREVIEW = "public/preview/lab/music-v0/architecture-swap";
const OUT = process.env.MM_GAP_OUT ?? "gap-report.md";

// catalog key -> preview stem
const ALIAS = {
  minimal_saas: "minimal-saas",
  terminal_hacker: "terminal",
  ai_research_lab: "research-lab",
  ai_workspace: "ai-workspace",
  chat_first: "chat-first",
  agent_canvas: "agent-canvas",
  command_center: "command-center",
};

/** Everything the preview declares, read rather than remembered. */
function declared(file) {
  const p = `${PREVIEW}/re-juliet-${file}-v1.html`;
  if (!existsSync(p)) return null;
  const s = readFileSync(p, "utf8");
  const root = s.match(/:root\{([^}]+)\}/)?.[1] ?? "";
  const palette = Object.fromEntries(
    [...root.matchAll(/--([a-z0-9]+):\s*([^;]+)/g)].map((m) => [m[1], m[2].trim()]),
  );
  const body = (s.match(/html,body\{([^}]*)\}/)?.[1] ?? "").trim();
  const photo = (s.match(/\.photo\{([^}]*)\}/)?.[1] ?? "").trim();
  const gradients = [...s.matchAll(/\.photo:after\{([^}]*)\}/g)].map((m) => m[1].trim());
  // the literal visible copy, in document order
  const copy = [
    ...s.matchAll(/<h1[^>]*>([\s\S]*?)<\/h1>/g),
    ...s.matchAll(/class="kicker"[^>]*>([^<]+)</g),
    ...s.matchAll(/class="label"[^>]*>([^<]+)</g),
    ...s.matchAll(/class="boot"[^>]*>([\s\S]*?)<\/div>/g),
  ]
    .map((m) => m[1].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim())
    .filter(Boolean);
  const fonts = [...new Set([...s.matchAll(/font-family:([^;}]+)/g)].map((m) => m[1].trim()))];
  const shellCols = (s.match(/\.app\{[^}]*grid-template-columns:\s*([^;}]+)/)?.[1] ?? "").trim();
  return { palette, body, photo, gradients, copy, fonts, shellCols, path: p };
}

/** What the live shell actually computes. */
const probe = () => {
  const cs = (el, p) => (el ? getComputedStyle(el)[p] : null);
  const root = document.querySelector(".mm-shell") ?? document.body;
  const side = document.querySelector(".mm-side, .mm-world, .mm-canvas, .mm-shelf, .mm-rail");
  const photo = document.querySelector(".mm-scene-plate, .mm-world-photo, .mm-core, .mm-worldpanel-photo");
  const screen = document.querySelector(".mm-screen, .mm-term, .mm-work, .mm-lab");
  const h1 = root.querySelector("h1, .mm-world-title, .mm-term-name, .mm-canvas-title");
  const buf = document.querySelector(".mm-buffer, .mm-scene-tab");
  const prompt = root.querySelector(".mm-boot, .mm-prompt");
  const head = document.querySelector(".mm-head, .mm-board-head, .mm-desk-head");
  return {
    shellClass: root.className,
    bodyBg: cs(document.body, "backgroundColor"),
    bodyColor: cs(document.body, "color"),
    bodyFont: cs(document.body, "fontFamily"),
    cols: cs(screen, "gridTemplateColumns"),
    sideCols: cs(root, "gridTemplateColumns"),
    sideBg: cs(side, "backgroundColor"),
    sideFilter: cs(side, "backdropFilter"),
    h1Font: (cs(h1, "fontFamily") ?? "").split(",")[0].replace(/["']/g, ""),
    h1Text: h1?.innerText?.trim().slice(0, 40) ?? "",
    monoUsed: cs(buf, "fontFamily")?.split(",")[0].replace(/["']/g, "") ?? "",
    promptText: prompt?.innerText?.trim().slice(0, 40) ?? "",
    headText: head?.innerText?.trim().slice(0, 40) ?? "",
    photoFilter: cs(photo, "filter"),
    photoPresent: !!photo,
    hasDot: !!document.querySelector(".mm-dot"),
  };
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
    await page.waitForTimeout(180);
    if (opts.some((o) => /minimal_saas|terminal_hacker/.test(o))) return i;
  }
  return 1;
}

const rows = [];

async function selectArchetype(page, arch) {
  await page.goto(BASE, { waitUntil: "networkidle" });
  const back = page.getByRole("button", { name: /back|theme|ubah|ganti/i }).first();
  if (await back.count()) { await back.click(); await page.waitForTimeout(1000); }
  const lb = page.locator('input[type="text"]');
  const lbtn = page.getByRole("button", { name: /login/i });
  if (await lbtn.count()) { await lb.fill(USER); await lbtn.click(); }
  await page.waitForSelector('button[role="combobox"]', { timeout: 20000 });

  // track first -- selecting it re-renders the panel
  await page.locator('button[role="combobox"]').first().click();
  await page.waitForTimeout(500);
  const trackOpt = page.getByRole("option", { name: new RegExp(TRACK, "i") }).first();
  if (!(await trackOpt.count())) { await page.keyboard.press("Escape"); return false; }
  await trackOpt.click();
  await page.waitForTimeout(1000);

  // then probe for the architecture selector, whose index moves after the re-render
  const boxes = page.locator('button[role="combobox"]');
  for (let i = 0, n = await boxes.count(); i < n; i++) {
    await boxes.nth(i).click();
    await page.waitForTimeout(450);
    const opts = await page.getByRole("option").allInnerTexts();
    if (opts.some((o) => /minimal_saas|terminal_hacker/.test(o))) {
      const opt = page.getByRole("option", { name: new RegExp(arch.replace(/_/g, "[-_ ]"), "i") }).first();
      if (await opt.count()) {
        await opt.click();
        await page.waitForTimeout(700);
        const apply = page.getByRole("button", { name: /apply composition/i });
        if (await apply.count()) { await apply.click(); await page.waitForTimeout(2000); }
        return true;
      }
    }
    await page.keyboard.press("Escape");
    await page.waitForTimeout(250);
  }
  return false;
}

for (const [arch, stem] of Object.entries(ALIAS)) {
  if (ONLY && arch !== ONLY) continue;
  const want = declared(stem);
  if (!want) { rows.push({ arch, absent: true }); continue; }
  const ok = await selectArchetype(page, arch);
  if (!ok) { rows.push({ arch, want, missing: true }); continue; }
  rows.push({ arch, want, got: await page.evaluate(probe) });
}
await browser.close();

// --- compare ---
const norm = (v) =>
  String(v ?? "")
    .toLowerCase()
    .replace(/["']/g, "")
    // Chromium serializes computed numbers with a leading zero (0.86) while
    // the previews author them without one (.86). Same value, so compare
    // the canonical form.
    .replace(/(^|[\s(,])0\./g, "$1.")
    .trim();
const hexOf = (css) => {
  const m = norm(css).match(/#([0-9a-f]{6})/);
  if (m) return m[1];
  const n = norm(css).match(/(\d+)[,\s]+(\d+)[,\s]+(\d+)/);
  if (n) return [n[1], n[2], n[3]].map((v) => (+v).toString(16).padStart(2, "0")).join("");
  return null;
};

const lines = [`# Preview gap audit — ${TRACK}`, ""];
let totalGap = 0, totalChecked = 0;

for (const r of rows) {
  if (r.absent) { lines.push(`## ${r.arch}`, "", "No preview file found. Missing upstream.", ""); continue; }
  if (r.missing) { lines.push(`## ${r.arch}`, "", "Archetype not selectable in the catalog.", ""); continue; }
  const w = r.want, g = r.got;
  const checks = [];

  // background: the preview's html,body colour
  const wantBg = hexOf(w.body);
  const gotBg = hexOf(g.bodyBg);
  if (wantBg) { checks.push(["body background", wantBg, gotBg ?? g.bodyBg]); }

  // shell geometry
  if (w.shellCols) checks.push(["shell columns", w.shellCols.slice(0, 40), (g.cols || g.sideCols || "").slice(0, 40)]);

  // type: the display face used for the h1
  const wantH1 = w.fonts.find((f) => /Kaisei|serif|Bowlby/i.test(f))?.split(",")[0];
  if (wantH1) checks.push(["h1 face", wantH1, g.h1Font]);

  // the mono face the previews use for chrome
  const wantMono = w.fonts.find((f) => /Plex Mono|DM Mono|monospace/i.test(f))?.split(",")[0];
  if (wantMono) checks.push(["chrome face", wantMono, g.monoUsed]);

  // the photo plate
  if (w.photo) checks.push(["photo filter", (w.photo.match(/filter:([^;}]+)/)?.[1] ?? "declared").trim(), g.photoFilter || (g.photoPresent ? "photo present, no filter" : "NO PHOTO")]);

  // copy that must be visible verbatim
  for (const c of w.copy.slice(0, 3)) {
    const blob = `${g.h1Text} ${g.promptText} ${g.headText}`.toLowerCase();
    const key = c.split(/\s+/).slice(0, 3).join(" ").toLowerCase();
    checks.push([`copy "${key}"`, "present", blob.includes(key) ? "present" : "MISSING"]);
  }

  const gaps = checks.filter(([, a, b]) => {
    const x = norm(a), y = norm(b);
    return x !== y && !(x.includes(y) && y.length > 3);
  });
  totalGap += gaps.length;
  totalChecked += checks.length;

  lines.push(`## ${r.arch}`, "", `preview: \`${w.path}\``, "");
  lines.push("| property | preview declares | reflex renders | |", "|---|---|---|---|");
  for (const [k, a, b] of checks) {
    const bad = gaps.includes(checks.find((c) => c[0] === k));
    lines.push(`| ${k} | \`${a}\` | \`${b}\` | ${bad ? "**GAP**" : "ok"} |`);
  }
  lines.push("", `palette declared: ${JSON.stringify(w.palette)}`, "");
}

lines.unshift(`Checked ${totalChecked} properties across ${rows.length} archetypes. **${totalGap} gaps.**`, "");
writeFileSync(OUT, lines.join("\n"));
console.log(lines.join("\n"));
console.log(`\nfull report -> ${OUT}`);