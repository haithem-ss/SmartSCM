from agents.orchestrator import LLMOrchestrator
import streamlit as st

# ---- Page Config ----
st.set_page_config(page_title="SmartSCM Assistant", layout="centered")
st.markdown("""
    <style>
            .stMainBlockContainer {
            padding-top: 1rem;}

            .stTooltipHoverTarget{
            width: 100% !important;}
    .title { font-size: 28px; font-weight: 500; color: white; line-height:1; margin-bottom: 0.75rem; }
    .step-title { font-size: 18px; font-weight: 600; margin-top: 1rem; }
    .step-item { margin: 0.2rem 0; padding-left: 10px; }
    .chat-box { background-color: #1f1f1f; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
    .user-msg { color: #00c6ff; }
    .ai-msg { color: #fff; }
    .thinking { color: #aaa; font-style: italic; }
    div[data-testid="stExpander"] button {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
    }
    footer {
        font-size: 12px;
        color: #555;
        margin-top: 2rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Hide the default Streamlit header */
    header {visibility: hidden;}
    /* Optional: Hide the hamburger menu (top right) */
    button[title="Open sidebar"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---- Session State Init ----
if "history" not in st.session_state:
    st.session_state.history = []
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "queued_prompt" not in st.session_state:
    st.session_state.queued_prompt = None

# ---- New Chat Button ----
if st.button("🔄 Start New Chat", disabled=st.session_state.is_generating):
    st.session_state.history = []
    st.session_state.queued_prompt = None
    st.rerun()

st.markdown(
    '''
    <div style="display: flex; align-items: flex-end; gap: 1rem;">
        <svg width="150" height="69"  viewBox="0 0 278 69" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M39.3652 27.7993C44.8726 44.1641 45.5283 60.87 45.607 66.7183C45.607 24.5735 70.8099 15.8403 70.8099 15.8403V0.445801C56.412 4.32721 46.3151 15.5518 39.3652 27.7993Z" fill="#FFDD12"/>
        <path d="M35.4316 35.4571C42.3815 50.5107 45.0827 65.2233 45.6072 68.2918V66.692C45.5286 60.8174 44.8729 44.1378 39.3655 27.7729C37.9231 30.3168 36.6118 32.9132 35.4316 35.4571Z" fill="white"/>
        <path d="M45.6066 68.4492C45.3181 65.3808 42.4071 50.2223 35.431 35.1425C33.1494 30.2121 30.4219 25.2554 27.1437 20.6397C27.0912 20.561 27.0125 20.4561 26.9601 20.3774C26.7765 20.1152 26.5929 19.8791 26.4093 19.6169C19.8791 10.569 11.3295 3.04219 0 0V15.3945C0 15.3945 5.06157 17.1516 10.6477 22.8426C18.1482 31.7856 24.3375 45.8164 25.2816 67.951C25.2816 68.1345 25.2816 68.3181 25.3079 68.5017H45.5804C45.5804 68.5017 45.6066 68.7115 45.6066 68.4492Z" fill="#FFDD12"/>
        <path d="M84.7883 59.6898C89.6663 59.6898 93.6789 57.7491 96.7735 53.8939L103.146 60.4503C98.0848 66.1413 92.1316 68.9999 85.2604 68.9999C78.3893 68.9999 72.7507 66.8232 68.3186 62.4959C63.8864 58.1687 61.6572 52.6875 61.6572 46.0786C61.6572 39.4697 63.9126 33.9623 68.4497 29.5301C72.9868 25.1242 78.5204 22.895 85.0506 22.895C92.3676 22.895 98.4782 25.6749 103.409 31.2348L97.2194 38.2895C94.0723 34.3819 90.1646 32.415 85.4964 32.415C81.7462 32.415 78.5728 33.6476 75.8978 36.0866C73.249 38.5256 71.9115 41.83 71.9115 45.9737C71.9115 50.1174 73.1703 53.448 75.6618 55.9395C78.1795 58.4309 81.2216 59.6898 84.7883 59.6898Z" fill="white"/>
        <path d="M155.965 68.4751L142.38 34.1194H152.319L160.869 55.7294L169.419 34.1194H179.358L165.773 68.4751H155.965Z" fill="white"/>
        <path d="M184.079 34.1982H193.625V68.4753H184.079V34.1982Z" fill="white"/>
        <path d="M267.582 21.1902H277.128V68.4752H267.582V21.1902Z" fill="white"/>
        <path fill-rule="evenodd" clip-rule="evenodd" d="M184.053 21.1118H193.809V30.5006H184.053V21.1118Z" fill="white"/>
        <path d="M39.3652 27.7993C44.8726 44.1641 45.5283 60.87 45.607 66.7183C45.607 24.5735 70.8099 15.8403 70.8099 15.8403V0.445801C56.412 4.32721 46.3151 15.5518 39.3652 27.7993Z" fill="#D3D3D7"/>
        <path d="M35.4316 35.4571C42.3815 50.5107 45.0827 65.2233 45.6072 68.2918V66.692C45.5286 60.8174 44.8729 44.1378 39.3655 27.7729C37.9231 30.3168 36.6118 32.9132 35.4316 35.4571Z" fill="white"/>
        <path d="M45.6066 68.4492C45.3181 65.3808 42.4071 50.2223 35.431 35.1425C33.1494 30.2121 30.4219 25.2554 27.1437 20.6397C27.0912 20.561 27.0125 20.4561 26.9601 20.3774C26.7765 20.1152 26.5929 19.8791 26.4093 19.6169C19.8791 10.569 11.3295 3.04219 0 0V15.3945C0 15.3945 5.06157 17.1516 10.6477 22.8426C18.1482 31.7856 24.3375 45.8164 25.2816 67.951C25.2816 68.1345 25.2816 68.3181 25.3079 68.5017H45.5804C45.5804 68.5017 45.6066 68.7115 45.6066 68.4492Z" fill="#D3D3D7"/>
        <path d="M84.7883 59.69C89.6663 59.69 93.6789 57.7493 96.7735 53.8941L103.146 60.4506C98.0848 66.1416 92.1316 69.0002 85.2604 69.0002C78.3893 69.0002 72.7507 66.8234 68.3186 62.4962C63.8864 58.1689 61.6572 52.6877 61.6572 46.0788C61.6572 39.4699 63.9126 33.9625 68.4497 29.5304C72.9868 25.1245 78.5204 22.8953 85.0506 22.8953C92.3676 22.8953 98.4782 25.6752 103.409 31.2351L97.2194 38.2898C94.0723 34.3821 90.1646 32.4152 85.4964 32.4152C81.7462 32.4152 78.5728 33.6478 75.8978 36.0868C73.249 38.5258 71.9115 41.8303 71.9115 45.9739C71.9115 50.1176 73.1703 53.4483 75.6618 55.9397C78.1795 58.4312 81.2216 59.69 84.7883 59.69Z" fill="white"/>
        <path d="M155.965 68.4754L142.38 34.1196H152.319L160.869 55.7297L169.419 34.1196H179.358L165.773 68.4754H155.965Z" fill="white"/>
        <path d="M184.079 34.1982H193.625V68.4753H184.079V34.1982Z" fill="white"/>
        <path d="M267.582 21.1904H277.128V68.4755H267.582V21.1904Z" fill="white"/>
        <path fill-rule="evenodd" clip-rule="evenodd" d="M184.053 21.1118H193.809V30.5006H184.053V21.1118Z" fill="white"/>
        <path d="M222.054 58.2211C220.822 59.8471 219.301 60.6338 217.517 60.6338C216.573 60.6338 215.786 60.2667 215.105 59.5061C214.423 58.7718 214.082 57.7228 214.082 56.4115V41.0432H222.369V34.172H214.082V21.1641H204.457V34.1983H200.444V41.0694H207.578C205.847 41.2268 204.483 42.6954 204.457 44.4788V56.8836C204.457 60.6338 205.585 63.5711 207.866 65.7479C210.148 67.9246 212.928 68.9999 216.206 68.9999C219.51 68.9999 222.631 67.6361 225.595 64.9086L222.054 58.2211Z" fill="white"/>
        <path d="M120.639 54.707C120.665 54.7333 120.665 54.707 120.639 54.707Z" fill="white"/>
        <path d="M116.075 47.8882C116.075 47.8358 116.101 47.8095 116.101 47.7571C116.101 47.7833 116.101 47.8358 116.075 47.8882Z" fill="white"/>
        <path d="M116.023 48.9634V51.0877C116.05 50.773 116.102 50.4845 116.207 50.196" fill="white"/>
        <path d="M141.017 54.7332V49.6454C141.017 44.6625 139.364 40.7549 136.086 37.9225C132.782 35.0639 128.795 33.6477 124.075 33.6477C119.354 33.6477 115.263 35.2475 111.801 38.4208C108.339 41.6203 106.608 45.8951 106.608 51.2976C106.608 56.7002 108.313 61.0012 111.696 64.2007C115.106 67.4003 119.407 69 124.599 69C129.792 69 134.329 67.1642 138.21 63.5188L132.86 57.723C130.684 59.9784 127.93 61.1061 124.573 61.1061C122.501 61.1061 120.613 60.5029 118.961 59.3227C117.309 58.1426 116.338 56.5952 116.023 54.7332H141.017ZM119.433 47.9145H119.38C118.41 47.9145 117.545 48.3341 116.941 48.9898C116.6 49.3307 116.364 49.7765 116.181 50.2224C116.076 50.5109 116.023 50.7994 115.997 51.1141V48.78C115.997 48.4915 116.023 48.203 116.05 47.9145V47.8883C116.05 47.8358 116.076 47.8096 116.076 47.7572C116.364 45.8689 117.466 44.374 119.013 43.2463C120.587 42.0924 122.318 41.5154 124.206 41.5154C126.094 41.5154 127.694 42.0662 129.005 43.1677C130.316 44.2691 131.077 45.8427 131.287 47.8883H119.433V47.9145Z" fill="white"/>
        <path d="M255.885 36.7425C253.263 34.6706 249.854 33.6216 245.684 33.6216C239.914 33.6216 234.774 35.2476 230.263 38.5258L234.538 44.7151C235.823 43.7447 237.37 42.9317 239.232 42.2499C241.068 41.5942 242.825 41.2533 244.477 41.2533C248.332 41.2533 250.273 43.0891 250.273 46.7345V46.918H243.14C238.708 46.918 235.246 47.7835 232.676 49.5406C230.132 51.2715 228.847 53.8941 228.847 57.4083C228.847 60.9226 230.079 63.7288 232.545 65.8268C235.01 67.9249 238.052 68.9739 241.697 68.9739C245.316 68.9739 248.385 67.4266 250.85 64.332V68.4756H259.846V46.6296C259.846 42.1187 258.534 38.8405 255.885 36.7425ZM250.221 55.4152C250.221 57.1461 249.565 58.5361 248.28 59.5851C246.995 60.6341 245.474 61.1586 243.795 61.1586C242.091 61.1586 240.779 60.8177 239.888 60.1621C238.97 59.5064 238.524 58.5623 238.524 57.3297C238.524 54.9431 240.438 53.763 244.267 53.763H246.89C248.726 53.7367 250.221 52.2681 250.273 50.4323L250.221 55.4152Z" fill="white"/>
        </svg>
        <div class="title"> SmartSCM Assistant</div>
    </div>
    ''',
    unsafe_allow_html=True
)

# ---- Predefined Prompts ----
predefined_prompts = [
    {
        "label": "📅 Daily orders report",
        "prompt": (
            "Generate a daily orders report for today. Include:\n"
            "- Number of orders with OrderDate = today\n"
            "- Order count by Status (Pending, In Transit, Completed)\n"
            "- Total revenue generated today (sum of TotalAmount)\n"
            "- Top 5 products ordered today by quantity\n"
            "- Number of Express vs Standard orders\n"
            "- List of pending orders with customer names\n"
            "- Average order value for today"
        ),
        "detail": "Today's orders summary: status breakdown, revenue, top products, and order types."
    },
    {
        "label": "📦 Customer analysis",
        "prompt": (
            "Generate a customer-wise summary for the last 30 days. For each customer, include:\n"
            "- Total number of orders\n"
            "- Order count by Status\n"
            "- Total and average order value (TotalAmount)\n"
            "- Top 3 products ordered\n"
            "- Percentage of Express vs Standard shipping\n"
            "- First and last order dates\n"
            "- Total quantity ordered across all products"
        ),
        "detail": "Last 30 days: customer orders, spending, preferences, and order patterns."
    },
    {
        "label": "🌍 Regional overview",
        "prompt": (
            "Group order data by Region and City. For each region, include:\n"
            "- Total number of orders\n"
            "- Total revenue (sum of TotalAmount)\n"
            "- Top 3 products by quantity\n"
            "- Average order value\n"
            "- Order count by OrderType (Standard, Express)\n"
            "- Number of unique customers\n"
            "- Status breakdown (Pending, In Transit, Completed)\n"
            "- Most active cities in the region"
        ),
        "detail": "Region-wise analysis: revenue, popular products, customers, and order distribution."
    }
]

with st.expander("💡 Try a predefined report", expanded=True):
    cols = st.columns(len(predefined_prompts))
    for i, item in enumerate(predefined_prompts):
        with cols[i]:
            if st.button(item["label"], disabled=st.session_state.queued_prompt is not None, help=item["detail"]):
                st.session_state.queued_prompt = item["prompt"]
                st.rerun()

# ---- Welcome Info Box ----
if not st.session_state.history and not st.session_state.queued_prompt:
    st.info("""
        👋 **Welcome to the SmartSCM Assistant!**

        This assistant helps you explore and understand your order data with AI-powered insights.

        💡 What It Can Do:
        - Answer questions using your latest data
        - Create charts, summaries, and insights
        - Help plan and validate your analysis steps

        🧠 How to Use It:
        1. Type a clear question or request below
        2. Example: “Show me orders by vendor”
        3. Expand **Agent Steps** to trace how it thinks
        4. Use the **🔄 Start New Chat** button anytime

        ✅ Tips:
        - Ask for charts or tables directly
        - Try: “What can you do with my data?”
        - Ask: “What does each column mean?” to understand your dataset

        ⚠️ It can’t change data or remember past sessions
    """)

# ---- Utils ----
def remove_consecutive_duplicates(steps):
    if not steps:
        return []
    deduped = [steps[0]]
    for step in steps[1:]:
        if step != deduped[-1]:
            deduped.append(step)
    return deduped

# ---- Chat History Display ----
for entry in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-box user-msg">{entry["message"]}</div>', unsafe_allow_html=True)

    if entry["steps"]:
        with st.expander("🔍 Agent Steps", expanded=False):
            for i, step in enumerate(entry["steps"]):
                st.markdown(f"{i+1}. {step}")

    if entry["response"]:
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-box ai-msg">{entry["response"]}</div>', unsafe_allow_html=True)

# ---- Input Handling ----
if not st.session_state.is_generating:
    user_prompt = st.chat_input("Type your message...") or st.session_state.queued_prompt
    if user_prompt:
        st.session_state.queued_prompt = None  # clear queued prompt
        st.session_state.is_generating = True

        # Append user prompt to history
        st.session_state.history.append({
            "role": "user",
            "message": user_prompt,
            "steps": [],
            "response": None
        })

        idx = len(st.session_state.history) - 1
        steps = []

        with st.chat_message("user"):
            st.markdown(f'<div class="chat-box user-msg">{user_prompt}</div>', unsafe_allow_html=True)

        step_placeholder = st.empty()
        response_placeholder = st.empty()

        def step_collector(step):
            steps.append(step)
            deduped = remove_consecutive_duplicates(steps)
            with step_placeholder.container():
                with st.expander("🔍 Agent Steps in progress...", expanded=True):
                    for i, s in enumerate(deduped):
                        if i == len(deduped) - 1:
                            st.markdown(f"🌀 **{i+1}. {s}**")
                        else:
                            st.markdown(f"{i+1}. {s}")

        with step_placeholder.container():
            st.markdown(f'<div class="thinking">Thinking... 🤖</div>', unsafe_allow_html=True)

        agent = LLMOrchestrator(step_callback=step_collector,verbose=True)

        try:
            with st.spinner("SmartSCM is working on your request..."):
                result = agent.orchestrate(user_prompt)
                print(result)
        except Exception as e:
            error_msg = f"⚠️ Oops! An error occurred: {e}"
            st.error(error_msg)
            # Save error in response for reference
            st.session_state.history[idx]["response"] = error_msg
            st.session_state.is_generating = False
            st.rerun()
        else:
            # Save results
            deduped = remove_consecutive_duplicates(steps)
            st.session_state.history[idx]["steps"] = deduped
            st.session_state.history[idx]["response"] = result["output"]

            with step_placeholder.container():
                if len(deduped) > 1:
                    with st.expander("🔍 Agent Steps", expanded=False):
                        for i, s in enumerate(deduped):
                            st.markdown(f"{i+1}. {s}")

            with response_placeholder.container():
                with st.chat_message("assistant"):
                    st.markdown(f'<div class="chat-box ai-msg">{result["output"]}</div>', unsafe_allow_html=True)

            st.session_state.is_generating = False
            st.rerun()
