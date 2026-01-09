# YES24 데이터 수집 명세서

## 1. 프로젝트 개요

- **목표**: YES24 사이트에서 도서 정보를 수집하고 분석함.
- **대상**: 베스트셀러 또는 특정 카테고리 도서 목록.

## 2. 수집 관련 정보

### 네트워크 메뉴를 통해 실제 데이터를 가져오는 URL

### 해당 Request에 대한 Header 정보

### Payload

### 응답 예시 (HTML, JSON 의 일부 정보)

## 3. 수집 데이터 항목 (Data Schema)

- [ ] 도서명 (Title)
- [ ] 저자 (Author)
- [ ] 출판사 (Publisher)
- [ ] 출판일 (Publish Date)
- [ ] 가격 (Price)
- [ ] 별점 (Rating)
- [ ] 리뷰 수 (Review Count)
- [ ] 상세 페이지 링크 (Detail URL)

## 4. 기술 스택

- **언어**: Python
- **라이브러리**: `requests`, `BeautifulSoup4`, `loguru`, `pandas`
- **시각화**: `matplotlib`, `koreanize-matplotlib`

## 5. 수집 정책

- **지연 시간**: 요청 간 1~2초의 딜레이 설정 (Robots.txt 준수)
- **저장 경로**: `yes24/data/raw/` 폴더 내 CSV 또는 JSON 형식으로 저장
- **로깅**: `loguru`를 활용하여 수집 성공 및 실패 기록

## 6. 향후 계획

- 데이터 전처리 및 EDA 진행
- 분야별 베스트셀러 트렌드 분석
