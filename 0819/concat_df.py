import pandas as pd
from glob import glob

# 列出有哪些檔案要concat
print(len(glob('./paper_csv/dblp_papers_*00000.csv')))

df_list = []

for i, csv_path in enumerate(glob('./paper_csv/dblp_papers_*00000.csv')):
    df = pd.read_csv(csv_path)
    df.drop(['indexed_abstract', 'page_end', 'page_start'], axis=1, inplace=True)
    df_list.append(df)
    del df

all_df = pd.concat(df_list)
print(all_df.info())
# all_df.to_csv('./concat_df/dblp_papers_4100000.csv', index=False, encoding='utf_8_sig')
# to pikle
all_df.to_pickle("./concat_df/dblp_papers_4100000.pkl")