# hwadzan

工具與資料庫，用於處理華藏淨宗學會（hwadzan）的佛教開示。資料來源：https://www.amtb.tw/

本倉庫包含兩大部分：

## 1. LLM 維基（wiki）

以 Karpathy「LLM Wiki」模式維護的**傳統中文佛學知識庫**。LLM 負責讀取原始開示、撰寫並持續更新 wiki 頁面；人類負責選材、提問與審閱。

- **原始資料（不可更動）**：`hwadzan/doc/` — 10 大類別、816 個系列、約 9,000 頁開示文稿。
- **維基**：`hwadzan/wiki/` — LLM 撰寫的互相連結 Markdown 頁面（類別、主題、開示、概念、問答）。
- **綱要**：`AGENTS.md`（結構與工作流程）、`wiki/SCHEMA.md`（頁面範本）。

主要工作流程（詳見 `AGENTS.md`）：

- **ingest**：把一個系列整理成開示頁，並更新概念頁、索引與日誌。
- **query**：查維基並以引用（`〔63-001〕`）作答；好的問答會存回 `wiki/問答/`。
- **lint**：定期健康檢查（矛盾、孤兒頁、缺頁等）。

瀏覽方式：用 Obsidian 開啟 `hwadzan/wiki/`；導覽起點為 `wiki/README.md` 與 `wiki/index.md`。

## 2. 資料工具

`hwadzan/` 下的 Python 腳本，用於自 amtb.tw 抓取與轉檔：

```
# 從 amtb.tw 抓取分類選單（menu.json）
cd hwadzan
python fetch.py

# 依 menu.json + 範本產生網頁 markdown
python gen.py

# 下載 doc / pdf / mp3 / mp4 資料與影音
python download.py

# 將 .doc 轉成 .md（需 markitdown）
python doc_to_md.py
```

## 目錄結構

```
hwadzan/
  AGENTS.md            <- LLM 維基綱要（schema）
  hwadzan/
    doc/               <- 原始開示（唯讀）
    menu.json
    fetch.py / download.py
    wiki/              <- LLM 維基（LLM 撰寫維護）
      tools/           <- 資料工具
```
