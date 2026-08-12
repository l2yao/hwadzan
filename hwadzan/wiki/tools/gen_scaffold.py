#!/usr/bin/env python3
"""One-off scaffold generator: create category + topic pages from the raw doc/
structure.

Run from hwadzan/hwadzan/ so that the doc/ folder is found at CWD.
Only used to bootstrap the wiki; subsequent updates are human/LLM-curated.
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))  # hwadzan/hwadzan
DOC = os.path.join(ROOT, "doc")
WIKI = os.path.join(ROOT, "wiki")
TODAY = "2026-08-12"

# category display order + one-line description (description refined later)
CATEGORY_ORDER = [
    "認識佛教", "淨土五經一論", "法音宣流", "儒釋道文化", "儒釋道經典",
    "弘法活動", "影片欣賞", "佛事共修", "多國語言", "有聲書",
]
DESC = {
    "認識佛教": "佛陀教育的本質與功能",
    "淨土五經一論": "淨土宗根本經論",
    "法音宣流": "開示講話、學佛答問、淨土念佛等",
    "儒釋道文化": "儒家、道家及其他講演者",
    "儒釋道經典": "佛經、儒學、因果教育等",
    "弘法活動": "座談會、活動紀實、祭祀大典等",
    "影片欣賞": "動畫、華藏短片、電影",
    "佛事共修": "梵唄教學、法會、讀誦",
    "多國語言": "各語系翻譯開示",
    "有聲書": "有聲書（多為音檔，多無 doc 文字）",
}
# categories that exist only as metadata JSON, with no doc/ text folder
AUDIO_ONLY = {"有聲書"}


def topics_of(cat):
    p = os.path.join(DOC, cat)
    if not os.path.isdir(p):
        return []
    return sorted(d for d in os.listdir(p) if os.path.isdir(os.path.join(p, d)))


def count_series(cat, topic):
    p = os.path.join(DOC, cat, topic)
    if not os.path.isdir(p):
        return 0
    return sum(1 for d in os.listdir(p) if os.path.isdir(os.path.join(p, d)))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote", os.path.relpath(path, ROOT))


def category_page(cat):
    topics = topics_of(cat)
    series_count = sum(count_series(cat, t) for t in topics)
    lines = [
        "---",
        "type: category",
        f"tags: [{cat}]",
        f"sources: {series_count}",
        f"updated: {TODAY}",
        "---",
        "",
        f"# {cat}",
        "",
        f"此類別涵蓋：{DESC.get(cat, cat)}。",
        "",
        "## 主題",
        "",
    ]
    if cat in AUDIO_ONLY:
        lines.append("本類別主要為有聲書（音檔），多數系列沒有 doc 文字。")
        lines.append("")
    elif topics:
        for t in topics:
            n = count_series(cat, t)
            lines.append(f"- [[{cat}/{t}]] — {t}（{n} 個系列）")
        lines.append("")
    else:
        lines.append("（尚無主題。待資料更新。）")
        lines.append("")
    lines += [
        "## 開示一覽",
        "",
        "依 [[index|索引]] 與 [[raw-manifest|原始清單]] 查閱。",
        "",
    ]
    return "\n".join(lines) + "\n"


def topic_page(cat, topic):
    n = count_series(cat, topic)
    lines = [
        "---",
        "type: topic",
        f"category: {cat}",
        f"tags: [{topic}]",
        f"updated: {TODAY}",
        "---",
        "",
        f"# {topic}",
        "",
        "本主題涵蓋此類別下的相關開示。",
        "",
        f"## 開示（{n} 個系列）",
        "",
        "- 依 [[raw-manifest|原始清單]] 查閱。",
        "",
        "## 相關概念",
        "",
        "- 待 ingest 後補上。",
        "",
    ]
    return "\n".join(lines) + "\n"


def main():
    cats = CATEGORY_ORDER + sorted(
        d for d in os.listdir(DOC)
        if os.path.isdir(os.path.join(DOC, d)) and d not in CATEGORY_ORDER
    )
    for cat in cats:
        write(os.path.join(WIKI, f"{cat}.md"), category_page(cat))
        for t in topics_of(cat):
            write(os.path.join(WIKI, cat, f"{t}.md"), topic_page(cat, t))


if __name__ == "__main__":
    main()
