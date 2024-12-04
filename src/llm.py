from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
from threading import Thread
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Any
import time
import json

class LLM:
    def __init__(self, model_name: str, device: str, use_openai: bool = False) -> None:
        # 判断是否使用 OpenAI 或 OpenRouter API
        self.use_openai = use_openai
        load_dotenv()
        
        if self.use_openai:
            self.api_key = os.getenv("OPENAI_API_KEY")
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
        
        self.valid_models = ["gpt-3.5-turbo", "gpt-4", "openai/gpt-4o-mini"]  # 添加其他有效模型

    def __call__(self, prompt: str, llm_type: str = "gpt-3.5-turbo", response_format: str = "text") -> str:
        if llm_type not in self.valid_models:
            raise ValueError(f"无效的模型 ID: {llm_type}. 有效模型包括: {self.valid_models}")

        messages = [{"role": "user", "content": prompt}]
        params = {
            "model": llm_type,
            "messages": messages,
            "temperature": 0.0001,
        }

        if response_format == "json_object":
            params["response_format"] = {"type": "json_object"}

        try:
            # 调用 OpenAI 或 OpenRouter API
            answer = self.client.chat.completions.create(**params)
            return answer.choices[0].message.content
        except Exception as e:
            print(f"调用 OpenAI API 时出错: {e}")
            return "在生成响应时发生错误。"


class LLM_TTS:
    def __init__(self) -> None:
        # 使用 OpenAI API
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)

    def __call__(self, text: str) -> Any:
        params = {
            "model": "tts-1",
            "input": text,
            "voice": "alloy",
        }
        # 调用 TTS API
        try:
            return self.client.audio.speech.create(**params)
        except Exception as e:
            print(f"调用 TTS API 时出错: {e}")
            return "在生成语音时发生错误。"


def generate_tts(text: str) -> Any:
    llm_model = LLM_TTS()
    tts = llm_model(text)
    return tts.content


def generate_answer(prompt: str, llm_type: str = "openai/gpt-4o-mini-2024-07-18", response_format: str = "text") -> str:
    llm_model = LLM(model_name="openai/gpt-4o-mini-2024-07-18", device="cpu", use_openai=True)  # 使用 OpenAI
    messages = [{"role": "user", "content": prompt}]
    
    if response_format == "json_object":
        messages.insert(0, {
            "role": "system",
            "content": (
                "提供有效的 JSON 输出。数据模式应该类似于: "
                f"{json.dumps({})}"  # 这里可以替换成你的 JSON Schema
            ),
        })
        
    answer = llm_model(messages[0]['content'], llm_type, response_format)
    
    content = answer
    if response_format == "markdown":
        content = content[12:-3]  # 这个切片可能需要根据实际响应结构进行调整
    return content