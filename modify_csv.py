# import pandas as pd
#
# df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='euc-kr')
# df_milyang = pd.read_csv("csv/경상남도 밀양시_캠핑장 현황_20220530.csv", encoding='euc-kr')
# merged_df = pd.merge(left=df_base, right=df_milyang, how='outer', left_on='캠핑(야영)장명', right_on='야영장')
#
# # print(df_merge.keys())
# print(merged_df.head)
# merged_df.to_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", index=True, encoding='utf-8-sig')

########################################################################
# import pandas as pd
#
# df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='euc-kr')
# df_milyang = pd.read_csv("csv/경상남도 밀양시_캠핑장 현황_20220530.csv", encoding='euc-kr')
#
# merged_df = df_base.merge(df_milyang, left_on='캠핑(야영)장명', right_on='야영장', how='inner')
#
# # merged_df['부지면적(제곱미터)'] = merged_df['부지면적(제곱미터)'].where(merged_df['부지면적(제곱미터)'].notnull(), merged_df['야영장'])
#
# print(merged_df)
#
# merged_df.to_csv("한국관광공사 전국 야영장 등록 현황.csv", index=False, encoding='utf-8-sig')

########################################################################

import pandas as pd

#### 밀양 #####
df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='euc-kr')
df_milyang = pd.read_csv("csv/경상남도 밀양시_캠핑장 현황_20220530.csv", encoding='euc-kr')

merged_df = pd.merge(left=df_base, right=df_milyang, left_on='캠핑(야영)장명', right_on='야영장', how='left')

merged_df = merged_df.drop(['야영장', '위치'], axis=1)
merged_df.to_csv("csv/한국관광공사 전국 야영장 등록 현황.csv")

#### 영양 #####
df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='utf-8')
df_youngyang = pd.read_csv("csv/경상북도 영양군_야영(캠핑)장 현황_20220922.csv", encoding='euc-kr')
merged_df = pd.merge(left=df_base, right=df_youngyang, left_on='캠핑(야영)장명', right_on='야영(캠핑)장명', how='left')
merged_df = merged_df.drop(['야영(캠핑)장명', '소재지도로명주소', '소재지지번주소'], axis=1)
merged_df.to_csv("csv/한국관광공사 전국 야영장 등록 현황.csv")

#### 문경 #####
df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='utf-8')
df_munkyung = pd.read_csv("csv/경상북도 문경시_캠핑장현황_20210913.csv", encoding='euc-kr')
merged_df = pd.merge(left=df_base, right=df_munkyung, left_on='캠핑(야영)장명', right_on='펜션명', how='left')
merged_df = merged_df.drop(['연번', '펜션명', '도로명 주소', '지번 주소'], axis=1)
merged_df.to_csv("csv/한국관광공사 전국 야영장 등록 현황.csv")

#### 포항 #####
df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='utf-8')
df_pohang = pd.read_csv("csv/경상북도 포항시_관광숙박업_20210910.csv", encoding='euc-kr')
merged_df = pd.merge(left=df_base, right=df_pohang, left_on='캠핑(야영)장명', right_on='숙소명', how='left')
merged_df = merged_df.drop(['업종', '숙소명'], axis=1)
merged_df.to_csv("csv/한국관광공사 전국 야영장 등록 현황.csv")

#### 영천 #####
df_base = pd.read_csv("csv/한국관광공사 전국 야영장 등록 현황.csv", encoding='utf-8')
df_youngchun = pd.read_csv("csv/경상북도 영천시_캠핑장 현황_20230306.csv", encoding='euc-kr')
merged_df = pd.merge(left=df_base, right=df_youngchun, left_on='캠핑(야영)장명', right_on='상호', how='left')
merged_df = merged_df.drop(['연번', '상호', '주소'], axis=1)
merged_df = merged_df.drop(['Unnamed: 0', 'Unnamed: 0.2', 'Unnamed: 0.1', 'Unnamed: 0.3'], axis=1)
merged_df.to_csv("csv/한국관광공사 전국 야영장 등록 현황.csv")
