import os
from typing import Any, List, Optional
import sys
import json
import traceback

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_KEY")
if not api_key:
    raise RuntimeError("Error: DeepSeek/OpenAI API key missing.")

client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

def _mask_token(token: Optional[str]) -> str:
    if not token:
        return "<none>"
    token = str(token)
    if len(token) <= 8:
        return "*" * len(token)
    return token[:4] + "*" * (len(token) - 8) + token[-4:]


def _extract_results(obj: Any, *, verbose: bool = False) -> List[Any]:
    """Best-effort extraction of a list of results from a JSON object."""
    preferred_keys = (
        "web_results",
        "webSearchResults",
        "results",
        "items",
        "documents",
        "hits",
        "records",
    )
    if isinstance(obj, list):
        if verbose:
            print("[bocha_search] _extract_results: object is a list with",
                  len(obj), "items", file=sys.stderr)
        return obj
    if isinstance(obj, dict):
        if verbose:
            print("[bocha_search] _extract_results: dict keys:",
                  list(obj.keys())[:20], file=sys.stderr)
        # Special handling for common container objects like Bing/Bocha style
        # e.g., { "webPages": { "value": [...] }, "images": { "value": [...] } }
        for container_key in ("webPages", "images", "videos"):
            if container_key in obj and isinstance(obj[container_key], dict):
                container = obj[container_key]
                values = container.get("value")
                if isinstance(values, list):
                    if verbose:
                        print(f"[bocha_search] _extract_results: using {container_key}.value with",
                              len(values), "items", file=sys.stderr)
                    return values
        # Direct 'value' list at this level
        if isinstance(obj.get("value"), list):
            vals = obj.get("value")
            if verbose:
                print("[bocha_search] _extract_results: using top-level 'value' with",
                      len(vals), "items", file=sys.stderr)
            return vals
        for key in preferred_keys:
            if key in obj and isinstance(obj[key], list):
                if verbose:
                    print(f"[bocha_search] _extract_results: found list under '{key}' (",
                          len(obj[key]), "items )", file=sys.stderr)
                return obj[key]
        # Fallback: return first list value we see
        for k, v in obj.items():
            if isinstance(v, list):
                if verbose:
                    print(f"[bocha_search] _extract_results: using first list under '{k}'",
                          f"({len(v)} items)", file=sys.stderr)
                return v
    return []


