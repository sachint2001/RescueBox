import requests

response = requests.post("http://localhost:8000/manage/list_plugins?streaming=True")

for chunk in response.iter_content(chunk_size=8192):
    print(chunk)
