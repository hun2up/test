# ------------------ 소속부문 및 입사연차별 신청인원(누계), 수료인원(누계) 집계 -----------------
df_crr_app = df_numbers(df_edu, '신청누계', '신청인원', '입사연차') # 입사연차별 신청인원 및 신청누계
df_com = df_edu.groupby('수료현황').get_group(1) # 수료현황이 '1'인 FA들로 재정렬
df_crr_com = df_numbers(df_com, '수료누계', '수료인원', '입사연차') # 입사연차별 수료인원 및 수료누계
# ---------- 소속부문 및 입사연차별 신청인원 데이터프레임과 수료인원 데이터프레임 병합 -----------
df_crr_numbers = pd.merge(df_crr_app, df_crr_com) # 입사연차별 신청인원, 신청누계, 수료인원, 수료누계



# ---------------------------- 수료율과 IMO신청률을 구해주는 함수 ----------------------------
# rt1 : 수료율/IMO신청률, rt2 : 수료누계/IMO신청누계, rt3 : 수료현황/IMO접수여부, rt4 : 소속부문/입사연차
def df_rates(df, rt1, rt2, rt3, rt4):
    df_func2 = pd.merge(df, df_selection\
        .groupby([rt4])[rt3]\
        .sum()\
        .reset_index(name=rt2),
        on=[rt4])
    df_func2[rt1] = df_func2[rt2]/df_func2['신청누계']*100
    df_func2[rt1] = df_func2[rt1].round(1)
    return df_func2
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ---------------- 소속부문 및 입사연차별 수료율, IMO신청누계 및 IMO신청률 집계 ----------------
df_chn_comrate = df_rates(df_chn_app, '수료율', '수료누계', '수료현황', '소속부문') # 위에서 제작한 소속부문별 dataframe에 수료율 붙이기
df_chn_imorate = df_rates(df_chn_app, 'IMO신청률', 'IMO신청누계', 'IMO접수여부', '소속부문') # 위에서 제작한 소속부문별 dataframe에 IMO신청누계 및 IMO신청률 붙이기
# ▼
df_chn_rate = pd.merge(df_chn_comrate, df_chn_imorate) # 위의 수료율과 IMO신청누계 및 IMO신청률 붙인 dataframe 합치기

df_crr_comrate = df_rates(df_crr_app, '수료율', '수료누계', '수료현황', '입사연차') # 위에서 제작한 입사연차별 dataframe에 수료율 붙이기
df_crr_imorate = df_rates(df_crr_app, 'IMO신청률', 'IMO신청누계', 'IMO접수여부', '입사연차') # 위에서 제작한 입사연차별 dataframe에 IMO신청누계 및 IMO신청률 붙이기
# ▼
df_crr_rate = pd.merge(df_crr_comrate, df_crr_imorate) # 위의 수료율과 IMO신청누계 및 IMO신청률 붙인 dataframe 합치기
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# 소속부문별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청누계, IMO신청률
# 입사연차별 신청인원, 신청누계, 수료인원, 수료누계, 수료율, IMO신청누계, IMO신청률



# 월별 수료율과 IMO신청률을 구해주는 함수 (신청인원, 신청누계, 수료누계, 수료율, IMO신청누계, IMO신청률)
# rt1 : 수료율/IMO신청률, rt2 : 수료누계/IMO신청누계, rt3 : 수료현황/IMO접수여부, rt4 : 소속부문/입사연차
def df_monthly(rt1, rt2, rt3, rt4):
    df_func3 = df_selection\
        .groupby(['월',rt4,'사원번호'])\
        .size()\
        .reset_index(name='신청누계')
    fn3_absolute = df_func3\
        .groupby(['월',rt4])['사원번호']\
        .count()\
        .reset_index(name='신청인원')
    fn3_cumulative = df_func3\
        .groupby(['월',rt4])['신청누계']\
        .sum()\
        .reset_index(name='신청누계')
    df_func3 = pd.merge(
        fn3_absolute, fn3_cumulative, on=['월',rt4]
    )
    df_func4 = pd.merge(df_func3, df_selection.groupby(['월', rt4])[rt3].sum().reset_index(name=rt2), on=['월', rt4])
    df_func4[rt1] = df_func4[rt2]/df_func3['신청누계']*100
    df_func4[rt1] = df_func4[rt1].round(1)
    return df_func4
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------
# ------------- 월별(소속부문별/입사연차별) 수료율, IMO신청누계 및 IMO신청률 집계 --------------
df_chn_comrate_month = df_monthly('수료율', '수료누계', '수료현황', '소속부문') # 월별(소속부문별) 신청인원, 신청누계, 수료누계, 수료율
df_chn_imorate_month = df_monthly('IMO신청률', 'IMO신청누계', 'IMO접수여부', '소속부문') # 월별(소속부문별) 소속부문별 신청인원, 신청누계, 수료누계, IMO신청누계, IMO신청률
# ▼
df_chn_rate_month = pd.merge(df_chn_comrate_month, df_chn_imorate_month, on=['월','소속부문','신청인원','신청누계']) # 위의 두 dataframe 합치기

