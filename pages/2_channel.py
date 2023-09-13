########################################################################################################################
##############################################     라이브러리 호출하기     ##################################################
########################################################################################################################
import streamlit as st
import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['XXX']).generate()
import yaml
from yaml.loader import SafeLoader
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
from utils import fn_sidebar, fn_status, fn_trends, generate_colors, generate_outsides, fig_hbarchart, fig_linechart
from utils import df_atd as df_chn

########################################################################################################################
################################################     인증페이지 설정     ###################################################
########################################################################################################################
# -----------------------------------------------------  사이드바  ---------------------------------------------------------
# 사이드바 헤더
st.sidebar.header("원하는 옵션을 선택하세요")
#사이드바 제작
month = fn_sidebar(df_chn,'월') # 월도 선택 사이드바
region = fn_sidebar(df_chn,'지역') # 지역 선택 사이드바
partner = fn_sidebar(df_chn,'보험사') # 보험사 선택 사이드바
line = fn_sidebar(df_chn,'과정형태') # 과정 온오프라인 선택 사이드바
theme = fn_sidebar(df_chn,'과정분류') # 과정 테마 선택 사이드바
name = fn_sidebar(df_chn,'과정명') # 세부과정 선택 사이드바
channel = fn_sidebar(df_chn,'소속부문') # 소속부문 선택 사이드바
career = fn_sidebar(df_chn,'입사연차') # 입사연차 선택 사이드바
# 데이터와 사이드바 연결
df_chn = df_chn.query(
    "월 == @month & 지역 == @region & 보험사 == @partner & 과정형태 == @line & 과정분류 == @theme & 과정명 == @name & 소속부문 == @channel & 입사연차 == @career"
)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status == None:
    st.warning('아이디와 패스워드를 입력해주세요')
if authentication_status == False:
    st.error('아이디와 패스워드를 확인해주세요')
if authentication_status:
    ########################################################################################################################
    ##################################################     자료 제작     #####################################################
    ########################################################################################################################
    # ------------------------------------------------  dataframe 제작  -----------------------------------------------------
    # barchart 제작을 위한 현황 dataframe (소속부문별)
    df_chn_stat = fn_status(df_chn, '소속부문')
    # linechart 제작을 위한 추세 dataframe (월별 & 소속부문별)
    df_chn_trnd = fn_trends(df_chn, '소속부문')

    # ------------------------------------------  차트 제작에 필요한 리스트 제작  ---------------------------------------------
    # 색상(hexcode) 제작
    chn_colors = generate_colors(df_chn_stat.shape[0])
    # 텍스트위치(outsides) 제작
    chn_outsides = generate_outsides(df_chn_stat.shape[0])
    # barchart 항목 순서 지정
    orders_chn_bar = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문'][::-1]
    # linechart 항목 순서 지정
    orders_chn_line = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문']

    # -------------------------------------------------  barchart 제작  ------------------------------------------------------
    # 차트에 필요한 리스트 제작
    barlist_chn = [
        [df_chn_stat, '소속부문', '신청인원', '신청누계', 'group', 'h', chn_colors, chn_outsides, orders_chn_bar, '부문별 교육신청 현황'],
        [df_chn_stat, '소속부문', '수료인원', '수료누계', 'group', 'h', chn_colors, chn_outsides, orders_chn_bar, '부문별 교육수료 현황'],
        [df_chn_stat, '소속부문', '수료율', '', 'single', 'h', chn_colors, chn_outsides, orders_chn_bar, '부문별 수료율'],
        [df_chn_stat, '소속부문', 'IMO신청률', '', 'single', 'h', chn_colors, chn_outsides, orders_chn_bar, '부문별 IMO신청률']
        ]
    # 막대그래프 (부문별 신청인원)
    bc_chn_apply = fig_hbarchart(barlist_chn[0])
    # 막대그래프 (부문별 수료인원)
    bc_chn_attend = fig_hbarchart(barlist_chn[1])
    # 막대그래프 (부문별 수료율)
    bc_chn_atdrate = fig_hbarchart(barlist_chn[2])
    # 막대그래프 (부문별 IMO신청률)
    bc_chn_imorate = fig_hbarchart(barlist_chn[3])

    # -------------------------------------------------  linechart 제작  ------------------------------------------------------
    linelist_chn = [
        [df_chn_trnd, '소속부문', '신청누계', '소속부문별 신청인원 추이 (신청누계 기준)', '월'],
        [df_chn_trnd, '소속부문', '수료누계', '소속부문별 수료인원 추이 (수료누계 기준)', '월'],
        [df_chn_trnd, '소속부문', '수료율', '소속부문별 수료율 추이', '월'],
        [df_chn_trnd, '소속부문', 'IMO신청률', '소속부문별 IMO신청률 추이', '월'],
    ]
    # 꺾은선그래피 (부문별 신청누계)
    lc_chn_apply = fig_linechart(linelist_chn[0])
    # 꺾은선그래피 (부문별 수료누계)
    lc_chn_attend = fig_linechart(linelist_chn[1])
    # 꺾은선그래피 (부문별 수료율)
    lc_chn_atdrate = fig_linechart(linelist_chn[2])
    # 꺾은선그래피 (부문별 IMO신청률)
    lc_chn_imorate = fig_linechart(linelist_chn[3])
    
    ########################################################################################################################
    ################################################     메인페이지 설정     ###################################################
    ########################################################################################################################
    authenticator.logout('Logout', 'sidebar')
    # --------------------------------------------------  페이지 타이틀  -------------------------------------------------------
    # 메인페이지 타이틀
    st.header("소속부문별 교육지표")

    # -----------------------------------------------------  차트 노출  ---------------------------------------------------------
    # 첫번째 행 (신청인원)
    r1_c1, r1_c2 = st.columns(2)
    r1_c1.plotly_chart(bc_chn_apply, use_container_width=True)
    # 두번째 행 (수료인원)
    r2_c1, r2_c2 = st.columns(2)
    r2_c1.plotly_chart(bc_chn_attend, use_container_width=True)
    # 세번째 행 (수료율 & IMO신청률)
    r3_c1, r3_c2 = st.columns(2)
    r3_c1.plotly_chart(bc_chn_atdrate, use_container_width=True)
    r3_c2.plotly_chart(bc_chn_imorate, use_container_width=True)

    # 추이그래프 (신청누계, 수료누계, 수료율, IMO신청률)
    st.plotly_chart(lc_chn_apply, use_container_width=True)
    st.plotly_chart(lc_chn_attend, use_container_width=True)
    st.plotly_chart(lc_chn_atdrate, use_container_width=True)
    st.plotly_chart(lc_chn_imorate, use_container_width=True)

    ########################################################################################################################
    ###########################################     stremalit 워터마크 숨기기     ##############################################
    ########################################################################################################################
    hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)