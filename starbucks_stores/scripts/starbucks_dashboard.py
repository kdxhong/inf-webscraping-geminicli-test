import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os

# ----------------- 1. 데이터 로드 및 기본 설정 -----------------
st.set_page_config(page_title="Starbucks 전국 매장 분석 v2", layout="wide", page_icon="☕")

@st.cache_data
def load_data():
    file_path = "starbucks_stores/data/raw/starbucks_all_stores.csv"
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    df = pd.read_csv(file_path)
    # 데이터 타입 보정
    if 'open_dt' in df.columns:
        df['open_dt'] = pd.to_datetime(df['open_dt'].astype(str), format='%Y%m%d', errors='coerce')
    
    # 위도 경도 결측치 제거
    df = df.dropna(subset=['lat', 'lot'])
    
    # 시도/시군구 공백 제거 및 보정 (결측치 대비 astype(str) 추가)
    if 'sido_nm' in df.columns: df['sido_nm'] = df['sido_nm'].astype(str).str.strip()
    if 'gugun_nm' in df.columns: df['gugun_nm'] = df['gugun_nm'].astype(str).str.strip()
    
    return df

df = load_data()

# ----------------- 2. 사이드바 컨트롤 -----------------
st.sidebar.title("☕ Starbucks Filter")
st.sidebar.markdown("---")

# 시도 선택
sido_list = ["전제"] + sorted(df['sido_nm'].unique().tolist())
selected_sido = st.sidebar.selectbox("🗺️ 시도 선택", sido_list)

# 시군구 선택 (시도에 종속)
if selected_sido != "전제":
    gugun_list = ["전체"] + sorted(df[df['sido_nm'] == selected_sido]['gugun_nm'].unique().tolist())
else:
    gugun_list = ["전체"]
selected_gugun = st.sidebar.selectbox("📍 시군구 선택", gugun_list)

# 매장명 검색 (글로벌 검색 기능 연동)
search_query = st.sidebar.text_input("🔍 매장명 검색", placeholder="매장 이름을 입력하세요...")

# 데이터 필터링 로직
filtered_df = df.copy()
if selected_sido != "전제":
    filtered_df = filtered_df[filtered_df['sido_nm'] == selected_sido]
if selected_gugun != "전체":
    filtered_df = filtered_df[filtered_df['gugun_nm'] == selected_gugun]
if search_query:
    filtered_df = filtered_df[filtered_df['s_name'].str.contains(search_query, case=False)]

# ----------------- 3. 메인 화면 구성 (탭) -----------------
st.title("☕ 스타벅스 전국 매장 분석 대시보드")
st.markdown(f"현재 선택된 지역: **{selected_sido} > {selected_gugun}** (총 {len(filtered_df)}개 매장)")

tabs = st.tabs(["📊 데이터 요약", "🏘️ 지역별 탐색", "🗺️ 전국 매장 지도", "📦 클러스터 맵", "🧬 군집화 분석", "🔍 상세 검색"])

