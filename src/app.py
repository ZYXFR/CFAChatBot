import streamlit as st
import time
import pandas as pd
from .llm import LLM,generate_answer, generate_tts
from .prompts import get_markdown_prompt, get_translation_prompt
from .prompts.fundamental_prompt import get_fundation_prompt
from .prompts.general_prompt import get_general_prompt
from .constants import JSON_RESPONSE_SCHEMA, OUTPUT_FORMAT, TARGET_LANGUAGES
from .utils import convert_str_to_markdown, save_data, stream_data


def run():
    st.set_page_config(layout="wide")
    st.title("📊📈CFA France Scociety Chatbot")

    # Store the initial value of widgets in session state
    if "disabled" not in st.session_state:
        st.session_state.disabled = False
        st.session_state.messages = []

    with st.sidebar:
        st.title("📊📈CFA France Scociety Chatbot")
        llm_type: str = "openai/gpt-4o-mini-2024-07-18"
        assistant_type: str = st.selectbox(
            "Select assistant type:",
            ["AI Analyzer"],
            index=0,
            disabled=st.session_state.disabled,
        )
        analyzer_type: str = st.selectbox(
            "Select data:",
            ["General questions", "Fundation questions"],
            index=0,
            disabled=st.session_state.disabled,
        )
        language: str = st.selectbox(
            "Target language:",
            list(TARGET_LANGUAGES.keys()),
            index=0,
            disabled=st.session_state.disabled,
        )
        output_format: str = st.selectbox(
            "Output format:",
            OUTPUT_FORMAT,
            index=0,
            disabled=st.session_state.disabled,
        )
        button = st.button("Generate AI analysis", disabled=st.session_state.disabled)
    if button and assistant_type == "AI Analyzer":
        if analyzer_type == "General questions":
            prompt = get_general_prompt()
        elif analyzer_type == "Funancial questions":
            prompt = get_fundation_prompt()
        print(prompt)
        answer = generate_answer(
            prompt,
            llm_type,
            response_format="json_object",
            json_schema=JSON_RESPONSE_SCHEMA[analyzer_type],
        )
        if language != "English":
            prompt = get_translation_prompt(answer, language, analyzer_type)
            answer = generate_answer(
                prompt,
                llm_type,
                response_format="json_object",
                json_schema=JSON_RESPONSE_SCHEMA[analyzer_type],
            )
        if output_format == "markdown":
            prompt = get_markdown_prompt(answer)
            answer = convert_str_to_markdown(
                generate_answer(
                    prompt, llm_type, response_format="markdown", json_schema=""
                )
            )
        st.write_stream(stream_data(answer))