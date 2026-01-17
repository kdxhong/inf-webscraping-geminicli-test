import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from loguru import logger
import koreanize_matplotlib

# 설정
DATA_PATH = r"kyobobook/data/raw/kyobo_bestseller_api_20260117.csv"
OUTPUT_DIR = r"kyobobook/eda_images"
REPORT_PATH = r"kyobobook/eda_report.md"
NL = chr(10)  # Newline character to avoid syntax errors in file generation

# 로깅 설정
logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("kyobobook/logs/eda.log", rotation="10 MB")

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"디렉토리 생성: {directory}")

def load_data(file_path):
    logger.info(f"데이터 로딩 시도: {file_path}")
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        logger.info("UTF-8로 로딩 성공")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='cp949')
            logger.info("CP949로 로딩 성공")
        except Exception as e:
            logger.error(f"로딩 실패: {e}")
            raise e
    except Exception as e:
        logger.error(f"로딩 실패: {e}")
        raise e
    
    return df

def analyze_structure(df):
    logger.info("데이터 구조 분석 중...")
    buffer = []
    buffer.append("## 2. 데이터 개요" + NL)
    buffer.append(f"- **행 수**: {df.shape[0]}" + NL)
    buffer.append(f"- **열 수**: {df.shape[1]}" + NL)
    buffer.append(NL + "### 컬럼 정보" + NL)
    buffer.append("| 컬럼명 | 데이터 타입 | 결측치 수 | 고유값 수 |" + NL)
    buffer.append("|---|---|---|---|" + NL)
    
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        unique_count = df[col].nunique()
        buffer.append(f"| {col} | {dtype} | {null_count} | {unique_count} |" + NL)
    
    buffer.append(NL)
    
    # 중복 데이터 확인
    duplicates = df.duplicated().sum()
    buffer.append(f"- **중복 행 개수**: {duplicates}" + NL)
    
    return "".join(buffer)

def analyze_statistics(df):
    logger.info("기술통계 분석 중...")
    buffer = []
    buffer.append("## 3. 기술통계 요약" + NL)
    
    # 수치형 변수
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        buffer.append("### 수치형 변수 통계" + NL)
        desc = numeric_df.describe().T
        desc = desc[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
        buffer.append(desc.to_markdown())
        buffer.append(NL + NL)
    
    # 범주형 변수
    categorical_df = df.select_dtypes(exclude=[np.number])
    if not categorical_df.empty:
        buffer.append("### 범주형 변수 통계 (Top 5)" + NL)
        for col in categorical_df.columns:
            buffer.append(f"#### {col}" + NL)
            vc = df[col].value_counts().head(5)
            buffer.append(vc.to_markdown(headers=["Count"]))
            buffer.append(NL + NL)
            
    return "".join(buffer)

def analyze_missing_outliers(df):
    logger.info("결측치 및 이상치 분석 중...")
    buffer = []
    buffer.append("## 4. 결측치 및 이상치 분석" + NL)
    
    # 결측치 시각화
    missing = df.isnull().mean()
    if missing.sum() > 0:
        plt.figure(figsize=(10, 6))
        missing[missing > 0].plot(kind='bar')
        plt.title('컬럼별 결측치 비율')
        plt.ylabel('비율')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'missing_values.png'))
        plt.close()
        buffer.append("### 결측치 시각화" + NL)
        buffer.append("![Missing Values](eda_images/missing_values.png)" + NL + NL)
    else:
        buffer.append("- 결측치가 없습니다." + NL + NL)

    # 이상치 시각화 (수치형)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        buffer.append("### 이상치 탐지 (Boxplot)" + NL)
        for col in numeric_cols:
            plt.figure(figsize=(8, 4))
            sns.boxplot(x=df[col])
            plt.title(f'{col} 이상치 (Boxplot)')
            plt.tight_layout()
            filename = f'outlier_{col}.png'.replace('/', '_').replace('\\', '_')
            plt.savefig(os.path.join(OUTPUT_DIR, filename))
            plt.close()
            buffer.append(f"#### {col}" + NL)
            buffer.append(f"![Outlier {col}](eda_images/{filename})" + NL + NL)
            
    return "".join(buffer)

