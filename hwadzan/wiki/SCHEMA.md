# SCHEMA.md — 頁面範本與範例

This file documents the exact page templates and examples for the wiki. Reference `AGENTS.md` for the overall schema. All page content is Traditional Chinese.

## 頁面類型速覽

| 類型 | 位置 | frontmatter `type` |
|---|---|---|
| 類別頁 | `wiki/<類別>.md` | `category` |
| 主題頁 | `wiki/<類別>/<主題>.md` | `topic` |
| 開示頁 | `wiki/<類別>/<CODE>.md` | `source` |
| 概念頁 | `wiki/概念/<概念>.md` | `concept` |
| 問答頁 | `wiki/問答/<題目>.md` | `answer` |

## 範本

### 類別頁 (category)

```markdown
---
type: category
tags: [淨土]
sources: 90
updated: 2026-08-12
---

# 淨土五經一論

此類別涵蓋淨土宗的根本經論：…（一段綜合說明）。

## 主題

- [[無量壽經]] — …
- [[阿彌陀經]] — …

## 開示一覽

依 [[index|索引]] 與 [[raw-manifest|原始清單]] 查閱。
```

### 主題頁 (topic)

```markdown
---
type: topic
category: 淨土五經一論
tags: [無量壽經]
updated: 2026-08-12
---

# 無量壽經

經義大要：…

## 開示

- [[63-001]] — …
- [[WD21-121]] — …

## 相關概念

- [[概念/阿彌陀佛]] [[概念/四十八願]]
```

### 開示頁 (source) — 每個系列一頁

```markdown
---
type: source
category: 佛事共修
topic: 梵唄教學
code: 63-001
title: 二ＯＯ五年古晉報恩念佛堂中元普度—法器儀規教學
date: 2005/8/16
place: 古晉報恩念佛堂
pages: 1
raw: doc/佛事共修/梵唄教學/63-001/
media: [mp3]
tags: [佛事共修, 法器儀規]
created: 2026-08-12
updated: 2026-08-12
---

# 二ＯＯ五年古晉報恩念佛堂中元普度—法器儀規教學（63-001）

- **檔名**：63-001
- **類別**：佛事共修 / 梵唄教學
- **集數**：共 1 集
- **日期地點**：2005/8/16，古晉報恩念佛堂
- **原始路徑**：`doc/佛事共修/梵唄教學/63-001/`

## 概要

一段話說明本開示講什麼。

## 重點

- 要點一〔63-001-0001〕
- 要點二

## 相關概念

- [[概念/法器]] [[概念/梵唄]]

## 相關頁面

- [[梵唄教學]] — 主題頁
- [[63-002]] — 同題材其他開示

## 原始資料與影音

原始資料夾：[GitHub](https://github.com/l2yao/hwadzan/tree/main/hwadzan/doc/佛事共修/梵唄教學/63-001)（doc/pdf/md 全部集數）

| 集數 | 文字 | 影音 |
|---|---|---|
| 0001 | [md](https://github.com/l2yao/hwadzan/blob/main/hwadzan/doc/佛事共修/梵唄教學/63-001/0001.md) · [doc](https://github.com/l2yao/hwadzan/blob/main/hwadzan/doc/佛事共修/梵唄教學/63-001/0001.doc) · [pdf](https://github.com/l2yao/hwadzan/blob/main/hwadzan/doc/佛事共修/梵唄教學/63-001/0001.pdf) | [mp3](https://tw4.hwadzan.info/redirect/media/mp3/63/63-001/63-001-0001.mp3) |

> 每集皆須列入；集數多（上百集）時亦須全列，不得省略。媒體類型由該系列於分類 JSON 的旗標決定：`mp3`（mp3=1）、`himp4`（himp4=1）、`mp4`（mp4=1 且 himp4=0）。
```

### 概念頁 (concept)

