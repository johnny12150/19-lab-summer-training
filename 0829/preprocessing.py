import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
from CTR_LR_keras import *
import time

df = pd.read_csv("F:/NCTU/lab/奧丁丁/奧丁丁資料前處理/OwlTing_整合資料/csv/final_data.csv")

# positive sample
df_feature = df[['user_id(phone)', 'source', 'night_amount', 'latitude', 'longitude']].copy()
df_label_pos = np.ones(len(df_feature))
df_label = np.copy(df_label_pos)

# negative sampling
# 顯示user是否住過
live = pd.crosstab(df['hotel_id'], df['user_id(phone)'])
never_live = live.astype(bool)
user_ids = never_live.columns.tolist()
# 存每個對應使用者住過的飯店id
user_hotels = []
# 存沒住過的(耗時且耗資源)
# user_new_hotels = []
for col in never_live:
    user_hotels.append(never_live.index[never_live[col]].tolist())
    # user_new_hotels.append(never_live.index[never_live[col] == False].tolist()) 

# 存沒住過的
unique_hotels = df['hotel_id'].unique()
# unique_hotels_2d = np.repeat(unique_hotels, len(user_hotels)).reshape(len(user_hotels),-1)
# 大幅加速
user_new_hotels = []
for j, user_set in enumerate(user_hotels):
    user_new_hotels.append(np.setdiff1d(unique_hotels, np.array(user_set)))

num_neg = 5
df_feature_neg_list = []
df_label_neg = np.zeros(num_neg* len(df['user_id(phone)'].unique()))
# 從每個使用者沒住過的飯店隨機取5個
for i, user in enumerate(user_ids):
    random_list = []
    # 隨機取五個沒住過的hotel_id, replace=False 避免隨機到重覆值
    random_list = np.random.choice(user_new_hotels[i], num_neg, replace=False)
    # 隨機取5筆符合條件的 (大幅加速)
    neg_hotel = df[df['hotel_id'].isin(random_list)].sample(5)
    neg_hotel['user_id(phone)'] = user
    df_feature_neg_list.extend(neg_hotel.values.tolist())

    # if len(user_hotels[i]) == 1:
        # 符合使用者與飯店的資料
        # df.loc[(df['hotel_id'] == user_hotels[i][0]) & (df['user_id(phone)'] == user)]

df_feature_neg = pd.DataFrame(columns=df.columns.tolist())
df_feature_neg = pd.DataFrame(df_feature_neg_list, columns=df.columns.tolist())
# 僅保留特定特徵
df_feature = df_feature.append(df_feature_neg[['user_id(phone)', 'source', 'night_amount', 'latitude', 'longitude']])
df_label = np.append(df_label, df_label_neg)        

# OneHot
encoder = OneHotEncoder(categories = "auto", handle_unknown = "ignore")
# train_encoded = encoder.fit_transform(df_feature['user_id(phone)'])
# TODO: 要採batch的方式，不然RAM一定爆炸
# pd.concat([df_feature, pd.DataFrame(train_encoded.todense())], axis=1)
# df_feature.drop(['user_id(phone)'], axis=1, inplace=True)

le = LabelEncoder()
df_feature['source'] = le.fit_transform(df_feature['source'])
df_feature['user_id(phone)'] = le.fit_transform(df_feature['user_id(phone)'])

# Normalize
scaler = StandardScaler()
df_feature['latitude'] = scaler.fit_transform(df_feature[['latitude']])
df_feature['longitude'] = scaler.fit_transform(df_feature[['longitude']])


# model
lr = lr_model(df_feature.shape[1])
lr.fit(df_feature, df_label, epochs=10, batch_size=300, validation_split=0.2)