# AGENTS.md — LLM Wiki Schema

This repository is configured as an **LLM-maintained wiki** following the Karpathy "LLM Wiki" pattern. This file is the schema: it tells the LLM how the wiki is structured, what conventions to follow, and what workflows to run. Read this file first at the start of every session before touching the wiki.

## Purpose

Build a persistent, interlinked, compounding knowledge base of Traditional Chinese Buddhist teachings (華藏淨宗學會 / hwadzan corpus). The wiki sits between the reader and the raw source corpus. The LLM writes and maintains the wiki; the human curates sources and asks questions.

## Repository layout

```
hwadzan/
  AGENTS.md           <- this file (schema)
  hwadzan/
    doc/              <- RAW SOURCES (updated only via wiki/tools, never hand-edited)
    wiki/             <- THE WIKI (LLM-owned markdown)
      SCHEMA.md       <- page templates & examples
      README.md       <- home/overview
      index.md        <- content catalog
      log.md          <- chronological activity log
      raw-manifest.md <- generated catalog of all raw series
      tools/
        fetch.py      <- pull hwadzan catalog (menu.json + category JSONs) from amtb.tw
        download.py   <- download .doc/.pdf into doc/ (incremental)
        doc_to_md.py  <- convert .doc -> .md via markitdown
        gen_manifest.py <- regenerate raw-manifest.md
        backfill_reflinks.py <- backfill reference-link tables into source pages
        gen_scaffold.py    <- one-off: bootstrap category/topic pages
        requirements.txt
      認識佛教/ 淨土五經一論/ ...   <- category folders
```

## The three layers

1. **Raw sources** — `hwadzan/doc/`. Curated, git-tracked. The LLM reads from here and **writes only via the source-update tools** (`wiki/tools/fetch.py`, `download.py`, `doc_to_md.py`, and the read-only `gen_manifest.py`). Never hand-edit anything under `doc/`.
2. **The wiki** — `hwadzan/wiki/`. LLM-owned markdown. Create/update pages on ingest, query, and lint.
3. **The schema** — this file + `wiki/SCHEMA.md`. Co-evolve with the human.

## Raw source format

- Categories (from the hwadzan catalog): 認識佛教, 淨土五經一論, 法音宣流, 儒釋道文化, 儒釋道經典, 弘法活動, 影片欣賞, 佛事共修, 多國語言, 有聲書. (有聲書 has metadata but mostly audio, may have no `doc/` text.)
- Each category → topic folders → **series folders** named by code (e.g. `63-001`, `WD21-121`) → numbered `.md` pages (`0001.md`, `0002.md`, ...).
- A series = one teaching title (possibly many sessions/集). There are **816 series folders, ~9,000 pages**.
- Every page's **first line** is metadata:
  `題目　　（共N集 | 第一集）　　日期　　地點　　檔名：CODE-PAGE`
  Example: `二ＯＯ五年古晉報恩念佛堂中元普度—法器儀規教學　　悟道法師主講　　（共一集）　　2005/8/16　　古晉報恩念佛堂　　檔名：63-001-0001`
- `.doc`/`.pdf`/`.docx` duplicates exist alongside `.md` — ignore them; read only `.md`.
- See `wiki/raw-manifest.md` for the full navigable catalog (regenerate with `python wiki/tools/gen_manifest.py` when needed).

## Wiki structure

One folder per category. Inside each category folder: a category page, topic pages, and source pages. Concept pages live in `wiki/概念/`.

```
wiki/
  佛事共修.md               <- category page
  佛事共修/
    梵唄教學.md            <- topic page
    63-001.md              <- source page (one per series)
  ...
  概念/
    三皈依.md
    念佛.md
    ...
```

**Language**: all wiki page content is Traditional Chinese. Frontmatter tags/values may be Chinese or English. Never auto-translate sources; quote sparingly.

## Page types

### Category page (`認識佛教.md`)
- YAML frontmatter: `type: category`, `tags`, `updated`, `sources` (count).
- Lists the topic pages with one-line descriptions, plus a short synthesis of what the category covers.

### Topic page (`認識佛陀教育.md`)
- `type: topic`, `category`.
- One per sutra/subject within a category. Lists its series with links, notes thematic structure.

### Source page (`63-001.md`)
- `type: source`, `category`, `topic`, `code`, `title`, `date`, `place`, `pages`, `raw`, `media`.
- Sections: 概要 (summary), 重點 (key teachings), 相關概念 (wikilinks to concepts), 相關頁面 (links to related series/topics), 原始資料與影音 (GitHub links to raw folder + a per-episode table of text/media links).
- One page per series; cite the raw path so the reader can drill in.

### Concept page (`概念/念佛.md`)
- `type: concept`.
- Cross-cutting Buddhist concepts that appear across many sources. Evolving entity page: definition, how different sources present it, key quotes with citation to series code, related concepts.
- Create a concept page when a term is central and recurs; do not create pages for one-off mentions.

### Answer pages (filed queries)
- `type: answer`. Created when a good Q&A result deserves persistence (comparisons, syntheses). Lives under `wiki/問答/`.

## Conventions

