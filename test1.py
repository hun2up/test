####################################################################################################
####################################     라이브러리 호출하기     #####################################
####################################################################################################
import pandas as pd
import streamlit as st
import plotly as pl
from datetime import datetime
import sqlalchemy as sql

####################################################################################################
###############################     출석부 데이터베이스 불러오기     #################################
####################################################################################################
# ------------------------------------- 데이터베이스 호출 --------------------------------------------
# MySQL 데이터베이스 접속
db_connection_str = 'mysql+pymysql://freedb_hun2up:u!jZQ7n7g38*$AU@sql.freedb.tech:3306/freedb_incar_edu'
db_connection = sql.create_engine(db_connection_str)
# 출석부 테이블과 과정 테이블을 조인
sql_query = """
    SELECT c.*, a.*
    FROM course c
    JOIN attendance a
    ON c.course_code = a.course_code
"""
# dataframe 생성
df_database = pd.read_sql(sql_query, con=db_connection)
# MySQL 데이터베이스 연결 해제
db_connection.dispose()

# -------------------------------------------- 자료정리 ---------------------------------------------
# JOIN한 dataframe의 전체 row 계산
num_rows = df_database.shape[0]
# course_date column의 날짜 값을 '월' 값으로 변환
for date_index in range(num_rows):
    date_object = pd.to_datetime(df_database.at[date_index, 'course_date'])
    month = date_object.month
    df_database.at[date_index, 'course_date'] = f'{month}월'
# '입사연차' 칼럼 추가
df_database['career'] = (datetime.now().year%100 + 1 - df_database['id'].astype(str).str[:2].astype(int, errors='ignore')).apply(lambda x: f'{x}년차')
# '번호' 컬럼 날리기
df_database = df_database.drop(columns=['number'])
# 컬럼 재정렬
df_database = df_database[['course_code',
    'course_theme',
    'course_name',
    'course_partner',
    'course_date',
    'course_line',
    'course_fee',
    'course_region',
    'course_place',
    'course_capacity',
    'course_target',
    'course_code',
    'channel',
    'department',
    'branch',
    'team',
    'id',
    'name',
    'imo',
    'attend',
    'career',
    'memo']]
# column 한글로 변환
df_database.rename(columns={
    'course_code':'과정코드',
    'course_theme':'과정분류',
    'course_name':'과정명',
    'course_partner':'보험사',
    'course_date':'월',
    'course_line':'과정형태',
    'course_fee':'수강료',
    'course_region':'지역',
    'course_place':'교육장소',
    'course_capacity':'정원',
    'course_target':'목표인원',
    'course_code':'과정코드',
    'channel':'소속부문',
    'department':'소속총괄',
    'branch':'소속부서',
    'team':'파트너',
    'id':'사원번호',
    'name':'성명',
    'imo':'IMO신청여부',
    'attend':'수료현황',
    'career':'입사연차',
    'memo':'비고'}, inplace=True)
df_database = df_database[df_database['소속부문'] != '마케팅부문']

# IMO신청여부를 Y/N 에서 1/0으로 변경
df_database['IMO신청여부'] = df_database['IMO신청여부'].replace({'Y':1, 'N':0})
# 수료현황 데이터를 숫자로 변환
df_database['수료현황'] = pd.to_numeric(df_database['수료현황'], errors='coerce')
####################################################################################################
####################################     필요한 함수 정의     #######################################
####################################################################################################

