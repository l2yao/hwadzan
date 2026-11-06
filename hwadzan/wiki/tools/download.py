from concurrent.futures import ThreadPoolExecutor
import json
import os
import sys
import threading
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

doc_type = ['doc', 'pdf']
media_type = ['mp3', 'mp4']
executor = ThreadPoolExecutor(max_workers=4)

# Series hosted in the AMTB repo (github.com/l2yao/amtb) — do not download
# them here even though the hwadzan catalog cross-lists them. Verified
# 2026-11-05 against amtb/amtb/doc: 02-039, 02-041, 25-156 are there.
EXCLUDED_AMTB_SERIES = {'02-039', '02-041', '25-156'}

# Verified last real episode per series (probed on ft.amtb.cn 2026-11-05).
# The catalog `numbers` field is inflated by alert stubs past these points,
# so cap the download loop here instead of fetching known stubs.
VERIFIED_LAST_EPISODE = {'WD20-064': 800, 'WD29-003': 784, 'WD29-006': 210, 'WD19-036': 108}

# Episodes verified empty on 2026-11-05 — do not re-download them on later
# syncs. Alert stubs (128-byte script page): 55-217/0072, WD03-004/0001.
# "無文字稿" (source returns a one-line no-transcript page): 62-348/0002,
# 62-348/0003, 62-348/0004, WD29-006/0163. Re-check upstream before lifting.
SKIP_EPISODES = {'55-217': {72}, 'WD03-004': {1}, '62-348': {2, 3, 4}, 'WD29-006': {163}}

# Series the upstream catalog moved to a new topic (Nov 2026 catalog) —
# the wiki keeps the original folder because the source pages, topic
# pages and concept links all point there. A later decision to follow
# the move would be a large rename PR; until then downloads go here.
CANONICAL_OVERRIDE = {
    'WD32-072': ('法音宣流', '開示講話'),   # catalog now: 三時繫念功德利益
    'WD20-065': ('儒釋道經典', '因果教育'),  # catalog now: 法音宣流/淨土念佛
    '56-053': ('弘法活動', '活動紀實'),    # catalog now: 儒釋道文化/其他講演者
}

# Series already downloaded to their canonical folder in this run
# (download_txt runs per topic JSON under threads; a dual-listed series
# must not download twice).
_downloaded = set()
_downloaded_lock = threading.Lock()

def download(url, path, filename, ext):
    out = Path(path) / f'{filename}.{ext}'
    if out.exists():
        print(f'skip existing: {out}')
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as f:
        doc = f.read()
        with open(out, 'wb') as wf:
            wf.write(doc)
    print(f'downloaded: {out}')


def _canonical_paths(menus):
    """A series can be listed under two topics in the catalog; download it
    only once, into the folder that already holds it on disk (else the
    first listing). Without this, each sync re-creates mirror folders of
    byte-identical files (e.g. WD32-072 under two topics, Nov 2026)."""
    listings = {}
    for categories in menus['categories']:
        for category in categories['categories']:
            dir = category['AMTB_NAME']
            for file in category['categories']:
                file_name = file['AMTB_NAME']
                with open(f'{dir}/{file_name}.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for doc in data['sutables']['data']:
                    if doc['txt'] == 1 and doc['menuid'] not in EXCLUDED_AMTB_SERIES:
                        listings.setdefault(doc['menuid'], []).append((dir, file_name))
    canonical = {}
    for menuid, paths in listings.items():
        if menuid in CANONICAL_OVERRIDE:
            canonical[menuid] = CANONICAL_OVERRIDE[menuid]
            continue
        canonical[menuid] = next(
            (p for p in paths
             if os.path.isdir(f'doc/{p[0]}/{p[1]}/{menuid}')
             and os.listdir(f'doc/{p[0]}/{p[1]}/{menuid}')),
            paths[0])
    return canonical


def download_all(menu, is_download_txt, is_download_media):
    with open(menu, 'r', encoding='utf-8') as menu:
        menus = json.load(menu)
        canonical = _canonical_paths(menus) if is_download_txt else {}
        for categories in menus['categories']:
            for category in categories['categories']:
                dir = category['AMTB_NAME']
                for file in category['categories']:
                    file_name = file['AMTB_NAME']
                    file_path = f'{dir}/{file_name}.json'
                    if is_download_txt:
                        executor.submit(download_txt, dir, file_path, file_name, canonical)
                    if is_download_media:
                        executor.submit(download_media, dir, file_path, file_name)

def download_txt(dir, file_path, file_name, canonical):
    with open(file_path, 'r', encoding='utf-8') as menu_file:
        menu_file = json.load(menu_file)
        for doc in menu_file['sutables']['data']:
            if doc['txt'] == 1 and doc['menuid'] not in EXCLUDED_AMTB_SERIES:
                menu_id = doc['menuid']
                numbers = min(doc['numbers'], VERIFIED_LAST_EPISODE.get(menu_id, doc['numbers']))
                target = canonical.get(menu_id, (dir, file_name))
                with _downloaded_lock:
                    if menu_id in _downloaded:
                        continue
                    _downloaded.add(menu_id)
                for index in range(numbers):
                    number = str(index+1).zfill(4)
                    if (index + 1) in SKIP_EPISODES.get(menu_id, set()):
                        continue
                    for ext in doc_type:
                        url = f'https://ft.amtb.cn/ft.php?sn={menu_id}-{number}&docstype={ext}'
                        download(url, f'doc/{target[0]}/{target[1]}/{menu_id}', f'{number}', ext)

def download_media(dir, file_path, file_name):
    with open(file_path, 'r', encoding='utf-8') as menu_file:
        menu_file = json.load(menu_file)
        for doc in menu_file['sutables']['data']:
            menu_id = doc['menuid']
            menu_id_parent = doc['menuidparent']
            numbers = doc['numbers']
            
            for index in range(numbers):
                number = str(index+1).zfill(4)
                for ext in media_type:
                    if doc[ext] == 1:
                        url = f'https://tw4.hwadzan.info/redirect/media/{ext}/{menu_id_parent}/{menu_id}/{menu_id}-{number}.{ext}'
                        download(url, f'media/{dir}/{file_name}/{menu_id}', f'{number}', ext)

if __name__ == "__main__":
    download_all('menu.json', True, False)