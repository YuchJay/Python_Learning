import requests

# Execute an API call and store the response
url = "https://api.github.com/search/repositories?q=language:python&sort=stars"
headers = {'Accept': 'application/vnd.github.v3+json'}
r = requests.get(url, headers=headers)
print(f"Status code: {r.status_code}") # 状态码200表示请求成功

response_dict = r.json()
print(f"Total repositories: {response_dict['total_count']}")

# Search for information about repositories
repo_dicts = response_dict['items']
print(f"Repositories returned: {len(repo_dicts)}")

print("\nSelected information about each repository:")
for repo_dict in repo_dicts:
    print(f"\nName: {repo_dict['name']}")
    print(f"Owner: {repo_dict['owner']['login']}")
    print(f"Stars: {repo_dict['stargazers_count']}")
    print(f"Repository URL: {repo_dict['html_url']}")
    print(f"Description: {repo_dict['description']}")
