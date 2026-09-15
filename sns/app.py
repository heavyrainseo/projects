from __future__ import annotations

import pandas as pd
import streamlit as st

from charts import annual_chart, heatmap, monthly_chart, timeline_chart
from data import (
    MONTH_LABELS,
    MONTH_ORDER,
    annual_summary,
    filter_flights,
    load_flights,
    monthly_summary,
    year_month_matrix,
    year_month_summary,
)


st.set_page_config(
    page_title="Flights 승객 추이",
    page_icon="✈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap');
    :root { --ink: #202a2e; --muted: #657276; --paper: #f6f8f5; --line: #dce5e2; --accent: #e05a47; }
    .stApp { background: var(--paper); color: var(--ink); }
    .block-container { max-width: 1480px; padding-top: 3rem; padding-bottom: 3rem; }
    h1, h2, h3, p, label, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { font-family: Manrope, "Noto Sans KR", sans-serif; }
    h1 { letter-spacing: 0; font-weight: 800; font-size: clamp(2rem, 4vw, 4rem); line-height: 1; margin-bottom: .5rem; }
    h2 { font-size: 1.2rem; margin-top: 1.8rem; }
    .eyebrow { color: var(--accent); font-family: "DM Mono", monospace; font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; }
    .lede { color: var(--muted); font-size: 1rem; margin-bottom: 2rem; }
    [data-testid="stMetric"] { background: white; border: 1px solid var(--line); border-radius: 6px; padding: 1.1rem 1.2rem; min-height: 126px; }
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: .8rem; }
    [data-testid="stMetricValue"] { color: var(--ink); font-size: 1.75rem; }
    [data-testid="stSidebar"] { background: #edf2ef; border-right: 1px solid var(--line); }
    .insight { border-left: 3px solid var(--accent); padding: .65rem 1rem; background: white; color: var(--muted); }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_flights()


flights = get_data()
available_years = sorted(flights["year"].unique())

st.sidebar.markdown("### 분석 조건")
year_range = st.sidebar.slider(
    "연도 범위",
    min_value=available_years[0],
    max_value=available_years[-1],
    value=(available_years[0], available_years[-1]),
)
selected_month_labels = st.sidebar.multiselect(
    "월 선택",
    options=[MONTH_LABELS[month] for month in MONTH_ORDER],
    default=[],
    placeholder="전체 월",
)
selected_months = [
    month for month in MONTH_ORDER if MONTH_LABELS[month] in selected_month_labels
]

filtered = filter_flights(flights, year_range, selected_months)

st.markdown('<div class="eyebrow">DATA STORY / FLIGHTS</div>', unsafe_allow_html=True)
st.title("하늘을 오간 사람들")
st.markdown(
    "<p class='lede'>1949년부터 1960년까지, 연도와 계절에 따라 달라진 항공 승객 흐름을 탐색합니다.</p>",
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다. 연도 또는 월을 조정해 주세요.")
    st.stop()

annual = annual_summary(filtered)
monthly = monthly_summary(filtered)
matrix = year_month_matrix(filtered)

total_passengers = int(filtered["passengers"].sum())
average_passengers = filtered["passengers"].mean()
peak_row = filtered.loc[filtered["passengers"].idxmax()]
first_year_total = annual.iloc[0]["total_passengers"]
last_year_total = annual.iloc[-1]["total_passengers"]
growth = ((last_year_total - first_year_total) / first_year_total * 100) if first_year_total else 0

metric_columns = st.columns(4)
metric_columns[0].metric("총 승객 수", f"{total_passengers:,.0f}명")
metric_columns[1].metric("월평균 승객 수", f"{average_passengers:,.0f}명")
metric_columns[2].metric(
    "최고 기록",
    f"{int(peak_row['passengers']):,}명",
    f"{int(peak_row['year'])}년 {peak_row['month_label']}",
)
metric_columns[3].metric("기간 내 성장률", f"{growth:+.1f}%")

st.markdown("## 전체 흐름")
left, right = st.columns(2)
with left:
    st.markdown("#### 연도별 승객 규모")
    st.plotly_chart(annual_chart(annual), use_container_width=True)
with right:
    st.markdown("#### 월별 평균 승객 수")
    st.plotly_chart(monthly_chart(monthly), use_container_width=True)

st.markdown("## 시간의 결")
moving_average_months = st.slider(
    "이동평균 기간",
    min_value=3,
    max_value=12,
    value=3,
    step=1,
    format="%d개월",
)
timeline = year_month_summary(filtered, moving_average_months)
st.plotly_chart(
    timeline_chart(timeline, moving_average_months), use_container_width=True
)

st.markdown("## 계절성 지도")
st.markdown(
    "<div class='insight'>색이 진할수록 해당 월의 승객 수가 많습니다. 특정 계절의 반복 패턴과 장기 증가 추세를 함께 확인할 수 있습니다.</div>",
    unsafe_allow_html=True,
)
st.plotly_chart(heatmap(matrix), use_container_width=True)