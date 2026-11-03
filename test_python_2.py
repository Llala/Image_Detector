import requests

url = "https://www.sportmaster.ru/upload/mdm/media_content/05e/175336730299.jpg"

session = requests.Session()
session.trust_env = False

try:
    response = session.get(url, timeout=15)
    response.raise_for_status()

    print("HTTP:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Size:", len(response.content))

except requests.RequestException as e:
    print(type(e).__name__, str(e))