df_crr_comrate_month = df_monthly('수료율', '수료누계', '수료현황', '입사연차') # 월별(입사연차별) 신청인원, 신청누계, 수료누계, 수료율
df_crr_imorate_month = df_monthly('IMO신청률', 'IMO신청누계', 'IMO접수여부', '입사연차') # 월별(입사연차별) 신청인원, 신청누계, 수료누계, IMO신청누계 IMO신청률
# ▼
df_crr_rate_month = pd.merge(df_crr_comrate_month, df_crr_imorate_month, on=['월','입사연차','신청인원','신청누계']) # 위의 두 dataframe 합치기
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------



# -------------------------- 전체현황 집계 (페이지 상단 요약보고) ----------------------------
df_total_app = df_numbers(df_selection, '신청누계', '신청인원', '월') # 월별 신청인원 및 신청누계
df_total_com = df_numbers(df_com, '수료누계', '수료인원', '월') # 월별 수료인원 및 수료누계
# ▼
df_total_month = pd.merge(df_total_app, df_total_com) # 위 두 dataframe 합치기 (월별 신청인원, 신청누계, 수료인원, 수료누계)

# 이게 뭘 의미하는지 모르겠음...(망함)
df_total = df_selection\
        .groupby(['월','사원번호'])\
        .size()\
        .reset_index(name='신청누계')
tt3_absolute = df_total\
        .groupby(['월'])['사원번호']\
        .count()\
        .reset_index(name='신청인원')
tt3_cumulative = df_total\
        .groupby(['월'])['신청누계']\
        .sum()\
        .reset_index(name='신청누계')
df_total = pd.merge(
        tt3_absolute, tt3_cumulative, on=['월']
)
# ----------------------------------

df_total_comrate = pd.merge(df_total, df_selection.groupby(['월'])['수료현황'].sum().reset_index(name='수료누계'), on=['월'])
df_total_comrate['수료율'] = df_total_comrate['수료누계']/df_total['신청누계']*100
df_total_comrate['수료율'] = df_total_comrate['수료율'].round(1)

df_total_imorate = pd.merge(df_total, df_selection.groupby(['월'])['IMO접수여부'].sum().reset_index(name='IMO신청누계'), on=['월'])
df_total_imorate['IMO신청률'] = df_total_imorate['IMO신청누계']/df_total['신청누계']*100
df_total_imorate['IMO신청률'] = df_total_imorate['IMO신청률'].round(1)

df_total_merge = pd.merge(df_total_comrate, df_total_imorate)
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------



####################################################################################################
#######################################     메인페이지     ##########################################
####################################################################################################

# ------------------------------ 메인페이지 (메인 차트 부분) ------------------------------

# 차트에 사용할 부문별 색상과 순서를 미리 지정
colors_channel = ['#F3BE64', '#F55700', '#32A77B', '#007BD0', '#EDA9AC', '#6A7BE0']
orders_channel_line = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문']
orders_channel_bar = ['개인부문', '전략부문', 'CA부문', 'MA부문', 'PA부문', '다이렉트부문'][::-1]


# Line Chart 제작 함수
def fig_linechart(df, lc1, lc2, lc3, lc4):
    fig_line = px.line(
        df,
        x=lc1,
        y=lc2,
        color=lc3,
        markers=True,
        orientation='h',
        title=lc4,
        text=lc2,
        category_orders={lc3 : orders_channel_line},
        color_discrete_sequence=colors_channel
    )
    fig_line.update_traces(textposition='top center')
    fig_line.update_layout(hovermode="x")
    return fig_line

