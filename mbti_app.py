import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# 啟用 wide 模式
st.set_page_config(layout="wide")

# 問卷資料與狀態初始化
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'scores' not in st.session_state:
    st.session_state.scores = {
        'Linguistic': 0,
        'Logical–Mathematical': 0,
        'Musical': 0,
        'Spatial': 0,
        'Bodily–Kinesthetic': 0,
        'Intrapersonal': 0,
        'Interpersonal': 0
    }
if 'name' not in st.session_state:
    st.session_state.name = ''
if 'age' not in st.session_state:
    st.session_state.age = 10  # default age
# 評語依照分數範圍
feedback_criteria = {
    "Linguistic": [
        (17, 20, "++ Strong verbal thinker; excels in written and oral expression"),
        (13, 16, "+ Solid potential; enjoys communication and word play"),
        (9, 12, "0 Moderate; communication is functional but not a primary strength"),
        (0, 8, "- Lower preference; may benefit from vocabulary support or language scaffolding"),
    ],
    "Logical–Mathematical": [
        (18, 20, "++ Strong analytical mind; quickly grasps patterns and logic"),
        (14, 17, "+ Good potential; enjoys reasoning but may need structure"),
        (10, 13, "0 Developing; benefits from guided practice with logic and sequencing"),
        (0, 9, "- Less natural inclination; scaffolded challenges help improve conceptual grasp"),
    ],
    "Musical": [
        (16, 20, "++ Deeply musical thinker; uses rhythm, melody, and tone for learning and emotion"),
        (12, 15, "+ Responsive to music; uses it for mood or memory"),
        (8, 11, "0 Occasional musical interests; not a learning preference"),
        (0, 7, "- Minimal interest; might respond better to other intelligences"),
    ],
    "Spatial": [
        (17, 20, "++ Highly visual-spatial thinker; strong with imagery, design, or navigation"),
        (13, 16, "+ Visual learner; enjoys maps, diagrams, and design tasks"),
        (9, 12, "0 Developing spatial skills; benefits from visual organizers"),
        (0, 8, "- Not a visual-first learner; may prefer verbal or bodily modes"),
    ],
    "Bodily–Kinesthetic": [
        (16, 20, "++ Highly physical learner; thinks best through movement or hands-on tasks"),
        (12, 15, "+ Enjoys physical activity; learns well through role-play or tactile experiences"),
        (8, 11, "0 Developing coordination; hands-on scaffolding recommended"),
        (0, 7, "- Less kinesthetic preference; may gravitate to abstract or verbal tasks"),
    ],
    "Intrapersonal": [
        (17, 20, "++ Strong self-awareness; reflective, goal-oriented, emotionally intelligent"),
        (13, 16, "+ Reflective tendencies; open to self-growth"),
        (9, 12, "0 Emerging awareness; may need prompts for reflection and goal-setting"),
        (0, 8, "- Struggles with emotional insight; scaffolded SEL strategies are helpful"),
    ],
    "Interpersonal": [
        (17, 20, "++ Socially intuitive; skilled at reading others and navigating group dynamics"),
        (13, 16, "+ Friendly and supportive; comfortable in team settings"),
        (9, 12, "0 Growing empathy and awareness; benefits from group roles and discussions"),
        (0, 8, "- Social cues are difficult; structured interaction and feedback are useful"),
    ]
}

# 評語查找函式
def get_feedback(intelligence_type, score):
    for lower, upper, text in feedback_criteria[intelligence_type]:
        if lower <= score <= upper:
            return text
    return "No interpretation available"

# 每頁問題資料
pages = [
    ('Linguistic', [
        "1.It’s easy for me to express my thoughts during an argument or debate. 在爭論或辯論時，我能輕鬆表達自己的想法。",
        "2.I enjoy a good lecture, speech or info session. 我喜歡聽精彩的演講、演說或說明會。",
        "3.I am irritated when I hear an argument or statement that sounds illogical. 聽到不合邏輯的論點或陳述時，我會感到煩躁。",
        "4.I'm good at finding the fine points of word meanings. 我擅長發現字裡行間的細微差別。",
        "5.I'd like to study the structure and logic of languages. 我對研究語言與邏輯有興趣。"
    ]),
    ('Logical–Mathematical', [
        "6.I can add or multiply in my head. 我可以心算加法或乘法。",
        "7.I like to work with calculators and computers. 我喜歡使用計算機和電腦。",
        "8.I like to work puzzles and play games. 我喜歡玩拼圖和遊戲。",
        "9.I often see patterns and relationships between numbers faster and easier than others. 我常常比別人更快、更容易發現數字裡的規律和關係。",
        "10.I like to work with numbers and figures. 我喜歡研究數字和圖形。"
    ]),
    ('Musical', [
        "11.I can play (or used to play) a musical instrument. 我能或(曾經能)演奏樂器。",
        "12.I can associate music with my moods. 我能用音樂表達自己的情緒。",
        "13.Life seems empty without music. 生活中沒有音樂會變得很空虛。",
        "14.I often connect a piece of music with some event in my life. 我的回憶常讓我聯想起某些音樂。",
        "15.I like to hum, whistle and sing in the shower or when I'm alone. 我喜歡在洗澡時或獨處時哼歌、吹口哨和唱歌。"
    ]),
    ('Spatial', [
        "16.I'd rather draw a map than give someone verbal directions. 我比較喜歡畫地圖描述勝過於口頭敘述。",
        "17.I always know north from south no matter where I am. 不論在哪裡，我都能清楚分辨南北方向。",
        "18.I always understand the directions that come with new gadgets or appliances. 我總是能理解新器材或家電所附的使用說明。",
        "19.I can look at an object one way and see it sideways or backwards just as easily. 我能輕鬆地把看到的東西轉換成側面或顛倒的樣子。",
        "20.Just looking at shapes of buildings and structures is pleasurable to me. 只是欣賞建築和結構的造型就能讓我感到愉悅。"
    ]),
    ('Bodily–Kinesthetic', [
        "21.I pick up new dance steps fast. 我很容易就能學會新的舞步。",
        "22.Learning to ride a bike (or skates) was easy. 學會騎腳踏車（或溜冰）對我而言很輕鬆。",
        "23.My sense of balance and coordination is good. 我的平衡感和協調性很好。",
        "24.I enjoy building models (or sculpting). 我喜歡做模型（或雕塑）。",
        "25.I'm good at athletics. 我在體育方面表現優秀。"
    ]),
    ('Intrapersonal', [
        "26.I'm usually aware of the expression on my face. 我通常能察覺自己臉部的表情變化。",
        "27.I stay 'in touch' with my moods. I have no trouble identifying them. 我很清楚自己的情緒，能輕鬆辨識並掌握它們。",
        "28.I often reflect on my emotions and try to understand their roots. 我經常深刻反思自己的情緒，尋找它們背後的根源。",
        "29.I regularly set goals for myself after reflecting. 我會經常反思並為自己設定具體的目標。",
        "30.I often take time to understand what truly makes me happy. 我會花時間去探索自己真正的快樂來源。"
    ]),
    ('Interpersonal', [
        "31.I'm sensitive to the expressions on other people's faces. 我很敏感，能察覺別人臉上的表情變化。",
        "32.I am sensitive to the moods of others. 我對別人的情緒很敏感。",
        "33.I can easily adapt my communication style to suit different people. 我可以輕易地配合不同的人改變自己的溝通風格。",
        "34.I can easily tell when someone is upset, even if they don’t say anything. 即使對方不開口，我也能輕易感覺到他們在生氣或難過。",
        "35.I can sense when someone is uncomfortable in a social situation. 我能感覺到別人在社交場合時的不安或尷尬。"
    ]),
    ('Summary', [])
]

