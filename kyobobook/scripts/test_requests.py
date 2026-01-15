import requests
from bs4 import BeautifulSoup

urls = [
    "https://store.kyobobook.co.kr/bestseller/total/daily",
    "https://product.kyobobook.co.kr/bestseller/total/daily",
    "https://store.kyobobook.co.kr/bestseller/best/daily",
    "https://product.kyobobook.co.kr/bestseller/daily",
    "https://store.kyobobook.co.kr/bestseller/online/daily"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://store.kyobobook.co.kr/"
}

for url in urls:
    try:
        print(f"Testing URL: {url}")
        response = requests.get(url, headers=headers, timeout=5)
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            if "홈으로 돌아가서" in response.text:
                print("  -> Error Page (Soft 404)")
            else:
                print("  -> SUCCESS! This seems to be the correct URL.")
                soup = BeautifulSoup(response.text, 'html.parser')
                print(f"  -> Title: {soup.title.text.strip() if soup.title else 'No Title'}")
                items = soup.select("li.prod_item")
                print(f"  -> Items: {len(items)}")
                break
    except Exception as e:
        print(f"  -> Error: {e}")

