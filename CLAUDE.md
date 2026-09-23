# book-of-tea-reader — 「茶の本」バイリンガル読書サイト

## プロジェクト概要

- **目的**: 公開 (GitHub Pages)
- **スタック**: 静的HTML/CSS + 軽量Node ビルドスクリプト (Reactなし)
- **ローカルパス**: `~/Documents/book-of-tea-reader/`

岡倉覚三(村岡博訳)「茶の本」を、日本語→英語の対訳チャンクで読めるサイト。
Phase 1: 7章分の読書サイト(インデックス+各章ページ)。
Phase 2: ブラウザ内蔵の Web Speech API による読み上げ(現在読んでいる箇所をハイライト)。

## ai-ops 連携

このプロジェクトは **ai-ops** (`~/Documents/ai-ops/`) の個人プロジェクトです。
Claude が積極的に介入してよい(コード変更・機能追加・バグ修正)。

参照コンテキスト:
- `~/Documents/ai-ops/obsidian-vault/04_Context/Philosophy & Values.md`
- `~/Documents/ai-ops/obsidian-vault/04_Context/Visual Design Principles.md` (§3.1 AIっぽさ回避 / §3.5 和文脈と西洋デザインの橋渡し / §4 NGリスト / §6 メタ原則を公開前チェックに使う)
- 承認済み実装プラン: `~/.claude/plans/pase1-audio-chapter-https-www-1101-com-cosmic-breeze.md`

## 方針

- シンプルに保つ。Reactやビルドパイプラインの過剰な追加は避ける(プレーンCSS + 最小限のNodeビルドスクリプトのみ)
- コンテンツ(対訳データ)は `data/chunks/*.json` に固定コミットする。Downloads配下の元データは実行時に参照しない
- 公開前(GitHub Pages公開)は河野の最終判断を仰ぐ(ai-ops CLAUDE.md §3: 公開コンテンツの最終Publishは人間判断)
- 困ったら ai-ops の AI Handoff に記録して翌セッションに引き継ぐ
