import requests
import json
import os

try:
    response = requests.get('https://www.amtb.tw/v2/newcategory?scope=amtb')
    menu = response.json()
    with open('menu.json', 'w', encoding='utf-8') as f:
        json.dump(menu, f, ensure_ascii=False, indent=4)
    for item in menu['categories']:
        for items in item['categories']:
            dir_name = items['AMTB_NAME']
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            for subitem in items['categories']:
                name = subitem['AMTB_NAME']
                id = subitem['AMTB_ID']
                response = requests.get('https://www.amtb.tw/v2/newcategory/'+str(id))
                subitem_json = response.json()
                with open(dir_name + '/' + name+'.json', 'w', encoding='utf-8') as subf:
                    json.dump(subitem_json, subf, ensure_ascii=False, indent=4)
except requests.exceptions.HTTPError as error:
    print(error)