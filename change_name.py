import requests
import json


headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6Ijk5NWJiZTY3LWQyMGItNDU3Mi04NmFiLWQ0NmVlMWUyNzFjMyJ9.3f5juiWxnbFFN1VKFsERRIjpXR7BkgxMlYLQv2oGHfw"}

# headers['Authorization'] += '1'
info = requests.get('https://suppliers-api.wildberries.ru/api/v1/directory/wbsizes', headers=headers)
print()


def search_data(nm_id):
    data = {
        "id": "1",
        "jsonrpc": "2.0",
        "params": {
            "filter": {
                # Поиск в соответсвии с условиями запроса
                "find": [
                    {
                        "column": "nomenclatures.nmId",  # поиск по NM id
                        "search": nm_id  # значение типа int
                    }
                ],
                # Сортировка по указанному полю в указанном порядке.
                "order": {
                    "column": "createdAt",
                    "order": "asc"
                }
            },
            # Пагинация. Вывести максимум 10 карточек после пропуска 20. Выведутся карточки с 20 по 30 из тех, которые соотетствуют фильтру.
            "query": {
                "limit": 10,
                "offset": 0
            },
            # "withError": false  # параметр, указывающий, что вернутся только карточки, в которых есть ошибки, которые не удалось создать. Параметр не обязательный, если его не указывать, вернутся только созданные карточки.
        }
    }
    return data


def get_card_info(data, headers):
    info = requests.post('https://suppliers-api.wildberries.ru/card/list', json=data, headers=headers)
    return info


def prepare_card_info(info, headers):
    info = json.loads(info.content.decode('utf8'))  # Делаем json
    info = info['result']['cards'][0]
    imt_id = info['imtId']
    supplier_id = info['supplierId']
    data = {
        "id": info['id'],
        "jsonrpc": "2.0",
        "params": {
            "imtID": imt_id,
            "supplierID": supplier_id
        }
    }
    info = requests.post('https://suppliers-api.wildberries.ru/card/cardByImtID', json=data, headers=headers)
    info = info.text
    info = json.loads(info)['result']
    return info


def info_to_upload(info, new_product_name):
    info['card']['addin'][1]['params'][0]['value'] = new_product_name
    updated_info = dict()
    updated_info['params'] = {'card': {}}

    card_params = ['id', 'imtId', 'userId', 'supplierId', 'imtSupplierId', 'object', 'parent', 'countryProduction',
                   'addin', 'nomenclatures']
    for param in card_params:
        updated_info['params']['card'][param] = info['card'][param]

    updated_info['jsonrpc'] = "2.0"
    updated_info['id'] = info['card']['nomenclatures'][0]['id']
    return updated_info

data = search_data(nm_id=78914388)
info = get_card_info(data, headers)
info = prepare_card_info(info, headers)

updated_info = info_to_upload(info, 'Лента для рукоделия ажурная')

updater = requests.post('https://suppliers-api.wildberries.ru/card/update', json=updated_info, headers=headers)

new_info = requests.post('https://suppliers-api.wildberries.ru/card/list', json=data, headers=headers)
new_info = json.loads(new_info.content.decode('utf8'))  # Делаем json
new_info = new_info['result']['cards'][0]
print()

# data_2 = search_data(nm_id=78850671)
# info_2 = get_card_info(data_2, headers)
# info_2 = prepare_card_info(info_2)
# updated_info_2 = info_to_upload(info_2, 'Спортивный пистолет')
# updater_2 = requests.post('https://suppliers-api.wildberries.ru/card/update', json=updated_info_2, headers=headers)
# new_info_2 = requests.post('https://suppliers-api.wildberries.ru/card/list', json=data_2, headers=headers)
# new_info_2 = json.loads(new_info_2.content.decode('utf8'))  # Делаем json
#
# print(updated_info)
# print(updater)