#!/usr/bin/env python3
"""Backfill ## 原始資料與影音 (reference links) into existing wiki source pages.

For each source page (code matching d{2}-d{3}.md) in wiki/:
  - ensures a `media:` frontmatter field from the category JSON flags
  - appends a `## 原始資料與影音` section listing every episode:
      text: md/doc/pdf GitHub blob links (UTF-8 percent-encoded)
      media: links per the series media flags (mp3/himp4/mp4)

Episode list = the set of .md files actually present in the page's raw folder
(on-disk ground truth, so every link points to a real file).

Idempotent: pages that already have `## 原始資料與影音` are skipped.

Run from the hwadzan/ directory (CWD-relative, matching the other wiki tools).
"""

import argparse
import glob
import json
import os
import re
import sys
import urllib.parse
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BLOB_BASE = "https://github.com/l2yao/hwadzan/blob/main/hwadzan/"
TREE_BASE = "https://github.com/l2yao/hwadzan/tree/main/hwadzan/"
CDN_BASE = "https://tw4.hwadzan.info/redirect/media/"

PAGE_RE = re.compile(r"^(?:\d{2}|WD\d{2})-\d{3}\.md$")


def build_code_map():
    """menuid -> dict(mp3, mp4, himp4, txt, menuidparent)."""
    code_map = {}
    for jf in glob.glob("**/*.json", recursive=True):
        try:
            with open(jf, encoding="utf-8") as f:
                d = json.load(f)
        except Exception:
            continue
        data = (d.get("sutables") or {}).get("data") or []
        for s in data:
            mid = s.get("menuid")
            if mid:
                code_map.setdefault(mid, {
                    "mp3": bool(s.get("mp3")),
                    "mp4": bool(s.get("mp4")),
                    "himp4": bool(s.get("himp4")),
                    "parent": s.get("menuidparent") or mid.split("-")[0],
                })
    return code_map


def media_types(info):
    """Ordered list of media types per SCHEMA (mp3, himp4, mp4)."""
    types = []
    if info and info["mp3"]:
        types.append("mp3")
    if info and info["himp4"]:
        types.append("himp4")
    if info and info["mp4"] and not (info and info["himp4"]):
        types.append("mp4")
    return types


def media_url(typ, parent, code, nnnn):
    sub = "mp3" if typ == "mp3" else "mp4"
    return f"{CDN_BASE}{sub}/{parent}/{code}/{code}-{nnnn}.mp3" if typ == "mp3" \
        else f"{CDN_BASE}himp4/{parent}/{code}/{code}-{nnnn}.mp4" if typ == "himp4" \
        else f"{CDN_BASE}mp4/{parent}/{code}/{code}-{nnnn}.mp4"


def enc(path):
    return urllib.parse.quote(path, safe="/")


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None, None
    fm = m.group(1)
    lines = fm.split("\n")
    fields = {}
    for ln in lines:
        if ":" in ln:
            k, _, v = ln.partition(":")
            fields[k.strip()] = v.strip()
    return lines, fields


def episode_numbers(raw_folder):
    """Sorted 4-digit episode numbers that have an .md file on disk."""
    if not os.path.isdir(raw_folder):
        return []
    nums = []
    for fn in os.listdir(raw_folder):
        if fn.endswith(".md"):
            stem = fn[:-3]
            if re.fullmatch(r"\d{4}", stem):
                nums.append(stem)
    return sorted(nums)


def build_section(raw, code, episode_nums, media_types_list, parent):
    folder_url = TREE_BASE + enc(raw.rstrip("/"))
    q_raw = enc(raw.rstrip("/"))
    lines = ["## 原始資料與影音", ""]
    lines.append(f"原始資料夾：[GitHub]({folder_url})（doc/pdf/md 全部集數）")
    lines.append("")
    lines.append("| 集數 | 文字 | 影音 |")
    lines.append("|---|--:|--:|")
    for nnnn in episode_nums:
        md_u = f"{BLOB_BASE}{q_raw}/{nnnn}.md"
        doc_u = f"{BLOB_BASE}{q_raw}/{nnnn}.doc"
        pdf_u = f"{BLOB_BASE}{q_raw}/{nnnn}.pdf"
        text_cell = f"[md]({md_u}) · [doc]({doc_u}) · [pdf]({pdf_u})"
        if media_types_list:
            media_cell = " · ".join(
                f"[{t}]({media_url(t, parent, code, nnnn)})" for t in media_types_list
            )
        else:
            media_cell = "—"
        lines.append(f"| {nnnn} | {text_cell} | {media_cell} |")
    return "\n".join(lines) + "\n"


def process_page(path, code_map):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()

    if "## 原始資料與影音" in text:
        return "skip-already"

    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return "skip-nofrontmatter"
    fm_block = m.group(1)
    body = text[m.end():]

    fm_lines, fields = parse_frontmatter(text)
    raw = fields.get("raw", "").strip()
    if not raw:
        return "skip-noraw"

    code = fields.get("code", "").strip()
    if not code:
        code = os.path.basename(path)[:-3]

    info = code_map.get(code)
    mtypes = media_types(info)

    # --- insert media: field after raw: (skip if already present) ---
    new_fm = []
    if "media" in fields:
        new_fm = fm_lines[:]
    else:
        for ln in fm_lines:
            new_fm.append(ln)
            if ln.strip().startswith("raw:"):
                new_fm.append(f"media: [{', '.join(mtypes)}]" if mtypes else "media: []")

    new_text = "---\n" + "\n".join(new_fm) + "\n---\n" + body

    # --- episode table from on-disk .md files ---
    raw_folder = raw
    if not os.path.isdir(raw_folder):
        raw_folder = os.path.join(os.getcwd(), raw)
    nums = episode_numbers(raw_folder)
    parent = info["parent"] if info else (code.split("-")[0])
    section = build_section(raw, code, nums, mtypes, parent)

    new_text = new_text.rstrip("\n") + "\n\n" + section

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)
    return f"updated codes={len(nums)} media=[{', '.join(mtypes)}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", default="wiki", help="wiki root dir")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default=None, help="only process page(s) matching substring of path")
    args = ap.parse_args()

    code_map = build_code_map()

    pages = []
    for root, _, files in os.walk(args.wiki):
        for fn in files:
            if PAGE_RE.match(fn):
                pages.append(os.path.join(root, fn))

    if args.only:
        pages = [p for p in pages if args.only in p.replace("\\", "/")]

    results = Counter()
    detail = []
    for p in sorted(pages):
        if args.dry_run:
            results["dry-run"] += 1
            continue
        r = process_page(p, code_map)
        results[r] += 1
        if r.startswith("updated") or (r not in ("skip-already", "skip-nofrontmatter", "skip-noraw")):
            detail.append((p, r))

    print("code map size:", len(code_map))
    print("pages:", len(pages))
    if args.dry_run:
        print("dry-run (no changes made):", results["dry-run"])
        return
    for k, v in results.most_common():
        print(f"{k}: {v}")
    if detail:
        print("--- details (first 200) ---")
        for p, r in detail[:200]:
            print(p, "=>", r)


if __name__ == "__main__":
    main()
