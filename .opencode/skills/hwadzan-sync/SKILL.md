---
name: hwadzan-sync
description: Sync the hwadzan raw corpus (hwadzan/doc/) with amtb.tw. Use when the user asks to "sync the input /doc folder", "sync doc", "refresh sources", "update corpus", "sync from amtb.tw", or "run the source update". Triggers on keywords like sync, doc, corpus, amtb.tw, hwadzan, fetch, download, manifest.
---

# Sync hwadzan raw corpus (doc/)

Updates `hwadzan/doc/` from amtb.tw. Run from the **`hwadzan/` directory** — all tools use CWD-relative paths for `menu.json` and `doc/`.

Never hand-edit anything under `doc/`; it is changed only through these tools.

## Prerequisites

- Python deps: `pip install -r wiki/tools/requirements.txt` (`requests`, `markitdown`).
- If markitdown fails to import (numpy DLL load error, broken `numpy\.libs`), repair: `pip install --no-cache-dir "numpy==2.0.2"` (2.5.2 is known-broken on this machine — its `numpy\.libs` DLLs go missing), then verify `python -c "import numpy, markitdown, onnxruntime"`.

## Workflow

Run these steps in order, from `C:\Users\Long\Documents\hwadzan\hwadzan`:

```
python wiki/tools/fetch.py        # refresh menu.json + per-category JSONs from amtb.tw
python wiki/tools/download.py     # download missing .doc/.pdf into doc/ (skips existing; incremental)
python wiki/tools/doc_to_md.py doc # convert new .doc -> .md via markitdown (skips existing .md)
python wiki/tools/gen_manifest.py # regenerate wiki/raw-manifest.md
```

Timeout notes: full downloads can take 30+ minutes on slow connections. Pass a large bash timeout and let it finish; re-running is safe because downloads are incremental.

## Verify

1. `raw-manifest.md` counts updated.
2. Spot-check a new `.md` first line (metadata): `題目　（集數）　日期　地點　檔名：CODE-PAGE`.
3. `git status` under `doc/` shows only expected new files.
4. Remove any stray Word temp files that slipped in (e.g. `~WRD1180.tmp`) with git rm before committing.

## Report

Tell the user what was added/updated (new series codes, page counts). If new series appeared, run the Ingest workflow on them next. Ask before committing unless the user already asked to commit and push. See wiki/raw-manifest.md for counts.
