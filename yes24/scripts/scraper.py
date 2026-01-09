import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from loguru import logger
import os

# 설정
BASE_URL = "https://www.yes24.com/product/category/CategoryProductContents"
DISP_NO = "001001003032" # 에세이? 카테고리 (명세서 기준)
PAGE_START = 1
PAGE_END = 10
PAGE_SIZE = 120
OUTPUT_DIR = "yes24/data/raw"
OUTPUT_FILE = "yes24_books.csv"

# 헤더 설정
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.yes24.com/product/category/display/001001003032",
    "X-Requested-With": "XMLHttpRequest"
}

# 로깅 설정
logger.add("yes24/logs/scraper.log", rotation="10 MB")

def get_page_data(page):
    params = {
        "dispNo": DISP_NO,
        "order": "SINDEX_ONLY",
        "addOptionTp": "0",
        "page": page,
        "size": PAGE_SIZE,
        "statGbYn": "N",
        "viewMode": "",
        "_options": "",
        "directDelvYn": "",
        "usedTp": "0",
        "elemNo": "0",
        "elemSeq": "0",
        "seriesNumber": "0"
    }
    
    try:
        response = requests.get(BASE_URL, params=params, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"페이지 {page} 요청 중 오류 발생: {e}")
        return None

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('div.itemUnit')
    data = []
    
    for item in items:
        try:
            # 도서명
            title_tag = item.select_one('a.gd_name')
            title = title_tag.text.strip() if title_tag else ""
            link = "https://www.yes24.com" + title_tag['href'] if title_tag else ""
            
            # 저자
            author_tag = item.select_one('span.authPub.info_auth')
            author = author_tag.text.strip().replace(" 저", "") if author_tag else ""
            
            # 출판사
            pub_tag = item.select_one('span.authPub.info_pub')
            publisher = pub_tag.text.strip() if pub_tag else ""
            
            # 출판일
            date_tag = item.select_one('span.authPub.info_date')
            pub_date = date_tag.text.strip() if date_tag else ""
            
            # 가격
            price_tag = item.select_one('strong.txt_num > em.yes_b')
            price = price_tag.text.strip().replace(",", "") if price_tag else "0"
            
            # 별점
            rating_tag = item.select_one('span.rating_grade > em.yes_b')
            rating = rating_tag.text.strip() if rating_tag else "0.0"
            
            # 리뷰 수
            review_tag = item.select_one('span.rating_rvCount em.txC_blue')
            review_count = review_tag.text.strip() if review_tag else "0"
            
            data.append({
                "Title": title,
                "Author": author,
                "Publisher": publisher,
                "Publish Date": pub_date,
                "Price": price,
                "Rating": rating,
                "Review Count": review_count,
                "Detail URL": link
            })
        except Exception as e:
            logger.warning(f"항목 파싱 중 오류 발생: {e}")
            continue
            
    return data

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    all_books = []
    
    logger.info("데이터 수집 시작")
    
    for page in range(PAGE_START, PAGE_END + 1):
        logger.info(f"페이지 {page}/{PAGE_END} 수집 중...")
        
        html = get_page_data(page)
        if html:
            books = parse_html(html)
            all_books.extend(books)
            logger.info(f"페이지 {page}: {len(books)}개 도서 수집 완료")
        
        # 딜레이
        time.sleep(random.uniform(1, 2))
        
    # 데이터프레임 변환 및 저장
    if all_books:
        df = pd.DataFrame(all_books)
        save_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
        df.to_csv(save_path, index=False, encoding='utf-8-sig')
        logger.info(f"총 {len(df)}개 데이터 수집 완료. 저장 경로: {save_path}")
        print(df.head()) # 일부 데이터 출력
    else:
        logger.warning("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
