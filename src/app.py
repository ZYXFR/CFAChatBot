import streamlit as st

def generate_response(prompt, language="English", format_type="Text"):
    """
    模拟生成响应，实际逻辑可替换为调用 LLM API。
    """
    # 模拟返回数据
    if language != "English":
        return f"Translated ({language}): {prompt}"
    if format_type == "Markdown":
        return f"**Markdown Format:** {prompt}"
    return f"Response: {prompt}"

def run():
    st.set_page_config(layout="wide")
    st.title("📊📈CFA France Society Chatbot")

    # 初始化 Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.title("📊📈 Chatbot Settings")
        # 设置 Prompt 类型
        prompt_type = st.selectbox(
            "Select Prompt Type:", 
            ["General questions", "Financial questions"], 
            index=0
        )
        # 选择语言
        language = st.selectbox(
            "Select Target Language:", 
            ["English", "French", "Spanish", "Chinese"], 
            index=0
        )
        # 输出格式
        output_format = st.selectbox(
            "Select Output Format:", 
            ["Text", "Markdown"], 
            index=0
        )
        # 按钮触发
        generate_button = st.button("Generate AI Analysis")

    # 主界面逻辑
    if generate_button:
        # 根据 Prompt 类型生成 Prompt
        if prompt_type == "General questions":
            prompt = "This is a general question prompt. Please modify as needed."
        elif prompt_type == "Financial questions":
            prompt = "This is a financial question prompt. Please modify as needed."

        # 生成 AI 响应
        response = generate_response(prompt, language, output_format)

        # 显示结果
        st.session_state.messages.append(response)
        for msg in st.session_state.messages:
            st.write(msg)

if __name__ == "__main__":
    run()
