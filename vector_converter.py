import json

import pandas as pd
import openai
import os

from dotenv import load_dotenv

from openai.embeddings_utils import (
    distances_from_embeddings,
    indices_of_nearest_neighbors_from_distances,
)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
epoch = 5

base_filepath = "csv/한국관광공사 전국 야영장 등록 현황.csv"
process1_filepath = "csv/process1.csv"
process2_filepath = "csv/process2.csv"

# process1
# 기초데이터를 바탕으로 json 생성
if not os.path.isfile("csv/process1.csv"):
    df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='utf-8')


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
if not os.path.isfile("csv/process2.csv"):
    df_process1 = pd.read_csv("csv/process1.csv", encoding='utf-8')


    def convert_detail(record):
        result = openai.Completion.create(
            model="text-davinci-003",
            prompt="{detail}\n\n캠핑장 설명:".format(detail=record['process1']),
            max_tokens=500,
            temperature=0
        )
        print(result.choices[0].text)
        return result.choices[0].text


    df_process1['process2'] = df_process1.tail(epoch)[:].apply(convert_detail, axis=1)
    df_process1.tail(epoch).to_csv('csv/process2.csv')

# process3
# 캠핑장 설명을 바탕으로 Vector 생성
if not os.path.isfile("csv/process3.csv"):
    df_process2 = pd.read_csv("csv/process2.csv", encoding='utf-8')


    def convert_vector(record):
        result = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=[record['process2']]
        )
        print(result.data[0].embedding)
        return json.dumps(result.data[0].embedding, ensure_ascii=False)


    df_process2['process3'] = df_process2.tail(epoch)[:].apply(convert_vector, axis=1)
    df_process2.tail(epoch).to_csv('csv/process3.csv')

# 유사도 검사


def recommend_camping(search_text):
    k_nearest_neighbors = 5

    df_process3 = pd.read_csv("csv/process3.csv", encoding='utf-8')

    search_vector = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=search_text
    ).data[0].embedding

    print('search_vector', search_vector)

    embeddings = df_process3['process3'].apply(lambda x: json.loads(x) if x is not None else None).to_list()
    embeddings.insert(0, search_vector)

    # get distances between the source embedding and other embeddings (function from embeddings_utils.py)
    distances = distances_from_embeddings(search_vector, embeddings, distance_metric="cosine")
    # get indices of nearest neighbors (function from embeddings_utils.py)
    indices_of_nearest_neighbors = indices_of_nearest_neighbors_from_distances(distances)
    print(indices_of_nearest_neighbors)

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


recommend_camping("일반야영장")
