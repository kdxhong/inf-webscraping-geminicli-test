import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from loguru import logger
import os

# 디렉토리 설정
IMG_DIR = "starbucks_stores/images"
RPT_DIR = "starbucks_stores/reports"
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(RPT_DIR, exist_ok=True)

logger.add("starbucks_stores/logs/eda.log", rotation="500 MB")

def perform_eda():
    logger.info("스타벅스 데이터 EDA 시작")
    
    # 1. 데이터 로드
    df = pd.read_csv('starbucks_stores/data/raw/starbucks_all_stores.csv')
    logger.info(f"데이터 로드 완료: {df.shape}")

    # 0. 데이터 정제: 결측치 및 단일값 컬럼 제거
    cols_to_drop = []
    for col in df.columns:
        if df[col].nunique() <= 1:
            cols_to_drop.append(col)
    
    df_cleaned = df.drop(columns=cols_to_drop)
    logger.info(f"불필요한 컬럼 {len(cols_to_drop)}개 제거. 남은 컬럼: {len(df_cleaned.columns)}개")

    # 2. 지역별 매장 분포
    sido_col = 'sido_nm' if 'sido_nm' in df_cleaned.columns else ('sido_name' if 'sido_name' in df_cleaned.columns else None)
    
    if sido_col and not df_cleaned[sido_col].empty:
        sido_counts = df_cleaned[sido_col].value_counts()
        plt.figure(figsize=(12, 6))
        sido_counts.plot(kind='bar', color='salmon')
        plt.title('지역별(시도) 스타벅스 매장 분포')
        plt.ylabel('매장 수')
        plt.tight_layout()
        plt.savefig(f"{IMG_DIR}/sido_distribution.png")
        plt.close()
        sido_pivot = sido_counts.to_frame(name='매장수').reset_index()
        sido_pivot.columns = ['지역(시도)', '매장수']
    else:
        sido_pivot = pd.DataFrame()

    # 3. 매장 특성 분석 (tXX, pXX 컬럼 활용)
    feature_cols = [c for c in df_cleaned.columns if (c.startswith('t') or c.startswith('p')) and len(c) <= 3]
    if feature_cols:
        feature_sums = df_cleaned[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum()
        feature_stats = (feature_sums / len(df_cleaned)).sort_values(ascending=False).head(10)
        
        if not feature_stats.empty and feature_stats.sum() > 0:
            plt.figure(figsize=(12, 6))
            feature_stats.plot(kind='bar', color='skyblue')
            plt.title('스타벅스 주요 서비스/테마 제공 비율 (Top 10)')
            plt.ylabel('비율')
            plt.xlabel('서비스 코드')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(f"{IMG_DIR}/top_services.png")
            plt.close()
        else:
            feature_stats = pd.Series()
    else:
        feature_stats = pd.Series()

    # 4. 오픈일 기반 분석 (날짜 형식 수정: YYYYMMDD string -> datetime)
    open_dt_col = 'open_dt' if 'open_dt' in df_cleaned.columns else None
    if open_dt_col:
        # 정수형 데이터를 문자열로 바꾸고 날짜로 변환
        open_dates = pd.to_datetime(df_cleaned[open_dt_col].astype(str), format='%Y%m%d', errors='coerce')
        df_cleaned['open_year'] = open_dates.dt.year
        yearly_growth = df_cleaned['open_year'].dropna().value_counts().sort_index()
        
        if not yearly_growth.empty:
            plt.figure(figsize=(12, 6))
            yearly_growth.plot(kind='line', marker='o', color='green')
            plt.title('연도별 스타벅스 신규 매장 오픈 추이')
            plt.ylabel('오픈 매장 수')
            plt.xlabel('연도')
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.savefig(f"{IMG_DIR}/yearly_growth.png")
            plt.close()
            yearly_pivot = yearly_growth.to_frame(name='오픈수').reset_index()
            yearly_pivot.columns = ['연도', '오픈수']
        else:
            yearly_pivot = pd.DataFrame()
    else:
        yearly_pivot = pd.DataFrame()

    # 5. 보고서 생성
    with open(f"{RPT_DIR}/eda_report.md", "w", encoding="utf-8") as f:
        f.write("# 스타벅스 매장 데이터 분석 보고서\n\n")
        
        f.write("## 1. 데이터 개요 및 품질\n")
        f.write(f"- 전체 수집 매장 수: {len(df_cleaned)}개\n")
        f.write(f"- 분석에 사용된 컬럼 수: {len(df_cleaned.columns)}개 (중복/무의미한 컬럼 제거 후)\n\n")
        
        if not sido_pivot.empty:
            f.write("## 2. 지역별 매장 분포\n")
            f.write("서울 및 수도권에 압도적으로 많은 매장이 분포하고 있습니다.\n\n")
            f.write(f"![지역별 분포](../images/sido_distribution.png)\n\n")
            f.write("### [지역별 매장 수 상세]\n")
            f.write(sido_pivot.to_markdown(index=False) + "\n\n")
        
        if not feature_stats.empty:
            f.write("## 3. 매장 특성 및 서비스 분석\n")
            f.write("매장별 다양한 편의 서비스(주차, 테라스 등) 제공 비율입니다.\n\n")
            if os.path.exists(f"{IMG_DIR}/top_services.png"):
                f.write(f"![주요 서비스](../images/top_services.png)\n\n")
            f.write("### [상위 10개 서비스 제공 비율]\n")
            f.write(feature_stats.to_frame(name='비율').to_markdown() + "\n\n")
        
        if not yearly_pivot.empty:
            f.write("## 4. 연도별 오픈 추이\n")
            f.write("매년 꾸준히 매장이 늘어나고 있으며, 특정 시점에 가파른 성장이 관찰됩니다.\n\n")
            f.write(f"![연도별 성장](../images/yearly_growth.png)\n\n")
            f.write("### [연도별 오픈 매장 수 상세]\n")
            f.write(yearly_pivot.to_markdown(index=False) + "\n\n")
        
        f.write("## 5. 결론 및 인사이트\n")
        f.write("- **입지 전략**: 수도권 밀집도가 매우 높으며, 이는 주요 소비층이 집중된 곳을 공략하는 전략으로 풀이됩니다.\n")
        f.write("- **미래 제안**: 테마별 매장(DT, 리저브 등)의 지역별 성장률을 분석하여 차별화된 입지 전략 수립이 가능할 것입니다.\n")

    logger.info("EDA 보고서 생성 완료: starbucks_stores/reports/eda_report.md")

if __name__ == "__main__":
    try:
        perform_eda()
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {e}")
