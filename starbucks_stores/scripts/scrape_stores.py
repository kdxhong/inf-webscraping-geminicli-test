import requests
import pandas as pd
from loguru import logger
import os
import time

# 로그 설정
os.makedirs("starbucks_stores/logs", exist_ok=True)
logger.add("starbucks_stores/logs/scraping.log", rotation="500 MB")

def fetch_starbucks_stores():
    url = "https://www.starbucks.co.kr/store/getStore.do?r=E5EB26LQO1"
    headers = {
        "host": "www.starbucks.co.kr",
        "origin": "https://www.starbucks.co.kr",
        "referer": "https://www.starbucks.co.kr/store/store_map.do",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    
    all_stores = []
    
    # p_sido_cd=01 부터 17까지 반복
    for sido_cd in range(1, 18):
        sido_cd_str = f"{sido_cd:02d}"
        logger.info(f"시도 코드 {sido_cd_str} 수집 시작...")
        
        payload = {
            "in_biz_cds": "0",
            "in_scodes": "0",
            "ins_lat": "37.5682",
            "ins_lng": "126.9977",
            "search_text": "",
            "p_sido_cd": sido_cd_str,
            "p_gugun_cd": "",
            "isError": "true",
            "in_distance": "0",
            "in_biz_cd": "",
            "iend": "1000",
            "searchType": "C",
            "set_date": "",
            "rndCod": "M3G913EGBS",
            "all_store": "0",
            "T03": "0",
            "T01": "0",
            "T27": "0",
            "T12": "0",
            "T09": "0",
            "T30": "0",
            "T05": "0",
            "T22": "0",
            "T21": "0",
            "T36": "0",
            "T43": "0",
            "Z9999": "0",
            "T64": "0",
            "T66": "0",
            "P02": "0",
            "P10": "0",
            "P50": "0",
            "P20": "0",
            "P60": "0",
            "P30": "0",
            "P70": "0",
            "P40": "0",
            "P80": "0",
            "whcroad_yn": "0",
            "P90": "0",
            "P01": "0",
            "new_bool": "0"
        }
        
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                stores = data.get("list", [])
                all_stores.extend(stores)
                logger.info(f"시도 코드 {sido_cd_str} 수집 완료: {len(stores)}개 매장")
            else:
                logger.error(f"시도 코드 {sido_cd_str} 요청 실패: {response.status_code}")
        except Exception as e:
            logger.error(f"시도 코드 {sido_cd_str} 처리 중 오류 발생: {e}")
        
        # 서버 부하 방지를 위한 딜레이
        time.sleep(1)
        
    return all_stores

if __name__ == "__main__":
    logger.info("스타벅스 전 매장 수집 프로세스 시작")
    stores_data = fetch_starbucks_stores()
    
    if stores_data:
        df = pd.DataFrame(stores_data)
        os.makedirs("starbucks_stores/data/raw", exist_ok=True)
        file_path = "starbucks_stores/data/raw/starbucks_all_stores.csv"
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        logger.info(f"수집 완료! 총 {len(df)}개 매장 데이터가 {file_path}에 저장되었습니다.")
    else:
        logger.warning("수집된 데이터가 없습니다.")