def df_basic(column_reference):
    # df_database를 '소속부문', '사원번호' 칼럼으로 묶고, 누적개수 구하기
    df_func_basic_apply = df_database.groupby([column_reference,'사원번호']).size().reset_index(name='신청누계')
    # df_func_number에서 묶여있는 '사원번호' 카운트 (중복값 제거한 인원)
    df_func_basic_apply_unique = df_func_basic_apply.groupby([column_reference])['사원번호'].count().reset_index(name='신청인원')
    # df_func_number에서 '누적개수' 카운트 (중복값 더한 인원)
    df_func_basic_apply_total = df_func_basic_apply.groupby([column_reference])['신청누계'].sum().reset_index(name='신청누계')
    # 위에서 중복값을 제거한 데이터프레임과 모두 더한 데이터프레임 병합
    df_func_basic_apply = pd.merge(df_func_basic_apply_unique, df_func_basic_apply_total)

    # 수료인원, 수료누계, IMO신청인원, IMO신청누계
    basic_index = [['수료현황', '수료인원', '수료누계', '수료율'], ['IMO신청여부', 'IMO신청인원', 'IMO신청누계', 'IMO신청률']]
    for basic_get_group in range(len(basic_index)):
        # 수료현황, IMO신청여부 1로 묶기
        df_for_basic = df_database.groupby(basic_index[basic_get_group][0]).get_group(1)
        # 수료현황 전체 더하기 (수료누계)
        df_for_basic_total = df_database.groupby([column_reference])[basic_index[basic_get_group][0]].sum().reset_index(name=basic_index[basic_get_group][2])
        # 수료현황(1,0)별 사원번호 개수 (수료인원)
        df_for_basic_unique = df_database.groupby([column_reference,basic_index[basic_get_group][0]])['사원번호'].nunique().reset_index(name=basic_index[basic_get_group][1])
        # 수료현항 0인 row 날리기
        df_for_basic_unique = df_for_basic_unique[df_for_basic_unique[basic_index[basic_get_group][0]] != 0]
        # 수료현황 column 날리기
        df_for_basic_unique = df_for_basic_unique.drop(columns=[basic_index[basic_get_group][0]])
        # 수료인원이랑 수료누계 합치기
        df_for_basic = pd.merge(df_for_basic_unique, df_for_basic_total, on=[column_reference])
        # 수료율
        df_for_basic_total[basic_index[basic_get_group][3]] = (df_for_basic_total[basic_index[basic_get_group][2]]/df_func_basic_apply['신청누계']*100).round(1)
        df_for_basic_total = df_for_basic_total.drop(columns=[basic_index[basic_get_group][2]])
        # 수료율/IMO신청률 합치기
        df_for_basic = pd.merge(df_for_basic, df_for_basic_total, on=[column_reference])
        df_func_basic_apply = pd.merge(df_func_basic_apply, df_for_basic, on=[column_reference])
        basic_get_group += 1

    # 다 합쳐서 반환
    return df_func_basic_apply

# 월별, 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
def df_monthly(column_reference):
    # 월, 소속부문, 사원번호, 그리고 신청누계(추가)
    df_func_monthly_apply = df_database.groupby(['월',column_reference,'사원번호']).size().reset_index(name='신청누계')
    # 월, 소속부문, 그리고 신청인원 (df_func_monthly에서 사원번호 중복제거) (추가)
    df_func_monthly_apply_unique = df_func_monthly_apply.groupby(['월',column_reference])['사원번호'].count().reset_index(name='신청인원')
    # 월, 소속부문, 신청인원 (df_func_monthly에서 사원번호 없애고 신청누계 다 더하기)
    df_func_monthly_apply_total = df_func_monthly_apply.groupby(['월',column_reference])['신청누계'].sum().reset_index(name='신청누계')
    # 월, 소속부문, 신청누계, 신청인원 (df_func_unique와 df_func_total 합치기)
    df_func_monthly_apply = pd.merge(df_func_monthly_apply_total, df_func_monthly_apply_unique, on=['월',column_reference])

    # 수료인원, 수료누계, IMO신청인원, IMO신청누계
    monthly_index = [['수료현황', '수료인원', '수료누계', '수료율'], ['IMO신청여부', 'IMO신청인원', 'IMO신청누계', 'IMO신청률']]
    for monthly_get_group in range(len(monthly_index)):
        # 수료현황, IMO신청여부 1로 묶기
        df_for_monthly = df_database.groupby(monthly_index[monthly_get_group][0]).get_group(1)
        # 수료현황(1,0)별 사원번호 개수 (수료인원)
        df_for_monthly_unique = df_database.groupby(['월',column_reference,monthly_index[monthly_get_group][0]])['사원번호'].count().reset_index(name=monthly_index[monthly_get_group][1])
        # 수료현항 0인 row 날리기
        df_for_monthly_unique = df_for_monthly_unique[df_for_monthly_unique[monthly_index[monthly_get_group][0]] != 0]
        # 수료현황 column 날리기
        df_for_monthly_unique = df_for_monthly_unique.drop(columns=[monthly_index[monthly_get_group][0]])
        # 수료현황 전체 더하기 (수료누계)
        df_for_monthly_total = df_database.groupby(['월',column_reference])[monthly_index[monthly_get_group][0]].sum().reset_index(name=monthly_index[monthly_get_group][2])
        # 수료율
        df_for_monthly_total[monthly_index[monthly_get_group][3]] = (df_for_monthly_total[monthly_index[monthly_get_group][2]]/df_func_monthly_apply['신청누계']*100).round(1)
        # 수료인원이랑 수료누계 합치기
        df_for_monthly = pd.merge(df_for_monthly_unique, df_for_monthly_total, on=['월',column_reference])
        df_func_monthly_apply = pd.merge(df_func_monthly_apply, df_for_monthly, on=['월',column_reference])
        monthly_get_group += 1
        
    # 다 합쳐서 반환
    return df_func_monthly_apply

print(df_monthly('소속부문'))