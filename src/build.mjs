#!/usr/bin/env node
// Reads data/chunks/*.json + chapters.json manifest, emits a static dist/ site.
// No framework, no bundler — plain string templates.

import { readFileSync, writeFileSync, mkdirSync, cpSync, readdirSync, rmSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const DATA_DIR = path.join(ROOT, "data", "chunks");
const DIST = path.join(ROOT, "dist");
const STYLES_DIR = path.join(ROOT, "src", "styles");
const PUBLIC_DIR = path.join(ROOT, "public");
const JS_DIR = path.join(ROOT, "src", "js");

function readJSON(p) {
  return JSON.parse(readFileSync(p, "utf-8"));
}

function esc(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

const chapters = readJSON(path.join(DATA_DIR, "chapters.json"));

// --- reset dist ---
rmSync(DIST, { recursive: true, force: true });
mkdirSync(DIST, { recursive: true });
mkdirSync(path.join(DIST, "chapters"), { recursive: true });
mkdirSync(path.join(DIST, "styles"), { recursive: true });
mkdirSync(path.join(DIST, "js"), { recursive: true });

// --- copy static assets ---
for (const f of readdirSync(STYLES_DIR)) {
  cpSync(path.join(STYLES_DIR, f), path.join(DIST, "styles", f));
}
for (const f of readdirSync(JS_DIR)) {
  cpSync(path.join(JS_DIR, f), path.join(DIST, "js", f));
}
cpSync(path.join(PUBLIC_DIR, "images"), path.join(DIST, "images"), { recursive: true });
if (readdirSync(PUBLIC_DIR).includes("favicon.svg")) {
  cpSync(path.join(PUBLIC_DIR, "favicon.svg"), path.join(DIST, "favicon.svg"));
}

function pageShell({ title, description, bodyClass, headExtra, body }) {
  return `<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="icon" href="/favicon.svg">
<link rel="stylesheet" href="/styles/tokens.css">
<link rel="stylesheet" href="/styles/base.css">
<link rel="stylesheet" href="/styles/reader.css">
${headExtra ?? ""}
</head>
<body class="${bodyClass ?? ""}">
${body}
</body>
</html>
`;
}

const rawIconCache = new Map();
function iconImg(icon, cls) {
  // Inlined (not <img src>) so the SVG's currentColor fill picks up the
  // wrapping element's CSS color — an <img>-referenced SVG is opaque to page CSS.
  if (!rawIconCache.has(icon)) {
    rawIconCache.set(icon, readFileSync(path.join(PUBLIC_DIR, "images", "icons", icon), "utf-8"));
  }
  return rawIconCache.get(icon).replace("<svg ", `<svg class="${cls}" aria-hidden="true" `);
}

// --- index page ---
function buildIndex() {
  const rows = chapters
    .map((c) => {
      return `
      <a class="chapter-row" href="/chapters/${c.slug}.html">
        <span class="num">${String(c.num).padStart(2, "0")}</span>
        ${iconImg(c.icon, "icon")}
        <span class="titles">
          <span class="en-title">${esc(c.en_title)}</span>
          <span class="jp-title">${esc(c.jp_title)}</span>
        </span>
        <span class="meta">${c.reading_minutes} min</span>
      </a>`;
    })
    .join("\n");

  const body = `
<div class="hero grain">
  <div class="hero-inner">
    ${iconImg("01-bowl.svg", "hero-icon")}
    <h1>The Book of Tea</h1>
    <p class="jp-title">茶の本</p>
    <p class="byline">岡倉覚三 (Kakuzo Okakura) — 村岡博訳 / English original, 1906</p>
  </div>
</div>
<div class="wrap">
  <ul class="chapter-list">
    ${rows}
  </ul>
  <footer class="site-footer">
    <p>英語原文: Global Grey 版 (1906年刊、パブリックドメイン)。日本語訳: 村岡博 (青空文庫、パブリックドメイン)。
    日本語→英語の対訳チャンクで交互に読めるよう構成しています。</p>
  </footer>
</div>`;

  writeFileSync(
    path.join(DIST, "index.html"),
    pageShell({
      title: "The Book of Tea 茶の本 — バイリンガル読書",
      description: "岡倉覚三「茶の本」を日本語→英語の対訳で読む",
      body,
    })
  );
}

// --- chapter page ---
function groupParagraphs(chunks) {
  const paras = [];
  let current = null;
  chunks.forEach((c, i) => {
    if (i === 0) return; // title handled separately
    if (c.para_break || !current) {
      current = [];
      paras.push(current);
    }
    current.push({ ...c, index: i });
  });
  return paras;
}

function chunkHtml(c) {
  return `<p class="chunk" data-chunk-index="${c.index}">
    <span class="jp" data-lang="jp">${esc(c.jp)}</span>
    <span class="en" data-lang="en">${esc(c.en)}</span>
  </p>`;
}

function buildChapter(c, prev, next) {
  const chunks = readJSON(path.join(DATA_DIR, `${c.slug}.chunks.json`));
  const paras = groupParagraphs(chunks);
  const bodyHtml = paras
    .map((p) => `<div class="para">\n${p.map(chunkHtml).join("\n")}\n</div>`)
    .join("\n");

  const prevLink = prev
    ? `<a href="/chapters/${prev.slug}.html"><span class="label">前の章</span>${esc(prev.en_title)}</a>`
    : `<a href="/index.html"><span class="label">戻る</span>目次</a>`;
  const nextLink = next
    ? `<a class="next" href="/chapters/${next.slug}.html"><span class="label">次の章</span>${esc(next.en_title)}</a>`
    : `<a class="next" href="/index.html"><span class="label">読了</span>目次に戻る</a>`;

  const body = `
<nav class="topnav"><a href="/index.html">← The Book of Tea 目次</a></nav>
<div class="wrap">
  <div class="chapter-head">
    <div class="num">CHAPTER ${String(c.num).padStart(2, "0")}</div>
    <h1>${esc(c.en_title)}</h1>
    <p class="jp-title">${esc(c.jp_title)}</p>
  </div>

  <div class="read-aloud-bar" id="read-aloud-bar" data-slug="${c.slug}">
    <button type="button" id="ra-play">▶ 読み上げ</button>
    <button type="button" id="ra-pause" hidden>❚❚ 一時停止</button>
    <label>速度
      <input type="range" id="ra-rate" min="0.8" max="1.3" step="0.1" value="1">
    </label>
  </div>

  ${bodyHtml}

  <div class="chapter-nav">
    ${prevLink}
    ${nextLink}
  </div>
</div>
<script>window.__CHAPTER_CHUNKS__ = ${JSON.stringify(chunks)};</script>
<script src="/js/read-aloud.js" defer></script>`;

  writeFileSync(
    path.join(DIST, "chapters", `${c.slug}.html`),
    pageShell({
      title: `${c.en_title} — The Book of Tea`,
      description: `${c.jp_title} / ${c.en_title}`,
      body,
    })
  );
}

buildIndex();
chapters.forEach((c, i) => {
  buildChapter(c, chapters[i - 1] ?? null, chapters[i + 1] ?? null);
});

console.log(`Built ${chapters.length} chapter pages + index into ${DIST}`);
