#!/usr/bin/env python3
"""Synthesize podcast-ready bilingual (JP->EN) chapter audio via Google Cloud
Text-to-Speech (REST API + API key). Output is licensed for public
redistribution per Google Cloud's terms (unlike macOS system voices).

Usage:
  export GOOGLE_TTS_API_KEY=...   # or pass --key
  python3 scripts/tts_google.py --chapter 01_cup_of_humanity
  python3 scripts/tts_google.py --all

Requires: ffmpeg (already used by the earlier macOS-say pipeline).
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS_DIR = os.path.join(REPO, "data", "chunks")
OUT_DIR = os.path.join(REPO, "audio_podcast")

JP_VOICE = {"languageCode": "ja-JP", "name": "ja-JP-Neural2-B"}  # female
EN_VOICE = {"languageCode": "en-US", "name": "en-US-Neural2-F"}  # female
GAP_WITHIN = 0.35
GAP_BETWEEN = 0.9
API_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"


def synth(text, voice, api_key, retries=3):
    payload = json.dumps({
        "input": {"text": text},
        "voice": voice,
        "audioConfig": {"audioEncoding": "MP3"},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{API_URL}?key={api_key}",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                return base64.b64decode(data["audioContent"])
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code in (429, 500, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"TTS request failed ({e.code}): {body}") from e
    raise RuntimeError("unreachable")


def make_silence(duration, out_path):
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
         "-i", "anullsrc=r=44100:cl=mono", "-t", str(duration), out_path],
        check=True,
    )


def build_chapter(slug, api_key):
    chunks_path = os.path.join(CHUNKS_DIR, f"{slug}.chunks.json")
    chunks = json.load(open(chunks_path, encoding="utf-8"))
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{slug}.mp3")

    with tempfile.TemporaryDirectory() as tmp:
        gap_within = os.path.join(tmp, "gap_within.aiff")
        gap_between = os.path.join(tmp, "gap_between.aiff")
        make_silence(GAP_WITHIN, gap_within)
        make_silence(GAP_BETWEEN, gap_between)

        segments = []
        for i, pair in enumerate(chunks):
            jp_text, en_text = pair.get("jp", "").strip(), pair.get("en", "").strip()
            if jp_text:
                jp_mp3 = os.path.join(tmp, f"{i:04d}_jp.mp3")
                open(jp_mp3, "wb").write(synth(jp_text, JP_VOICE, api_key))
                segments += [jp_mp3, gap_within]
            if en_text:
                en_mp3 = os.path.join(tmp, f"{i:04d}_en.mp3")
                open(en_mp3, "wb").write(synth(en_text, EN_VOICE, api_key))
                segments += [en_mp3, gap_between]
            print(f"  [{slug}] {i + 1}/{len(chunks)} synthesized", flush=True)

        concat_list = os.path.join(tmp, "concat.txt")
        with open(concat_list, "w") as f:
            for p in segments:
                f.write(f"file '{p}'\n")
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", concat_list, "-c:a", "libmp3lame", "-b:a", "128k", out_path],
            check=True,
        )
    print(f"Wrote {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", help="single chapter slug, e.g. 01_cup_of_humanity")
    ap.add_argument("--all", action="store_true", help="build all 7 chapters")
    ap.add_argument("--key", help="Google TTS API key (else reads GOOGLE_TTS_API_KEY env var)")
    args = ap.parse_args()

    api_key = args.key or os.environ.get("GOOGLE_TTS_API_KEY")
    if not api_key:
        sys.exit("No API key. Set GOOGLE_TTS_API_KEY or pass --key.")

    if args.all:
        slugs = sorted(
            f[: -len(".chunks.json")]
            for f in os.listdir(CHUNKS_DIR)
            if f.endswith(".chunks.json") and f != "chapters.json"
        )
    elif args.chapter:
        slugs = [args.chapter]
    else:
        sys.exit("Pass --chapter <slug> or --all")

    for slug in slugs:
        build_chapter(slug, api_key)


if __name__ == "__main__":
    main()
