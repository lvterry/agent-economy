from typing import Any, Dict, Optional, AsyncGenerator, List
import json
import asyncio

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from app.tools import client, tools as tool_schema, get_weather, bocha_search


app = FastAPI(title="LLM Tools Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_tool(name: str, args: Dict[str, Any]) -> str:
    if name == "get_weather":
        location = args.get("location")
        return get_weather(location) if location else ""
    if name == "bocha_search":
        query = args.get("query")
        if not query:
            return json.dumps({"error": "missing query"}, ensure_ascii=False)
        try:
            results = bocha_search(query)
            return json.dumps(results[:5] if isinstance(results, list) else results, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    return json.dumps({"error": f"Unsupported tool: {name}"}, ensure_ascii=False)


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    user_message: str = body.get("message", "").strip()
    if not user_message:
        return JSONResponse({"error": "message required"}, status_code=400)

    messages: List[Dict[str, Any]] = [{"role": "user", "content": user_message}]

    # Tool-call loop (non-stream)
    for _ in range(5):
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tool_schema,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)
        if not tool_calls:
            return {"content": msg.content or ""}

        # append the assistant message that contains tool_calls
        messages.append({
            "role": msg.role,
            "content": msg.content,
            "tool_calls": tool_calls,
        })

        # Execute tools and append results
        for tc in tool_calls:
            fn_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            result = _resolve_tool(fn_name, args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return JSONResponse({"error": "max tool iterations reached"}, status_code=500)


@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    user_message: str = body.get("message", "").strip()
    if not user_message:
        return JSONResponse({"error": "message required"}, status_code=400)

    async def generate() -> AsyncGenerator[bytes, None]:
        # Emit a start event
        yield (json.dumps({"type": "start"}) + "\n").encode("utf-8")

        messages: List[Dict[str, Any]] = [{"role": "user", "content": user_message}]

        # Tool-call loop (non-stream phase)
        for _ in range(5):
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=tool_schema,
                tool_choice="auto",
            )
            msg = resp.choices[0].message
            tool_calls = getattr(msg, "tool_calls", None)
            if not tool_calls:
                # No tool calls; proceed to streaming final content
                break

            # Record the assistant tool call message
            messages.append({
                "role": msg.role,
                "content": msg.content,
                "tool_calls": tool_calls,
            })

            # Execute tools
            for tc in tool_calls:
                fn_name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except Exception:
                    args = {}
                # Stream a tool_call event
                yield (json.dumps({
                    "type": "tool_call",
                    "name": fn_name,
                    "args": args,
                }, ensure_ascii=False) + "\n").encode("utf-8")

                result = _resolve_tool(fn_name, args)
                # Stream a tool_result event
                yield (json.dumps({
                    "type": "tool_result",
                    "name": fn_name,
                    "result": result,
                }, ensure_ascii=False) + "\n").encode("utf-8")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        # Now stream final content tokens
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True,
        )
        try:
            for chunk in stream:
                try:
                    # OpenAI v1: delta.content holds incremental text
                    delta = chunk.choices[0].delta
                    text = getattr(delta, "content", None)
                except Exception:
                    text = None
                if text:
                    yield (json.dumps({"type": "content_delta", "text": text}, ensure_ascii=False) + "\n").encode("utf-8")
                await asyncio.sleep(0)
        finally:
            yield (json.dumps({"type": "done"}) + "\n").encode("utf-8")

    return StreamingResponse(generate(), media_type="application/x-ndjson")


# Convenience root
@app.get("/")
def root():
    return {"status": "ok"}

