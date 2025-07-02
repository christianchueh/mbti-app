import streamlit as st

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

# 評語依照分數範圍
feedback_criteria = {
    "Linguistic": [
        (17, 20, "++ Strong verbal thinker; excels in written and oral expression"),
        (13, 16, "+ Solid potential; enjoys communication and word play"),
        (9, 12, "- Moderate; communication is functional but not a primary strength"),
        (0, 8, "0 Lower preference; may benefit from vocabulary support or language scaffolding"),
    ],
    "Logical–Mathematical": [
        (18, 20, "Strong analytical mind; quickly grasps patterns and logic"),
        (14, 17, "Good potential; enjoys reasoning but may need structure"),
        (10, 13, "Developing; benefits from guided practice with logic and sequencing"),
        (0, 9, "Less natural inclination; scaffolded challenges help improve conceptual grasp"),
    ],
    "Musical": [
        (16, 20, "Deeply musical thinker; uses rhythm, melody, and tone for learning and emotion"),
        (12, 15, "Responsive to music; uses it for mood or memory"),
        (8, 11, "Occasional musical interests; not a learning preference"),
        (0, 7, "Minimal interest; might respond better to other intelligences"),
    ],
    "Spatial": [
        (17, 20, "Highly visual-spatial thinker; strong with imagery, design, or navigation"),
        (13, 16, "Visual learner; enjoys maps, diagrams, and design tasks"),
        (9, 12, "Developing spatial skills; benefits from visual organizers"),
        (0, 8, "Not a visual-first learner; may prefer verbal or bodily modes"),
    ],
    "Bodily–Kinesthetic": [
        (16, 20, "Highly physical learner; thinks best through movement or hands-on tasks"),
        (12, 15, "Enjoys physical activity; learns well through role-play or tactile experiences"),
        (8, 11, "Developing coordination; hands-on scaffolding recommended"),
        (0, 7, "Less kinesthetic preference; may gravitate to abstract or verbal tasks"),
    ],
    "Intrapersonal": [
        (17, 20, "Strong self-awareness; reflective, goal-oriented, emotionally intelligent"),
        (13, 16, "Reflective tendencies; open to self-growth"),
        (9, 12, "Emerging awareness; may need prompts for reflection and goal-setting"),
        (0, 8, "Struggles with emotional insight; scaffolded SEL strategies are helpful"),
    ],
    "Interpersonal": [
        (17, 20, "Socially intuitive; skilled at reading others and navigating group dynamics"),
        (13, 16, "Friendly and supportive; comfortable in team settings"),
        (9, 12, "Growing empathy and awareness; benefits from group roles and discussions"),
        (0, 8, "Social cues are difficult; structured interaction and feedback are useful"),
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
        "It’s easy for me to express my thoughts during an argument or debate.",
        "I enjoy a good lecture, speech or info session.",
        "I am irritated when I hear an argument or statement that sounds illogical.",
        "I'm good at finding the fine points of word meanings.",
        "I'd like to study the structure and logic of languages."
    ]),
    ('Logical–Mathematical', [
        "I can add or multiply in my head.",
        "I like to work with calculators and computers.",
        "I like to work puzzles and play games.",
        "I often see patterns and relationships between numbers faster and easier than others.",
        "I like to work with numbers and figures."
    ]),
    ('Musical', [
        "I can play (or used to play) a musical instrument.",
        "I can associate music with my moods.",
        "Life seems empty without music.",
        "I often connect a piece of music with some event in my life.",
        "I like to hum, whistle and sing in the shower or when I'm alone."
    ]),
    ('Spatial', [
        "I'd rather draw a map than give someone verbal directions.",
        "I always know north from south no matter where I am.",
        "I always understand the directions that come with new gadgets or appliances.",
        "I can look at an object one way and see it sideways or backwards just as easily.",
        "Just looking at shapes of buildings and structures is pleasurable to me."
    ]),
    ('Bodily–Kinesthetic', [
        "I pick up new dance steps fast.",
        "Learning to ride a bike (or skates) was easy.",
        "My sense of balance and coordination is good.",
        "I enjoy building models (or sculpting).",
        "I'm good at athletics."
    ]),
    ('Intrapersonal', [
        "I'm usually aware of the expression on my face.",
        "I stay 'in touch' with my moods. I have no trouble identifying them.",
        "I often reflect on my emotions and try to understand their roots.",
        "I regularly set goals for myself after reflecting.",
        "I often take time to understand what truly makes me happy."
    ]),
    ('Interpersonal', [
        "I'm sensitive to the expressions on other people's faces.",
        "I am sensitive to the moods of others.",
        "I can easily adapt my communication style to suit different people.",
        "I can easily tell when someone is upset, even if they don’t say anything.",
        "I can sense when someone is uncomfortable in a social situation."
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
    if current_page == 'Summary':
        st.title("📊 統計結果與分析")
        for key in st.session_state.scores:
            score = st.session_state.scores[key]
            interpretation = get_feedback(key, score)
            st.markdown(f"### {key}: {score} 分\n> {interpretation}")
        st.markdown("---")
        st.success("感謝您的填答！")
    else:
        st.header(f"🧠 {current_page} Intelligence")
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
