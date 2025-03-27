import streamlit as st
from utils.interaction import interaction_manager
from utils.html_processing import HtmlProcessing
from langchain.memory import ChatMessageHistory
import json

st.set_page_config(page_title="Web Editor", page_icon="💻", layout="centered")

# Initialize html processor
html_processor = HtmlProcessing(r'placeholder.html')

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "is_dict_complete" not in st.session_state:
    st.session_state.is_dict_complete = None

if "user_interact_history" not in st.session_state:
    st.session_state.user_interact_history = ChatMessageHistory()

if "html_template" not in st.session_state:
    with open('placeholder.html', 'r', encoding='utf-8') as f:
        html_placeholder = f.read()
    
    st.session_state.html_template = html_placeholder

if "json_placeholder" not in st.session_state:
    with open('placeholder.json', 'r', encoding='utf-8') as f:
        json_placeholder = json.load(f)
    
    st.session_state.json_placeholder = json_placeholder

if "customized_html" not in st.session_state:
    st.session_state.customized_html = None


def display_history(messages):
    for role, msg in messages:
        with st.chat_message(role):
            st.markdown(msg)


def main():
    display_history(st.session_state.chat_history)

    user_input = st.chat_input("Type a message...", key="ChatInput")

    if user_input:
        # Handle starting the questioning process
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append(("user", user_input))


        if not st.session_state.is_dict_complete:
            st.session_state.user_interact_history.add_user_message(user_input)
            (
                llm_respond,
                st.session_state.json_placeholder,
                st.session_state.is_dict_complete,
                st.session_state.user_interact_history,
            ) = interaction_manager(
                st.session_state.json_placeholder, st.session_state.user_interact_history
            )
            
            st.session_state.chat_history.append(("assistant", llm_respond))
            
            with st.chat_message("assistant"):
                st.markdown(llm_respond)
        
        
        else:
            # Replace placeholders in the HTML with values from the JSON dictionary
            for key, value in st.session_state.json_placeholder.items():
                placeholder = f"{key}"  # Assuming placeholders in HTML are in the format {{C1}}, {{C2}}, etc.
                st.session_state.html_template = st.session_state.html_template.replace(placeholder, value)
            st.session_state.customized_html = st.session_state.html_template
        
        
        if st.session_state.customized_html:
            with st.chat_message("assistant"):
                st.markdown("Your Lnadpage is ready!")
                html_processor.save_html('new_placeholder.html', st.session_state.customized_html)


if __name__ == "__main__":
    main()