- **Naming**: files use the natural Chinese name for concepts/topics; source pages use the numeric code (e.g. `63-001.md`, `WD21-121.md`). No spaces in filenames; if needed use `_`.
- **Links**: Obsidian-style wikilinks `[[認識佛陀教育]]`, `[[概念/念佛]]`. For source pages, link the code text: `[[63-001]]`.
- **Frontmatter**: always YAML `---` block. Keys: `type`, `category`, `topic`, `code`, `title`, `date`, `place`, `pages`, `raw`, `media`, `tags`, `updated`. Use `date: YYYY/MM/DD` or `YYYY/M` as available.
- **Citations**: when a claim comes from a specific series, cite it as `〔63-001〕` or link `[[63-001]]`. When a concept page synthesizes multiple sources, list source codes.
- **Reference links**: every source page carries a `## 原始資料與影音` section with a per-episode table of text (`md`/`doc`/`pdf`) and media links — every episode, no omission. Media types come from the category JSON flags (`mp3`/`himp4`/`mp4`), never guessed. See SCHEMA.md for exact URL formats.
- **Tool-managed raw**: never hand-edit anything under `hwadzan/doc/`; change it only through the source-update tools (see Source update workflow).

## Workflows

### Source update (refresh raw corpus)
Run when the human asks to sync new/updated teachings from amtb.tw / hwadzan, or at session start if unsure whether `doc/` is current.

1. Install tool deps if needed: `pip install -r wiki/tools/requirements.txt`.
2. Run from the **`hwadzan/` directory** (all tools use CWD-relative paths for `menu.json` and `doc/`):
   ```
   cd hwadzan
   python wiki/tools/fetch.py        # refresh menu.json + per-category JSONs
   python wiki/tools/download.py     # download missing .doc/.pdf into doc/ (skips existing)
   python wiki/tools/doc_to_md.py doc # convert new .doc -> .md via markitdown
   python wiki/tools/gen_manifest.py # regenerate wiki/raw-manifest.md
   ```
3. Verify: `raw-manifest.md` counts update; spot-check a new `.md` first line (`題目　（集數）　日期　地點　檔名：CODE-PAGE`); `git status` under `doc/` shows only expected new files.
4. Report to the human what was added/updated; if new series appeared, run the Ingest workflow on them next.

Notes:
- `download.py` is **incremental** — re-running it only fetches files that don't already exist locally.
- Never hand-edit anything under `doc/`; always go through the tools.

### Ingest (one series at a time, with human review)
1. Read `wiki/raw-manifest.md` and `wiki/index.md` to find the series and check what exists.
2. Read the source pages of the series (all `.md` in the folder; start with `0001.md`).
3. Write/update the **source page** in the wiki: 概要, 重點, metadata, raw path, and the `## 原始資料與影音` section (GitHub links to the raw folder + first/last episode text `md`/`doc`/`pdf` and media links; media types come from the category JSON flags, e.g. `認識佛陀教育.json`, never guessed — see SCHEMA.md for the exact link formats).
4. Update/create **concept pages** referenced by the teachings.
5. Update the **topic page** and **category page** if the series adds structure or emphasis.
6. Update **`index.md`** (add/refresh the entry).
7. Append an entry to **`log.md`**: `## [YYYY-MM-DD] ingest|CODE 標題` plus a short note.
8. Report to the human what was done; ask which series to ingest next.

### Query
1. Read `wiki/index.md` first to find relevant pages, then drill into them.
2. Synthesize an answer citing sources (`〔CODE〕`).
3. If the answer is durable (comparison, analysis, synthesis), file it as an answer page under `wiki/問答/` and update `index.md` + `log.md`.

### Lint (periodic health-check)
- Find contradictions between pages, stale claims superseded by newer sources, orphan pages (no inbound links), important concepts missing a page, and data gaps fillable by web search.
- Fix what is fixable in the wiki; report findings to the human; append a `lint` entry to `log.md`.

## index.md and log.md

- **index.md** — content catalog, organized by category. Every page gets a line: link + one-line summary (+ optional tags). Updated on every ingest/query-filing. The primary navigation tool.
- **log.md** — append-only timeline. Every entry starts with `## [YYYY-MM-DD] type|detail`. Types: `ingest`, `query`, `answer`, `lint`, `schema`. The log is parseable with `grep "^## \[" wiki/log.md`.

## Tools

- `python wiki/tools/fetch.py` — pulls the hwadzan catalog (`menu.json` + per-category JSONs). Run from `hwadzan/` (writes CWD-relative).
- `python wiki/tools/download.py` — downloads `.doc`/`.pdf` for each course into `doc/…`. Incremental: skips files that already exist. Media (mp3/mp4) is off by default.
- `python wiki/tools/doc_to_md.py <dir>` — converts `.doc`/`.docx` → `.md` via markitdown (skips existing `.md`). Requires `markitdown` (and on Windows, `pywin32`; LibreOffice `soffice` as fallback).
- `python wiki/tools/gen_manifest.py` — regenerates `wiki/raw-manifest.md` from the raw corpus. Run when the corpus changes or at session start if unsure.
- `python wiki/tools/backfill_reflinks.py` — appends the `## 原始資料與影音` per-episode table + `media:` frontmatter to every existing source page. Idempotent (skips pages already carrying the section). Derives the episode list from on-disk `.md` files and media types from the category JSON flags. Run from `hwadzan/`.
- `python wiki/tools/gen_scaffold.py` — one-off bootstrap: creates category/topic pages from the raw `doc/` structure. Run from `hwadzan/`. Only needed when adding a new category/topic.
- Dependencies: `pip install -r wiki/tools/requirements.txt` (`requests`, `markitdown`).

## Rules of thumb

- Prefer updating existing pages over creating new ones; keep the wiki small and linked.
- When in doubt about emphasis, ask the human.
- Never invent metadata; if the raw line is missing a field, leave it blank rather than guess.
- Keep every page focused; split long pages when they exceed roughly 150 lines. Exception: the `## 原始資料與影音` per-episode reference table grows with episode count by design and is exempt from the line limit (full tables never truncated).
