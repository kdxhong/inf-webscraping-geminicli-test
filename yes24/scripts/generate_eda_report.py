import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from loguru import logger
import os

# 설정
DATA_PATH = "yes24/data/raw/yes24_books.csv"
IMG_DIR = "yes24/reports/images"
os.makedirs(IMG_DIR, exist_ok=True)

logger.add("yes24/logs/eda.log")

def load_data():
    logger.info("데이터 로드 중...")
    try:
        df = pd.read_csv(DATA_PATH)
        # 데이터 전처리: 쉼표 제거 및 숫자 변환
        if df['Price'].dtype == object:
            df['Price'] = df['Price'].astype(str).str.replace(',', '').astype(float)
        
        # Rating, Review Count도 확인
        if df['Rating'].dtype == object:
             df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        
        if df['Review Count'].dtype == object:
            df['Review Count'] = df['Review Count'].astype(str).str.replace(',', '').astype(float)
            
        return df
    except Exception as e:
        logger.error(f"데이터 로드 실패: {e}")
        return None

def generate_plots(df):
    logger.info("시각화 생성 중...")
    
    # 1. 가격 분포
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Price'], kde=True, color='skyblue')
    plt.title('도서 가격 분포')
    plt.xlabel('가격 (원)')
    plt.ylabel('빈도')
    plt.savefig(f"{IMG_DIR}/price_distribution.png")
    plt.close()
    
    # 2. 평점 분포
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Rating'], kde=True, color='orange', bins=20)
    plt.title('도서 평점 분포')
    plt.xlabel('평점')
    plt.ylabel('빈도')
    plt.savefig(f"{IMG_DIR}/rating_distribution.png")
    plt.close()
    
    # 3. 상위 10개 출판사
    top_publishers = df['Publisher'].value_counts().head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_publishers.values, y=top_publishers.index, palette='viridis')
    plt.title('상위 10개 출판사 (도서 수 기준)')
    plt.xlabel('도서 수')
    plt.savefig(f"{IMG_DIR}/top_publishers.png")
    plt.close()
    
    # 4. 가격 vs 평점 산점도
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Price', y='Rating', alpha=0.5)
    plt.title('가격과 평점의 상관관계')
    plt.xlabel('가격 (원)')
    plt.ylabel('평점')
    plt.savefig(f"{IMG_DIR}/price_vs_rating.png")
    plt.close()

def save_report(df):
    report_path = "yes24/agent_eda.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Yes24 도서 데이터 분석 보고서\n\n")
        f.write(f"**생성 일자:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**데이터 소스:** `yes24/data/raw/yes24_books.csv`\n\n")
        
        f.write("## 1. 데이터 요약\n")
        f.write(f"- **총 도서 수:** {len(df):,}권\n")
        f.write(f"- **평균 가격:** {df['Price'].mean():,.0f}원\n")
        f.write(f"- **중앙 가격:** {df['Price'].median():,.0f}원\n")
        f.write(f"- **최고 가격:** {df['Price'].max():,.0f}원\n")
        f.write(f"- **최저 가격:** {df['Price'].min():,.0f}원\n")
        f.write(f"- **평균 평점:** {df['Rating'].mean():.2f}점\n")
        f.write(f"- **평균 리뷰 수:** {df['Review Count'].mean():.1f}개\n\n")
        
        f.write("## 2. 주요 통계\n")
        f.write("### 상위 5개 출판사 (도서 수 기준)\n")
        for pub, count in df['Publisher'].value_counts().head(5).items():
            f.write(f"- {pub}: {count}권\n")
        f.write("\n")

        f.write("### 가장 비싼 도서 Top 3\n")
        for _, row in df.nlargest(3, 'Price').iterrows():
            f.write(f"- **{row['Title']}**: {row['Price']:,.0f}원\n")
        f.write("\n")
        
        f.write("### 리뷰가 가장 많은 도서 Top 3\n")
        for _, row in df.nlargest(3, 'Review Count').iterrows():
            f.write(f"- **{row['Title']}**: {row['Review Count']:,}개\n")
        f.write("\n")
        
        f.write("## 3. 시각화\n")
        f.write("### 가격 분포\n")
        f.write("![가격 분포](reports/images/price_distribution.png)\n\n")
        
        f.write("### 평점 분포\n")
        f.write("![평점 분포](reports/images/rating_distribution.png)\n\n")
        
        f.write("### 상위 출판사\n")
        f.write("![상위 출판사](reports/images/top_publishers.png)\n\n")
        
        f.write("### 가격과 평점의 상관관계\n")
        f.write("![상관관계](reports/images/price_vs_rating.png)\n")
    
    logger.info(f"보고서 저장 완료: {report_path}")

def main():
    df = load_data()
    if df is not None:
        generate_plots(df)
        save_report(df) # 변경된 부분
        logger.info("분석 완료")

if __name__ == "__main__":
    main()
