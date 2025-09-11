import os, requests, json
from dotenv import load_dotenv
from typing import Any, List, Optional


load_dotenv()
jina_api_key = os.getenv("JINA_API_KEY")
if not jina_api_key:
    raise RuntimeError("JINA_API_KEY is missing")

bocha_api_key = os.getenv("BOCHA_API_KEY")
if not bocha_api_key:
    raise RuntimeError("BOCHA_API_KEY is missing")

def fetch(url: str) -> str:
    if not url:
        return ""
    headers = {'Authorization': f"Bearer {jina_api_key}"}
    print("[fetch]", url)
    response = requests.get(f"https://r.jina.ai/{ url }", headers=headers)
    return response.text

def get_weather(location: str) -> str:
    print("[get_weather]: " + location)
    if location == "Hangzhou":
        return "38 degrees"
    else:
        return "24 degrees"

def bocha_search(query: str) -> str:

    url = "https://api.bochaai.com/v1/web-search"
    
    payload = {
        "query": query,
        "summary": True,
        "count": 10,
    }
    headers = {
        "Authorization": f"Bearer {bocha_api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        print("[bocha_search]", query)

        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        
        #ct = resp.headers.get("content-type", "")
        #print("[bocha_search] Status:", resp.status_code)
        #print("[bocha_search] Content-Type:", ct)
        
        # Try json first; if it fails, print raw text for debugging.
        try:
            data = _extract_webpages(resp.json())
            print("[bocha_search]", f"{len(data)} results")
            return str(data)
        except Exception:
            text_snippet = resp.text[:2000]
            print("[bocha_search] Non-JSON response snippet:\n" + text_snippet)
            return []
    except Exception as e:
        print("[bocha_search] Request failed:", repr(e))
        return []


def _extract_webpages(data) -> list:
    if not data:
        return []
    
    webpages = []
    try:
        for webpage in data["data"]["webPages"]["value"]:
            webpages.append({
                "title": webpage["name"],
                "url": webpage["url"]
            })
        return webpages
    except Exception as e:
        print("Error extracting webpages.", str(e))
        return []
    

def run_tool(fn_name, args):
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
            tool_output = json.dumps({"error": "bocha_search: missing query"})
    elif fn_name == "fetch":
        url = args.get("url")
        if url:
            try:
                tool_output = fetch(url)
            except Exception as e:
                tool_output = json.dumps({"error": str(e)})
        else:
            tool_output = json.dumps({"error": "fetcH: missing url"})
    else:
        tool_output = f"Unsupported tool: {fn_name}"
    
    return tool_output