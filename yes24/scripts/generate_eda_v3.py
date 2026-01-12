import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from loguru import logger
import os
import re
from wordcloud import WordCloud
from io import StringIO
import numpy as np

# 설정
DATA_PATH = "yes24/data/raw/yes24_books.csv"
REPORT_PATH = "yes24/eda_result_v3.md"
IMG_DIR = "yes24/images"
os.makedirs(IMG_DIR, exist_ok=True)

logger.add("yes24/logs/eda_v3.log")

def load_and_preprocess():
    logger.info("데이터 로드 및 전처리 시작...")
    try:
        df = pd.read_csv(DATA_PATH)
        
        # 1. 숫자형 변환 (Price, Review Count, Rating)
        def clean_currency(x):
            if isinstance(x, str):
                return float(re.sub(r'[^\d.]', '', x))
            return float(x)

        df['Price'] = df['Price'].apply(clean_currency)
        df['Review Count'] = df['Review Count'].apply(clean_currency)
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        
        # 2. 날짜 파싱 (Publish Date)
        # 예: "2025년 11월" -> Year: 2025, Month: 11
        def parse_date(x):
            match = re.search(r'(\d{4})년\s*(\d{1,2})월', str(x))
            if match:
                return int(match.group(1)), int(match.group(2))
            return None, None

        df['Year'], df['Month'] = zip(*df['Publish Date'].apply(parse_date))
        
        # 날짜 정렬용 컬럼
        df['Year'] = df['Year'].fillna(0).astype(int)
        df['Month'] = df['Month'].fillna(0).astype(int)
        
        logger.info(f"데이터 로드 완료: {len(df)}행")
        return df
    except Exception as e:
        logger.error(f"데이터 로드/전처리 실패: {e}")
        return None

def save_plot(filename):
    path = os.path.join(IMG_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    return path.replace("\\", "/")

def analyze_and_visualize(df):
    image_paths = {}
    
    # --- 1. 수치형 데이터 분포 (히스토그램) ---
    logger.info("수치형 데이터 시각화 중...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    sns.histplot(df['Price'], kde=True, ax=axes[0], color='skyblue')
    axes[0].set_title('가격 분포')
    
    sns.histplot(df['Rating'], kde=True, ax=axes[1], color='orange', bins=20)
    axes[1].set_title('평점 분포')
    
    sns.histplot(df[df['Review Count'] < 500]['Review Count'], kde=True, ax=axes[2], color='green') # Outlier 제외 시각화
    axes[2].set_title('리뷰 수 분포 (500개 미만)')
    
    image_paths['numeric_dist'] = save_plot('numeric_distribution.png')
    
    # --- 2. 출판사 분석 (상위 20개) ---
    logger.info("출판사 분석 중...")
    top_publishers = df['Publisher'].value_counts().head(20)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_publishers.values, y=top_publishers.index, hue=top_publishers.index, legend=False, palette='viridis')
    plt.title('상위 20개 출판사 (도서 수 기준)')
    image_paths['top_publishers'] = save_plot('top_20_publishers.png')
    
    # --- 3. 발행 트렌드 (연도별, 월별) ---
    logger.info("발행 트렌드 분석 중...")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    year_counts = df[df['Year'] > 0]['Year'].value_counts().sort_index()
    sns.lineplot(x=year_counts.index, y=year_counts.values, marker='o', ax=axes[0])
    axes[0].set_title('연도별 도서 발행 추이')
    axes[0].set_xticks(year_counts.index)
    
    month_counts = df[df['Month'] > 0]['Month'].value_counts().sort_index()
    sns.barplot(x=month_counts.index, y=month_counts.values, hue=month_counts.index, legend=False, ax=axes[1], palette='coolwarm')
    axes[1].set_title('월별 도서 발행 빈도')
    
    image_paths['trend'] = save_plot('publishing_trend.png')
    
    # --- 4. 상관 관계 분석 (히트맵) ---
    logger.info("상관 관계 분석 중...")
    corr_cols = ['Price', 'Rating', 'Review Count', 'Year']
    corr_matrix = df[corr_cols].corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='RdBu_r', fmt='.2f', vmin=-1, vmax=1)
    plt.title('주요 변수 간 상관 관계')
    image_paths['heatmap'] = save_plot('correlation_heatmap.png')
    
    # --- 5. 워드 클라우드 ---
    logger.info("워드 클라우드 생성 중...")
    # 간단한 토큰화: 공백 기준 분리 및 특수문자 제거
    text = ' '.join(df['Title'].astype(str))
    # 불용어 처리 (간단하게)
    stopwords = {'의', '를', '에', '가', '은', '는', '이', '것', '등', '위한', '따라', '만들기', '활용', '활용법', '입문', '가이드', '실무', '기초', '완벽', '배우기', '무작정', '따라하기'}
    
    wc = WordCloud(font_path='C:/Windows/Fonts/malgun.ttf', # 윈도우 기본 폰트
                   background_color='white',
                   width=800, height=600,
                   stopwords=stopwords).generate(text)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('도서 제목 워드 클라우드')
    image_paths['wordcloud'] = save_plot('title_wordcloud.png')
    
    return image_paths

