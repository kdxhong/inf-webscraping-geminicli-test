import requests # HTTP 요청을 보내기 위한 라이브러리 임포트
from bs4 import BeautifulSoup # HTML 파싱을 위한 BeautifulSoup 라이브러리 임포트
import pandas as pd # 데이터 분석 및 처리를 위한 pandas 라이브러리 임포트
import time # 시간 지연을 위한 time 라이브러리 임포트
import random # 무작위 지연 시간을 생성하기 위한 random 라이브러리 임포트
from loguru import logger # 로그 기록을 위한 loguru 라이브러리 임포트
import os # 운영체제 및 파일 경로 조작을 위한 os 라이브러리 임포트

# 설정
BASE_URL = "https://www.yes24.com/product/category/CategoryProductContents" # 예스24의 카테고리별 상품 목록 데이터를 가져올 기본 URL 주소
DISP_NO = "001001003032" # 수집 대상 카테고리 번호 (에세이 등 특정 카테고리 식별자)
PAGE_START = 1 # 수집을 시작할 페이지 번호
PAGE_END = 10 # 수집을 종료할 마지막 페이지 번호
PAGE_SIZE = 120 # 한 페이지당 수집할 도서 수
OUTPUT_DIR = "yes24/data/raw" # 결과물을 저장할 폴더 경로
OUTPUT_FILE = "yes24_books.csv" # 결과물을 저장할 파일명

# 헤더 설정
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", # 봇 차단을 방지하기 위한 실제 브라우저 형태의 유저 에이전트 정보
    "Referer": "https://www.yes24.com/product/category/display/001001003032", # 요청 시의 이전 페이지 정보를 포함하는 레퍼러 헤더
    "X-Requested-With": "XMLHttpRequest" # AJAX 요청임을 서버에 알리는 헤더
}

# 로깅 설정
logger.add("yes24/logs/scraper.log", rotation="10 MB") # 로그 정보를 파일에 기록하며, 10MB 크기가 넘으면 새 로그 파일을 생성하도록 설정

def get_page_data(page):
    """지정된 페이지의 HTML 데이터를 가져오는 함수"""
    params = {
        "dispNo": DISP_NO, # 카테고리 번호 매개변수 설정
        "order": "SINDEX_ONLY", # 정렬 기준 매개변수 설정
        "addOptionTp": "0", # 추가 옵션 타입 매개변수 설정
        "page": page, # 요청할 페이지 번호 매개변수 설정
        "size": PAGE_SIZE, # 한 번에 가져올 상품 수 매개변수 설정
        "statGbYn": "N", # 통계 구분 여부 매개변수 설정
        "viewMode": "", # 뷰 모드 매개변수 설정
        "_options": "", # 기타 옵션 매개변수 설정
        "directDelvYn": "", # 직배송 여부 매개변수 설정
        "usedTp": "0", # 중고 타입 매개변수 설정
        "elemNo": "0", # 요소 번호 매개변수 설정
        "elemSeq": "0", # 요소 순번 매개변수 설정
        "seriesNumber": "0" # 시리즈 번호 매개변수 설정
    }
    
    try:
        response = requests.get(BASE_URL, params=params, headers=HEADERS) # 설정된 주소, 파라미터, 헤더를 사용하여 GET 방식 요청을 보냄
        response.raise_for_status() # HTTP 응답 상태 코드가 정상이 아닐 경우 예외 발생
        return response.text # 응답 받은 HTML 문서 텍스트를 반환
    except requests.RequestException as e:
        logger.error(f"페이지 {page} 요청 중 오류 발생: {e}") # 요청 중 오류 발생 시 로그에 에러 내용 기록
        return None # 오류 발생 시 None 반환

