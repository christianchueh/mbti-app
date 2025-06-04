# 可在 Google Colab 或 Streamlit Cloud 執行的 MBTI 測驗（使用 fpdf2 英文版）
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
from fpdf import FPDF

st.set_page_config(page_title="MBTI 測驗系統", layout="centered")

st.title("MBTI 測驗系統")

# 第一頁：個人資料
with st.form("user_info"):
    name = st.text_input("姓名")
    age = st.number_input("年紀", min_value=0, max_value=120, step=1)
    gender = st.selectbox("性別", ["男", "女", "其他"])
    next1 = st.form_submit_button("下一頁")

if next1 and name:
    st.session_state.name = name
    st.session_state.age = age
    st.session_state.gender = gender
    st.session_state.page = 2

if st.session_state.get("page") == 2:
    st.subheader("MBTI 測驗 (30題)")
    mbti_questions = [
        ("我喜歡參加社交活動。", 'E'), ("我偏好獨處時間。", 'I'),
        ("我做決定時依據邏輯。", 'T'), ("我做決定時依據感受。", 'F'),
        ("我偏好事先規劃好一切。", 'J'), ("我偏好隨機應變。", 'P'),
        ("我關注具體細節。", 'S'), ("我著重大局與可能性。", 'N'),
    ] * 4
    mbti_answers = []
    with st.form("mbti_form"):
        for i, (q, d) in enumerate(mbti_questions[:30]):
            ans = st.radio(f"問題 {i+1}: {q}", ["非常同意", "同意", "普通", "不同意", "非常不同意"], key=f"q{i}")
            mbti_answers.append((ans, d))
        next2 = st.form_submit_button("下一頁")

    if next2:
        st.session_state.mbti = mbti_answers
        st.session_state.page = 3

if st.session_state.get("page") == 3:
    st.subheader("興趣與經歷")
    interests_list = ["Programming", "數學", "英文", "積木", "繪畫", "閱讀", "寫作", "表達", "邏輯推理", "機器人", "團隊合作", "領導", "設計"]
    interests = st.multiselect("請選擇您的興趣：", interests_list)
    experience = st.text_area("參賽或個人經歷簡述")

    if st.button("生成 PDF 報告"):
        scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
        mapping = {"非常同意": 1, "同意": 2, "普通": 3, "不同意": 4, "非常不同意": 5}
        for ans, dim in st.session_state.mbti:
            val = mapping[ans]
            if dim in ['E', 'S', 'T', 'J']:
                scores[dim] += 6 - val
            else:
                scores[dim] += val

        result = ''.join([
            'E' if scores['E'] >= scores['I'] else 'I',
            'S' if scores['S'] >= scores['N'] else 'N',
            'T' if scores['T'] >= scores['F'] else 'F',
            'J' if scores['J'] >= scores['P'] else 'P'
        ])

        # 雷達圖
        labels = ['E', 'I', 'S', 'N', 'T', 'F', 'J', 'P']
        values = [scores[l] for l in labels]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(subplot_kw=dict(polar=True))
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)
        ax.set_yticklabels([])
        ax.set_title("MBTI 向度雷達圖")

        tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.savefig(tmp_img.name)
        plt.close()

        # 建立 PDF（完全英文內容，避免亂碼）
        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="MBTI Test Report", ln=True, align='C')
        pdf.ln(10)
        name_str = st.session_state.name if st.session_state.name else "User"
        gender_en = {'男': 'Male', '女': 'Female', '其他': 'Other'}.get(st.session_state.gender, 'Other')
        pdf.multi_cell(0, 10, txt=f"Name: {name_str}    Age: {st.session_state.age}    Gender: {gender_en}")
        pdf.cell(200, 10, txt=f"MBTI Personality Type: {result}", ln=True)
        for pair in [('E', 'I'), ('S', 'N'), ('T', 'F'), ('J', 'P')]:
            pdf.cell(200, 10, txt=f"{pair[0]}: {scores[pair[0]]} / {pair[1]}: {scores[pair[1]]}", ln=True)
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt="Interests: " + ", ".join(interests))
        pdf.ln(2)
        pdf.multi_cell(0, 10, txt="Experience: " + experience)
        pdf.image(tmp_img.name, x=50, w=100)

        pdf.output(tmp_pdf.name)
        with open(tmp_pdf.name, "rb") as f:
            st.download_button("📄 下載 PDF 報告", f, file_name="MBTI_Report.pdf")
