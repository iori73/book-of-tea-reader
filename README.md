# book-of-tea-reader

岡倉覚三(Kakuzo Okakura)「茶の本」(The Book of Tea, 1906) を、日本語→英語の対訳チャンクで
交互に読めるバイリンガル読書サイト。静的HTML/CSS + 軽量Nodeビルドスクリプト(フレームワークなし)。

## 出典・著作権

- **英語原文**: Global Grey 版 (1906年刊、Kakuzo Okakura 著、1913年没につきパブリックドメイン)
- **日本語訳**: 村岡博訳「茶の本」(青空文庫でパブリックドメイン公開済み)
- 両方とも著作権が切れているため、対訳データの再配布・公開に問題はない

## 構成

```
data/chunks/*.chunks.json   対訳チャンクデータ (章ごと、{jp, en, para_break} の配列)
data/chunks/chapters.json   章マニフェスト (自動生成、チャンクの先頭要素=タイトルから作る)
src/build.mjs               ビルドスクリプト。data/ → dist/ の静的HTMLを生成
src/styles/                 デザイントークン・基本スタイル・読書ページ固有スタイル
src/js/read-aloud.js        Phase 2: ブラウザ内蔵 Web Speech API による読み上げ
public/images/icons/        章アイコン (フラットSVG、8点)
scripts/                    データ準備用の一回きりのPythonスクリプト (再実行は基本不要)
```

## ビルド・ローカル確認

```bash
npm run build   # dist/ に生成
npm run serve   # ビルド + ローカルサーバ起動 (http://localhost:8080)
```

## データについて

`data/chunks/*.chunks.json` は、英語原文PDFと日本語訳HTMLから対訳チャンク(1節〜短文、
JP先行→EN追従の順)を作成したもの。`para_break: true` が付いたチャンクは、原文の段落境界
(空行区切り)から機械的に判定した「新しい段落の先頭」を示す。`scripts/add_para_breaks.py` が
その判定ロジック。`scripts/make_manifest.py` は `chapters.json` を各章の先頭チャンク(章タイトル)
から自動生成する。どちらも一度実行済みで、data/chunks の元データを差し替えない限り再実行は不要。

## Phase 2: 読み上げの既知の制約

事前生成した音声ファイル(macOS `say` による .m4a、別途 `~/Downloads/茶の本 the book of tea/audio/`
に保存済み)はサイズが大きいため埋め込んでいない。代わりにブラウザ内蔵の `window.speechSynthesis`
(無料・追加コストなし)を使ってその場で読み上げる。そのため:

- 読み上げ音声の質・日本語/英語ボイスの有無は訪問者のOS/ブラウザに依存する
- オフラインの `.m4a` 版のような一貫した音声にはならない

この制約は結果的に安全側にも効いている。下記「音声ファイルの公開範囲について」を参照。

## 音声ファイルの公開範囲について (2026-09-24 追記)

`~/Downloads/茶の本 the book of tea/audio/` の .m4a(macOS `say` の Kyoko/Samantha による録音)は、
**河野個人のオフライン再生用に限る。Spotify・Apple Podcasts等への公開はしない。**

- Kyoko/Samantha は Apple の macOS システム音声。「無料で使える」は端末内利用の話であり、
  録音物の公開・再配布(営利・非営利問わず)は macOS の使用許諾(SLA)で禁止されている
- 一方、本サイトの Phase 2(`window.speechSynthesis` によるその場読み上げ)は、
  訪問者自身の端末がその場で音声合成しているだけで録音物を再配布していないため、
  同じ制約には当たらない、と判断している
- 本文(英語原文 Global Grey/Project Gutenberg 版・日本語訳 青空文庫 村岡博訳)は
  どちらも著作権保護期間満了でパブリックドメイン。制約があるのは音声側だけ
- もし将来 Spotify/Apple Podcasts で音声版を出す場合は、Kyoko/Samantha ではなく
  (a) 自分の声で朗読する、または (b) 公開・再配布を利用規約上明示的に許可している
  TTSサービス(有償が多い、§5.5コスト規律により導入前に河野確認)のどちらかに録り直す必要がある
- 同様の対訳バイリンガル音声化を検討する他の書籍(例: 「学問のすすめ」)にもこの制約はそのまま適用される

## 公開について

GitHub Pages で公開予定(著作権が切れているため公開自体に問題はない)。実際にリポジトリを
public化してGitHub Pagesを有効化する操作は、河野の最終判断を待ってから行う
(ai-ops CLAUDE.md §3: 公開コンテンツの最終Publishは人間判断)。

## モバイル表示の確認について (引き継ぎメモ)

ローカルのheadless Chrome CLIスクリーンショット(`--window-size=390,...`)で確認したところ、
390px幅の画面で本文が折り返さずに右へはみ出す現象が見えた。最小限のテストHTML(このCSSに
依存しない3行だけのファイル)でも同じ現象が再現したため、これは本サイトのCSSの不具合ではなく
「ヘッドレスChromeのCLIスクリーンショットがviewport meta タグを正しく解釈しない」というツール側の
既知の制約と判断した(モバイルUser-Agentを付けても同じ結果)。ページには
`<meta name="viewport" content="width=device-width, initial-scale=1">` が入っており、
実機のブラウザ(iPhone Safari / Android Chrome等)やブラウザのレスポンシブモードでは正しく
折り返されるはず。**実機かブラウザのdevtoolsレスポンシブモードで一度目視確認することを推奨**。
