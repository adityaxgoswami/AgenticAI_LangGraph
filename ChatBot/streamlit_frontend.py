import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage,AIMessage
import uuid

#========================= UTILITY FUNCTIONS ==================================
def generate_session_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread = generate_session_id()
    st.session_state['thread_id'] = thread
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
def load_convo(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id':st.session_state['thread_id']}})
    return  state.values.get('messages',[])
    
#------------------------------------------------------------------------------  
if "message_history" not in st.session_state:
    st.session_state['message_history'] = []
    
if "thread_id" not in st.session_state:
    st.session_state['thread_id'] = generate_session_id()


if "chat_threads" not in st.session_state:
    st.session_state['chat_threads'] = []
    #hmlog ko 2 baar threads ko add krna hoga 
    # 1. when the whole chat is loaded 
    # 2. when the user click the new chat button
add_thread(st.session_state['thread_id'])  
#==============================XXXXXXXXXX=====================================
st.title("ChatBot with LangGraph")
#========================== SIDE BAR =========================================
st.sidebar.title("Langgraph ChatBot")
if st.sidebar.button('New Chat'):
    reset_chat()
st.sidebar.header("Chat History")

for thread in st.session_state['chat_threads'][::-1]:
    # if this thread is clicked then load the convo history
    if st.sidebar.button(str(thread)):
        st.session_state['thread_id'] = thread
        messages = load_convo(thread)
        
        temp_history = []
        for mssg in messages:
            if isinstance(mssg, HumanMessage):
                temp_history.append({'role': 'user', 'content': mssg.content})
            elif isinstance(mssg, AIMessage):
                temp_history.append({'role': 'assistant', 'content': mssg.content})
        st.session_state['message_history'] = temp_history

#================================XXXXXXXXXXXXX=======================================
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

     # first add the message to message_history
    with st.chat_message("assistant"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    # yield only assistant tokens
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
