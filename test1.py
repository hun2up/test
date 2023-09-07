####################################################################################################
####################################     라이브러리 호출하기     #####################################
####################################################################################################
import pandas as pd
import streamlit as st
import plotly as pl
from datetime import datetime

####################################################################################################
###################################     페이지 기본정보 설정     #####################################
####################################################################################################
# 페이지 설정
# emoji : https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)
# 메인페이지 타이틀
st.header(":bar_chart: 인카금융서비스 교육과정 대시보드")
st.subheader("주요지표현황")
st.markdown("##")
st.markdown("---")

####################################################################################################
###############################     출석부 데이터베이스 불러오기     #################################
####################################################################################################
# ------------------------------------- 데이터베이스 호출 --------------------------------------------
# Read in data from the Google Sheet.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

df_attend = load_data(st.secrets["attend_url"])
df_course = load_data(st.secrets["course_url"])
df_today = load_data(st.secrets("today_url"))

####################################################################################################
#########################################     자료정리     #########################################
####################################################################################################
# ------------------- 교육과정수료현황 테이블 정리 ----------------------------------=
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
    date_object = pd.to_datetime(df_course.at[date_index, '교육일자'], format="%Y. %m. %d")
    month = date_object.month
    df_course.at[date_index, '교육일자'] = f'{month}월'
# ------------------- 교육수료현황 테이블 & 과정현황 테이블 병함 ----------------------------------
df_course['과정코드'] = df_course['과정코드'].astype(str)
df_attend['과정코드'] = df_attend['과정코드'].astype(str)
df_database = pd.merge(df_course, df_attend, on=['과정코드'])
df_database.rename(columns={'교육일자':'월'}, inplace=True)

####################################################################################################
####################################     필요한 함수 정의     #######################################
####################################################################################################
# -------------------------------------- 사이드바 제작 함수 ------------------------------------------
def func_sidebar(select_dataframe, select_column):
    return st.sidebar.multiselect(
        select_column,
        options=select_dataframe[select_column].unique(),
        default=select_dataframe[select_column].unique()
    )

# ----------------------------- 고유값과 누계값을 구해주는 함수 ----------------------------------------
# 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청인원, IMO신청누계, IMO신청률
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

# ----- Bar Chart 제작 함수 (bar_type : 'Basic Bar Chart'이면 True, 'Grouped Bar Chart'이면 False) -----
# bar_type: True/False, bar_number_unique: , bar_number_total: , bar_reference: 
# bar_hexcodes: 차트 색상 지정을 위한 헥스코드 리스트, bar_orders: 차트 항목(축)별 순서 지정을 위한 리스트, list_outside: 'outside'를 항목 개수만큼 넣은 리스트
def fig_barchart(df, bar_type, bar_number_unique, bar_number_total, bar_reference, bar_title, bar_hexcodes, bar_orders, bar_outsides):
    # Basic Bar Chart 만들기
    if bar_type == True :
        fig_basicbar = pl.graph_objs.Bar(
            x=df[bar_number_unique],
            y=df[bar_number_total],
            width=0.3,
            name=bar_number_total,
            text=df[bar_number_unique],
            marker={'color':bar_hexcodes}, # 여기수정
            orientation='h'
        )
        data_bar_basic = [fig_basicbar]
        layout_bar_basic = pl.graph_objs.Layout(title=bar_reference,yaxis={'categoryorder':'array', 'categoryarray':bar_orders}) # 여기수정
        return_bar_basic = pl.graph_objs.Figure(data=data_bar_basic,layout=layout_bar_basic)
        return_bar_basic.update_traces(textposition=bar_outsides) #여기수정
        return_bar_basic.update_layout(showlegend=False) 
        return return_bar_basic
    # Grouped Bar Chart 만들기
    else :
        fig_groupbar1 = pl.graph_objs.Bar(
            x=df[bar_number_unique],
            y=df[bar_reference],
            name=bar_number_unique,
            text=df[bar_number_unique],
            marker={'color':'grey'},
            orientation='h'
        )
        fig_groupbar2 = pl.graph_objs.Bar(
            x=df[bar_number_total],
            y=df[bar_reference],
            name=bar_number_total,
            text=df[bar_number_total],
            marker={'color':bar_hexcodes}, # 여기수정
            orientation='h'
        )
        data_bar_group = [fig_groupbar1, fig_groupbar2]
        layout_bar_group = pl.graph_objs.Layout(title=bar_title,yaxis={'categoryorder':'array', 'categoryarray':bar_orders})
        return_bar_group = pl.graph_objs.Figure(data=data_bar_group,layout=layout_bar_group)
        return_bar_group.update_traces(textposition=bar_outsides) #여기수정
        return_bar_group.update_layout(showlegend=False)
        return return_bar_group
def fig_linechart(numbers, line_reference, line_title):
    fig_line = pl.graph_objs.Figure()
    # Iterate over unique channels and add a trace for each
    for reference in df_monthly(line_reference)[line_reference].unique():
        line_data = df_monthly(line_reference)[df_monthly(line_reference)[line_reference] == reference]
        fig_line.add_trace(pl.graph_objs.Scatter(
            x=line_data['월'],
            y=line_data[numbers],
            mode='lines+markers',
            name=reference
        ))
    # Update the layout
    fig_line.update_layout(
        title=line_title,
        xaxis_title='월',
        yaxis_title=numbers,
        legend_title=line_reference,
        hovermode='x',
        template='plotly_white'  # You can choose different templates if you prefer
    )
    return fig_line

####################################################################################################
################################     straemlit 워터마크 숨기기     ##################################
####################################################################################################
hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)
