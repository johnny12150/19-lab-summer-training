import json
count = 0
n = 10
result = []
# 讀取原始dataset
with open("C:\\Users\\Wade\\Downloads\\dblp.v11\\dblp_papers_v11.txt", 'r') as f:
    # 根據 \n分批讀取，避免ram大爆炸 (全部一次讀入加上轉成json需要大概 45G RAM)
    for line in f:
        count += 1
        lines = json.loads(line)
        result.append(lines)
        # 決定想要轉幾筆資料存到json檔
        if n >= 10:
            with open('./data.json', 'w', encoding='utf-8') as f2:
                json.dump(result, f2, ensure_ascii=False, indent=4)
            break
