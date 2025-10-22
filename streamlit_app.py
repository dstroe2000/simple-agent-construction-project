from history import ChatHistoryDB
import streamlit as st
import asyncio
from agent import AIAgent
from dotenv import load_dotenv
import os




# Load environment variables
load_dotenv()
endpoint = os.getenv("ENDPOINT")

# Initialize ChatHistoryDB and load history
history_db = ChatHistoryDB()
if "history" not in st.session_state:
    st.session_state["history"] = history_db.load_history()




st.set_page_config(page_title="Local Assistant", layout="wide")


# Custom CSS for sticky sidebar
st.markdown("""
    <style>
    .css-1lcbmhc {position: sticky !important; top: 0 !important;}
    </style>
""", unsafe_allow_html=True)

# Sidebar with app name and history management buttons
with st.sidebar:
    st.markdown("<h2 style='margin-top:0;margin-bottom:0;'>🏠 Local Assistant</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<b>History Controls</b>", unsafe_allow_html=True)
    reset_clicked = st.button("🔄 Reset Chat", help="Clear chat history")
    save_clicked = st.button("💾 Save Chat", help="Download chat history")
    export_clicked = st.button("📤 Export Chat", help="Import chat history")
    st.markdown("---")
    # Handle button actions
    if reset_clicked:
        st.session_state["history"] = []
        history_db.clear_history()
        st.rerun()
    if save_clicked:
        st.download_button("Download History", data="\n".join([f"You: {u}\nAssistant: {a}" for u,a in st.session_state["history"]]), file_name="chat_history.txt")
    if export_clicked:
        uploaded = st.file_uploader("Upload History", type=["txt"])
        if uploaded:
            content = uploaded.read().decode("utf-8")
            pairs = [tuple(block.split("\nAssistant: ")) for block in content.split("You: ") if block.strip()]
            st.session_state["history"] = [(u.strip(), a.strip()) for u,a in pairs if a]
            st.rerun()

# Custom CSS for sticky input bar, chat bubbles, and aligned input/button
st.markdown("""
    <style>
    .sticky-input {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100vw;
        background: #181818;
        padding: 16px 0 16px 0;
        z-index: 100;
        box-shadow: 0 -2px 8px rgba(0,0,0,0.2);
    }
    .chat-history {
        height: 500px;
        overflow-y: auto;
        background: #181818;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 80px;
        display: flex;
        flex-direction: column;
    }
    .user-bubble {
        background: #222;
        color: #FFD700;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin-bottom: 8px;
        max-width: 70%;
        align-self: flex-end;
        margin-left: auto;
        font-weight: bold;
    }
    .assistant-bubble {
        background: #222;
        color: #00FF99;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin-bottom: 16px;
        max-width: 70%;
        align-self: flex-start;
        margin-right: auto;
        font-weight: bold;
    }
    .input-row {
        display: flex;
        align-items: center;
        gap: 8px;
        width: 100%;
    }
    .input-row .stTextInput {
        flex: 1 1 auto;
        margin-bottom: 0 !important;
    }
    .input-row .stButton {
        flex: 0 0 auto;
        margin-bottom: 0 !important;
    }
    .streamlit-expanderHeader {z-index: 101;}
    </style>
""", unsafe_allow_html=True)


# Chat history as alternating bubbles with logos
st.markdown('<div class="chat-history">', unsafe_allow_html=True)
for user, assistant in st.session_state["history"]:
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:flex-end;margin-bottom:8px;">'
        f'<div class="user-bubble">'
        f'<span style="font-size:1.5em;margin-right:8px;vertical-align:middle;">🧑</span>'
        f'{user}'
        f'</div>'
        f'</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:flex-start;margin-bottom:16px;">'
        f'<div class="assistant-bubble">'
        f'<span style="font-size:1.5em;margin-right:8px;vertical-align:middle;">🤖</span>'
        f'{assistant}'
        f'</div>'
        f'</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
model = os.getenv("MODEL", "qwen3:4b")
system_prompt = os.getenv("SYSTEM_PROMPT")

# Initialize agent
agent = AIAgent(model, endpoint, system_prompt)

st.set_page_config(page_title="Local AI Code Assistant", layout="wide")
st.title("🏠 Local AI Code Assistant (Streamlit)")
st.caption("Private, fast, and cost-free conversational AI agent with file editing capabilities")

if "history" not in st.session_state:
    st.session_state["history"] = []




st.markdown('<div class="sticky-input">', unsafe_allow_html=True)
st.markdown('<div class="input-row">', unsafe_allow_html=True)
user_input = st.text_input("Type your message and press Send...", value=st.session_state.get("user_input", ""), key="user_input")
send_clicked = st.button("Send", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
if send_clicked and user_input.strip():
    async def get_response():
        response = ""
        async for chunk in agent.chat(user_input):
            response += chunk
        return response
    response = asyncio.run(get_response())
    st.session_state["history"].append((user_input, response))
    history_db.add_to_history(user_input, response)
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
