import requests

url = "https://www.sportmaster.ru/upload/mdm/media_content/05e/175336730299.jpg"

session = requests.Session()
session.trust_env = False

response = session.get(
    url,
    timeout=30,
    headers={
        "User-Agent": "curl/8.18.0",
        "Accept": "*/*",
    }
)

print("Status:", response.status_code)
print("Server:", response.headers.get("Server"))
print("Content-Type:", response.headers.get("Content-Type"))
print("Size:", len(response.content))
print("Final URL:", response.url)