import streamlit as st
import matplotlib.pyplot as plt
import datetime
import os, textwrap
from PIL import Image, ImageDraw, ImageFont

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
if 'mbti_scores' not in st.session_state:
    st.session_state.mbti_scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
if 'mbti_answers' not in st.session_state:
    st.session_state.mbti_answers = {}

# MBTI 題庫與解釋
mbti_questions = [
    ('E', "我在社交場合感到活力充沛。"),
    ('E', "與人互動比獨處更讓我放鬆。"),
    ('I', "我傾向說話前先思考。"),
    ('E', "我喜歡與許多人一起完成任務。"),
    ('E', "獨處太久會讓我感到不安。"),
    ('E', "我經常主動發起對話或活動。"),
    ('I', "我偏好深入交談而非閒聊。"),
    ('E', "與他人共處讓我更容易激發創意。"),
    ('S', "我重視實際經驗勝過抽象理論。"),
    ('S', "我善於觀察細節。"),
    ('N', "我喜歡嘗試新的概念和想法。"),
    ('S', "過去的經驗常引導我的決策。"),
    ('S', "我偏好清楚明確的指令。"),
    ('N', "我喜歡探索『如果…那會怎樣』的情境。"),
    ('N', "我傾向相信直覺而非證據。"),
    ('N', "我常發想未來的各種可能性。"),
    ('T', "做決定時我優先考量邏輯與事實。"),
    ('F', "我很容易同情別人的情緒。"),
    ('T', "我在意是否公平，而非是否讓人開心。"),
    ('F', "我在意他人的感受超過結果。"),
    ('T', "我認為說真話比說好聽話重要。"),
    ('F', "我傾向避免衝突，重視和諧。"),
    ('T', "做事有效率比顧及他人感受更重要。"),
    ('F', "我會因他人的傷心而感到難過。"),
    ('J', "我喜歡事情有計畫並按步驟進行。"),
    ('P', "我很靈活，能隨情況調整安排。"),
    ('J', "做事前我會先做清單與安排。"),
    ('P', "我能夠輕鬆接受突發事件或改變。"),
    ('J', "我喜歡掌控時間表與截止日。"),
    ('P', "我會在最後一刻才開始行動。"),
]
mbti_options = {"非常同意": 3, "同意": 2, "不同意": 1, "非常不同意": 0}
# 更新 trait_labels 為英文
trait_labels = {
    'E': 'E.Extroversion', 'I': 'I.Introversion',
    'S': 'S.Sensing', 'N': 'N.Intuition',
    'T': 'T.Thinking', 'F': 'F.Feeling',
    'J': 'J.Judging', 'P': 'P.Perceiving'
}


# 畫雷達圖，並直接顯示而不儲存
def draw_radar_chart(scores):
    traits = list(trait_labels.keys())
    labels = [trait_labels[t] for t in traits]  # 使用英文標籤
    values = [scores[t] for t in traits] + [scores[traits[0]]]
    angles = [n / float(len(traits)) * 2 * 3.14159 for n in range(len(traits))] + [0]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True})
    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)  # 顯示英文標籤
    ax.set_yticklabels([])
    st.pyplot(fig)  # 直接顯示在 Streamlit 中，而不儲存為檔案


