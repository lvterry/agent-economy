import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Button } from './components/ui/button'
import { Input } from './components/ui/input'
import { Card, CardHeader, CardContent } from './components/ui/card'
import { ScrollArea } from './components/ui/scroll-area'

type EventItem =
  | { type: 'start' }
  | { type: 'tool_call'; name: string; args: any }
  | { type: 'tool_result'; name: string; result: string }
  | { type: 'content_delta'; text: string }
  | { type: 'done' }

type ChatMessage = { role: 'user' | 'assistant' | 'tool'; content: string }

function useChatStream() {
  const [events, setEvents] = useState<EventItem[]>([])
  const [output, setOutput] = useState('')
  const controllerRef = useRef<AbortController | null>(null)

  const start = useCallback(async (message: string) => {
    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller
    setEvents([])
    setOutput('')

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
          if (evt.type === 'content_delta') setOutput(prev => prev + (evt.text || ''))
        } catch {
          // ignore parse errors
        }
      }
    }
  }, [])

  const stop = useCallback(() => {
    controllerRef.current?.abort()
  }, [])

  return { events, output, start, stop }
}

export default function App() {
  const [input, setInput] = useState('How\'s the weather in Hangzhou?')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const { events, output, start } = useChatStream()
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, output, events])

  const onSend = useCallback(() => {
    if (!input.trim()) return
    setMessages(prev => [...prev, { role: 'user', content: input }])
    start(input)
  }, [input, start])

  const toolEvents = useMemo(() => events.filter(e => e.type === 'tool_call' || e.type === 'tool_result'), [events])

  return (
    <div className="min-h-full bg-gray-50">
      <div className="mx-auto max-w-3xl p-4 space-y-4">
        <h1 className="text-xl font-semibold">LLM Tools Demo</h1>
        <Card>
          <CardHeader className="pb-2">Chat</CardHeader>
          <CardContent>
            <ScrollArea className="h-[50vh] w-full overflow-auto border rounded-md bg-white">
              <div className="p-4 space-y-4">
                {messages.map((m, i) => (
                  <div key={i} className="space-y-1">
                    <div className="text-xs text-gray-500">{m.role === 'user' ? 'You' : 'Assistant'}</div>
                    <div className="whitespace-pre-wrap">{m.content}</div>
                  </div>
                ))}

                {toolEvents.map((e, i) => (
                  e.type === 'tool_call' ? (
                    <div key={`tc-${i}`} className="text-xs text-blue-600">
                      Tool call: {e.name} {JSON.stringify(e.args)}
                    </div>
                  ) : (
                    <div key={`tr-${i}`} className="text-xs text-green-700">
                      Tool result: {e.name} {e.result?.slice(0, 200)}
                    </div>
                  )
                ))}

                {output && (
                  <div className="space-y-1">
                    <div className="text-xs text-gray-500">Assistant</div>
                    <div className="whitespace-pre-wrap">{output}</div>
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

