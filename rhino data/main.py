# @Author   :155
# @File     :main.py
# @Time     :2024/12/24 10:56
# @Software :PyCharm
import time
import random
import execjs
import json
import requests
import base64


def get_encrypt_params(pagenum):
    with open('encrypt_params.js', 'r', encoding="utf-8") as fp:
        encrypt_params_code = fp.read()
        ctx = execjs.compile(encrypt_params_code)
        encrypt_prepare_data = {
            "payload": {
                "sort": 1,
                "start": pagenum * 20,
                "limit": 20
            }
        }
        params = ctx.call("ret_load_params", encrypt_prepare_data)
        return params


def get_data(params_data):
    url = 'https://www.xiniudata.com/api2/service/x_service/person_industry_list/list_industries_by_sort'
    headers = {
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.xiniudata.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.xiniudata.com/industry/newest',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }
    cookies = {

    }
    json_data = {
        'payload': params_data['f'],
        'sig': params_data['p'],
        'v': 1,
    }
    response = requests.post(
        url=url,
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    return json.loads(response.text)


def get_ret_rawdata(response_json):
    with open('decrypt_data.js', 'r', encoding="utf-8") as fp:
        decrypt_data_code = fp.read()
        ctx = execjs.compile(decrypt_data_code)
        raw_data = ctx.call("decrypt", response_json['d'])
        raw_data = base64.b64decode(raw_data['Data'])
        return raw_data


def parse_data(raw_data):
    loc_raw_data = json.loads(raw_data)
    data = loc_raw_data['list']
    for each_data in data:
        Company_name_list = []
        for index, value in enumerate(each_data['companyVOs']):
            Company_name = value['name']
            Company_name_dict = {
                "name": Company_name,
                "index": index + 1
            }
            Company_name_list.append(Company_name_dict)

        if each_data['lastUpdateVO']['lastUpdateNews'] is None:
            title = ''
        else:
            title_json = json.loads(each_data['lastUpdateVO']['lastUpdateNews'])
            title = title_json['title']
        data_dict = {
            "name": each_data['name'],
            "event": each_data['event'],
            "countCompany": each_data['countCompany'],
            "companyVOs": Company_name_list,
            "title": title
        }
        print(data_dict)


if __name__ == '__main__':
    for pagenum in range(0, 67):
        params_data = get_encrypt_params(pagenum)
        response_json = get_data(params_data)
        raw_data = get_ret_rawdata(response_json)
        parse_data(raw_data)
        random.uniform(1, 2)