def analyze_relationships(df):
    logger.info("변수 간 관계 분석 중...")
    buffer = []
    buffer.append("## 5. 변수 간 관계 분석" + NL)
    
    numeric_df = df.select_dtypes(include=[np.number])
    if len(numeric_df.columns) > 1:
        # 상관관계 히트맵
        plt.figure(figsize=(10, 8))
        corr = numeric_df.corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('수치형 변수 상관관계 히트맵')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'))
        plt.close()
        
        buffer.append("### 상관관계 히트맵" + NL)
        buffer.append("![Correlation Heatmap](eda_images/correlation_heatmap.png)" + NL + NL)
    
    # 범주형 ↔ 수치형 변수 간 관계 분석
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns

    target_num = None
    target_cat = None
    
    for col in numeric_cols:
        if df[col].nunique() > 5:
            target_num = col
            break
            
    for col in categorical_cols:
        if 2 <= df[col].nunique() <= 20:
            target_cat = col
            break
            
    if target_num and target_cat:
        plt.figure(figsize=(12, 6))
        sns.boxplot(x=target_cat, y=target_num, data=df)
        plt.title(f'{target_cat}에 따른 {target_num} 분포')
        plt.xticks(rotation=45)
        plt.tight_layout()
        filename = f'relation_{target_cat}_{target_num}.png'.replace('/', '_')
        plt.savefig(os.path.join(OUTPUT_DIR, filename))
        plt.close()
        
        buffer.append(f"### {target_cat} - {target_num} 관계" + NL)
        buffer.append(f"![Relation](eda_images/{filename})" + NL + NL)

    return "".join(buffer)

def analyze_distributions(df):
    logger.info("데이터 분포 시각화 중...")
    buffer = []
    buffer.append("## 6. 데이터 분포 시각화" + NL)
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[col], kde=True)
        plt.title(f'{col} 분포')
        plt.tight_layout()
        filename = f'dist_{col}.png'.replace('/', '_')
        plt.savefig(os.path.join(OUTPUT_DIR, filename))
        plt.close()
        
        buffer.append(f"### {col} 분포" + NL)
        buffer.append(f"![Distribution {col}](eda_images/{filename})" + NL + NL)
        
    return "".join(buffer)

def generate_insights(df):
    buffer = []
    buffer.append("## 7. 주요 인사이트" + NL)
    buffer.append("- 데이터의 전반적인 구조와 통계량을 확인하였습니다." + NL)
    buffer.append("- 결측치와 이상치를 시각화를 통해 파악할 수 있었습니다." + NL)
    buffer.append("- 변수 간의 상관관계를 통해 데이터 내의 잠재적인 패턴을 유추해볼 수 있습니다." + NL)
    return "".join(buffer)

def main():
    ensure_dir(OUTPUT_DIR)
    
    df = load_data(DATA_PATH)
    
    report_content = []
    report_content.append(f"# 데이터 탐색적 분석 (EDA) 리포트" + NL)
    report_content.append(f"**분석 일시**: {pd.Timestamp.now()}" + NL)
    report_content.append(f"**대상 파일**: {DATA_PATH}" + NL + NL)
    report_content.append("## 1. 데이터 불러오기" + NL)
    report_content.append("데이터 로드 완료. 인코딩 및 파싱 성공." + NL + NL)
    
    report_content.append(analyze_structure(df))
    report_content.append(analyze_statistics(df))
    report_content.append(analyze_missing_outliers(df))
    report_content.append(analyze_relationships(df))
    report_content.append(analyze_distributions(df))
    report_content.append(generate_insights(df))
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write("".join(report_content))
        
    logger.info(f"리포트 생성 완료: {REPORT_PATH}")

if __name__ == "__main__":
    main()