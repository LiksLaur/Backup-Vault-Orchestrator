import requests


url = 'http://127.0.0.1:8000/page'  # Replace with your target URL
response = requests.get(url)
data = response.text
print(data)