[Agent 모드 프롬프트]

pension.py를 국민연금 사업장 분석 대시보드로 새로 작성해줘.
Chapter 14에서 만든 cleaned_pension.csv를 사용해.

[기본 설정]
- 파일 경로: data/cleaned_pension.csv
- encoding: utf-8-sig
- st.set_page_config: 페이지 제목 "📋 국민연금 사업장 분석 대시보드", layout="wide"
- @st.cache_data로 데이터 로딩 최적화
- 국민연금 보험료율 상수: PENSION_RATE = 0.095
- 기준소득 상한액 상수: SALARY_CAP = 6_590_000

[상단 전국 요약 지표]
아래 4개의 st.metric을 한 행에 나란히 표시해줘.
- 총 등록 사업장 수
- 총 가입자 수 (천 단위 쉼표 포함)
- 전국 평균 1인당 추정 월급여 (천 단위 쉼표, "원" 단위)
- 데이터 기준 연월 (year_month 컬럼의 최신 값)

[사이드바]
사이드바에 아래 두 섹션을 만들어줘.

섹션 1. 지역 선택
- 시도 selectbox (sido 컬럼 고유값으로 선택지 구성, 가나다 정렬)

섹션 2. 분석 필터
- 사업장 형태 selectbox: "전체", "법인", "개인"
- 최소 가입자 수 slider: 1 ~ 100, 기본값 1

이 기본 구조만 먼저 만들어줘.
코드 전체를 pension.py에 작성해줘.

여기까지만 만들었어. 계속 코딩해 줘
