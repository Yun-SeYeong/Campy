import pandas as pd

df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='utf-8')
df_busan = pd.read_csv("csv/부산광역시 기장군_야영장(캠핑장)_20230407.csv", encoding='euc-kr')

# print('left: ', df_base.tail(5))
# print('right: ', df_busan.tail(5))

df_base['캠핑(야영)장명'] = df_base['캠핑(야영)장명'].apply(lambda x: x.strip())

df_merge = pd.merge(left=df_base, right=df_busan, how='left', left_on='캠핑(야영)장명', right_on='상호')

# print('keys', df_merge.keys())
# print('left_on', df_base[df_base['캠핑(야영)장명'] == '장안캠프'])
# print('right_on', df_busan[df_busan['상호'] == '장안캠프'])
# print('merge', df_merge[df_merge['상호'] == '장안캠프'].to_dict('records'))
# print('result:', df_merge.tail(2).to_dict("records"))

df_merge.to_csv('csv/process0.csv')
