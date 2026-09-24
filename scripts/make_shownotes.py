#!/usr/bin/env python3
"""Build per-episode show notes markdown from chapters.json + the verbatim
村岡博訳 table-of-contents synopsis lines (sourced from the Aozora Bunko text,
not fabricated). English descriptions are original summaries written for this
podcast (the Global Grey/Gutenberg English edition has no per-chapter synopsis
to draw from), clearly not presented as Okakura's own words.
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS = json.load(open(os.path.join(REPO, "data", "chunks", "chapters.json"), encoding="utf-8"))
OUT_DIR = os.path.join(REPO, "shownotes")

# Verbatim from the Aozora Bunko 村岡博訳 table of contents (目次), split on the "――" dashes.
JP_SYNOPSIS = {
    "01_cup_of_humanity": [
        "茶は日常生活の俗事の中に美を崇拝する一種の審美的宗教すなわち茶道の域に達す",
        "茶道は社会の上下を通じて広まる",
        "新旧両世界の誤解",
        "西洋における茶の崇拝",
        "欧州の古い文献に現われた茶の記録",
        "物と心の争いについての道教徒の話",
        "現今における富貴権勢を得ようとする争い",
    ],
    "02_schools_of_tea": [
        "茶の進化の三時期――唐、宋、明の時代を表わす煎茶、抹茶、淹茶",
        "茶道の鼻祖陸羽",
        "三代の茶に関する理想",
        "後世のシナ人には、茶は美味な飲料ではあるが理想ではない",
        "日本においては茶は生の術に関する宗教である",
    ],
    "03_taoism_and_zennism": [
        "道教と禅道との関係",
        "道教とその後継者禅道は南方シナ精神の個人的傾向を表わす",
        "道教は浮世をかかるものとあきらめて、この憂き世の中にも美を見いだそうと努める",
        "禅道は道教の教えを強調している",
        "精進静慮することによって自性了解の極致に達せられる",
        "禅道は道教と同じく相対を崇拝する",
        "人生の些事の中にも偉大を考える禅の考え方が茶道の理想となる",
        "道教は審美的理想の基礎を与え禅道はこれを実際的なものとした",
    ],
    "04_the_tea_room": [
        "茶室は茅屋に過ぎない",
        "茶室の簡素純潔",
        "茶室の構造における象徴主義",
        "茶室の装飾法",
        "外界のわずらわしさを遠ざかった聖堂",
    ],
    "05_art_appreciation": [
        "美術鑑賞に必要な同情ある心の交通",
        "名人とわれわれの間の内密の黙契",
        "暗示の価値",
        "美術の価値はただそれがわれわれに語る程度による",
        "現今の美術に対する表面的の熱狂は真の感じに根拠をおいていない",
        "美術と考古学の混同",
        "われわれは人生の美しいものを破壊することによって美術を破壊している",
    ],
    "06_flowers": [
        "花はわれらの不断の友",
        "「花の宗匠」",
        "西洋の社会における花の浪費",
        "東洋の花卉栽培",
        "茶の宗匠と生花の法則",
        "生花の方法",
        "花のために花を崇拝すること",
        "生花の宗匠",
        "生花の流派、形式派と写実派",
    ],
    "07_tea_masters": [
        "芸術を真に鑑賞することはただ芸術から生きた力を生み出す人にのみ可能である",
        "茶の宗匠の芸術に対する貢献",
        "処世上に及ぼした影響",
        "利休の最後の茶の湯",
    ],
}

# Original English summaries written for this podcast (not a translation
# presented as Okakura's own text — the English edition has no such synopsis).
EN_SUMMARY = {
    "01_cup_of_humanity": "What Teaism actually is: a quiet aesthetic religion of the "
        "imperfect, and how the West has usually misunderstood it.",
    "02_schools_of_tea": "Tea's three historical stages in China — boiled, whipped, "
        "steeped — and how each shaped a different idea of what tea is for.",
    "03_taoism_and_zennism": "How Taoism and Zen shaped Teaism's core idea: greatness "
        "hiding in small, ordinary acts.",
    "04_the_tea_room": "Inside the tea-room: deliberate simplicity, and a space built "
        "to shut the noisy world out.",
    "05_art_appreciation": "On really seeing art — the quiet, sympathetic exchange "
        "between a work and the person looking at it.",
    "06_flowers": "Flowers as tea's oldest friend, and the line between arranging them "
        "and merely using them up.",
    "07_tea_masters": "What tea masters actually gave to art and everyday life — and "
        "the death of Rikyu.",
}


def main():
    for c in CHAPTERS:
        slug = c["slug"]
        jp_bullets = "\n".join(f"- {s}" for s in JP_SYNOPSIS[slug])
        body = f"""# 第{c['num']}章　{c['jp_title'].split('　', 1)[-1]} / {c['en_title']}

**{c['jp_title']} / {c['en_title']}** (The Book of Tea, 岡倉覚三・村岡博訳)

{EN_SUMMARY[slug]}

## この章の内容 (原文目次より)

{jp_bullets}

## 出典・ライセンス

英語原文: Kakuzo Okakura, *The Book of Tea* (1906, public domain)。日本語訳: 村岡博訳
(青空文庫、public domain)。音声: Google Cloud Text-to-Speech(公開・再配布が利用規約で許可
されたサービス)。制作: 河野いおり。

読書サイト(対訳・読み上げ付き): https://iori73.github.io/book-of-tea-reader/chapters/{slug}.html
"""
        out_path = os.path.join(OUT_DIR, f"{slug}.md")
        open(out_path, "w", encoding="utf-8").write(body)
        print("wrote", out_path)


if __name__ == "__main__":
    main()
