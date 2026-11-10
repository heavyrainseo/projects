import os

import pandas as pd
import streamlit as st


APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_DIR, "data")
INPUT_PATH = os.path.join(DATA_DIR, "pension_raw.csv")
OUTPUT_PATH = os.path.join(DATA_DIR, "cleaned_pension.csv")

STATUS_COLUMN = "사업장가입상태코드 1 등록 2 탈퇴"
TYPE_COLUMN = "사업장형태구분코드 1 법인 2 개인"

REQUIRED_COLUMNS = [
    "사업장명",
    STATUS_COLUMN,
    "사업장도로명상세주소",
    "법정동주소광역시도코드",
    "사업장업종코드명",
    "가입자수",
    "당월고지금액",
    TYPE_COLUMN,
    "신규취득자수",
    "상실가입자수",
]


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    try:
        return pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="utf-8-sig")


def preview_step(step_name: str, message: str, data: pd.DataFrame) -> None:
    with st.expander(step_name, expanded=True):
        st.success(message)
        st.dataframe(data.head(10), width="stretch")


def main() -> None:
    st.set_page_config(page_title="국민연금 사업장 데이터 전처리", layout="wide")
    st.title("📋 국민연금 사업장 데이터 전처리")

    try:
        raw_data = load_data(INPUT_PATH)
    except FileNotFoundError:
        st.error(f"원본 CSV 파일을 찾을 수 없습니다: {INPUT_PATH}")
        st.stop()

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in raw_data.columns]
    if missing_columns:
        st.error(f"원본 CSV에 필요한 컬럼이 없습니다: {', '.join(missing_columns)}")
        st.stop()

    stage_previews: list[tuple[str, str, pd.DataFrame]] = [
        ("1단계. CSV 읽기", f"원본 CSV를 읽었습니다. 전체 {len(raw_data):,}행입니다.", raw_data.head(10))
    ]

    data = raw_data.loc[:, REQUIRED_COLUMNS].copy()
    stage_previews.append(
        (
            "2단계. 필요한 컬럼만 선택",
            f"후속 전처리에 필요한 {len(REQUIRED_COLUMNS)}개 컬럼만 선택했습니다.",
            data.head(10),
        )
    )

    data = data.rename(
        columns={
            "사업장명": "company_name",
            STATUS_COLUMN: "status_code",
            "사업장도로명상세주소": "address",
            "법정동주소광역시도코드": "sido_code",
            "사업장업종코드명": "industry",
            "가입자수": "member_count",
            "당월고지금액": "charge_amount",
            TYPE_COLUMN: "type_code",
            "신규취득자수": "new_members",
            "상실가입자수": "lost_members",
        }
    )
    stage_previews.append(
        ("3단계. 컬럼명 영문으로 변경", "선택한 컬럼명을 영문으로 변경했습니다.", data.head(10))
    )

    data["status"] = data["status_code"].map({1: "등록", 2: "탈퇴"})
    data["company_type"] = data["type_code"].map({1: "법인", 2: "개인"})
    data = data.drop(columns=["status_code", "type_code"])
    stage_previews.append(
        (
            "4단계. 코드값을 텍스트로 변환",
            "가입 상태와 사업장 형태 코드를 텍스트로 변환했습니다.",
            data.head(10),
        )
    )

    data["sido"] = data["address"].str.split().str[0]
    data = data.drop(columns=["address", "sido_code"])
    stage_previews.append(
        ("5단계. 시도명 추출", "도로명 주소에서 시도명을 추출했습니다.", data.head(10))
    )

    numeric_columns = [
        "member_count",
        "charge_amount",
        "new_members",
        "lost_members",
    ]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)
    stage_previews.append(
        (
            "6단계. 숫자 컬럼 타입 변환",
            "가입자·고지 금액·신규 취득·상실 가입자 컬럼을 숫자형으로 변환했습니다. "
            "변환할 수 없는 값은 0으로 처리했습니다.",
            data.head(10),
        )
    )

    data["estimated_salary_total"] = data["charge_amount"] / 0.095
    data["estimated_salary_per"] = (
        data["estimated_salary_total"]
        .div(data["member_count"])
        .where(data["member_count"].ne(0), 0)
    )
    data["net_change"] = data["new_members"] - data["lost_members"]
    stage_previews.append(
        ("7단계. 파생 컬럼 생성", "추정 급여와 순증감 컬럼을 생성했습니다.", data.head(10))
    )

    data = data.loc[
        (data["status"] == "등록")
        & (data["member_count"] > 0)
        & (data["charge_amount"] > 0)
    ].copy()
    stage_previews.append(
        (
            "8단계. 이상값 처리",
            f"등록 상태이며 가입자 수와 당월 고지 금액이 0보다 큰 행만 유지했습니다. "
            f"남은 행: {len(data):,}개",
            data.head(10),
        )
    )

    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        data.to_csv(OUTPUT_PATH, encoding="utf-8", index=False)
    except OSError as error:
        st.error(f"전처리 결과를 저장하지 못했습니다: {error}")
        st.stop()

    stage_previews.append(
        (
            "9단계. 전처리 결과 저장",
            f"전처리된 데이터를 저장했습니다: {OUTPUT_PATH}",
            data.head(10),
        )
    )

    before_metric, after_metric = st.columns(2)
    before_metric.metric("전처리 전 행 수", f"{len(raw_data):,}")
    after_metric.metric("전처리 후 행 수", f"{len(data):,}")

    for step_name, message, preview in stage_previews:
        preview_step(step_name, message, preview)

    st.success("cleaned_pension.csv 저장이 완료되었습니다.")

    st.subheader("전처리 데이터 기본 통계")
    total_salary = data["estimated_salary_total"].sum()
    total_members = data["member_count"].sum()
    overall_salary_per_member = total_salary / total_members if total_members else 0

    total_companies, sido_count, member_count, average_salary = st.columns(4)
    total_companies.metric("총 사업장 수", f"{len(data):,}")
    sido_count.metric("시도 수", f"{data['sido'].nunique():,}")
    member_count.metric("총 가입자 수", f"{total_members:,.0f}")
    average_salary.metric("전체 1인당 추정 평균 월급여", f"{overall_salary_per_member:,.0f}원")


if __name__ == "__main__":
    main()
