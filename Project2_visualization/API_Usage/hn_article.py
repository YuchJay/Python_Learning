import requests
import json

# hacker-news.firebaseio.com 在当前网络环境下被拦截（返回401），
# 改用 Hacker News 官方的 Algolia 搜索 API（同一数据源，公开免费）
url = "https://hn.algolia.com/api/v1/items/19155826"
r = requests.get(url)
print(f"Status code: {r.status_code}") # 状态码200表示请求成功

# explore structure of the data
response_dict = r.json()
readable_file = 'API_Usage/readable_hn_data.json'
with open(readable_file, 'w') as f:
    json.dump(response_dict, f, indent=4) # 将数据写入文件，并格式化缩进为4个空格
