from concurrent.futures import ThreadPoolExecutor
import json
import sys
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


def download_all(menu, is_download_txt, is_download_media):
    with open(menu, 'r', encoding='utf-8') as menu:
        menus = json.load(menu)
        for categories in menus['categories']:
            for category in categories['categories']:
                dir = category['AMTB_NAME']
                for file in category['categories']:
                    file_name = file['AMTB_NAME']
                    file_path = f'{dir}/{file_name}.json'
                    if is_download_txt:
                        executor.submit(download_txt, dir, file_path, file_name)
                    if is_download_media:
                        executor.submit(download_media, dir, file_path, file_name)

def download_txt(dir, file_path, file_name):
    with open(file_path, 'r', encoding='utf-8') as menu_file:
        menu_file = json.load(menu_file)
        for doc in menu_file['sutables']['data']:
            if doc['txt'] == 1 and doc['menuid'] not in EXCLUDED_AMTB_SERIES:
                menu_id = doc['menuid']
                numbers = doc['numbers']
                for index in range(numbers):
                    number = str(index+1).zfill(4)
                    for ext in doc_type:
                        url = f'https://ft.amtb.cn/ft.php?sn={menu_id}-{number}&docstype={ext}'
                        download(url, f'doc/{dir}/{file_name}/{menu_id}', f'{number}', ext)

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