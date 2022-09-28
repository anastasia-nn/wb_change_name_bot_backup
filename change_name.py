import requests
import json


# headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6Ijk5NWJiZTY3LWQyMGItNDU3Mi04NmFiLWQ0NmVlMWUyNzFjMyJ9.3f5juiWxnbFFN1VKFsERRIjpXR7BkgxMlYLQv2oGHfw"}
#
# # headers['Authorization'] += '1'


def search_data(nm_id):
    data = {
          "vendorCodes": [
            str(nm_id)
          ]
    }
    return data


def get_card_info(data, headers):
    info = requests.post('https://suppliers-api.wildberries.ru/content/v1/cards/filter', json=data, headers=headers)
    return info


def prepare_card_info(info):
    info = json.loads(info.content.decode('utf8'))['data'][0]  # Делаем json
    return info


def info_to_upload(info, new_product_name):
    for i in range(len(info['characteristics'])):
        if list(info['characteristics'][i].keys())[0] == 'Наименование':
            info['characteristics'][i] = {'Наименование': new_product_name}
            break
        if i == len(info['characteristics']) - 1:
            info['characteristics'].append({'Наименование': new_product_name})
    updated_info = dict()
    card_params = ['nmID', 'vendorCode', 'sizes', 'characteristics']
    for param in card_params:
        updated_info[param] = info[param]

    return [updated_info]