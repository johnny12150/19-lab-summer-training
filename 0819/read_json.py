import pandas as pd
import json
from pandas.io.json import json_normalize

df = pd.read_json('./data_100000.json')
print("RAM用量: "+ str(df.memory_usage(index=True).sum()))
print(df.info())

# data_str = open('data_100000.json', "r",encoding="utf-8").read()
# data_list = json.loads(data_str)
# df2 = json_normalize(data_list)
# print(df2.info())