# 將資料與作答轉成圖檔（不儲存）
def generate_summary_image():
    W, H = 1000, 3000  # 延長高度以容納所有問題與答案
    img = Image.new("RGB", (W, H), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("NotoSansTC-Regular.otf", 24)
    except:
        font = ImageFont.load_default()

    y = 20
    draw.text((20, y), "📋 學涯健診摘要", fill="black", font=font)
    y += 40
    for k, v in st.session_state.data.items():
        draw.text((30, y), f"{k}: {v}", fill="black", font=font)
        y += 30

    # 顯示所有MBTI問題與答案
    y += 40
    draw.text((20, y), "🧠 MBTI 題目與作答：", fill="black", font=font)
    y += 40
    for i, (trait, question) in enumerate(mbti_questions):
        ans = st.session_state.mbti_answers.get(i, "")
        lines = textwrap.wrap(f"{i + 1}. {question} → {ans}", width=44)
        for line in lines:
            draw.text((40, y), line, fill="black", font=font)
            y += 30
        y += 10  # 調整每題之間的間距

    # 不儲存圖片，直接顯示摘要內容
    st.image(img)  # 顯示在 Streamlit 頁面上，而不是儲存


# 更新 `save_mbti_to_txt` 使其直接下載 TXT 文件
def save_mbti_to_txt():
    # 生成 TXT 文件並提供下載
    txt_path = f"{datetime.date.today()}_{st.session_state.data['name']}_mbti.txt"
    with open(txt_path, "w", encoding="utf-8") as file:
        file.write("📋 學涯健診摘要\n")
        for k, v in st.session_state.data.items():
            file.write(f"{k}: {v}\n")
        file.write("\n🧠 MBTI 題目與作答：\n")
        for i, (trait, question) in enumerate(mbti_questions):
            ans = st.session_state.mbti_answers.get(i, "")
            file.write(f"{i + 1}. {question} → {ans}\n")
    return txt_path

# 各分頁內容
def page_basic_info():
    st.header("👤 基本資料")
    for field in ['name', 'age', 'gender', 'grade']:
        st.session_state.data[field] = st.text_input(field, st.session_state.data[field])

def page_family_info():
    st.header("🏠 家庭背景")
    st.session_state.data['family_background'] = st.text_area("家庭背景", st.session_state.data['family_background'])
    st.session_state.data['education_expectation'] = st.text_area("升學期待", st.session_state.data['education_expectation'])

def page_learning_style():
    st.header("📚 學習興趣與風格")
    st.session_state.data['favorite_subjects'] = st.text_input("喜歡的科目", st.session_state.data['favorite_subjects'])
    st.session_state.data['learning_style'] = st.text_input("學習風格", st.session_state.data['learning_style'])

def page_experience_skills():
    st.header("🎖️ 活動與技能")
    st.session_state.data['activities'] = st.text_area("活動經歷", st.session_state.data['activities'])
    st.session_state.data['awards'] = st.text_area("得獎紀錄", st.session_state.data['awards'])

def page_mbti():
    st.header("🧠 MBTI 測驗")
    for i, (trait, question) in enumerate(mbti_questions):
        key = f"mbti_{i}"
        answer = st.radio(f"{i+1}. {question}", list(mbti_options.keys()), key=key)
        st.session_state.mbti_scores[trait] += mbti_options[answer]
        st.session_state.mbti_answers[i] = answer
# 在結果統整頁面添加簡單的分析與類型解釋
def page_summary():
    st.header("📋 結果統整與匯出")

    # 直接顯示雷達圖，而不儲存
    draw_radar_chart(st.session_state.mbti_scores)

    mbti = ''
    mbti += 'E' if st.session_state.mbti_scores['E'] >= st.session_state.mbti_scores['I'] else 'I'
    mbti += 'S' if st.session_state.mbti_scores['S'] >= st.session_state.mbti_scores['N'] else 'N'
    mbti += 'T' if st.session_state.mbti_scores['T'] >= st.session_state.mbti_scores['F'] else 'F'
    mbti += 'J' if st.session_state.mbti_scores['J'] >= st.session_state.mbti_scores['P'] else 'P'

    st.success(f"你的 MBTI 類型是：**{mbti}**")

    # 添加簡單分析
    mbti_analysis = {
        'ESTJ': "ESTJ - 實踐型領導者：注重邏輯與事實，擅長規劃與決策，強調秩序與效率，擅長管理與組織。",
        'ESFJ': "ESFJ - 人際關係協調者：注重他人需求，具強烈的社會責任感，喜歡幫助他人，擅長合作與協調。",
        'ENTJ': "ENTJ - 戰略型領導者：具有高度的組織能力與決策能力，注重結果，善於領導和規劃。",
        'ENFJ': "ENFJ - 群體激勵者：具有領導力與高度的同理心，善於理解他人需求並促使人群合作。",
        'ISTJ': "ISTJ - 負責型守護者：注重責任與秩序，實事求是，喜歡按部就班，具高度的責任心與專業能力。",
        'ISFJ': "ISFJ - 保護者：深具同理心，為他人著想，重視忠誠與關懷，喜歡提供穩定支持。",
        'INTJ': "INTJ - 創新型策略家：以邏輯與理性為主導，善於規劃長期目標，追求創新，擅長分析複雜問題。",
        'INFJ': "INFJ - 慈善型理想主義者：具有高度的同理心與洞察力，注重理想與價值，尋求真理與內心的意義。",
        'ESTP': "ESTP - 活力型冒險者：喜歡即時的挑戰與冒險，注重實際的體驗與快樂，擅長解決眼前的問題。",
        'ESFP': "ESFP - 表現型娛樂者：享受社交與娛樂，喜歡即時的體驗與快樂，能夠激發他人的興趣。",
        'ENTP': "ENTP - 創新型辯論者：具有創造力，善於發掘新機會並思考未來的可能性，喜歡挑戰舊有觀念。",
        'ENFP': "ENFP - 熱情型探索者：擁有豐富的創造力與熱情，重視價值觀與人際連結，擅長激發創新。",
        'ISTP': "ISTP - 工程型探索者：實事求是，擅長解決技術性問題，偏好單獨工作，喜歡操作工具和機械。",
        'ISFP': "ISFP - 審美型藝術家：重視內心感受與美感，追求寧靜與自我表達，擅長藝術與創作。",
        'INTP': "INTP - 理論型思考者：注重理性與邏輯，喜歡探索抽象的理論，具高度的創造力與分析能力。",
        'INFP': "INFP - 理想主義者：關注內心價值與理想，具有強烈的同理心與創造力，尋求內心的意義與和平。"
    }

    # 顯示簡單分析
    st.write(f"📝 **{mbti}**：{mbti_analysis.get(mbti, '無法識別的MBTI類型')}")

    # 顯示所有類型的中文解釋
    st.write("### MBTI 類型解釋：")
    st.write("**E:外向** , **I:內向** , **S:實感** , **N:直覺**")
    st.write("**T:思考** , **F:情感** , **J:判斷型** , **P:感知型**")

    # 生成並提供下載 TXT 檔案
    txt_path = save_mbti_to_txt()
    st.download_button(
        label="下載MBTI結果",
        data=open(txt_path, "r", encoding="utf-8").read(),
        file_name=f"{datetime.date.today()}_{st.session_state.data['name']}_mbti.txt",
        mime="text/plain"
    )


# 主流程
pages = [page_basic_info, page_family_info, page_learning_style, page_experience_skills, page_mbti, page_summary]
pages[st.session_state.page]()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.session_state.page > 0:
        st.button("← 上一頁", on_click=lambda: st.session_state.update({'page': st.session_state.page - 1}))
    if st.session_state.page < len(pages) - 1:
        st.button("下一頁 →", on_click=lambda: st.session_state.update({'page': st.session_state.page + 1}))