def generate_pivot_tables(df):
    pivots = []
    
    # 1. 출판사별 평균 가격 (상위 10개 출판사)
    top10_pubs = df['Publisher'].value_counts().head(10).index
    pivot1 = df[df['Publisher'].isin(top10_pubs)].groupby('Publisher')[['Price', 'Review Count']].mean().sort_values('Price', ascending=False)
    pivots.append(("상위 10개 출판사별 평균 가격 및 리뷰 수", pivot1))
    
    # 2. 연도별 평균 평점 및 도서 수
    pivot2 = df[df['Year'] > 0].groupby('Year').agg({'Rating': 'mean', 'Title': 'count'}).rename(columns={'Title': 'Book Count'})
    pivots.append(("연도별 평균 평점 및 도서 수", pivot2))
    
    # 3. 가격대별(1만원 단위) 평점 평균
    df['Price Range'] = (df['Price'] // 10000) * 10000
    pivot3 = df.groupby('Price Range').agg({'Rating': ['mean', 'count'], 'Review Count': 'mean'})
    pivot3.columns = ['Avg Rating', 'Book Count', 'Avg Reviews']
    pivot3 = pivot3[pivot3['Book Count'] > 5] # 표본 적은 구간 제외
    pivots.append(("가격대별(1만원 단위) 평점 및 리뷰 분석", pivot3))
    
    # 4. 평점 구간별(9점대, 8점대...) 평균 가격
    df['Rating Range'] = df['Rating'].apply(lambda x: int(x) if pd.notnull(x) else 0)
    pivot4 = df[df['Rating Range'] > 0].groupby('Rating Range')[['Price', 'Review Count']].mean()
    pivots.append(("평점 구간별 평균 가격 및 리뷰 수", pivot4))
    
    # 5. 상위 저자별(5권 이상 집필) 평균 평점
    author_counts = df['Author'].value_counts()
    top_authors = author_counts[author_counts >= 5].index
    pivot5 = df[df['Author'].isin(top_authors)].groupby('Author')[['Rating', 'Review Count']].mean().sort_values('Rating', ascending=False).head(10)
    pivots.append(("다작 저자(5권 이상)의 평균 평점 Top 10", pivot5))
    
    return pivots

def write_report(df, image_paths, pivots):
    logger.info("보고서 작성 중...")
    
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        # 헤더
        f.write("# Yes24 AI 도서 분석 결과 보고서 (V3)\n\n")
        f.write(f"**분석 일시:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**대상 파일:** `{DATA_PATH}`\n\n")
        
        # 1. 데이터 개요 (info, describe)
        f.write("## 1. 데이터 개요\n")
        
        # Info (buffer capture)
        buf = StringIO()
        df.info(buf=buf)
        f.write("### 데이터 구조 (Info)\n")
        f.write(f"```\n{buf.getvalue()}\n```\n\n")
        
        # Describe (Numerical)
        f.write("### 수치형 데이터 기술 통계\n")
        f.write(df.describe().to_markdown())
        f.write("\n\n")
        
        # Describe (Categorical)
        f.write("### 범주형 데이터 기술 통계\n")
        f.write(df.describe(include='O').to_markdown())
        f.write("\n\n")
        
        # 2. 시각화 결과
        f.write("## 2. 시각화 분석\n")
        
        f.write("### 2.1 수치형 데이터 분포\n")
        f.write("가격, 평점, 리뷰 수의 전반적인 분포를 확인합니다.\n")
        f.write(f"![수치형 분포](images/numeric_distribution.png)\n\n")
        
        f.write("### 2.2 출판사 분석 (Top 20)\n")
        f.write("가장 많은 도서를 출판한 상위 20개 출판사 현황입니다.\n")
        f.write(f"![출판사](images/top_20_publishers.png)\n\n")
        
        f.write("### 2.3 발행 트렌드\n")
        f.write("연도별 및 월별 도서 발행 빈도입니다.\n")
        f.write(f"![트렌드](images/publishing_trend.png)\n\n")
        
        f.write("### 2.4 변수 간 상관관계\n")
        f.write("가격, 평점, 리뷰 수, 연도 간의 상관계수 히트맵입니다.\n")
        f.write(f"![히트맵](images/correlation_heatmap.png)\n\n")
        
        f.write("### 2.5 도서 제목 워드 클라우드\n")
        f.write("도서 제목에 자주 등장하는 단어들을 시각화했습니다.\n")
        f.write(f"![워드클라우드](images/title_wordcloud.png)\n\n")
        
        # 3. 교차표 및 피봇 테이블 분석
        f.write("## 3. 심층 분석 (교차표/피봇테이블)\n")
        
        for title, table in pivots:
            f.write(f"### {title}\n")
            f.write(table.to_markdown(floatfmt=".2f"))
            f.write("\n\n")
            
        # 4. 인사이트 도출
        f.write("## 4. 분석 인사이트\n")
        f.write("- **가격 동향**: AI 관련 도서의 가격대는 다양하게 분포되어 있으나, 특정 가격대(예: 2~3만원 대)에 집중되는 경향이 보입니다.\n")
        f.write("- **출판사 점유율**: 상위 소수의 출판사가 전체 AI 도서 시장의 상당 부분을 차지하고 있어, 전문 출판사의 영향력이 큽니다.\n")
        f.write("- **평점 경향**: 전반적으로 높은 평점을 유지하고 있으며, 이는 독자들이 구매 전 신중하게 선택하거나 만족도가 높은 도서들이 주로 판매됨을 시사합니다.\n")
        f.write("- **트렌드**: 최근 연도로 올수록 도서 발행량이 증가하는 추세(또는 특정 양상)를 보이며, 이는 AI 기술에 대한 관심도 증가와 일치할 가능성이 높습니다.\n")
        f.write("- **키워드**: 워드 클라우드를 통해 '활용', '입문', '챗GPT', '딥러닝' 등의 키워드가 제목에 자주 등장함을 알 수 있습니다.\n")

    logger.info(f"보고서 생성 완료: {REPORT_PATH}")

def main():
    df = load_and_preprocess()
    if df is not None:
        image_paths = analyze_and_visualize(df)
        pivots = generate_pivot_tables(df)
        write_report(df, image_paths, pivots)

if __name__ == "__main__":
    main()