# 전체현황 그래프
fig_total_com = go.Scatter(
    x=df_total_merge['월'],
    y=df_total_merge['수료누계'],
    mode='lines+markers+text',
    name='수료인원',
    text=df_total_merge['수료누계'],
    textposition='top center'
)
fig_total_comrate = go.Scatter(
    x=df_total_merge['월'],
    y=df_total_merge['수료율'],
    mode='lines+markers+text',
    name='수료율',
    text=df_total_merge['수료율']\
        .apply(lambda x: str(round(x, 2))+'%'),
    textposition='top center',
    yaxis='y2'
)
fig_total_imorate = go.Scatter(
    x=df_total_merge['월'],
    y=df_total_merge['IMO신청률'],
    mode='lines+markers+text',
    name='IMO신청률',
    text=df_total_merge['IMO신청률']\
        .apply(lambda x: str(round(x, 2))+'%'),
    textposition='top center',
    yaxis='y2'
)
data_total = [fig_total_com, fig_total_comrate, fig_total_imorate]
layout_total = go.Layout(title="월별 전체현황")
fig_total = go.Figure(data=data_total,layout=layout_total)
fig_total.update_layout(yaxis2=dict(title='수료율/INO신청률',overlaying='y',side='right'),hovermode='x')
# ------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------



# ------------------------------ 메인차트 (부문별) ------------------------------


# 소속부문별 추이 종합
fig_chn_com_monthly = fig_linechart(df_chn_rate_month, '월', '수료누계', '소속부문', '<b>소속부문별 수료인원 추이</b>') # 소속부문별 교육수료 인원 추이
fig_chn_comrate_monthly = fig_linechart(df_chn_rate_month, '월', '수료율', '소속부문', '<b>소속부문별 수료율 추이</b>') # 소속부문별 수료율 추이
fig_chn_imorate_monthly = fig_linechart(df_chn_rate_month, '월', 'IMO신청률', '소속부문', '<b>소속부문별 IMO신청률 추이</b>') # 소속부문별 IMO신청률 추이



# ------------------------------ 메인차트 (연차별) ------------------------------
# 부문별 신청인원, 수료인원, 수료율, IMO신청률
fig_crr_app = fig_barchart(df_crr_numbers, False, '신청인원', '신청누계', '입사연차', '부문별 교육신청 현황') # 부문별 신청인원
fig_chn_com = fig_barchart(df_chn_numbers, False, '수료인원', '수료누계', '소속부문', '부문별 교육수료 현황') # 부문별 수료인원
fig_chn_comrate = fig_barchart(df_chn_rate, True, '수료율', '소속부문', '부문별 수료율', '') # 부문별 수료율
fig_chn_imorate = fig_barchart(df_chn_rate, True, 'IMO신청률', '소속부문', '부문별 IMO신청률', '') # 부문별 IMO 신청률
fig_chn_temp = fig_barchart(df_chn_rate, True, '수료율', '소속부문', '부문별 수료율', '') # 부문별 수료율

# 소속부문별 추이 종합
fig_chn_com_monthly = fig_linechart(df_chn_rate_month, '월', '수료누계', '소속부문', '<b>소속부문별 수료인원 추이</b>') # 소속부문별 교육수료 인원 추이
fig_chn_comrate_monthly = fig_linechart(df_chn_rate_month, '월', '수료율', '소속부문', '<b>소속부문별 수료율 추이</b>') # 소속부문별 수료율 추이
fig_chn_imorate_monthly = fig_linechart(df_chn_rate_month, '월', 'IMO신청률', '소속부문', '<b>소속부문별 IMO신청률 추이</b>') # 소속부문별 IMO신청률 추이



# ------------------------------ 메인페이지 레이아웃 설정 ------------------------------
# 첫번째 행
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
r1_c1.plotly_chart(fig_chn_app, use_container_width=True)
r1_c2.plotly_chart(fig_chn_com, use_container_width=True)
r1_c3.plotly_chart(fig_chn_comrate, use_container_width=True)
r1_c4.plotly_chart(fig_chn_imorate, use_container_width=True)

# 두번째 행
r2_c1, r2_c2 = st.columns(2)
r2_c1.plotly_chart(fig_total, use_container_width=True)
r2_c2.plotly_chart(fig_chn_com_monthly, use_container_width=True)

# 세번째 행
r3_c1, r3_c2 = st.columns(2)
r3_c1.plotly_chart(fig_chn_comrate_monthly, use_container_width=True)
r3_c2.plotly_chart(fig_chn_imorate_monthly, use_container_width=True)

# 네번째 행
'''


# ------------------------------ straemlit 워터마크 숨기기 ------------------------------
hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)
