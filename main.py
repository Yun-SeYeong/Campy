import json
import os
import pandas as pd
import openai
import requests
from urllib import parse
import xmltodict as xmltodict
from dotenv import load_dotenv
from flask import Flask, request, Response

app = Flask(__name__)

from openai.embeddings_utils import (
    distances_from_embeddings,
    indices_of_nearest_neighbors_from_distances,
)

load_dotenv(dotenv_path='.env')


def get_go_camping(name):
    url = 'https://apis.data.go.kr/B551011/GoCamping/searchList?serviceKey=922T%2FggEzFLCf3DO224yyCR0geVmU6X1KwM%2FDq%2Bp%2FcW6UueOtxRERU7eEJgiOnIyv5MvbcsOJd6HeRdYZwO1Hw%3D%3D&numOfRows=10&pageNo=1&MobileOS=ETC&MobileApp=AppTest&keyword='
    response = requests.get(url + parse.quote(name))

    content = response.content
    status_code = response.status_code

    dict_content = xmltodict.parse(content)

    if status_code != 200 and dict_content['response'] is None:
        return ""

    items = dict_content['response']['body']['items']

    if items is None:
        return ""

    return (items['item'][0]['intro'] if isinstance(items['item'], list) else items['item']['intro']) or ""


def init(epoch):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    base_filepath = os.getenv("BASE_PATH")

    print(epoch)
    print(base_filepath)

    # process1
    # 기초데이터를 바탕으로 json 생성
    if not os.path.isfile("csv/process1.csv"):
        df_base = pd.read_csv(base_filepath, encoding='utf-8')

        def convert_json(record):
            data = record.to_dict()
            converted_record = {}
            for key in data:
                if not pd.isna(data[key]) and data[key] != 0:
                    converted_record[key] = data[key]
            return json.dumps(converted_record, ensure_ascii=False)

        df_base['process1'] = df_base.tail(epoch)[:].apply(convert_json, axis=1)
        df_base.tail(epoch).to_csv('csv/process1.csv')

    # process2
    # 생성된 json을 바탕으로 캠핑장 설명 생성
    df_process1 = pd.read_csv("csv/process1.csv", encoding='utf-8')
    df_cached = None
    if os.path.isfile("csv/process2.csv"):
        df_cached = pd.read_csv("csv/process2.csv", encoding='utf-8')

    def convert_detail(process1, name):
        result = openai.Completion.create(
            model="text-davinci-003",
            prompt="{detail}\n\n캠핑장 설명:".format(detail=process1),
            max_tokens=500,
            temperature=0
        )
        print(result.choices[0].text)
        return result.choices[0].text.replace('\n', ' ', -1).strip() + get_go_camping(name)

    if df_cached is not None:
        df_process1['process2'] = df_cached['process2']
    else:
        df_process1['process2'] = None

    for i in df_process1.index:
        print(i)
        if i > epoch:
            break
        if pd.isna(df_process1._get_value(i, 'process2')):
            description = convert_detail(df_process1._get_value(i, 'process1'), df_process1._get_value(i, '캠핑(야영)장명'))
            df_process1._set_value(i, 'process2', description)
            df_process1.to_csv('csv/process2.csv')

    # process3
    # 캠핑장 설명을 바탕으로 Vector 생성
    if not os.path.isfile("csv/process3.csv"):
        df_process2 = pd.read_csv("csv/process2.csv", encoding='utf-8')

        def convert_vector(record):
            if record is None:
                return None

            result = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=[record['process2']]
            )
            print(result.data[0].embedding)
            return json.dumps(result.data[0].embedding, ensure_ascii=False)

        df_process2['process3'] = df_process2.tail(epoch)[:].apply(convert_vector, axis=1)
        df_process2.tail(epoch).to_csv('csv/process3.csv')


def recommend_camping(search_text):
    k_nearest_neighbors = 5

    df_process3 = pd.read_csv("csv/process3.csv", encoding='utf-8')

    search_vector = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=search_text
    ).data[0].embedding

    embeddings = df_process3['process3'].apply(lambda x: json.loads(x) if x is not None else None).to_list()
    embeddings.insert(0, search_vector)

    # get distances between the source embedding and other embeddings (function from embeddings_utils.py)
    distances = distances_from_embeddings(search_vector, embeddings, distance_metric="cosine")
    # get indices of nearest neighbors (function from embeddings_utils.py)
    indices_of_nearest_neighbors = indices_of_nearest_neighbors_from_distances(distances)

    result = []

    print(f"Source string: {search_text}")
    k_counter = 0
    for i in indices_of_nearest_neighbors:
        # skip any strings that are identical matches to the starting string
        if i == 0:
            continue
        # stop after printing out k articles
        if k_counter >= k_nearest_neighbors:
            break
        k_counter += 1

        # print out the similar strings and their distances
        print(
            f"""
    --- Recommendation #{k_counter} (nearest neighbor {k_counter} of {k_nearest_neighbors}) ---
    String: {df_process3.iloc[i - 1]['process2']}
    Distance: {distances[i]:0.3f}"""
        )
        result.append(df_process3.iloc[i - 1]['process2'])
    return result


chat_list = []


@app.route('/v1/generate-vector', methods=['POST'])
def generate_vector():
    init(int(json.loads(request.get_data().decode())['count']))
    return Response(status=200)


@app.route('/v1/chat/open', methods=['POST'])
def chat():
    chat_list.append([])
    return {"code": len(chat_list)}


@app.route('/v1/chat', methods=['POST'])
def post_chat():
    data = json.loads(request.get_data().decode())
    print(data['code'])
    print(data['msg'])

    code = int(data['code']) - 1
    msg = data['msg']

    if len(chat_list) <= code:
        return Response(status=400)

    question = ""
    for user_msg in chat_list[int(code) - 1]:
        if user_msg['role'] == 'user':
            question += "과거 질문: " + user_msg['content'] + "\n"
    question += "질문: " + msg + "\n"

    print("question", question)

    msg_completion = openai.Completion.create(
        model="text-davinci-003",
        prompt="질문들이 요구하는 내용을 5가지 다른 문장으로 만들어줘\n{detail}".format(
            detail=question),
        max_tokens=500,
        temperature=1
    )
    print("msg_completion", msg_completion.choices[0].text)

    chat_completion = [
        {
            "role": "system",
            "content": "Use the following step-by-step instructions to respond to user inputs.\n" +
                       "질문과 관련된 캠핑장 정보를 조회해.\n" +
                       "조회한 정보를 바탕으로 정확한 답변을 할 수 있는 것은 답변해(답변은 \"지금까지 종합한 결과\"로 시작해)\n"
                       "답변할 수 없다면 답변을 하지마."
        }, {
            "role": "user",
            "content": question
        }, {
            "role": "assistant",
            "content": "캠핑장 정보\n - ".join(
                recommend_camping(msg + msg_completion.choices[0].text)) + "\n\n"
        }
    ]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_completion
    )
    chat_list[code].append(
        {
            "role": "user",
            "content": msg
        }
    )

    chat_list[code].append(completion.choices[0].message)

    return completion.choices[0].message


@app.route('/v1/chat/<code>', methods=['GET'])
def get_chat(code):
    print(chat_list)
    for msg in chat_list[int(code) - 1]:
        if msg['role'] == 'user' and '\n\n질문: ' in msg['content']:
            msg['content'] = msg['content'].split('\n\n질문: ')[1]

    return chat_list[int(code) - 1]


if __name__ == '__main__':
    init(int(os.getenv("EPOCH")))

    app.debug = True
    app.run()
