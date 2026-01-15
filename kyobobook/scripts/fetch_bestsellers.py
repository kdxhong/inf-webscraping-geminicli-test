import sys
import os
import time
import requests
import pandas as pd
from datetime import datetime
from loguru import logger

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 로깅 설정
LOG_DIR = os.path.join(os.path.dirname(__file__), '../logs')
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(os.path.join(LOG_DIR, "scraping.log"), rotation="10 MB", level="INFO")

def fetch_kyobo_bestsellers_api():
    """교보문고 베스트셀러 API를 호출하여 데이터 수집"""
    
    base_url = "https://store.kyobobook.co.kr/api/gw/best/best-seller/online"
    
    headers = {
        "referer": "https://store.kyobobook.co.kr/bestseller/online/daily?page=1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }
    
    all_books = []
    
    # 1페이지부터 10페이지까지 수집 (총 500권)
    for page in range(1, 11):
        params = {
            "page": page,
            "per": 50,
            "period": "001",
            "dsplDvsnCode": "000",
            "dsplTrgtDvsnCode": "001"
        }
        
        logger.info(f"Fetching page {page}...")
        
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page {page}: Status {response.status_code}")
                continue
                
            data = response.json()
            
            # 데이터 구조 확인 (첫 페이지 첫 아이템만 로그로 확인)
            if page == 1 and data.get('data') and data['data'].get('bestSeller'):
                 logger.info(f"Sample Item Keys: {data['data']['bestSeller'][0].keys()}")

            if 'data' in data and 'bestSeller' in data['data']:
                books = data['data']['bestSeller']
                for book in books:
                    # 필요한 필드 추출
                    # API 응답 필드명은 추정 및 일반적인 이름 사용. 실제 응답에 따라 조정 필요할 수 있음.
                    # 보통: cmtdName(상품명), chrcName(저자), pbcmName(출판사), price(가격), salePrice(판매가)
                    
                    item = {
                        "rank": book.get('prstRnkn'), # 순위 (prstRnkn 사용)
                        "title": book.get('cmdtName'),
                        "author": book.get('chrcName'),
                        "publisher": book.get('pbcmName'),
                        "pub_date": book.get('rlseDate'),
                        "price": book.get('price'),      # 정가
                        "sale_price": book.get('sapr'),  # 할인가
                        "review_score": book.get('buyRevwRvgr'), # 리뷰 점수
                        "review_count": book.get('buyRevwNumc'), # 리뷰 개수
                        "category": book.get('saleCmdtClstName'), # 카테고리
                        "link_url": f"https://product.kyobobook.co.kr/detail/{book.get('cmdtCode')}",
                        "crawled_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    all_books.append(item)
                
                logger.info(f"Page {page}: {len(books)} items collected.")
            else:
                logger.warning(f"Page {page}: No 'bestSeller' data found.")
                
            # 예절: 요청 간 지연
            time.sleep(1.5)
            
        except Exception as e:
            logger.error(f"Error fetching page {page}: {e}")
            time.sleep(3) # 에러 시 좀 더 대기

    return all_books

def save_data(data):
    if not data:
        logger.warning("No data collected to save.")
        return

    df = pd.DataFrame(data)
    
    # 저장 경로 설정
    today_str = datetime.now().strftime("%Y%m%d")
    output_dir = os.path.join(os.path.dirname(__file__), '../data/raw')
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"kyobo_bestseller_api_{today_str}.csv"
    output_path = os.path.join(output_dir, filename)
    
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"Data saved to {output_path}")
    print(f"✅ 수집 완료: 총 {len(df)}건 저장됨 -> {output_path}")
    
    # 데이터 샘플 출력
    print("\n[Data Sample]")
    print(df[['rank', 'title', 'author', 'sale_price']].head().to_string())

if __name__ == "__main__":
    logger.info("Starting Kyobo Bestseller Scraping (API Method)")
    data = fetch_kyobo_bestsellers_api()
    save_data(data)