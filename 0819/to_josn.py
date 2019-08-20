import json
count = 0
path = "C:\\Users\\Wade\\Downloads\\dblp.v11\\dblp_papers_v11.txt"
n = 100000
result = []
# 讀取原始dataset
with open(path, 'r') as f:
    # 根據 \n分批讀取，避免ram大爆炸 (全部一次讀入加上轉成json需要大概 45G RAM)
    for line in f:
        count += 1
        lines = json.loads(line)
        result.append(lines)
        # 決定想要轉幾筆資料存到json檔
        if count >= n:
            with open('./data_' + str(n)+'.json', 'w', encoding='utf-8') as f2:
                json.dump(result, f2, indent=4)
            break
