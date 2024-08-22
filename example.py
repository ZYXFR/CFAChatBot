import streamlit as st
import pandas as pd
import csv
import torch
import numpy as np
from tc_common_py import config, internal_api, s3_gate
from tc_common_py.config_plugins import api, aws, logs
from transformers import AutoModelForCausalLM, AutoTokenizer
import time
from . import prompts, utils, tc_utils

DEVICE: str = "cuda"
# MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.2"
MODEL_NAME: str = "/disk2/elvys/Mistral-7B-Instruct-v0.2"

class LLM:
    def __init__(self) -> None:
        # self.model = AutoModelForCausalLM.from_pretrained(MODEL_NAME).to(DEVICE)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float16, attn_implementation="flash_attention_2", device_map="auto")
        self.model.eval()
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def __call__(self, messages: list) -> str:
        # Tokenize messages
        model_inputs = self.tokenizer.apply_chat_template(messages, return_tensors="pt").to(DEVICE)
        # Generate answer for the given input
        with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
            generated_ids = self.model.generate(model_inputs, max_new_tokens=1100, do_sample=False)
            decoded = self.tokenizer.batch_decode(generated_ids)
        return decoded[0]


class APIConnectionTestEnv(internal_api.APIConnection):
    def __init__(self, api_domain: str = "", timeout: int = 5) -> None:
        self.domain = api_domain
        self.timeout = timeout

        conf = config.load()
        self.client_id = conf.env_space.get("api_client_id_env")
        self.auth_api_key = conf.env_space.get("api_key_env", "")
        if not self.domain:
            self.domain = conf.env_space.get("api_domain_env")

        self.token = ""
        self.reset_token()


def run() -> None:
    st.set_page_config(
        layout="wide",
    )

    @st.cache_resource
    def load_llm_model() -> LLM:
        return LLM()
    llm_model = load_llm_model()

    @st.cache_resource
    def load_api_connection() -> APIConnectionTestEnv:
        conf = config.load()
        conf.plug(logs, aws, api)
        return APIConnectionTestEnv()
    _api = load_api_connection()

    @st.cache_resource
    def get_tc_data(_api) -> tuple:
        classic_patterns: list = utils.load_patterns()
        assets = utils.load_assets()
        prices: dict = {}
        smas: dict = {}
        support_resistances: dict = {}
        active_patterns: dict = {}
        anticipated_patterns: dict = {}
        oscillators_values: dict = {}
        for asset in assets:
            prices[asset] = tc_utils.get_price_performance(assets[asset]["instrument_id"], _api)
            smas[asset] = tc_utils.get_simple_moving_average_performance(assets[asset]["instrument_id"], _api)
            support_resistances[asset] = tc_utils.get_support_and_resistance_performance(assets[asset]["instrument_id"],  _api)
            oscillators_values[asset] = tc_utils.get_technical_indicators_performance(assets[asset]["instrument_id"], _api)
            active_patterns[asset] = tc_utils.get_active_events(assets[asset]["instrument_id"], _api)
            anticipated_patterns[asset] = tc_utils.get_anticipated_events(assets[asset]["instrument_id"], _api)
        return assets, prices, smas, support_resistances, oscillators_values, active_patterns, anticipated_patterns

    assets, prices, smas, support_resistances, oscillators_values, active_patterns, anticipated_patterns = get_tc_data(_api)

    # Store the initial value of widgets in session state
    if "disabled" not in st.session_state:
        st.session_state.disabled = False
        st.session_state.messages = []

    with st.sidebar:
        st.title('Rene: Investment assistant')
        assistant_type = st.selectbox('Select assistant type:', ["AI Technical analysis", "Chatbot"], index=0, disabled=st.session_state.disabled)
        analysis_type = st.selectbox('AI Analysis Style:', ["Analytical", "Advisory"], index=0, disabled=st.session_state.disabled)
        experience_user = st.selectbox('Knowledge Level:', ["Novice", "Specialist"], index=0, disabled=st.session_state.disabled)
        selected_asset = st.selectbox('Select an asset:', assets.keys(), index=0, disabled=st.session_state.disabled)
        # st.write("")
        # if assets[selected_asset]["logo"]:
        #     st.image(assets[selected_asset]["logo"])
        # st.write(assets[selected_asset]["description"])
    
    if assistant_type == "AI Technical analysis":
        with st.sidebar:
            button = st.button('Generate AI Technical analysis', disabled=st.session_state.disabled)
        if button and assistant_type == "AI Technical analysis":
            st.session_state.disabled = True
            if selected_asset == "General":
                st.markdown(utils.convert_str_to_markdown("Select an asset to get the AI Technical analysis."))
            else:
                start = time.time()
                prompt = prompts.get_prompt(
                    selected_asset, 
                    experience_user,
                    analysis_type,
                    f"Provide the financial analysis of {selected_asset}", 
                    prices[selected_asset], 
                    smas[selected_asset], 
                    support_resistances[selected_asset], 
                    oscillators_values[selected_asset],
                    active_patterns[selected_asset], 
                    anticipated_patterns[selected_asset],
                )
                print("PROMPT:", prompt)
                chat_model_response = llm_model([{"role": "user", "content": prompt}])
                chat_model_response = chat_model_response.split("[/INST]")[-1].split("</s>")[0]
                st.markdown(utils.convert_str_to_markdown(chat_model_response))
                print("Inference duration:", time.time() - start)
            st.session_state.disabled = False
    elif assistant_type == "Chatbot":
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(utils.convert_str_to_markdown(message["content"]))

        if query := st.chat_input("Write your query ...", disabled=st.session_state.disabled):
            # Display user message in chat message container
            st.chat_message("user").markdown(utils.convert_str_to_markdown(query))
            st.session_state.disabled = True
            start = time.time()
            prompt = prompts.get_prompt(
                selected_asset,
                experience_user,
                assistant_type,
                query,
                prices[selected_asset],
                smas[selected_asset],
                support_resistances[selected_asset],
                oscillators_values[selected_asset],
                active_patterns[selected_asset],
                anticipated_patterns[selected_asset],
            )
            print("PROMPT:", prompt)
            # chat_model_response = llm_model(st.session_state.messages + [{"role": "user", "content": prompt}])
            chat_model_response = llm_model([{"role": "user", "content": prompt}])
            chat_model_response = chat_model_response.split("[/INST]")[-1].split("</s>") [0]
            # Add user and system messages to chat history
            st.session_state.messages.append({"role": "user", "content": query})
            st.session_state.messages.append({"role": "assistant", "content": chat_model_response})
            print("ANSWER:", chat_model_response)
            print("Inference duration:", time.time() - start)
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(utils.convert_str_to_markdown(chat_model_response))
            st.session_state.disabled = False

if __name__ == "__main__":
    run()
