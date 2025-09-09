import os
import sys
import time
import threading
from dotenv import load_dotenv

from openai import OpenAI

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError( "API key missing.")

llm = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
response = llm.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant, if asked your name say Hello World."},
        {"role": "user", "content": "What is your name?"},
    ],
    stream=False,
)

respContent = response.choices[0].message.content

print(respContent)
