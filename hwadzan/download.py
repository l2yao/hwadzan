from concurrent.futures import ThreadPoolExecutor
import json
import urllib.request
from pathlib import Path

doc_type = ['doc', 'pdf']
media_type = ['mp3', 'mp4']
executor = ThreadPoolExecutor(max_workers=4)

def download(url, path, filename, ext):
    Path(path).mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as f:
        doc = f.read()
        with open(f'{path}/{filename}.{ext}', 'wb') as wf:
            wf.write(doc)


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
            if doc['txt'] == 1:
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

download_all('menu.json', True, False)