def parse_html(html):
    """HTML 소스에서 도서 정보를 추출하는 함수"""
    soup = BeautifulSoup(html, 'html.parser') # BeautifulSoup을 이용해 HTML 텍스트를 파싱 가능한 객체로 변환
    items = soup.select('div.itemUnit') # 개별 도서 정보가 들어있는 div 요소들을 선택
    data = [] # 추출된 데이터를 저장할 빈 리스트
    
    for item in items: # 각 도서 요소에 대해 반복 수행
        try:
            # 도서명
            title_tag = item.select_one('a.gd_name') # 도서명이 포함된 태그 선택
            title = title_tag.text.strip() if title_tag else "" # 도서명 텍스트 추출 및 앞뒤 공백 제거
            link = "https://www.yes24.com" + title_tag['href'] if title_tag else "" # 도서 상세 페이지로 연결되는 전체 URL 생성
            
            # 저자
            author_tag = item.select_one('span.authPub.info_auth') # 저자 정보가 포함된 태그 선택
            author = author_tag.text.strip().replace(" 저", "") if author_tag else "" # 저자 텍스트 추출 및 불필요한 단어 제거
            
            # 출판사
            pub_tag = item.select_one('span.authPub.info_pub') # 출판사 정보가 포함된 태그 선택
            publisher = pub_tag.text.strip() if pub_tag else "" # 출판사 이름 텍스트 추출
            
            # 출판일
            date_tag = item.select_one('span.authPub.info_date') # 출판일 정보가 포함된 태그 선택
            pub_date = date_tag.text.strip() if date_tag else "" # 출판일 텍스트 추출
            
            # 가격
            price_tag = item.select_one('strong.txt_num > em.yes_b') # 가격 정보가 포함된 태그 선택
            price = price_tag.text.strip().replace(",", "") if price_tag else "0" # 쉼표를 제거한 숫자 형태의 가격 추출
            
            # 별점
            rating_tag = item.select_one('span.rating_grade > em.yes_b') # 별점 정보가 포함된 태그 선택
            rating = rating_tag.text.strip() if rating_tag else "0.0" # 별점 텍스트 추출
            
            # 리뷰 수
            review_tag = item.select_one('span.rating_rvCount em.txC_blue') # 리뷰 개수 정보가 포함된 태그 선택
            review_count = review_tag.text.strip() if review_tag else "0" # 리뷰 수 텍스트 추출
            
            data.append({ # 수집된 개별 도서 정보를 딕셔너리 형태로 리스트에 추가
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
            logger.warning(f"항목 파싱 중 오류 발생: {e}") # 특정 도서 파싱 중 오류 발생 시 경고 로그 기록
            continue # 오류가 발생한 도서는 건너뛰고 다음 도서 진행
            
    return data # 해당 페이지에서 수집 완료된 전체 도서 데이터 반환

def main():
    """스크래퍼를 실행하는 메인 함수"""
    if not os.path.exists(OUTPUT_DIR): # 데이터를 저장할 폴더가 존재하는지 확인
        os.makedirs(OUTPUT_DIR) # 폴더가 존재하지 않으면 새로 생성
        
    all_books = [] # 모든 페이지에서 수집한 도서 데이터를 통합 저장할 리스트
    
    logger.info("데이터 수집 시작") # 데이터 수집 작업 시작을 알리는 로그 기록
    
    for page in range(PAGE_START, PAGE_END + 1): # 시작 페이지부터 종료 페이지까지 반복
        logger.info(f"페이지 {page}/{PAGE_END} 수집 중...") # 현재 처리 중인 페이지 정보 로그 기록
        
        html = get_page_data(page) # 해당 페이지의 HTML 데이터를 가져옴
        if html: # HTML 데이터를 성공적으로 가져왔을 경우
            books = parse_html(html) # 가져온 HTML에서 도서 정보 파싱
            all_books.extend(books) # 수집된 리스트를 전체 도서 리스트에 추가
            logger.info(f"페이지 {page}: {len(books)}개 도서 수집 완료") # 해당 페이지 수집 성공 로그 기록
        
        # 딜레이
        time.sleep(random.uniform(1, 2)) # 서버 부하 방지를 위해 1초에서 2초 사이의 임의의 시간 동안 대기
        
    # 데이터프레임 변환 및 저장
    if all_books: # 수집된 전체 데이터가 존재할 경우
        df = pd.DataFrame(all_books) # 수집된 리스트를 pandas 데이터프레임 구조로 변환
        save_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE) # 저장할 파일의 전체 경로 생성
        df.to_csv(save_path, index=False, encoding='utf-8-sig') # 데이터프레임을 CSV 파일로 저장 (한글 깨짐 방지를 위해 utf-8-sig 인코딩 사용)
        logger.info(f"총 {len(df)}개 데이터 수집 완료. 저장 경로: {save_path}") # 최종 수집 완료 정보 로그 기록
        print(df.head()) # 수집된 데이터 중 상위 5개를 화면에 출력하여 확인
    else:
        logger.warning("수집된 데이터가 없습니다.") # 수집된 데이터가 하나도 없을 경우 경고 로그 기록

if __name__ == "__main__": # 스크립트가 직접 실행되는 경우에만 아래 블록 실행
    main() # main 함수 호출하여 프로그램 실행