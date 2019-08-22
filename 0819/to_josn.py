import json
import sys
import pandas as pd
from pandas.io.json import json_normalize
count = 0
path = "C:\\Users\\Wade\\Downloads\\dblp.v11\\dblp_papers_v11.txt"
# 每n筆存一個檔
n = 100000
# 開始存檔的位置
start_from = 0
result = []
i = 1
# 讀取原始dataset
with open(path, 'r') as f:
    # 根據 \n分批讀取，避免ram大爆炸 (全部一次讀入加上轉成json需要大概 45G RAM)
    for count, line in enumerate(f):
        lines = json.loads(line)
        result.append(lines)
        if (count+1) % n ==0 and count >= start_from:
            # 決定想要轉幾筆資料存到json檔
            # if count >= n:
            # with open('./data_' + str(n)+'.json', 'w', encoding='utf-8') as f2:
            #     json.dump(result, f2, indent=4)
            # df = json_normalize(result)
            df = pd.DataFrame.from_records(result)
            df.to_csv('./paper_csv/dblp_papers_' + str(i*n+start_from) +'.csv', index=False, encoding='utf_8_sig') 
            result = []
            del df
            i +=1
            # break
