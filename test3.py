from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 구글 스프레드시트 접속
url = "https://docs.google.com/spreadsheets/d/1AG89W1nwRzZxYreM6i1qmwS6APf-8GM2K_HDyX7REG4/edit?usp=sharing"
conn = st.experimental_connection("gsheets", type=GSheetsConnection)
# df_attend = 교육과정수료현황 / df_course = 과정현황
df_attend = conn.read(spreadsheet=url, usecols=list(range(11)), worksheet="0")
df_course = conn.read(spreadsheet=url, usecols=list(range(12)), worksheet="591706408")

# ------------------- 교육과정수료현황 테이블 정리 ----------------------------------
# '과정코드' 컬럼 부여하기
df_attend.insert(loc=1, column='과정코드', value=None)
# '과정코드'를 정리해 봅시다.
for modify in range(df_attend.shape[0]):
    df_attend.iloc[modify,1] = df_attend.iloc[modify,2].split(")")[0].replace('(','')
# '과정명' 컬럼 날리기
df_attend = df_attend.drop(columns=['번호','과정명','비고'])
# IMO신청여부를 Y/N 에서 1/0으로 변경
df_attend['IMO신청여부'] = df_attend['IMO신청여부'].replace({'Y':1, 'N':0})
# 수료현황 데이터를 숫자로 변환
df_attend['수료현황'] = pd.to_numeric(df_attend['수료현황'], errors='coerce')
# '입사연차' 칼럼 추가
df_attend['입사연차'] = (datetime.now().year%100 + 1 - df_attend['사원번호'].astype(str).str[:2].astype(int, errors='ignore')).apply(lambda x: f'{x}년차')
# '파트너'가 '인카본사'인 사람도 없애줍시당
df_attend = df_attend.drop(df_attend[df_attend.iloc[:,4] == '인카본사'].index)
# ------------------- 과정현황 테이블 정리 ----------------------------------
# '과정명' 컬럼 날리기
df_course = df_course.drop(columns=['번호'])
# JOIN한 dataframe의 전체 row 계산
num_rows = df_course.shape[0]
# course_date column의 날짜 값을 '월' 값으로 변환
for date_index in range(num_rows):
    date_object = pd.to_datetime(df_course.at[date_index, '교육일자'])
    month = date_object.month
    df_course.at[date_index, '교육일자'] = f'{month}월'
# ------------------- 교육수료현황 테이블 & 과정현황 테이블 병함 ----------------------------------
df_course['과정코드'] = df_course['과정코드'].astype(str)
df_attend['과정코드'] = df_attend['과정코드'].astype(str)
df_database = pd.merge(df_course, df_attend, on=['과정코드'])
print(df_database)