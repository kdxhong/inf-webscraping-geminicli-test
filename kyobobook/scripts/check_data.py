import pandas as pd
import os
import sys

# 인코딩 문제 방지
sys.stdout.reconfigure(encoding='utf-8')

data_dir = os.path.join(os.path.dirname(__file__), '../data/raw')
# 가장 최근 파일 찾기
files = [f for f in os.listdir(data_dir) if f.startswith('kyobo_bestseller_api_') and f.endswith('.csv')]
files.sort(reverse=True)

if not files:
    print("No data file found.")
    sys.exit(1)

latest_file = os.path.join(data_dir, files[0])
print(f"Checking file: {latest_file}")

try:
    df = pd.read_csv(latest_file)
    print(f"Total records: {len(df)}")
    print("\n[Columns]")
    print(df.columns.tolist())
    
    print("\n[First 5 rows]")
    # 탭으로 구분하여 출력하거나, 특정 컬럼만 출력
    print(df[['rank', 'title', 'author', 'price', 'sale_price']].head().to_string())
    
    # Null 값 확인
    print("\n[Null Count]")
    print(df.isnull().sum())
    
except Exception as e:
    print(f"Error reading file: {e}")
