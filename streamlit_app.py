from history import ChatHistoryDB
import streamlit as st
import asyncio
from agent import AIAgent
from dotenv import load_dotenv
import os
from streamlit_js_eval import streamlit_js_eval




# Load environment variables
load_dotenv()
endpoint = os.getenv("ENDPOINT")



# Initialize ChatHistoryDB and chat state
history_db = ChatHistoryDB()
if "chat_id" not in st.session_state:
    chats = history_db.list_chats()
    if chats:
        st.session_state["chat_id"] = chats[0][0]  # Select most recent chat
    else:
        st.session_state["chat_id"] = history_db.create_chat("New Chat")
if "chats" not in st.session_state:
    st.session_state["chats"] = history_db.list_chats()
if "history" not in st.session_state:
    st.session_state["history"] = history_db.load_history(st.session_state["chat_id"])




st.set_page_config(page_title="Local Assistant", layout="wide")


# Custom CSS for sticky sidebar
st.markdown("""
    <style>
    .css-1lcbmhc {position: sticky !important; top: 0 !important;}
    </style>
""", unsafe_allow_html=True)


# Sidebar: Open WebUI style
with st.sidebar:
    st.markdown("<h2 style='margin-top:0;margin-bottom:0;color:#FFD700;'>🏠 Local Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<button style='width:100%;margin:12px 0;padding:8px 0;background:#23272f;color:#FFD700;border:none;border-radius:8px;font-size:1em;cursor:pointer;' id='new-chat-btn'>➕ New Chat</button>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top:16px;'><b style='color:#aaa;'>Chats</b></div>", unsafe_allow_html=True)
    for chat_id, chat_name, created_at in st.session_state["chats"]:
        selected = chat_id == st.session_state["chat_id"]
        chat_style = f"background:#23272f;color:#FFD700;border-radius:8px;padding:8px;margin:4px 0;"
        if selected:
            chat_style += "border:2px solid #FFD700;"
        col1, col2, col3 = st.columns([8, 2, 2])
        with col1:
            if selected:
                new_name = st.text_input("Rename chat", value=chat_name, key=f"rename_{chat_id}")
                if new_name != chat_name:
                    history_db.rename_chat(chat_id, new_name[:64])
                    st.session_state["chats"] = history_db.list_chats()
                    st.rerun()
            else:
                if st.button(f"🗂️ {chat_name}", key=f"select_{chat_id}", help="Select chat", use_container_width=True):
                    st.session_state["chat_id"] = chat_id
                    st.session_state["history"] = history_db.load_history(chat_id)
                    st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat", use_container_width=True):
                history_db.delete_chat(chat_id)
                st.session_state["chats"] = history_db.list_chats()
                # If deleted current chat, switch to another
                if st.session_state["chat_id"] == chat_id:
                    chats = st.session_state["chats"]
                    st.session_state["chat_id"] = chats[0][0] if chats else history_db.create_chat("")
                    st.session_state["history"] = history_db.load_history(st.session_state["chat_id"])
                st.rerun()
        with col3:
            st.write("")
    # Handle new chat and delete chat
    query_params = st.query_params
    if "chat_id" in query_params:
        new_chat_id = int(query_params["chat_id"][0])
        st.session_state["chat_id"] = new_chat_id
        st.session_state["history"] = history_db.load_history(new_chat_id)
        st.query_params.clear()
        st.rerun()
    if "delete_chat" in query_params:
        del_id = int(query_params["delete_chat"][0])
        history_db.delete_chat(del_id)
        st.session_state["chats"] = history_db.list_chats()
        # If deleted current chat, switch to another
        if st.session_state["chat_id"] == del_id:
            chats = st.session_state["chats"]
            st.session_state["chat_id"] = chats[0][0] if chats else history_db.create_chat("New Chat")
            st.session_state["history"] = history_db.load_history(st.session_state["chat_id"])
        st.query_params.clear()
        st.rerun()
    # New chat button
    if st.button("➕ New Chat", key="new_chat_btn_sidebar"):
        new_id = history_db.create_chat("")  # Empty name for now
        st.session_state["chats"] = history_db.list_chats()
        st.session_state["chat_id"] = new_id
        st.session_state["history"] = []
        st.session_state["pending_chat_rename"] = True
        st.query_params.clear()
        st.rerun()

