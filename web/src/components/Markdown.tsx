import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type Props = {
  children: string
  className?: string
}

export default function Markdown({ children, className }: Props) {
  return (
    <div className={className ?? ''}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ node, ...props }) => (
            <a {...props} target="_blank" rel="noreferrer" className="text-blue-600 underline" />
          ),
          code: ({ inline, className, children, ...props }) => (
            <code className={`bg-gray-100 rounded px-1 ${className ?? ''}`}{...props}>
              {children}
            </code>
          ),
          pre: ({ node, ...props }) => (
            <pre {...props} className="bg-gray-100 p-3 rounded overflow-x-auto" />
          ),
          ul: ({ node, ...props }) => <ul className="list-disc pl-5" {...props} />,
          ol: ({ node, ...props }) => <ol className="list-decimal pl-5" {...props} />,
        }}
        className="prose prose-sm max-w-none"
      >
        {children}
      </ReactMarkdown>
    </div>
  )
}

