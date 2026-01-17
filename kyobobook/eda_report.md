# 데이터 탐색적 분석 (EDA) 리포트
**분석 일시**: 2026-01-17 23:22:58.922734
**대상 파일**: kyobobook/data/raw/kyobo_bestseller_api_20260117.csv

## 1. 데이터 불러오기
데이터 로드 완료. 인코딩 및 파싱 성공.

## 2. 데이터 개요
- **행 수**: 500
- **열 수**: 12

### 컬럼 정보
| 컬럼명 | 데이터 타입 | 결측치 수 | 고유값 수 |
|---|---|---|---|
| rank | int64 | 0 | 500 |
| title | object | 0 | 486 |
| author | object | 1 | 381 |
| publisher | object | 2 | 251 |
| pub_date | float64 | 1 | 288 |
| price | int64 | 0 | 100 |
| sale_price | int64 | 0 | 116 |
| review_score | float64 | 0 | 85 |
| review_count | int64 | 0 | 267 |
| category | object | 19 | 31 |
| link_url | object | 0 | 488 |
| crawled_at | object | 0 | 10 |

- **중복 행 개수**: 0
## 3. 기술통계 요약
### 수치형 변수 통계
|              |            mean |         std |            min |             25% |             50% |             75% |             max |
|:-------------|----------------:|------------:|---------------:|----------------:|----------------:|----------------:|----------------:|
| rank         |   251.388       |   144.655   |    1           |   126.75        |   251.5         |   376.25        |   501           |
| pub_date     |     2.02382e+07 | 35456.9     |    2.00201e+07 |     2.02408e+07 |     2.02509e+07 |     2.02512e+07 |     2.02602e+07 |
| price        | 20763           |  8926.61    | 3000           | 16800           | 19000           | 23000           | 95000           |
| sale_price   | 18754.6         |  8125.31    | 2700           | 15120           | 17100           | 20565           | 85500           |
| review_score |     9.03114     |     2.56922 |    0           |     9.58        |     9.785       |     9.94        |    10           |
| review_count |   252.062       |   510.895   |    0           |    12.75        |    65           |   233.5         |  4371           |

### 범주형 변수 통계 (Top 5)
#### title
|                               |   Count |
|:------------------------------|--------:|
| 텐배거 포트폴리오             |       2 |
| 절창                          |       2 |
| 요리를 한다는 것              |       2 |
| 다크 심리학: 심리 조종의 기술 |       2 |
| 프롬프트 텔링                 |       2 |

#### author
|                         |   Count |
|:------------------------|--------:|
| 해커스 공무원시험연구소 |      11 |
| David Cho 외            |       8 |
| ETS                     |       8 |
| 신민숙                  |       7 |
| 해커스 어학연구소       |       7 |

#### publisher
|                  |   Count |
|:-----------------|--------:|
| 해커스어학연구소 |      27 |
| 해커스공무원     |      21 |
| 민음사           |      18 |
| 문학동네         |      11 |
| YBM              |       8 |

#### category
|             |   Count |
|:------------|--------:|
| 취업/수험서 |      61 |
| 소설        |      57 |
| 외국어      |      56 |
| 인문        |      55 |
| 경제/경영   |      52 |

#### link_url
|                                                      |   Count |
|:-----------------------------------------------------|--------:|
| https://product.kyobobook.co.kr/detail/9791141602376 |       2 |
| https://product.kyobobook.co.kr/detail/9791193262757 |       2 |
| https://product.kyobobook.co.kr/detail/9788937473401 |       2 |
| https://product.kyobobook.co.kr/detail/9791193282533 |       2 |
| https://product.kyobobook.co.kr/detail/9791169851763 |       2 |

#### crawled_at
|                     |   Count |
|:--------------------|--------:|
| 2026-01-17 22:57:54 |      50 |
| 2026-01-17 22:58:00 |      50 |
| 2026-01-17 22:58:07 |      50 |
| 2026-01-17 22:58:14 |      50 |
| 2026-01-17 22:58:20 |      50 |

## 4. 결측치 및 이상치 분석
### 결측치 시각화
![Missing Values](eda_images/missing_values.png)

### 이상치 탐지 (Boxplot)
#### rank
![Outlier rank](eda_images/outlier_rank.png)

#### pub_date
![Outlier pub_date](eda_images/outlier_pub_date.png)

#### price
![Outlier price](eda_images/outlier_price.png)

#### sale_price
![Outlier sale_price](eda_images/outlier_sale_price.png)

#### review_score
![Outlier review_score](eda_images/outlier_review_score.png)

#### review_count
![Outlier review_count](eda_images/outlier_review_count.png)

## 5. 변수 간 관계 분석
### 상관관계 히트맵
![Correlation Heatmap](eda_images/correlation_heatmap.png)

### crawled_at - rank 관계
![Relation](eda_images/relation_crawled_at_rank.png)

## 6. 데이터 분포 시각화
### rank 분포
![Distribution rank](eda_images/dist_rank.png)

### pub_date 분포
![Distribution pub_date](eda_images/dist_pub_date.png)

### price 분포
![Distribution price](eda_images/dist_price.png)

### sale_price 분포
![Distribution sale_price](eda_images/dist_sale_price.png)

### review_score 분포
![Distribution review_score](eda_images/dist_review_score.png)

### review_count 분포
![Distribution review_count](eda_images/dist_review_count.png)

## 7. 주요 인사이트
- 데이터의 전반적인 구조와 통계량을 확인하였습니다.
- 결측치와 이상치를 시각화를 통해 파악할 수 있었습니다.
- 변수 간의 상관관계를 통해 데이터 내의 잠재적인 패턴을 유추해볼 수 있습니다.