# 分頁切換按鈕
def navigation():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_left, col_right = st.columns(2)
        with col_left:
            if st.session_state.page > 0:
                st.button("← 上一頁", on_click=lambda: st.session_state.update(page=st.session_state.page - 1))
        with col_right:
            if st.session_state.page < len(pages) - 1:
                st.button("下一頁 →", on_click=lambda: st.session_state.update(page=st.session_state.page + 1))

# 顯示當前頁面
current_page, questions = pages[st.session_state.page]

col_center = st.columns([1, 4, 1])[1]
with col_center:
    def save_to_google_sheet(name, age, scores):
        creds_dict = st.secrets["gcp_service_account"]
        creds = Credentials.from_service_account_info(creds_dict)
        client = gspread.authorize(creds)

        sheet = client.open("MI-Results").sheet1  # 試算表名稱
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, name, age] + [scores[key] for key in scores]
        sheet.append_row(row)
    if current_page == 'Summary' and not st.session_state.get("submitted"):
        save_to_google_sheet(
            st.session_state.name,
            st.session_state.age,
            st.session_state.scores
        )
        st.session_state.submitted = True
        st.title("📊 統計結果與分析")
        st.markdown(f"👤 **姓名：** {st.session_state.name}　🎂 **年齡：** {st.session_state.age} 歲")
        st.markdown("---")
        # --- 圖表區 ---
        st.markdown("### 📈 視覺化圖表")

        # 整理資料
        labels = list(st.session_state.scores.keys())
        values = list(st.session_state.scores.values())

        # --------- 🎯 雷達圖 ----------
        st.subheader("🎯 7 向度雷達圖")

        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values_radar = values + [values[0]]
        angles += [angles[0]]

        fig_radar, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values_radar, color='teal', linewidth=2)
        ax.fill(angles, values_radar, color='skyblue', alpha=0.4)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=10)
        ax.set_yticklabels([])
        ax.set_title('Multiple Intelligences Radar Chart', y=1.1, fontsize=14)
        st.pyplot(fig_radar)

        # --------- 🥧 圓餅圖 ----------
        st.subheader("🥧 向度占比圓餅圖")

        fig_pie, ax2 = plt.subplots(figsize=(6, 6))
        ax2.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Pastel1.colors)
        ax2.axis('equal')
        st.pyplot(fig_pie)
        positive_traits = []
        for key in st.session_state.scores:
            score = st.session_state.scores[key]
            interpretation = get_feedback(key, score)
            st.markdown(f"### {key}: {score} 分\n> {interpretation}")
            if interpretation.startswith("++") or interpretation.startswith("+"):
                positive_traits.append(f"{key} ({interpretation[:2]})")
        if positive_traits:
            st.markdown(f"\n**🟢 你的優勢向度為：** {', '.join(positive_traits)}")
        st.markdown("---")
        st.success("感謝您的填答！")
    else:
        st.header(f"🧠 {current_page} Intelligence")
        if st.session_state.page == 0:
            st.markdown("### 🧾 請先填寫您的基本資料")
            st.session_state.name = st.text_input("姓名", st.session_state.name)
            st.session_state.age = st.slider("年齡", min_value=6, max_value=99, value=st.session_state.age)
        total = 0
        for i, q in enumerate(questions):
            response = st.radio(
                f"{i+1}. {q}",
                ["Strongly Agree", "Agree", "Disagree", "Strongly Disagree"],
                key=f"{current_page}_{i}"
            )
            score = {"Strongly Agree": 4, "Agree": 3, "Disagree": 2, "Strongly Disagree": 1}[response]
            total += score
        st.session_state.scores[current_page] = total

navigation()
