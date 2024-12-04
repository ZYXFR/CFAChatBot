import streamlit as st

def render_ui():
    
    st.set_page_config(layout="wide")

        # Store the initial value of widgets in session state
    if "disabled" not in st.session_state:
        st.session_state.disabled = False
        st.session_state.messages = []

    with st.sidebar:
        st.title('Financial Assistant')
        if "assistant_type" not in st.session_state:
            st.session_state.assistant_type = "Exam rule"
        if "analysis_type" not in st.session_state:
            st.session_state.analysis_type = "Analytical"
        if "experience_user" not in st.session_state:
            st.session_state.experience_user = "Novice"
        
        st.session_state.assistant_type = st.selectbox('Select assistant type:', ["Exam rule", "Financial Basic knowledge expert"], index=0, disabled=st.session_state.disabled)
        st.session_state.analysis_type = st.selectbox('AI Analysis Style:', ["Analytical", "Advisory"], index=0, disabled=st.session_state.disabled)
        st.session_state.experience_user = st.selectbox('Knowledge Level:', ["Novice", "Confirmed", "Expert"], index=0, disabled=st.session_state.disabled)
