import requests

response = requests.post("http://localhost:5000/v1/chat", data="test")
print(response)
