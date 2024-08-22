import streamlit as st
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import time

DEVICE: str = "cuda"
MODEL_NAME: str = "/disk2/elvys/Mistral-7B-Instruct-v0.2"

class LLM:
    def __init__(self) -> None:
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            attn_implementation="flash_attention_2",
            device_map="auto"
        )
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"

    def __call__(self, prompt: str) -> str:
        model_inputs = self.tokenizer.encode_plus(prompt, return_tensors="pt", padding=True).to(DEVICE)
        with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
            generated_ids = self.model.generate(model_inputs['input_ids'], max_new_tokens=1100, do_sample=False)
            decoded = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        return decoded[0]

st.set_page_config(layout="wide")

def get_test_prompt(query: str, role: str) -> str:
    if role == "Exam rule":
        role_description = "CFA EXAM rule expert"
    elif role == "Financial Basic knowledge":
        role_description = "Financial Basic knowledge expert"
    else:
        raise ValueError("Invalid role type. Please choose 'Exam rule' or 'Financial Basic knowledge'.")
    
    prompt = f"""
Imagine you're a helpful {role_description}, you should only respond to the question of the user in this area. For other types of questions, just say: 'this is not my area'.
----------------------------
QUESTION: {query}
Your response has to be concise and answer only the question of the user. 
Your response should be in Markdown and adapted to the user's knowledge level in finance. The different knowledge levels of the user are:
- For Novice user: Use simple words; give a short definition of each indicator and its interpretation. Analysis needs to be understandable by users with no knowledge in finance.
- Confirmed: The user has some knowledge but is not an expert in finance.
- Expert: The user is an expert in finance, so you can elaborate on a sophisticated analysis.
You should highlight in **bold** relevant passages/key words in your response to make it easier to understand.
Finally, your response cannot have any notes about rewording or user experience.
    """
    return prompt
def convert_str_to_markdown(text: str) -> str:
    text = text.replace("$", r"\$")
    text = text.replace("\n", "\n\n")
    return text

@st.cache_resource
def load_llm_model() -> LLM:
    return LLM()

llm_model = load_llm_model()

# Store the initial value of widgets in session state
if "disabled" not in st.session_state:
    st.session_state.disabled = False
    st.session_state.messages = []

with st.sidebar:
    st.title('CFA Assistant')
    assistant_type = st.selectbox('Select assistant type:', ["Exam rule", "Financial Basic knowledge expert"], index=0, disabled=st.session_state.disabled)
    analysis_type = st.selectbox('AI Analysis Style:', ["Analytical", "Advisory"], index=0, disabled=st.session_state.disabled)
    experience_user = st.selectbox('Knowledge Level:', ["Novice", "Confirmed", "Expert"], index=0, disabled=st.session_state.disabled)

query = st.chat_input("Write your query ...", disabled=st.session_state.disabled)

if query:
    st.chat_message("user").markdown(query)
    st.session_state.disabled = True
    start = time.time()
    prompt = get_test_prompt(query,assistant_type)
    print("PROMPT:", prompt)
    chat_model_response = llm_model(prompt)
    chat_model_response = chat_model_response.split("[/INST]")[-1].split("</s>")[0]
    print("Inference duration:", time.time() - start)
    st.chat_message("assistant").markdown(chat_model_response)
    st.session_state.disabled = False
