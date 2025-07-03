import streamlit as st
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
import json

# Load .env file
load_dotenv()

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment. Please check your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Dynamically load PYTHONPATH
pythonpath = os.getenv("PYTHONPATH")
if pythonpath and pythonpath not in sys.path:
    sys.path.append(pythonpath)

from src.PROMPTS import PROMPTS  # Prompt dictionary or functions

def save_log(function, question, answer, filename="chat_log.jsonl"):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "function": function,
        "question": question,
        "answer": answer
    }
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def query_openai(prompt, user_input):
    """
    Calls OpenAI API with the given prompt and user input.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        st.error(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
        return None


def query_openai_stream(prompt, user_input):
    """
    Calls OpenAI API using streaming mode.
    Yields content chunks as they arrive.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
            max_tokens=500,
            stream=True  # ✅ 关键：启用流式输出
        )

        full_response = ""
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                yield delta  # 每次返回新增字符
        return full_response

    except OpenAIError as e:
        yield f"\n\n[OpenAI API Error]: {e}"
    except Exception as e:
        yield f"\n\n[Unexpected Error]: {e}"

def main():
    st.set_page_config(page_title="CFA Chatbot", layout="wide")
    st.title("📊📈 CFA France Society Chatbot")
    st.write("Welcome to the CFA chatbot! Select a function and type your question below.")

    # Sidebar selection
    function = st.sidebar.selectbox("Select a Function", list(PROMPTS.keys()), index=0)
    st.sidebar.write(f"**Selected Function:** {function}")

    # Input area
    user_input = st.text_area("Enter your question:", placeholder="Type your question here...")
    submit_button = st.button("Submit Question")

    if submit_button:
        if not user_input.strip():
            st.warning("Please enter a valid question before submitting.")
        else:
            st.write("### Your Question:")
            st.write(user_input)

            with st.spinner("Generating answer..."):
                # Get prompt
                prompt_func = PROMPTS.get(function)
                prompt = prompt_func(user_input) if callable(prompt_func) else prompt_func

                # Streaming response
                if prompt:
                    output_area = st.empty()  # 用于动态更新输出
                    streamed_answer = ""
                    for chunk in query_openai_stream(prompt, user_input):  # <-- 使用流式接口
                        streamed_answer += chunk
                        output_area.markdown(f"### Answer:\n\n{streamed_answer}")
                    answer = streamed_answer
                else:
                    answer = "Invalid prompt. Please check your PROMPTS configuration."
                    st.error(answer)

            if answer:
                # 保存到历史记录
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.append({
                    "function": function,
                    "question": user_input,
                    "answer": answer
                })
                save_log(function, user_input, answer)

    # 显示历史记录
    if "history" in st.session_state and st.session_state.history:
        st.write("### Chat History:")
        for i, record in enumerate(st.session_state.history):
            st.write(f"**{i+1}. Function:** {record['function']}")
            st.write(f"**Question:** {record['question']}")
            st.write(f"**Answer:** {record['answer']}")
            st.write("---")


if __name__ == "__main__":
    main()
