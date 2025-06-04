# 可在 Google Colab 或 Streamlit Cloud 執行的 MBTI 測驗
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

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
    interests_list = ["程式", "數學", "英文", "積木", "繪畫", "閱讀", "寫作", "表達", "邏輯推理", "機器人", "團隊合作", "領導", "設計"]
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

        # 產生雷達圖
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

        # 使用 reportlab 產生 PDF（含中文字體）
        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pdfmetrics.registerFont(TTFont('Noto', 'NotoSansTC-Regular.ttf'))  # 請上傳字體檔案
        doc = SimpleDocTemplate(tmp_pdf.name, pagesize=A4)
        styles = getSampleStyleSheet()
        styles['Normal'].fontName = 'Noto'
        styles['Title'].fontName = 'Noto'
        content = []

        content.append(Paragraph("MBTI 測驗報告", styles['Title']))
        content.append(Spacer(1, 12))
        content.append(Paragraph(f"姓名: {st.session_state.name} 年紀: {st.session_state.age} 性別: {st.session_state.gender}", styles['Normal']))
        content.append(Paragraph(f"MBTI 人格類型: {result}", styles['Normal']))
        for pair in [('E', 'I'), ('S', 'N'), ('T', 'F'), ('J', 'P')]:
            content.append(Paragraph(f"{pair[0]}: {scores[pair[0]]} / {pair[1]}: {scores[pair[1]]}", styles['Normal']))
        content.append(Paragraph("興趣: " + ", ".join(interests), styles['Normal']))
        content.append(Paragraph("經歷: " + experience, styles['Normal']))
        content.append(Spacer(1, 12))
        content.append(Image(tmp_img.name, width=12*cm, height=12*cm))

        doc.build(content)

        with open(tmp_pdf.name, "rb") as f:
            st.download_button("📄 下載 PDF 報告", f, file_name="MBTI_報告.pdf")
