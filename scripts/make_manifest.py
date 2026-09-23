import json, glob, os

OUT_DIR = "/Users/iorikawano/Documents/book-of-tea-reader/data/chunks"
files = sorted(glob.glob(os.path.join(OUT_DIR, "*.chunks.json")))

icons = {
    "01_cup_of_humanity": "01-bowl.svg",
    "02_schools_of_tea": "02-leaves.svg",
    "03_taoism_and_zennism": "03-enso.svg",
    "04_the_tea_room": "04-lattice.svg",
    "05_art_appreciation": "05-scroll.svg",
    "06_flowers": "06-flower.svg",
    "07_tea_masters": "07-whisk.svg",
}

chapters = []
for i, f in enumerate(files, start=1):
    base = os.path.basename(f).replace(".chunks.json", "")
    chunks = json.load(open(f, encoding="utf-8"))
    title = chunks[0]
    word_count = sum(len(c.get("en", "").split()) for c in chunks)
    reading_minutes = max(1, round(word_count / 200))
    chapters.append({
        "num": i,
        "slug": base,
        "jp_title": title["jp"],
        "en_title": title["en"],
        "icon": icons[base],
        "chunk_count": len(chunks),
        "reading_minutes": reading_minutes,
    })

manifest_path = os.path.join(OUT_DIR, "chapters.json")
json.dump(chapters, open(manifest_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for c in chapters:
    print(c["num"], c["slug"], c["jp_title"], "|", c["en_title"], "~", c["reading_minutes"], "min")
