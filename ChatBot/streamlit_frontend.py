import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# ========================= UTILITY FUNCTIONS ==================================
def generate_session_id():
    return uuid.uuid4()

def reset_chat():
    thread = generate_session_id()
    st.session_state['thread_id'] = thread
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
def load_convo(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])
    
# ------------------------------------------------------------------------------  
if "message_history" not in st.session_state:
    st.session_state['message_history'] = []
    
if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_session_id()

if "chat_threads" not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])  

# ============================== UI SETUP =====================================
st.title("ChatBot with LangGraph")

# =========================== SIDEBAR =========================================
st.sidebar.title("LangGraph ChatBot")
if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header("Chat History")

for thread in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread), key=f"btn_{thread}"):
        st.session_state['thread_id'] = thread
        messages = load_convo(thread)
        
        temp_history = []
        for mssg in messages:
            if isinstance(mssg, HumanMessage):
                temp_history.append({'role': 'user', 'content': mssg.content})
            elif isinstance(mssg, AIMessage):
                temp_history.append({'role': 'assistant', 'content': mssg.content})
        st.session_state['message_history'] = temp_history

# ========================== CHAT DISPLAY ======================================
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})