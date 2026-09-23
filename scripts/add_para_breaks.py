import json, re, glob, os

CH_DIR = "/tmp/booktea_chapters"
OUT_DIR = "/Users/iorikawano/Documents/book-of-tea-reader/data/chunks"

def paragraphs(text):
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return paras

def normalize(s):
    return re.sub(r'\s+', '', s)

for chunks_path in sorted(glob.glob(os.path.join(OUT_DIR, "*.chunks.json"))):
    base = os.path.basename(chunks_path).replace(".chunks.json", "")
    en_txt = open(os.path.join(CH_DIR, base + ".en.txt"), encoding="utf-8").read()
    en_paras = paragraphs(en_txt)
    chunks = json.load(open(chunks_path, encoding="utf-8"))

    para_idx = 0
    para_norm = normalize(en_paras[para_idx]) if en_paras else ""
    consumed = ""
    n_para_breaks = 0
    for i, ch in enumerate(chunks):
        if i == 0:
            ch["para_break"] = True
            n_para_breaks += 1
            continue
        en = ch.get("en", "")
        en_n = normalize(en)
        if not en_n:
            ch["para_break"] = False
            continue
        remainder = para_norm[len(consumed):]
        probe = en_n[:15] if len(en_n) >= 15 else en_n
        idx = remainder.find(probe)
        if idx != -1 and idx < 40:
            consumed += remainder[:idx] + en_n
            ch["para_break"] = False
        else:
            advanced = False
            for look_ahead in range(1, 4):
                npi = para_idx + look_ahead
                if npi >= len(en_paras):
                    break
                cand = normalize(en_paras[npi])
                cidx = cand.find(probe)
                if cidx != -1 and cidx < 40:
                    para_idx = npi
                    para_norm = cand
                    consumed = cand[:cidx] + en_n
                    ch["para_break"] = True
                    n_para_breaks += 1
                    advanced = True
                    break
            if not advanced:
                ch["para_break"] = False
                consumed += en_n

    json.dump(chunks, open(chunks_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(base, "chunks:", len(chunks), "para_breaks:", n_para_breaks, "source_paras:", len(en_paras))