# --- 탭 1: 데이터 요약 ---
with tabs[0]:
    st.header("📋 데이터 개요 (EDA)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("전체 매장 수", f"{len(df):,} 개")
    c2.metric("필터링된 매장", f"{len(filtered_df):,} 개")
    c3.metric("시도 유형", f"{df['sido_nm'].nunique()} 종")
    c4.metric("분석 가능 지점", f"{len(df.dropna(subset=['lat', 'lot'])):,} 개")
    
    st.divider()
    
    col_plot1, col_plot2 = st.columns(2)
    with col_plot1:
        st.subheader("📍 시도별 매장 분포")
        sido_counts = df['sido_nm'].value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        sido_counts.plot(kind='bar', ax=ax, color='#00704A')
        ax.set_title("전국 시도별 스타벅스 매장 수")
        st.pyplot(fig)
    
    with col_plot2:
        st.subheader("📅 연도별 오픈 추이")
        if 'open_dt' in df.columns:
            yearly = df['open_dt'].dt.year.value_counts().sort_index()
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            yearly.plot(kind='line', marker='o', ax=ax2, color='#00704A')
            ax2.set_title("연도별 신규 오픈 추이")
            st.pyplot(fig2)

# --- 탭 2: 지역별 탐색 ---
with tabs[1]:
    st.header("🏢 시군구 상세 탐색")
    if selected_sido != "전제":
        st.subheader(f"{selected_sido} 내 구군 분포")
        gugun_df = filtered_df['gugun_nm'].value_counts().reset_index()
        gugun_df.columns = ['구군', '매장수']
        st.bar_chart(gugun_df.set_index('구군'))
        st.dataframe(filtered_df[['s_name', 'gugun_nm', 'doro_address', 'tel', 'open_dt']].sort_values('open_dt'))
    else:
        st.info("왼쪽 사이드바에서 시도를 선택하면 상세 정보를 볼 수 있습니다.")

# --- 탭 3: 전국 매장 지도 ---
with tabs[2]:
    st.header("🗺️ 전국 매장 지도")
    if not filtered_df.empty:
        # 매장 수가 너무 많으면 경고
        if len(filtered_df) > 1000:
            st.warning("매장 수가 1,000개가 넘어 성능이 저하될 수 있습니다. 필터를 활용해 범위를 좁히시는 것을 추천합니다.")
        
        m_base = folium.Map(location=[filtered_df['lat'].mean(), filtered_df['lot'].mean()], zoom_start=12 if selected_sido != "전제" else 7)
        for _, row in filtered_df.iterrows():
            popup_html = f"""
            <div style="width:200px">
                <h4>{row['s_name']}</h4>
                <p><b>주소:</b> {row['doro_address']}</p>
                <p><b>전화:</b> {row['tel'] if pd.notna(row['tel']) else '정보없음'}</p>
                <p><b>오픈일:</b> {row['open_dt'].strftime('%Y-%m-%d') if pd.notna(row['open_dt']) else '정보없음'}</p>
            </div>
            """
            folium.Marker(
                [row['lat'], row['lot']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row['s_name']
            ).add_to(m_base)
        st_folium(m_base, width=1200, height=600, key="base_map")
    else:
        st.error("데이터가 없습니다.")

# --- 탭 4: 클러스터 맵 ---
with tabs[3]:
    st.header("📦 클러스터링(MarkerCluster) 맵")
    st.write("전국 매장을 그룹화하여 보여줍니다. 지도를 확대하면 개별 마커를 볼 수 있습니다.")
    m_cluster = folium.Map(location=[36.5, 127.5], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m_cluster)
    
    for _, row in filtered_df.iterrows():
        folium.Marker(
            [row['lat'], row['lot']],
            popup=row['s_name'],
            tooltip=row['s_name']
        ).add_to(marker_cluster)
    st_folium(m_cluster, width=1200, height=600, key="cluster_marker_map")

# --- 탭 5: 군집화 분석 ---
with tabs[4]:
    st.header("🧬 머신러닝 군집화 (K-Means)")
    st.write("위치(위도/경도) 정보를 기반으로 매장의 밀집 영역을 분석합니다.")
    
    k_val = st.slider("군집 개수(K) 선택", 2, 20, 5)
    if st.button("분석 실행"):
        # 머신러닝 분석
        data_for_cluster = filtered_df[['lat', 'lot']].dropna()
        if len(data_for_cluster) >= k_val:
            model = KMeans(n_clusters=k_val, random_state=42)
            filtered_df['ml_cluster'] = model.fit_predict(data_for_cluster)
            
            st.success(f"{k_val}개의 군집으로 분석이 완료되었습니다.")
            
            # 클러스터 시각화 지도
            m_ml = folium.Map(location=[data_for_cluster['lat'].mean(), data_for_cluster['lot'].mean()], zoom_start=11 if selected_sido != "전제" else 7)
            colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
            
            for _, row in filtered_df.iterrows():
                folium.CircleMarker(
                    [row['lat'], row['lot']],
                    radius=6,
                    color=colors[int(row['ml_cluster']) % len(colors)],
                    fill=True,
                    popup=f"군집 {row['ml_cluster']}: {row['s_name']}"
                ).add_to(m_ml)
            st_folium(m_ml, width=1200, height=600, key="ml_cluster_map")
            
            # 클러스터 통계
            st.subheader("📌 군집별 매장 수 요약")
            summary = filtered_df.groupby('ml_cluster').size().reset_index(name='매장수')
            st.dataframe(summary)
        else:
            st.error("데이터가 너무 적어 분석을 수행할 수 없습니다.")

# --- 탭 6: 상세 검색 ---
with tabs[5]:
    st.header("🔍 상세 매장 검색 및 포커싱")
    search_target = st.text_input("검색할 매장명 입력 (예: 강남역)", "")
    if search_target:
        res = df[df['s_name'].str.contains(search_target, case=False)]
        if not res.empty:
            st.success(f"총 {len(res)}개의 매장이 검색되었습니다.")
            st.dataframe(res[['s_name', 'sido_nm', 'gugun_nm', 'doro_address', 'tel']])
            
            # 검색 결과 중 첫 번째 매장 위치로 지도 포커싱
            first_store = res.iloc[0]
            st.info(f"가장 유사한 매장 '{first_store['s_name']}' 위치로 이동합니다.")
            m_search = folium.Map(location=[first_store['lat'], first_store['lot']], zoom_start=15)
            folium.Marker(
                [first_store['lat'], first_store['lot']],
                popup=first_store['s_name'],
                icon=folium.Icon(color='red', icon='star')
            ).add_to(m_search)
            st_folium(m_search, width=1200, height=400, key="search_map")
        else:
            st.warning("검색 결과가 없습니다.")
    else:
        st.write("매장명을 입력하면 실시간으로 지도와 정보를 찾을 수 있습니다.")
