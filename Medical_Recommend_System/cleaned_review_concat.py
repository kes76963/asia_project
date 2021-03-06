import pandas as pd

# #중복 제거
# df_dup = pd.read_csv('./crawling/cleaned_review_2020.csv', index_col=0)
# print(df_dup.duplicated().sum())
# df_undup = df_dup.drop_duplicates()
# print(df_undup.duplicated().sum())
# df_undup.to_csv('./crawling/cleaned_review_2020.csv')
# exit()

df = pd.read_csv('./cleaned_review_치과.csv', index_col=0)
print(df.info())
df.drop_duplicates()
df.dropna(inplace=True)
print(df.info())

titles = ['치과', '피부과', '성형외과', '안과', '산부인과', '비뇨기과', '정신건강의학과', '정형외과', '마취통증의학과',
              '신경외과', '재활의학과', '영상의학과', '외과', '신경과', '소아과', '내과', '이비인후과', '가정의학과', '한의원']

df.columns = ['names', 'cleaned_sentences']
df['title'] = '치과'
df.to_csv('./cleaned_review_2_치과.csv')

for i in range(1, 19):
    df_temp = pd.read_csv(f'./cleaned_review_{titles[i]}.csv', index_col=0)
    df.drop_duplicates()
    df_temp.dropna(inplace=True)
    df_temp.columns = ['names', 'cleaned_sentences']
    df_temp.to_csv(f'./cleaned_review_2_{titles[i]}.csv', encoding='utf-8-sig')
    df_temp['title'] = titles[i]
    df = pd.concat([df, df_temp], ignore_index=True)
df = df[['title', 'names','cleaned_sentences']]
print(df.info())
df.to_csv('./total_cleaned_review.csv', encoding='utf-8-sig')