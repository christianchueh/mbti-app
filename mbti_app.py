
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont

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
        ("我在人群中感到充滿活力。", 'E'), ("我獨處時感到充電。", 'I'),
        ("我習慣用理性解決問題。", 'T'), ("我重視他人感受。", 'F'),
        ("我喜歡列出待辦清單。", 'J'), ("我傾向臨場反應。", 'P'),
        ("我觀察力敏銳、注重現實。", 'S'), ("我喜歡幻想與可能性。", 'N'),
        ("我喜歡和很多人互動。", 'E'), ("我只和熟悉的人互動。", 'I'),
        ("我說話直白。", 'T'), ("我說話委婉。", 'F'),
        ("我喜歡掌控事情的進度。", 'J'), ("我隨遇而安。", 'P'),
        ("我相信眼見為憑。", 'S'), ("我相信直覺。", 'N'),
        ("我重視效率。", 'T'), ("我重視和諧。", 'F'),
        ("我會把事情安排妥當。", 'J'), ("我容易被突發事件吸引。", 'P'),
        ("我依據現實做選擇。", 'S'), ("我經常腦中浮現新想法。", 'N')
    ]
    mbti_answers = []
    with st.form("mbti_form"):
        for i, (q, d) in enumerate(mbti_questions):
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

        # 建立包含中文姓名、興趣、經歷的圖片
        img_width, img_height = 800, 500
        info_img = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(info_img)
        try:
            font = ImageFont.truetype("NotoSansTC-Regular.otf", size=22)
        except:
            font = ImageFont.load_default()

        draw.text((10, 10), f"姓名: {st.session_state.name}", font=font, fill="black")
        draw.text((10, 60), "興趣: " + ", ".join(interests), font=font, fill="black")
        draw.text((10, 130), "經歷: " + experience, font=font, fill="black")

        info_img_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        info_img.save(info_img_file.name)

        # 建立 PDF
        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, "MBTI Test Report", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)
        pdf.cell(200, 10, f"MBTI Personality Type: {result}", new_x="LMARGIN", new_y="NEXT")
        for pair in [('E', 'I'), ('S', 'N'), ('T', 'F'), ('J', 'P')]:
            pdf.cell(200, 10, f"{pair[0]}: {scores[pair[0]]} / {pair[1]}: {scores[pair[1]]}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.image(tmp_img.name, x=50, w=100)
        pdf.image(info_img_file.name, x=10, y=None, w=180)

        pdf.output(tmp_pdf.name)
        with open(tmp_pdf.name, "rb") as f:
            st.download_button("📄 下載 PDF 報告", f, file_name="MBTI_報告.pdf")
