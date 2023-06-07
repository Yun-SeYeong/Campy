import pandas as pd
import requests
from urllib import parse
import xmltodict as xmltodict



df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='utf-8')

df_base['캠핑(야영)장명'] = df_base['캠핑(야영)장명'].apply(lambda x: x.strip())


def get_go_camping(name):
    url = 'https://apis.data.go.kr/B551011/GoCamping/searchList?serviceKey=922T%2FggEzFLCf3DO224yyCR0geVmU6X1KwM%2FDq%2Bp%2FcW6UueOtxRERU7eEJgiOnIyv5MvbcsOJd6HeRdYZwO1Hw%3D%3D&numOfRows=10&pageNo=1&MobileOS=ETC&MobileApp=AppTest&keyword='
    response = requests.get(url + parse.quote(name))

    content = response.content
    status_code = response.status_code

    dict_content = xmltodict.parse(content)

    if status_code != 200:
        print('status code: ', status_code)
        return None

    print('name', parse.quote(name))
    print(dict_content)

    items = dict_content['response']['body']['items']

    if items is None:
        return None

    return items['item'][0]['intro'] if isinstance(items['item'], list) else items['item']['intro']


df_base['intro'] = df_base['캠핑(야영)장명'].tail(100).apply(get_go_camping)

df_base.to_csv('csv/merge_intro.csv')
