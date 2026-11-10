import os

import pandas as pd
import plotly.express as px
import streamlit as st


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "cleaned_pension.csv")

PENSION_RATE = 0.095
SALARY_CAP = 6_590_000

REQUIRED_COLUMNS = {
    "company_name",
    "company_type",
    "industry",
    "sido",
    "status",
    "member_count",
    "estimated_salary_per",
    "new_members",
    "lost_members",
}


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path, encoding="utf-8-sig")


def main() -> None:
    st.set_page_config(page_title="📋 국민연금 사업장 분석 대시보드", layout="wide")
    st.title("📋 국민연금 사업장 분석 대시보드")

    try:
        data = load_data(DATA_PATH)
    except FileNotFoundError:
        st.error(f"정제된 CSV 파일을 찾을 수 없습니다: {DATA_PATH}")
        st.stop()

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        st.error(f"정제된 CSV에 필요한 컬럼이 없습니다: {', '.join(sorted(missing_columns))}")
        st.stop()

    registered_data = data.loc[data["status"].eq("등록")].copy()
    registered_data["member_count"] = pd.to_numeric(
        registered_data["member_count"], errors="coerce"
    ).fillna(0)
    registered_data["estimated_salary_per"] = pd.to_numeric(
        registered_data["estimated_salary_per"], errors="coerce"
    ).fillna(0).clip(upper=SALARY_CAP)
    registered_data["estimated_salary_per"] = registered_data[
        "estimated_salary_per"
    ].where(registered_data["member_count"].gt(0), 0)
    for column in ("new_members", "lost_members"):
        registered_data[column] = pd.to_numeric(
            registered_data[column], errors="coerce"
        ).fillna(0)
    registered_data["net_change"] = (
        registered_data["new_members"] - registered_data["lost_members"]
    )

    total_members = registered_data["member_count"].sum()
    average_monthly_salary = registered_data["estimated_salary_per"].mean()
    if pd.isna(average_monthly_salary):
        average_monthly_salary = 0

    if "year_month" in registered_data.columns:
        year_month_values = registered_data["year_month"].dropna().astype(str).str.strip()
        latest_year_month = (
            year_month_values.max() if not year_month_values.empty else "정보 없음"
        )
    else:
        latest_year_month = "정보 없음"

    total_companies_metric, total_members_metric, average_salary_metric, year_month_metric = (
        st.columns(4)
    )
    total_companies_metric.metric("총 등록 사업장 수", f"{len(registered_data):,}")
    total_members_metric.metric("총 가입자 수", f"{total_members:,.0f}")
    average_salary_metric.metric(
        "전국 평균 1인당 추정 월급여", f"{average_monthly_salary:,.0f}원"
    )
    year_month_metric.metric("데이터 기준 연월", latest_year_month)

    with st.sidebar:
        st.subheader("지역 선택")
        sido_options = sorted(data["sido"].dropna().astype(str).unique().tolist())
        selected_sido = st.selectbox("시도", options=sido_options)

        st.subheader("분석 필터")
        selected_company_type = st.selectbox("사업장 형태", options=["전체", "법인", "개인"])
        minimum_members = st.slider("최소 가입자 수", min_value=1, max_value=100, value=1)

    region_data = registered_data.loc[registered_data["sido"].eq(selected_sido)]
    region_average_salary = region_data["estimated_salary_per"].mean()
    if pd.isna(region_average_salary):
        region_average_salary = 0
    salary_delta = region_average_salary - average_monthly_salary

    filtered_data = region_data.loc[
        region_data["member_count"].ge(minimum_members)
    ]
    if selected_company_type != "전체":
        filtered_data = filtered_data.loc[
            filtered_data["company_type"].eq(selected_company_type)
        ]

    st.divider()
    st.subheader(f"{selected_sido} 사업장 분석")

    st.markdown("#### 지역 요약 지표")
    region_summary = st.columns(4)
    region_summary[0].metric("해당 시도 사업장 수", f"{len(region_data):,}")
    region_summary[1].metric(
        "해당 시도 총 가입자 수",
        f"{region_data['member_count'].sum():,.0f}",
    )
    region_summary[2].metric(
        "해당 시도 평균 1인당 추정 월급여",
        f"{region_average_salary:,.0f}원",
        delta=f"{salary_delta:+,.0f}원",
        delta_color="normal",
    )
    region_summary[3].metric(
        "전국 평균 대비 차이",
        f"{salary_delta:+,.0f}원",
    )

    filtered_members = filtered_data["member_count"].sum()
    filtered_average_salary = filtered_data["estimated_salary_per"].mean()
    if pd.isna(filtered_average_salary):
        filtered_average_salary = 0
    summary_columns = st.columns(4)
    summary_columns[0].metric("조건에 맞는 사업장 수", f"{len(filtered_data):,}")
    summary_columns[1].metric("조건에 맞는 가입자 수", f"{filtered_members:,.0f}")
    summary_columns[2].metric(
        "1인당 추정 월급여", f"{filtered_average_salary:,.0f}원"
    )
    summary_columns[3].metric(
        "가입자 순증감",
        f"{filtered_data['net_change'].sum():,.0f}명",
    )

    if filtered_data.empty:
        st.info("선택한 조건에 해당하는 등록 사업장이 없습니다.")
        return

    industry_data = filtered_data.assign(
        industry=filtered_data["industry"].fillna("미분류")
    )
    industry_company_counts = (
        industry_data.groupby("industry")
        .size()
        .nlargest(10)
        .sort_values()
        .rename("사업장 수")
        .rename_axis("industry")
        .reset_index()
    )
    company_count_fig = px.bar(
        industry_company_counts,
        x="사업장 수",
        y="industry",
        orientation="h",
        title="선택 시도 업종별 사업장 수 TOP 10",
        labels={"industry": "업종명"},
        category_orders={
            "industry": industry_company_counts["industry"].tolist(),
        },
    )
    company_count_fig.update_yaxes(categoryorder="array")

    industry_salary_averages = (
        industry_data.groupby("industry")["estimated_salary_per"]
        .mean()
        .nlargest(10)
        .sort_values()
        .rename("평균 추정 월급여")
        .rename_axis("industry")
        .reset_index()
    )
    salary_fig = px.bar(
        industry_salary_averages,
        x="평균 추정 월급여",
        y="industry",
        orientation="h",
        title="선택 시도 업종별 평균 추정 월급여 TOP 10",
        labels={"industry": "업종명"},
        text="평균 추정 월급여",
        category_orders={
            "industry": industry_salary_averages["industry"].tolist(),
        },
    )
    salary_fig.update_traces(
        texttemplate="%{x:,.0f}원",
        textposition="outside",
        cliponaxis=False,
    )
    salary_fig.add_vline(
        x=SALARY_CAP,
        line_dash="dash",
        line_color="red",
        annotation_text="기준소득 상한액",
        annotation_position="top",
    )
    company_chart_column, salary_chart_column = st.columns(2)
    company_chart_column.plotly_chart(
        company_count_fig, use_container_width=True
    )
    salary_chart_column.plotly_chart(salary_fig, use_container_width=True)

    chart_column, type_column = st.columns(2)
    industry_summary = (
        filtered_data.assign(industry=filtered_data["industry"].fillna("미분류"))
        .groupby("industry")["member_count"]
        .sum()
        .nlargest(10)
        .sort_values()
        .rename("가입자 수")
    )
    chart_column.subheader("업종별 가입자 수 TOP 10")
    chart_column.bar_chart(industry_summary)

    type_summary = (
        filtered_data["company_type"]
        .fillna("미분류")
        .value_counts()
        .rename_axis("사업장 형태")
        .rename("사업장 수")
    )
    type_column.subheader("사업장 형태별 사업장 수")
    type_column.bar_chart(type_summary)

    st.subheader("가입자 수 상위 사업장 TOP 10")
    top_companies = filtered_data.nlargest(10, "member_count")[
        ["company_name", "industry", "company_type", "member_count", "estimated_salary_per"]
    ].rename(
        columns={
            "company_name": "사업장명",
            "industry": "업종",
            "company_type": "사업장 형태",
            "member_count": "가입자 수",
            "estimated_salary_per": "1인당 추정 월급여",
        }
    )
    st.dataframe(
        top_companies,
        hide_index=True,
        width="stretch",
        column_config={
            "가입자 수": st.column_config.NumberColumn(format="%,d명"),
            "1인당 추정 월급여": st.column_config.NumberColumn(format="%,d원"),
        },
    )


if __name__ == "__main__":
    main()
