import streamlit as st
import openai
import os
from dotenv import load_dotenv
import sys


# Load credentials from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Add PYTHONPATH dynamically
pythonpath = os.getenv("PYTHONPATH")
if pythonpath and pythonpath not in sys.path:
    sys.path.append(pythonpath)

from src.PROMPTS import PROMPTS  # Ensure PROMPTS is correctly imported


# Function to query OpenAI API
def query_openai(prompt, user_input):
    """
    Calls OpenAI API with the given prompt and user input.
    """
    try:
        # Use the `openai.ChatCompletion.create` for sync API call
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        return response['choices'][0]['message']['content']
    except openai.OpenAIError as e:
        st.error(f"OpenAI API Error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
        return None


# Streamlit UI and main logic
def main():
    # Configure the Streamlit page
    st.set_page_config(page_title="CFA Chatbot", layout="wide")
    st.title("📊📈 CFA France Society Chatbot")
    st.write("Welcome to the CFA chatbot! Select a function and type your question below.")

    # Sidebar for function selection
    function = st.sidebar.selectbox(
        "Select a Function",
        list(PROMPTS.keys()),  # Dynamically fetch function names from PROMPTS
        index=0,
    )
    st.sidebar.write(f"**Selected Function:** {function}")

    # Input area for user question
    user_input = st.text_area("Enter your question:", placeholder="Type your question here...")
    submit_button = st.button("Submit Question")

    # Process user input
    if submit_button:
        if not user_input.strip():
            st.warning("Please enter a valid question before submitting.")
        else:
            st.write("### Your Question:")
            st.write(user_input)

            with st.spinner("Generating answer..."):
                # Get the corresponding prompt
                prompt_func = PROMPTS.get(function)
                if callable(prompt_func):  # Ensure the value is callable (a function)
                    # Pass the required parameter (user_input) to the function
                    prompt = prompt_func(user_input)
                else:  # If it's already a string, use it directly
                    prompt = prompt_func

                # Query OpenAI
                if prompt:
                    answer = query_openai(prompt, user_input)
                else:
                    answer = "Invalid prompt. Please check your PROMPTS configuration."

            # Display the answer
            if answer:
                st.write("### Answer:")
                st.write(answer)

                # Save question and answer to session state
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.append({"function": function, "question": user_input, "answer": answer})

    # Display chat history
    if "history" in st.session_state and st.session_state.history:
        st.write("### Chat History:")
        for i, record in enumerate(st.session_state.history):
            st.write(f"**{i+1}. Function:** {record['function']}")
            st.write(f"**Question:** {record['question']}")
            st.write(f"**Answer:** {record['answer']}")
            st.write("---")


if __name__ == "__main__":
    main()
