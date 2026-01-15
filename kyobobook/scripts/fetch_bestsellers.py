import sys
import os
import time
from datetime import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from loguru import logger

# 프로젝트 루트 경로를 sys.path에 추가 (모듈 임포트 등을 위해)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 로깅 설정
LOG_DIR = os.path.join(os.path.dirname(__file__), '../logs')
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(os.path.join(LOG_DIR, "scraping.log"), rotation="10 MB", level="INFO")

def setup_driver():
    """Selenium WebDriver 설정 (Headless 모드)"""
    chrome_options = Options()
    # 최신 Headless 모드 사용 (탐지 회피에 유리)
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    return driver

def parse_book_item(item, rank):
    """개별 도서 요소에서 정보 추출"""
    try:
        # 제목: prod_link이면서 line-clamp-2 클래스를 가진 요소
        # <a class="prod_link line-clamp-2 ...">제목</a> 형태 추정
        title_tag = item.select_one(".prod_link.line-clamp-2")
        title = title_tag.text.strip() if title_tag else "N/A"
        
        # 링크
        link = title_tag['href'] if title_tag and title_tag.has_attr('href') else "N/A"

        # 저자 및 출판사
        # 구조가 불명확하므로 텍스트 뭉치에서 추출하거나, 특정 클래스 시도
        # 교보문고 구버전 클래스인 .prod_author가 남아있을 수도 있고, 없을 수도 있음.
        # 보통 제목 아래에 저자/출판사 정보가 있음.
        
        # 저자 정보가 들어있는 태그 찾기 (상대적 위치나 텍스트로 찾기 어려움)
        # 일단 전체 텍스트에서 파싱하거나, N/A로 둠.
        # 하지만 li 내부의 텍스트를 다 긁어서 분석하는 게 나을 수도 있음.
        
        # 임시: author, publisher는 공란 또는 단순 텍스트 추출 시도
        # " · " 로 구분된 텍스트를 찾는 방식 시도
        text_content = item.get_text(" ", strip=True)
        # 예: "홍길동 저 · 출판사 · 2024.01.01" 패턴이 있다면 정규식으로 추출 가능
        
        author = "N/A"
        publisher = "N/A"
        
        # 가격: "원"으로 끝나는 텍스트 중 숫자와 콤마만 있는 것
        price = "0"
        # item 내부의 모든 span/div 텍스트 중 가격 패턴 찾기
        import re
        price_match = re.search(r'([\d,]+)원', text_content)
        if price_match:
            price = price_match.group(1).replace(",", "")

        return {
            "rank": rank,
            "title": title,
            "author": author, # 현재 정확한 셀렉터 모름
            "publisher": publisher, # 현재 정확한 셀렉터 모름
            "price": price,
            "link": link,
            "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Error parsing item rank {rank}: {e}")
        return None

def fetch_kyobo_bestsellers():
    # URL 수정: bestseller/online/daily
    url = "https://store.kyobobook.co.kr/bestseller/online/daily"
    logger.info(f"Start scraping: {url}")
    
    driver = setup_driver()
    data = []

    try:
        driver.get(url)
        time.sleep(10) # 넉넉히 대기
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Tailwind Grid OL 찾기
        # class="grid border-t border-gray-400 grid-cols-1 pt-9" 등
        # 가장 확실한 건 ol 태그 중 grid-cols-1 클래스를 가진 것
        ol_list = soup.select("ol.grid-cols-1")
        items = []
        if ol_list:
            # 보통 첫 번째나 두 번째 ol이 리스트임. 
            # 아이템이 많은 것을 선택
            for ol in ol_list:
                lis = ol.find_all("li", recursive=False)
                if len(lis) > 5: # 베스트셀러라면 적어도 5개 이상
                    items = lis
                    break
        
        if not items:
            logger.warning("No items found using 'ol.grid-cols-1 > li'. Saving page source.")
            debug_path = os.path.join(os.path.dirname(__file__), '../logs/debug_kyobo.html')
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info(f"Saved page source to {debug_path}")
            
        logger.info(f"Found {len(items)} items.")

        for i, item in enumerate(items, 1):
            book_info = parse_book_item(item, i)
            if book_info:
                data.append(book_info)
                
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
    finally:
        driver.quit()
        logger.info("Driver closed.")
    
    return data

def save_data(data):
    if not data:
        logger.warning("No data to save.")
        return

    df = pd.DataFrame(data)
    
    # 저장 경로 설정
    today_str = datetime.now().strftime("%Y%m%d")
    output_dir = os.path.join(os.path.dirname(__file__), '../data/raw')
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"kyobo_bestseller_{today_str}.csv"
    output_path = os.path.join(output_dir, filename)
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"Data saved to {output_path}")
    print(f"✅ 수집 완료: {len(df)}건 저장됨 -> {output_path}")

if __name__ == "__main__":
    bestseller_data = fetch_kyobo_bestsellers()
    save_data(bestseller_data)
