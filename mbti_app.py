# MBTI Test System (English version for Google Colab / Streamlit Cloud)
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
from fpdf import FPDF

st.set_page_config(page_title="MBTI Test System", layout="centered")

st.title("MBTI Test System")

# Page 1: User Info
with st.form("user_info"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    next1 = st.form_submit_button("Next")

if next1 and name:
    st.session_state.name = name
    st.session_state.age = age
    st.session_state.gender = gender
    st.session_state.page = 2

if st.session_state.get("page") == 2:
    st.subheader("MBTI Test (30 questions)")
    mbti_questions = [
        ("I enjoy attending social events.", 'E'), ("I prefer spending time alone.", 'I'),
        ("I make decisions based on logic.", 'T'), ("I make decisions based on feelings.", 'F'),
        ("I prefer to plan ahead.", 'J'), ("I prefer to be spontaneous.", 'P'),
        ("I focus on concrete details.", 'S'), ("I focus on the big picture and possibilities.", 'N'),
    ] * 4
    mbti_answers = []
    with st.form("mbti_form"):
        for i, (q, d) in enumerate(mbti_questions[:30]):
            ans = st.radio(f"Question {i+1}: {q}", ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"], key=f"q{i}")
            mbti_answers.append((ans, d))
        next2 = st.form_submit_button("Next")

    if next2:
        st.session_state.mbti = mbti_answers
        st.session_state.page = 3

if st.session_state.get("page") == 3:
    st.subheader("Interests & Experiences")
    interests_list = ["Programming", "Math", "English", "Blocks", "Drawing", "Reading", "Writing", "Speaking", "Logic", "Robotics", "Teamwork", "Leadership", "Design"]
    interests = st.multiselect("Select your interests:", interests_list)
    experience = st.text_area("Briefly describe your personal or competition experience")

    if st.button("Generate PDF Report"):
        scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
        mapping = {"Strongly Agree": 1, "Agree": 2, "Neutral": 3, "Disagree": 4, "Strongly Disagree": 5}
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

        # Radar Chart
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
        ax.set_title("MBTI Dimensions Radar Chart")

        tmp_img = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.savefig(tmp_img.name)
        plt.close()

        # Create PDF (fully English)
        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="MBTI Test Report", ln=True, align='C')
        pdf.ln(10)
        name_str = st.session_state.name if st.session_state.name else "User"
        pdf.multi_cell(0, 10, txt=f"Name: {name_str}    Age: {st.session_state.age}    Gender: {st.session_state.gender}")
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
            st.download_button("📄 Download PDF Report", f, file_name="MBTI_Report.pdf")
