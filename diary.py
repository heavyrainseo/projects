import os
from datetime import date

import pandas as pd
import streamlit as st


DIARY_FILE = "diary.csv"
DIARY_COLUMNS = ["날짜", "제목", "내용", "날씨"]

st.title("📔 나의 일기장")

title = st.text_input("제목")
content = st.text_area("내용", height=150)
weather = st.selectbox("오늘의 날씨", ["맑음", "흐림", "비", "눈", "바람"])

if st.button("저장"):
    new_entry = pd.DataFrame(
        [
            {
                "날짜": date.today().isoformat(),
                "제목": title,
                "내용": content,
                "날씨": weather,
            }
        ],
        columns=DIARY_COLUMNS,
    )

    if os.path.exists(DIARY_FILE):
        saved_entries = pd.read_csv(DIARY_FILE, encoding="utf-8-sig")
        diary = pd.concat([saved_entries, new_entry], ignore_index=True)
    else:
        diary = new_entry

    diary.to_csv(DIARY_FILE, index=False, encoding="utf-8-sig")
    st.success("일기가 저장되었습니다!")

st.subheader("저장된 일기")
if os.path.exists(DIARY_FILE):
    st.dataframe(pd.read_csv(DIARY_FILE, encoding="utf-8-sig"))
else:
    st.write("아직 작성된 일기가 없어요.")
