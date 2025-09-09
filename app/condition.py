import os
import json
from dotenv import load_dotenv

from openai import OpenAI

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_KEY")
if not api_key:
    raise RuntimeError("API key missing.")

llm = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

system_prompt = "You are a helpful assitant. You answer in a clear and concise way. If you don't know the anwser, say you don't know."

user_prompt = "What is the average wing speed of a swallow?"

print("-" * 10)
print(f"Question: { user_prompt }")

response = llm.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    stream=False,
)

answer = response.choices[0].message.content

print(f"\nAnswer: { answer }")

print("-" * 10)

judge_prompt = """
You are a strict critic. 
Given the following question, determine if the answer a full anwser to the question.
Your output is in json format.

EXAMPLE JSON OUTPUT:
{ "is_full_answer": true }
"""

judge_prompt += f"\n\nQuestion: { user_prompt } \n\n Answer: { answer }"

judge = llm.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": judge_prompt},
    ],
    stream=False,
    response_format={
        'type': 'json_object'
    }
)

judge_output_raw = judge.choices[0].message.content

# Parse judge output to boolean
is_full_answer = False
try:
    data = json.loads(judge_output_raw or "{}")
    value = data.get("is_full_answer")
    if isinstance(value, bool):
        is_full_answer = value
    elif isinstance(value, str):
        is_full_answer = value.strip().lower() in {"true", "yes", "1"}
    elif isinstance(value, (int, float)):
        is_full_answer = bool(value)
except Exception:
    # Keep default False if parsing fails
    pass

if is_full_answer:
    print("LLM judge: 👍")
else:
    print("LLM judge: 👎")