import pathlib
import re
import sys

TOOLS_DIR = pathlib.Path(__file__).resolve().parent
WIKI_DIR = TOOLS_DIR.parent
ROOT_DIR = WIKI_DIR.parent
RAW_DIR = ROOT_DIR / "doc"
OUT_FILE = WIKI_DIR / "raw-manifest.md"

CODE_RE = re.compile(r"^(?:\d{2}|WD\d{2})-\d{3}(?:_[A-Za-z]+)?$")
DATE_RE = re.compile(r"^\d{4}[/\d]*")
EP_RE = re.compile(r"^（(.+)）$")
FILE_RE = re.compile(r"^檔名[:：]\s*(.+)$")

TOP_CATEGORY_ORDER = [
    "認識佛教", "淨土五經一論", "法音宣流", "儒釋道文化", "儒釋道經典",
    "弘法活動", "影片欣賞", "佛事共修", "多國語言", "有聲書",
]


def read_first_line(path):
    for cand in sorted(path.glob("*.md")):
        raw = cand.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        for line in text.splitlines():
            if line.strip():
                return line.strip()
    return ""


def parse_meta(line):
    result = {
        "title": "", "episode": "", "date": "", "place": "", "file": "",
    }
    if not line:
        return result
    parts = [p for p in line.split("\u3000") if p]
    if not parts:
        result["title"] = line.strip()
        return result
    result["title"] = parts[0].strip()
    for p in parts[1:]:
        m = FILE_RE.match(p)
        if m:
            result["file"] = m.group(1).strip()
            continue
        m = EP_RE.match(p)
        if m:
            result["episode"] = m.group(1).strip()
            continue
        if DATE_RE.match(p) and not result["date"]:
            result["date"] = p.strip()
            continue
        if p != result["title"] and not result["place"]:
            result["place"] = p.strip()
            continue
        if not result["place"]:
            result["place"] = p.strip()
    return result


def collect():
    categories = {}
    if not RAW_DIR.is_dir():
        print(f"raw dir not found: {RAW_DIR}", file=sys.stderr)
        return categories
    for cat_dir in sorted(RAW_DIR.iterdir()):
        if not cat_dir.is_dir():
            continue
        for topic_dir in sorted(cat_dir.iterdir()):
            if not topic_dir.is_dir():
                continue
            for series_dir in sorted(topic_dir.iterdir()):
                if not series_dir.is_dir() or not CODE_RE.match(series_dir.name):
                    continue
                pages = sorted(series_dir.glob("*.md"))
                first = read_first_line(series_dir)
                meta = parse_meta(first)
                categories.setdefault(cat_dir.name, {}).setdefault(
                    topic_dir.name, []
                ).append({
                    "code": series_dir.name,
                    "pages": len(pages),
                    "title": meta["title"],
                    "episode": meta["episode"],
                    "date": meta["date"],
                    "place": meta["place"],
                    "file": meta["file"],
                    "rel": series_dir.relative_to(ROOT_DIR).as_posix(),
                })
    return categories


def fmt_rel(rel):
    return "`{}/`".format(rel)


def render(categories):
    out = []
    out.append("---")
    out.append("type: manifest")
    out.append("generated: 2026-08-04")
    out.append("---")
    out.append("")
    out.append("# 原始開示清單")
    out.append("")
    total_series = sum(len(s) for topics in categories.values() for s in topics.values())
    total_pages = sum(
        s["pages"] for topics in categories.values() for series in topics.values() for s in series
    )
    out.append(
        f"自動產生自 `hwadzan/doc/`。共 **{total_series}** 個系列、**{total_pages}** 頁。"
    )
    out.append("")
    out.append("> 由 `wiki/tools/gen_manifest.py` 產生，請勿手動編輯。")
    out.append("")
    cat_names = [c for c in TOP_CATEGORY_ORDER if c in categories]
    cat_names += sorted(c for c in categories if c not in TOP_CATEGORY_ORDER)
    for cat in cat_names:
        out.append(f"## {cat}")
        out.append("")
        topics = categories[cat]
        for topic in sorted(topics):
            series = sorted(topics[topic], key=lambda s: s["code"])
            out.append(f"### {topic}")
            out.append("")
            out.append("| 檔名 | 頁數 | 題目 | 集數 | 日期 | 地點 | 原始路徑 |")
            out.append("|---|---|---|---|---|---|---|")
            for s in series:
                out.append(
                    "| [[{code}]] | {pages} | {title} | {episode} | {date} | {place} | {rel} |".format(
                        code=s["code"],
                        pages=s["pages"],
                        title=s["title"] or "—",
                        episode=s["episode"] or "—",
                        date=s["date"] or "—",
                        place=s["place"] or "—",
                        rel=fmt_rel(s["rel"]),
                    )
                )
            out.append("")
    return "\n".join(out)


def main():
    categories = collect()
    content = render(categories)
    OUT_FILE.write_text(content, encoding="utf-8")
    print(f"wrote {OUT_FILE} ({len(content)} bytes)")


if __name__ == "__main__":
    main()
