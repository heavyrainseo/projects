import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="Geyser Data Analysis Dashboard",
    page_icon="🌋",
    layout="wide"
)

# 데이터 로드 함수
@st.cache_data
def load_data():
    df = sns.load_dataset('geyser')
    return df

df = load_data()

# 사이드바 구성
st.sidebar.title("🌋 Geyser 분석기")
st.sidebar.markdown("Old Faithful 간헐천 데이터를 분석하고 예측합니다.")
menu = st.sidebar.radio("이동할 페이지", ["데이터 개요", "시각적 분석", "분출 시간 예측 모델"])

# 1. 데이터 개요 페이지
if menu == "데이터 개요":
    st.title("📊 데이터 개요")
    st.markdown("""
    Seaborn의 **geyser** 데이터셋은 미국 옐로스톤 국립공원에 있는 'Old Faithful' 간헐천의 분출 정보를 담고 있습니다.
    - **duration**: 분출 지속 시간 (분)
    - **waiting**: 다음 분출까지의 대기 시간 (분)
    - **kind**: 분출의 종류 (long, short)
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Raw Data (상위 10개)")
        st.dataframe(df.head(10), use_container_width=True)
        
    with col2:
        st.subheader("기초 통계량")
        st.write(df.describe())

    st.subheader("데이터 분포 요약")
    kinds = ", ".join(df['kind'].unique().tolist())
    st.info(f"전체 데이터 개수: {len(df)}개 / 분출 종류: {kinds}")

    st.subheader("종류별 심층 분석")
    col_stats, col_hist = st.columns([1, 2])

    with col_stats:
        st.markdown("**기초 통계량 (kind별)**")
        grouped_stats = df.groupby('kind').describe().T
        st.dataframe(grouped_stats, use_container_width=True)

    with col_hist:
        st.markdown("**분출 지속 시간(duration) 분포 비교**")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(data=df, x='duration', hue='kind', kde=True, element="step", ax=ax)
        st.pyplot(fig)

# 2. 시각적 분석 페이지
elif menu == "시각적 분석":
    st.title("🎨 시각적 탐색 분석 (EDA)")
    
    plot_type = st.segmented_control(
        "그래프 종류를 선택하세요",
        ["Scatter Plot (산점도)", "Joint Plot (결합 분포)", "KDE Plot (밀도 추정)"],
        default="Scatter Plot (산점도)",
    )
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if plot_type == "Scatter Plot (산점도)":
        st.subheader("대기 시간 vs 분출 지속 시간")
        sns.scatterplot(data=df, x='waiting', y='duration', hue='kind', style='kind', s=100, ax=ax)
        st.pyplot(fig)
        st.write("대기 시간과 분출 지속 시간 사이에 뚜렷한 군집(Cluster)이 형성됨을 알 수 있습니다.")
        
    elif plot_type == "Joint Plot (결합 분포)":
        st.subheader("변수별 분포와 상관관계")
        g = sns.jointplot(data=df, x='waiting', y='duration', hue='kind', kind='kde', fill=True, alpha=0.5)
        st.pyplot(g.fig)
        
    elif plot_type == "KDE Plot (밀도 추정)":
        st.subheader("데이터 밀도 (2D KDE)")
        sns.kdeplot(data=df, x='waiting', y='duration', hue='kind', fill=True, ax=ax)
        st.pyplot(fig)

# 3. 예측 모델 페이지
elif menu == "분출 시간 예측 모델":
    st.title("🤖 분출 시간(Duration) 예측 (수학 공식 활용)")
    st.markdown("단순 선형 회귀 공식을 사용하여 대기 시간(`waiting`)에 따른 분출 시간(`duration`)을 예측합니다.")

    # 변수 설정
    x = df['waiting']
    y = df['duration']

    # 통계량 계산
    mean_x = x.mean()
    mean_y = y.mean()
    std_x = x.std()
    std_y = y.std()
    r = x.corr(y) # 상관계수

    # 기울기(slope)와 절편(intercept) 계산
    # 공식: slope = r * (std_y / std_x)
    # 공식: intercept = mean_y - (slope * mean_x)
    slope = r * (std_y / std_x)
    intercept = mean_y - (slope * mean_x)
    
    # 결정계수 (R-squared) - 단순 선형 회귀에서는 상관계수의 제곱
    r2 = r ** 2
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🔍 예측 계산기")
        input_waiting = st.slider("현재 대기 시간(waiting)을 입력하세요 (분)", 
                                  min_value=int(x.min()), 
                                  max_value=int(x.max()), 
                                  value=int(mean_x))
        
        # 예측 수행: y = ax + b
        predicted_duration = (slope * input_waiting) + intercept
        
        st.metric(label="예상 분출 시간 (Duration)", value=f"{predicted_duration:.2f} 분")
        
        with st.expander("사용한 수학 공식 보기"):
            st.latex(r"a (기울기) = r \times \frac{\sigma_y}{\sigma_x}")
            st.latex(r"b (절편) = \bar{y} - a\bar{x}")
            st.latex(f"y = {slope:.4f}x + ({intercept:.4f})")
            st.write(f"- 상관계수(r): {r:.4f}")
            st.write(f"- 모델 설명력 (R²): {r2:.4f}")

    with col2:
        st.subheader("📈 회귀 분석 시각화")
        fig2, ax2 = plt.subplots()
        sns.regplot(data=df, x='waiting', y='duration', scatter_kws={'alpha':0.5}, line_kws={'color':'red'}, ax=ax2)
        # 사용자가 입력한 값 표시
        ax2.scatter(input_waiting, predicted_duration, color='green', s=150, edgecolors='black', label='Your Input', zorder=5)
        ax2.legend()
        st.pyplot(fig2)

    st.success(f"대기 시간이 {input_waiting}분일 때, 계산된 예상 분출 시간은 약 {predicted_duration:.2f}분입니다.")
