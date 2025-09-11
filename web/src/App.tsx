import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
import { Card, CardHeader, CardContent } from './components/ui/card'
import { ScrollArea } from './components/ui/scroll-area'
import Markdown from './components/Markdown'
import { Trash2 } from 'lucide-react'

type EventItem =
  | { type: 'start' }
  | { type: 'tool_call'; name: string; args: any }
  | { type: 'tool_result'; name: string; result: string }
  | { type: 'content_delta'; text: string }
  | { type: 'done' }

type ToolEvent =
  | { kind: 'call'; name: string; args: any }
  | { kind: 'result'; name: string; result: string }

type ChatMessage = { role: 'user' | 'assistant' | 'tool'; content: string; toolEvents?: ToolEvent[] }

function useChatStream() {
  const [events, setEvents] = useState<EventItem[]>([])
  const [output, setOutput] = useState('')
  const controllerRef = useRef<AbortController | null>(null)
  const [loading, setLoading] = useState(false)

  const start = useCallback(async (message: string) => {
    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller
    setEvents([])
    setOutput('')
    setLoading(true)

    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
      signal: controller.signal,
    })
    if (!resp.body) return

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      let idx: number
      while ((idx = buffer.indexOf('\n')) !== -1) {
        const line = buffer.slice(0, idx).trim()
        buffer = buffer.slice(idx + 1)
        if (!line) continue
        try {
          const evt: EventItem = JSON.parse(line)
          setEvents(prev => [...prev, evt])
          // Only hide when first displayable assistant text arrives
          if (evt.type === 'content_delta' && evt.text) {
            setLoading(false)
            setOutput(prev => prev + (evt.text || ''))
          } else if (evt.type === 'content_delta') {
            // ensure we accumulate even empty chunks without hiding
            setOutput(prev => prev + (evt.text || ''))
          }
        } catch {
          // ignore parse errors
        }
      }
    }
    setLoading(false)
  }, [])

  const stop = useCallback(() => {
    controllerRef.current?.abort()
    setLoading(false)
  }, [])

  const reset = useCallback(() => {
    controllerRef.current?.abort()
    setEvents([])
    setOutput('')
    setLoading(false)
  }, [])

  const clearOutput = useCallback(() => setOutput(''), [])

  return { events, output, start, stop, reset, loading, clearOutput }
}

export default function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const { events, output, start, reset, loading, clearOutput } = useChatStream()
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, output, events])

  // When a stream completes, move the streamed output into the messages list
  const lastEventType = events.length ? events[events.length - 1].type : undefined
  useEffect(() => {
    if (lastEventType === 'done' && output.trim().length > 0) {
      const persistedToolEvents: ToolEvent[] = events
        .filter(e => e.type === 'tool_call' || e.type === 'tool_result')
        .map(e => (e.type === 'tool_call'
          ? { kind: 'call', name: e.name, args: e.args }
          : { kind: 'result', name: e.name, result: e.result }
        )) as ToolEvent[]
      setMessages(prev => [...prev, { role: 'assistant', content: output, toolEvents: persistedToolEvents }])
      clearOutput()
    }
  }, [lastEventType, output, clearOutput])

  const onSend = useCallback(() => {
    if (!input.trim()) return
    const msg = input
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setInput("")
    start(msg)
  }, [input, start])

  // Tool events are persisted per-assistant message; avoid rendering live duplicates below.

  function parseBochaResults(raw: string | undefined | null): { title: string; url: string }[] {
    if (!raw) return []
    try {
      const data = JSON.parse(raw)
      const list = Array.isArray(data) ? data : (Array.isArray((data as any)?.webPages?.value) ? (data as any).webPages.value : [])
      const mapped = list.map((item: any) => {
        const title = item?.name || item?.title || item?.headline || 'Untitled'
        const url = item?.url || item?.link || item?.sourceUrl || '#'
        return { title, url }
      }).filter((x: any) => typeof x.url === 'string' && x.url)
      return mapped
    } catch {
      return []
    }
  }

  function BochaResultsList({ raw }: { raw: string }) {
    const items = parseBochaResults(raw)
    if (!items.length) return <div className="text-xs text-gray-500">No web results.</div>
    return (
      <ul className="list-disc pl-5 space-y-1 text-xs">
        {items.map((it, idx) => (
          <li key={idx}>
            <a href={it.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:text-blue-700">{it.title}</a>
          </li>
        ))}
      </ul>
    )
  }

  return (
    <div className="min-h-full bg-gray-50">
      <div className="mx-auto max-w-3xl p-4 space-y-4">
        <h1 className="text-xl font-semibold">LLM Tools Demo</h1>
        <Card>
          <CardHeader className="pb-2 flex flex-row items-center justify-between space-y-0">
            <div>Chat</div>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Clear chat"
              title="Clear chat"
              onClick={() => {
                reset()
                setMessages([])
              }}
            >
              <Trash2 className="h-5 w-5" />
            </Button>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[50vh] w-full overflow-auto border rounded-md bg-white">
              <div className="p-4 space-y-4">
                {messages.map((m, i) => (
                  <div key={i} className="space-y-1">
                    <div className="text-xs text-gray-500">{m.role === 'user' ? 'You' : 'Assistant'}</div>
                    {m.toolEvents && m.toolEvents.length > 0 && (
                      <div className="space-y-1">
                        {m.toolEvents.map((te, j) => (
                          te.kind === 'call' ? (
                            <div key={`m${i}-tc-${j}`} className="text-xs text-blue-600">
                              Tool call: {te.name} {JSON.stringify(te.args)}
                            </div>
                          ) : te.name === 'bocha_search' && te.result ? (
                            <div key={`m${i}-tr-${j}`} className="text-xs">
                              <div className="text-green-700">Tool result: {te.name}</div>
                              <BochaResultsList raw={te.result} />
                            </div>
                          ) : (
                            <div key={`m${i}-tr-${j}`} className="text-xs text-green-700">
                              Tool result: {te.name} {te.result?.slice(0, 200)}
                            </div>
                          )
                        ))}
                      </div>
                    )}
                    <Markdown>{m.content}</Markdown>
                  </div>
                ))}


                {output && (
                  <div className="space-y-1">
                    <div className="text-xs text-gray-500">Assistant</div>
                    <Markdown>{output}</Markdown>
                  </div>
                )}

                {loading && (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-700" />
                    <span>Waiting for server…</span>
                  </div>
                )}

                <div ref={endRef} />
              </div>
            </ScrollArea>

            <div className="mt-3 flex gap-2">
              <Input
                placeholder="Ask something..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) onSend() }}
              />
              <Button onClick={onSend}>Send</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