```markdown
---
type: concept
tags: [戒律]
sources: [16-001, 63-001]
updated: 2026-08-12
---

# 五戒

定義：…

## 各開示的講法

- [[63-001]] — 強調 …
- [[WD21-121]] — …

## 要點

- …

## 相關概念

- [[概念/十善]] [[概念/三皈依]]

## 引用出處

- 〔63-001〕〔WD21-121〕
```

### 問答頁 (answer)

```markdown
---
type: answer
tags: [比較]
updated: 2026-08-12
---

# 標題

**問題**：…

**回答**：…

## 出處

- 〔CODE〕
- [[63-001]]

## 相關頁面

- …
```

## 命名與連結規則

- 檔名：概念/主題用中文名；開示頁用代碼（如 `63-001.md`、`WD21-121.md`）。檔名不含空格。
- 內部連結：`[[頁面名]]`；開示頁連結代碼 `[[63-001]]`；概念頁用 `[[概念/念佛]]`。
- 引用：`〔63-001〕` 引用整個系列，`〔63-001-0001〕` 引用特定一集。
- 開示頁需附 `## 原始資料與影音` 區段，提供：原始資料夾的 GitHub 連結（`https://github.com/l2yao/hwadzan/tree/main/hwadzan/doc/<路徑>`），以及**每一集**的文字（`md`/`doc`/`pdf`，GitHub blob：`https://github.com/l2yao/hwadzan/blob/main/hwadzan/doc/<路徑>/<NNNN>.<副檔名>`）與影音連結，以表格逐集列出。中文路徑在 URL 中須以 UTF-8 百分比編碼。
- 影音連結格式（hwadzan CDN 重新導向，`parent` 為 `code` 之首段，如 `63-001` → `63`、`WD21-121` → `WD21`；`NNNN` 為集數補零至四位）：
  - mp3：`https://tw4.hwadzan.info/redirect/media/mp3/{parent}/{code}/{code}-{NNNN}.mp3`
  - himp4：`https://tw4.hwadzan.info/redirect/media/himp4/{parent}/{code}/{code}-{NNNN}.mp4`
  - mp4：`https://tw4.hwadzan.info/redirect/media/mp4/{parent}/{code}/{code}-{NNNN}.mp4`
  - 依 frontmatter `media` 列出之類型取用。

## 前導資料 (frontmatter)

可用欄位：

| 欄位 | 說明 | 例 |
|---|---|---|
| `type` | 頁面類型 | `source` |
| `category` | 類別（中文） | `佛事共修` |
| `topic` | 主題（中文） | `梵唄教學` |
| `code` | 系列代碼 | `63-001` |
| `title` | 開示題目 | `法器儀規教學` |
| `date` | 日期，`YYYY-M` 或 `YYYY/MM/DD` | `2005/8/16` |
| `place` | 地點 | `古晉報恩念佛堂` |
| `pages` | 集數 | `1` |
| `raw` | 原始資料夾路徑 | `doc/佛事共修/梵唄教學/63-001/` |
| `media` | 可取得的影音類型（取自分類 JSON 旗標） | `[mp3]` / `[mp3, himp4]` |
| `tags` | 標籤 | `[淨土, 阿彌陀佛]` |
| `created` / `updated` | 日期 | `2026-08-12` |
| `sources` | 概念頁引用的系列代碼 | `[63-001, WD21-121]` |

## 長度規則

- 單頁約 150 行內；超過則拆分。
- 例外：`## 原始資料與影音` 的逐集表格依集數增長，屬設計使然，不受行數限制（全表不得截斷）。
- 概念頁、問答頁隨內容演化而更新，不需每次重寫。

## 參考連結回填工具

`python wiki/tools/backfill_reflinks.py` 可為既有開示頁批次加入 `media:` frontmatter 與 `## 原始資料與影音` 逐集表格（由分類 JSON 旗標與磁碟上 `.md` 檔案推導，永不臆測）。冪等：已有該區段之頁面會跳過。由 `hwadzan/` 目錄執行。
