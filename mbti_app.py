import streamlit as st

# 自訂 CSS：優化排版與響應式樣式
st.markdown("""
<style>
    body {
        font-family: "Noto Sans TC", sans-serif;
    }
    .stTextInput > div > input, .stTextArea > div > textarea {
        font-size: 16px;
    }
    .stButton > button {
        font-size: 16px;
        padding: 8px 24px;
    }
    .stHeader {
        margin-top: 20px;
    }
    @media screen and (max-width: 600px) {
        .stTextInput > div > input, .stTextArea > div > textarea {
            font-size: 14px;
        }
        .stButton > button {
            width: 100%;
            margin-top: 5px;
        }
    }
</style>
""", unsafe_allow_html=True)

# 初始化 Session State
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'data' not in st.session_state:
    st.session_state.data = {
        'name': '', 'age': '', 'gender': '', 'grade': '',
        'family_background': '', 'education_expectation': '',
        'favorite_subjects': '', 'learning_style': '',
        'activities': '', 'awards': ''
    }

def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1

# 每頁的內容函數
def page_basic_info():
    with st.container():
        st.header("👤 基本資料")
        st.session_state.data['name'] = st.text_input("姓名", st.session_state.data['name'])
        st.session_state.data['age'] = st.text_input("年齡", st.session_state.data['age'])
        st.session_state.data['gender'] = st.text_input("性別", st.session_state.data['gender'])
        st.session_state.data['grade'] = st.text_input("就讀年級", st.session_state.data['grade'])

def page_family_info():
    with st.container():
        st.header("🏠 家庭背景")
        st.session_state.data['family_background'] = st.text_area("家庭背景", st.session_state.data['family_background'])
        st.session_state.data['education_expectation'] = st.text_area("升學期待", st.session_state.data['education_expectation'])

def page_learning_style():
    with st.container():
        st.header("📚 學習興趣與風格")
        st.session_state.data['favorite_subjects'] = st.text_input("喜歡的科目", st.session_state.data['favorite_subjects'])
        st.session_state.data['learning_style'] = st.text_input("學習風格（例如：視覺型、動手型）", st.session_state.data['learning_style'])

def page_experience_skills():
    with st.container():
        st.header("🎖️ 活動與技能")
        st.session_state.data['activities'] = st.text_area("活動經歷", st.session_state.data['activities'])
        st.session_state.data['awards'] = st.text_area("得獎紀錄", st.session_state.data['awards'])

def page_summary():
    with st.container():
        st.header("📋 輸入摘要確認")
        for key, value in st.session_state.data.items():
            st.markdown(f"**{key}**: {value}")

# 頁面清單
pages = [page_basic_info, page_family_info, page_learning_style, page_experience_skills, page_summary]
pages[st.session_state.page]()

# 分頁按鈕置中
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.session_state.page > 0:
        st.button("← 上一頁", on_click=prev_page)
    if st.session_state.page < len(pages) - 1:
        st.button("下一頁 →", on_click=next_page)
