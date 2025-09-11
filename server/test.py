import os, sys, json
from openai import OpenAI
from dotenv import load_dotenv
from tools import bocha_search, get_weather, run_tool

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise RuntimeError("Error: DeepSeek API key missing.")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bocha_search",
            "description": "Search the web using Bocha Web Search and return a list of results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to look up on the web",
                    }
                },
                "required": ["query"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch",
            "description": "Visit a URL and return a markdown version of the browsed page content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The url of the web page to go get and return as markdown.",
                    }
                },
                "required": ["url"]
            },
        }
    },
]

def parse_is_full_answer(text: str) -> bool:
    try:
        data = json.loads(text or "{}")
    except Exception:
        return False
    value = data.get("is_full_answer")
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}
    if isinstance(value, (int, float)):
        return bool(value)
    return False

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
    )
    return response.choices[0].message

def send_messages_with_tools(messages, tools):
    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    return completion.choices[0].message

def chatbot(user_prompt: str):
    user_prompt = "杭州天气怎么样" if not user_prompt else user_prompt
    system_prompt = "You are a helpful assistant. You answer in a clear and concise way. Match your output language with user's question."
    messages = [{
        "role": "system",
        "content": system_prompt
    }]
    messages.append({
        "role": "user",
        "content": user_prompt
    })
    print("-" * 30)
    print("User > " + user_prompt)

    answer = send_messages(messages).content
    print("\nAssistant > " + answer)
    print("-" * 30)

    check_answer(user_prompt, answer)

def chatbot_with_tools(user_prompt: str):
    user_prompt = "杭州天气怎么样" if not user_prompt else user_prompt
    # system_prompt = "You are a helpful assistant. You answer in a clear and concise way. Match your output language with user's question."
    messages = [{
        "role": "user",
        "content": user_prompt
    }]

    print("-" * 30)
    print("User > " + user_prompt)

    # Limit rounds of tool calls to avoid infinite loop
    for _ in range(10):
        message = send_messages_with_tools(messages, tools)
        messages.append({
            "role": message.role,
            "content": message.content,
            # include tool_calls if present so the model can see its own call history
            **({"tool_calls": message.tool_calls} if getattr(message, "tool_calls", None) else {}),
        })
    
        tool_calls = getattr(message, "tool_calls", None)
        if not tool_calls:
            # No tool call needed. final anwser
            print("\nAssistant > ", message.content)
            # Ask LLM to judge the answer
            check_answer(user_prompt, message.content)
            return message.content
        
        for tool_call in tool_calls:
            fn_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments or "{}")
            except Exception:
                args = {}
        
            tool_output = run_tool(fn_name, args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_output)
            })

    # Loop exits without returning
    print("[tools] Reached max tool rounds without final content.")
    return None

def check_answer(question, answer):
    judge_prompt = """
        You are a strict critic. 
        Given the following question, determine if the answer a full anwser to the question.
        Your output is in json format.

        EXAMPLE JSON OUTPUT:
        { "is_full_answer": true }"""
    judge_prompt += f"\n\nQuestion: { question } \n\n Answer: { answer }"
    messages = [{
        "role": "user",
        "content": judge_prompt
    }]
    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={ 'type': 'json_object' }
    )
    resultStr = completion.choices[0].message.content
    result = parse_is_full_answer(resultStr)

    print("\nLLM judge > 👍") if result else print("LLM judge > 👎")
    print("-" * 30)


if __name__ == "__main__":
    # Demo: run a prompt that should trigger the get_weather tool
    query = sys.argv[1] if len(sys.argv) > 1 else "杭州天气怎么样"
    chatbot_with_tools(query)