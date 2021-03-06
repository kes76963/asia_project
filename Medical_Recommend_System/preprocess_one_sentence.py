import pandas as pd

df = pd.read_csv('./total_cleaned_review.csv', index_col=0)
df.dropna(inplace=True)
print(len(df['names'].unique()))
one_sentences = []
titles = []
for name in df['names'].unique():
    title = df[df['names']==name].iloc[0,0]
    temp = df[df['names']==name]['cleaned_sentences']
    one_sentence = ' '.join(temp)       # 여러개 리뷰 한 문장으로 이어붙이기
    one_sentences.append(one_sentence)      # 병원별 리뷰 리스트에 넣기
    titles.append(title)
df_one_sentences = pd.DataFrame({'names':df['names'].unique(), 'reviews':one_sentences, 'titles':titles})
df_one_sentences = df_one_sentences[['titles', 'names','reviews']]

print(df_one_sentences.head())
print(df_one_sentences.info())
df_one_sentences.to_csv('./total_hospital_review_one_sentence.csv', encoding='utf-8-sig')