## Remove custom JS for copy, use streamlit_js_eval instead
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
    .user-bubble, .assistant-bubble {
        position: relative;
        transition: box-shadow 0.2s;
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
    .bubble-actions {
        position: absolute;
        top: 8px;
        right: 12px;
        display: none;
        gap: 4px;
        z-index: 10;
    }
    .user-bubble:hover .bubble-actions,
    .assistant-bubble:hover .bubble-actions {
        display: flex;
    }
    .bubble-action-btn {
        background: #23272f;
        color: #FFD700;
        border: none;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 1em;
        cursor: pointer;
        margin-left: 2px;
        position: relative;
    }
    /* Tooltip CSS */
    .bubble-action-btn[data-tooltip]:hover:after {
        content: attr(data-tooltip);
        position: absolute;
        top: -32px;
        right: 0;
        background: #23272f;
        color: #FFD700;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.95em;
        white-space: nowrap;
        z-index: 100;
        opacity: 1;
        pointer-events: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)


st.markdown('<div class="chat-history">', unsafe_allow_html=True)
for idx, (user, assistant) in enumerate(st.session_state["history"]):
    user_html = user.replace("\n", "<br>")
    # Only user bubble, no copy button
    st.markdown(
        f'<div class="user-bubble">'
        f'<span style="font-size:1.5em;margin-right:8px;vertical-align:middle;">🧑</span>'
        f'{user_html}'
        f'</div>', unsafe_allow_html=True)
    # Only assistant bubble, no copy button
    st.markdown(
        f'<div class="assistant-bubble">'
        f'<span style="font-size:1.5em;margin-right:8px;vertical-align:middle;">🤖</span>'
        f'{assistant}'
        f'</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
model = os.getenv("MODEL", "qwen3:4b")
system_prompt = os.getenv("SYSTEM_PROMPT")

# Initialize agent
agent = AIAgent(model, endpoint, system_prompt)


if "history" not in st.session_state:
    st.session_state["history"] = []





# Custom CSS for modern input bar
st.markdown("""
    <style>
    .modern-input-bar {
        position: fixed;
        bottom: 32px;
        left: 50%;
        transform: translateX(-50%);
        width: 600px;
        max-width: 90vw;
        background: #222;
        border-radius: 24px;
        box-shadow: 0 2px 16px rgba(0,0,0,0.3);
        padding: 12px 24px;
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 100;
    }
    .modern-input-bar input {
        background: #181818;
        color: #fff;
        border: none;
        border-radius: 16px;
        padding: 10px 16px;
        font-size: 1em;
        flex: 1 1 auto;
        outline: none;
    }
    .modern-input-bar button {
        background: #23272f;
        color: #FFD700;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3em;
        cursor: pointer;
        margin-left: 4px;
    }
    .modern-input-bar .icon {
        font-size: 1.3em;
        color: #aaa;
        margin-right: 8px;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)



st.markdown('<div class="modern-input-bar">', unsafe_allow_html=True)
colInput, colSend = st.columns([8, 1])
with colInput:
    # Use clear_input flag to reset input value before widget instantiation
    input_value = ""
    if "user_input_modern" in st.session_state and not st.session_state.get("clear_input"):
        input_value = st.session_state["user_input_modern"]
    if st.session_state.get("clear_input"):
        input_value = ""
        st.session_state["clear_input"] = False
    user_input = st.text_area(
        "Send a Message",
        value=input_value,
        key="user_input_modern",
        label_visibility="collapsed",
        height=60,
        placeholder="Type your message. Shift+Enter for new line."
    )
    st.caption("Press ⏎ to send, Shift+Enter for new line.")
with colSend:
    send_clicked = st.button("⏎", key="send_modern", help="Send message", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if send_clicked and user_input.strip():
    # Set flag to clear input on next rerun
    st.session_state["clear_input"] = True
    async def get_response():
        response = ""
        async for chunk in agent.chat(user_input):
            response += chunk
        return response
    response = asyncio.run(get_response())
    st.session_state["history"].append((user_input, response))
    history_db.add_to_history(st.session_state["chat_id"], user_input, response)
    # If this is the first message in a new chat, set chat name to user_input
    if st.session_state.get("pending_chat_rename"):
        # Update chat name in DB
        history_db.rename_chat(st.session_state["chat_id"], user_input[:64])
        st.session_state["chats"] = history_db.list_chats()
        del st.session_state["pending_chat_rename"]
    st.rerun()
