import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from loguru import logger
import os

# 설정
DATA_PATH = "yes24/data/raw/yes24_books.csv"
REPORT_PATH = "yes24/agent_eda2.md"
IMG_DIR = "yes24/reports/images"
os.makedirs(IMG_DIR, exist_ok=True)

logger.add("yes24/logs/eda_v2.log")

def load_data():
    try:
        df = pd.read_csv(DATA_PATH)
        # 데이터 전처리
        if df['Price'].dtype == object:
            df['Price'] = df['Price'].astype(str).str.replace(',', '').astype(float)
        
        if df['Rating'].dtype == object:
             df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        
        if df['Review Count'].dtype == object:
            df['Review Count'] = df['Review Count'].astype(str).str.replace(',', '').astype(float)
            
        return df
    except Exception as e:
        logger.error(f"데이터 로드 실패: {e}")
        return None

def generate_plots(df):
    # 1. 가격 분포
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Price'], kde=True, color='skyblue')
    plt.title('도서 가격 분포')
    plt.xlabel('가격 (원)')
    plt.ylabel('빈도')
    plt.savefig(f"{IMG_DIR}/price_distribution_v2.png")
    plt.close()
    
    # 2. 평점 분포
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Rating'], kde=True, color='orange', bins=20)
    plt.title('도서 평점 분포')
    plt.xlabel('평점')
    plt.ylabel('빈도')
    plt.savefig(f"{IMG_DIR}/rating_distribution_v2.png")
    plt.close()
    
    # 3. 상위 10개 출판사
    top_publishers = df['Publisher'].value_counts().head(10)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=top_publishers.values, y=top_publishers.index, hue=top_publishers.index, legend=False, palette='viridis')
    plt.title('상위 10개 출판사 (도서 수 기준)')
    plt.xlabel('도서 수')
    plt.savefig(f"{IMG_DIR}/top_publishers_v2.png")
    plt.close()
    
    # 4. 가격 vs 평점 산점도
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Price', y='Rating', alpha=0.5)
    plt.title('가격과 평점의 상관관계')
    plt.xlabel('가격 (원)')
    plt.ylabel('평점')
    plt.savefig(f"{IMG_DIR}/price_vs_rating_v2.png")
    plt.close()

def save_markdown(df):
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Yes24 도서 데이터 심층 분석 보고서 (v2)\n\n")
        f.write(f"**생성 일자:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**데이터 소스:** `{DATA_PATH}`\n\n")
        
        f.write("## 1. 데이터 개요\n")
        f.write(f"- **총 도서 수:** {len(df):,}권\n")
        f.write(f"- **가격 범위:** {df['Price'].min():,.0f}원 ~ {df['Price'].max():,.0f}원 (평균: {df['Price'].mean():,.0f}원)\n")
        f.write(f"- **평점 평균:** {df['Rating'].mean():.2f}점\n")
        f.write(f"- **리뷰 평균:** {df['Review Count'].mean():.1f}개\n\n")
        
        f.write("## 2. 출판사 분석\n")
        f.write("도서 출판 수가 가장 많은 상위 5개 출판사는 다음과 같습니다.\n")
        for pub, count in df['Publisher'].value_counts().head(5).items():
            f.write(f"- **{pub}**: {count}권\n")
        f.write("\n![상위 출판사](reports/images/top_publishers_v2.png)\n\n")

        f.write("## 3. 가격 및 평점 분석\n")
        f.write("### 가격 분포\n")
        f.write("도서 가격의 전반적인 분포를 보여줍니다.\n")
        f.write("![가격 분포](reports/images/price_distribution_v2.png)\n\n")
        
        f.write("### 평점 분포\n")
        f.write("독자들의 평점 분포 현황입니다.\n")
        f.write("![평점 분포](reports/images/rating_distribution_v2.png)\n\n")
        
        f.write("### 가격과 평점의 상관관계\n")
        f.write("가격대가 평점에 미치는 영향을 시각화했습니다.\n")
        f.write("![상관관계](reports/images/price_vs_rating_v2.png)\n\n")
        
        f.write("## 4. 특이 사항 (Top 3)\n")
        f.write("### 최고가 도서\n")
        for _, row in df.nlargest(3, 'Price').iterrows():
            f.write(f"- [{row['Title']}]({row['Detail URL']}): {row['Price']:,.0f}원\n")
        f.write("\n")
        
        f.write("### 최다 리뷰 도서\n")
        for _, row in df.nlargest(3, 'Review Count').iterrows():
            f.write(f"- [{row['Title']}]({row['Detail URL']}): {row['Review Count']:,}개\n")

def main():
    df = load_data()
    if df is not None:
        generate_plots(df)
        save_markdown(df)
        logger.info(f"Report generated: {REPORT_PATH}")

if __name__ == "__main__":
    main()