def bocha_search(query: str, *, verbose: bool = False) -> List[Any]:
    """
    Perform a Bocha web search and return the results as a list.

    Defaults to the official endpoint from the sample:
      https://api.bochaai.com/v1/web-search

    Env configuration:
    - BOCHA_SEARCH_URL (optional): override the endpoint
    - BOCHA_API_KEY (required): bearer token (e.g., sk-...)

    Returns [] on error or if no list-like results are found.
    """
    load_dotenv()

    url = os.getenv("BOCHA_SEARCH_URL", "https://api.bochaai.com/v1/web-search")
    api_key = os.getenv("BOCHA_API_KEY") or os.getenv("BOCHA_TOKEN")
    if not api_key:
        raise RuntimeError("BOCHA_API_KEY is required to call Bocha search API.")

    payload = {
        "query": query,
        "summary": True,
        "count": 10,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        if verbose:
            print("[bocha_search] URL:", url, file=sys.stderr)
            print("[bocha_search] Headers.Authorization:", _mask_token(headers.get("Authorization")), file=sys.stderr)
            print("[bocha_search] Payload:", json.dumps(payload, ensure_ascii=False), file=sys.stderr)

        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        ct = resp.headers.get("content-type", "")
        if verbose:
            print("[bocha_search] Status:", resp.status_code, file=sys.stderr)
            print("[bocha_search] Content-Type:", ct, file=sys.stderr)
        # Try json first; if it fails, print raw text for debugging.
        try:
            data = resp.json()
        except Exception:
            text_snippet = resp.text[:2000]
            if verbose:
                print("[bocha_search] Non-JSON response snippet:\n" + text_snippet, file=sys.stderr)
            return []
    except Exception as e:
        if verbose:
            print("[bocha_search] Request failed:", repr(e), file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        return []

    # Normalize to list
    if isinstance(data, list):
        if verbose:
            print("[bocha_search] Top-level list with", len(data), "items", file=sys.stderr)
        return data
    if isinstance(data, dict):
        if verbose:
            print("[bocha_search] Top-level keys:", list(data.keys())[:20], file=sys.stderr)
        # Common schema: { code, msg, data: {...} }
        if "data" in data:
            nested = data["data"]
            if isinstance(nested, dict) and verbose:
                print("[bocha_search] Nested 'data' keys:", list(nested.keys())[:20], file=sys.stderr)
            results = _extract_results(nested, verbose=verbose)
            if results:
                return results
        # Fallback to scan top-level
        results = _extract_results(data, verbose=verbose)
        if results:
            return results
        if verbose:
            print("[bocha_search] No list-like results found in response", file=sys.stderr)
    else:
        if verbose:
            print("[bocha_search] Unexpected response type:", type(data), file=sys.stderr)
    return []


def test_bocha_search(query: str = "天空为什么是蓝色的？", *, verbose: bool = True) -> List[Any]:
    """Simple test helper that calls bocha_search and prints results.

    - Accepts an optional query (defaults to a Chinese sample from the docs).
    - Prints count and a pretty JSON preview of the results.
    - Returns the results list for programmatic use.
    """
    try:
        results = bocha_search(query, verbose=verbose)
    except Exception as e:
        print(f"Bocha search failed: {e}")
        if verbose:
            traceback.print_exc()
        return []

    print(f"Results: {len(results)} items")
    if results:
        preview = results[:3]
        print("Preview (up to 3 items):")
        print(json.dumps(preview, ensure_ascii=False, indent=2))
    return results

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
]

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    return response.choices[0].message

def get_weather(location: str) -> str:
    if location == "Hangzhou":
        return "38 degrees"
    else:
        return "24 degrees"

def run_with_tools(user_content: str, *, verbose: bool = False):
    messages = [{"role": "user", "content": user_content}]
    if verbose:
        print(f"User > {user_content}")

    # Limit number of tool-call rounds to avoid infinite loops
    for _ in range(5):
        message = send_messages(messages)
        messages.append({
            "role": message.role,
            "content": message.content,
            # include tool_calls if present so the model can see its own call history
            **({"tool_calls": message.tool_calls} if getattr(message, "tool_calls", None) else {}),
        })

        tool_calls = getattr(message, "tool_calls", None)
        if not tool_calls:
            # No tool call; final answer
            if verbose:
                print(f"Model > {message.content}")
            return message.content

        # Execute each tool call and append tool results
        for tool_call in tool_calls:
            fn_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments or "{}")
            except Exception:
                args = {}
            if verbose:
                print(f"[tools] calling {fn_name} with args: {args}")

            tool_output = ""
            if fn_name == "get_weather":
                location = args.get("location")
                tool_output = get_weather(location) if location else ""
            elif fn_name == "bocha_search":
                query = args.get("query")
                if query:
                    try:
                        results = bocha_search(query)
                        # Keep payload compact: limit to first 5 results
                        preview = results[:5] if isinstance(results, list) else results
                        tool_output = json.dumps(preview, ensure_ascii=False)
                    except Exception as e:
                        tool_output = json.dumps({"error": str(e)})
                else:
                    tool_output = json.dumps({"error": "missing query"})
            else:
                tool_output = f"Unsupported tool: {fn_name}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_output),
            })

    # If loop exits without returning
    if verbose:
        print("[tools] Reached max tool rounds without final content.")
    return None


if __name__ == "__main__":
    # Demo: run a prompt that should trigger the get_weather tool
    query = sys.argv[1] if len(sys.argv) > 1 else "How's the weather in Hangzhou?"
    run_with_tools(query, verbose=True)
