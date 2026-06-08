import { useState, useRef, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Send, Sparkles, MessageSquare, Terminal, ArrowRight, CornerDownLeft,
  Shield, AlertTriangle, TrendingUp, Compass, Copy, Check, RefreshCw,
  Trash2, Database, Bot, User, Zap
} from 'lucide-react'
import api from '../../services/api'

/* ─── Types ─────────────────────────────────────────────────── */
interface Reference { type: string; label: string }

interface Message {
  id: string
  sender: 'user' | 'assistant'
  text: string
  references?: Reference[]
  intent?: string
  timestamp: Date
}

/* ─── Constants ─────────────────────────────────────────────── */
const SUGGESTIONS = [
  { question: 'Which customers are most likely to churn this month?', icon: AlertTriangle, color: '#EF4444' },
  { question: 'Show me campaign performance and ROI breakdown.', icon: TrendingUp, color: '#8B5CF6' },
  { question: 'What is our current revenue at risk?', icon: TrendingUp, color: '#10B981' },
  { question: 'How can I improve customer trust scores?', icon: Shield, color: '#3B82F6' },
  { question: 'Which products are our top sellers?', icon: Zap, color: '#F59E0B' },
  { question: 'Show me the emotion distribution across customers.', icon: Sparkles, color: '#EC4899' },
]

const ROUTE_MAP: Record<string, string> = {
  churn_center: '/admin/churn',
  campaign_center: '/admin/campaigns',
  roi_center: '/admin/roi',
  trust_center: '/admin/trust',
  emotion_center: '/admin/emotions',
  fairness_center: '/admin/fairness',
  nba_center: '/admin/nba',
  customer_360: '/admin/customer360',
  observability: '/admin/observability',
  products: '/admin/products',
  overview: '/admin',
}

/* ─── Copy Button Component ─────────────────────────────────── */
function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  const handleCopy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button
      onClick={handleCopy}
      className="p-1 rounded hover:bg-white/10 transition-colors"
      title="Copy response"
    >
      {copied
        ? <Check size={12} style={{ color: '#10B981' }} />
        : <Copy size={12} style={{ color: '#64748B' }} />}
    </button>
  )
}

/* ─── Markdown Components for Rendering ─────────────────────── */
const mdComponents = {
  table: (props: any) => (
    <div className="overflow-x-auto my-3 rounded-lg" style={{ border: '1px solid #2A2D3A' }}>
      <table className="w-full text-xs" {...props} />
    </div>
  ),
  thead: (props: any) => <thead style={{ background: '#1E293B' }} {...props} />,
  th: (props: any) => (
    <th className="text-left px-3 py-2 text-[11px] font-semibold" style={{ color: '#94A3B8', borderBottom: '1px solid #2A2D3A' }} {...props} />
  ),
  td: (props: any) => (
    <td className="px-3 py-1.5 text-[11px] mono" style={{ color: '#CBD5E1', borderBottom: '1px solid #1E293B' }} {...props} />
  ),
  tr: (props: any) => <tr className="hover:bg-white/[0.02] transition-colors" {...props} />,
  p: (props: any) => <p className="mb-2 last:mb-0" {...props} />,
  ul: (props: any) => <ul className="list-disc list-inside mb-2 space-y-0.5" {...props} />,
  ol: (props: any) => <ol className="list-decimal list-inside mb-2 space-y-0.5" {...props} />,
  li: (props: any) => <li className="text-sm" {...props} />,
  strong: (props: any) => <strong className="font-semibold" style={{ color: '#E2E8F0' }} {...props} />,
  h1: (props: any) => <h1 className="text-base font-bold text-white mb-2 mt-3" {...props} />,
  h2: (props: any) => <h2 className="text-sm font-bold text-white mb-1.5 mt-2" {...props} />,
  h3: (props: any) => <h3 className="text-xs font-bold mb-1 mt-2" style={{ color: '#CBD5E1' }} {...props} />,
  code: ({ inline, children, ...props }: any) =>
    inline
      ? <code className="px-1 py-0.5 rounded text-[11px] mono" style={{ background: '#1E293B', color: '#7DD3FC' }} {...props}>{children}</code>
      : <pre className="p-3 rounded-lg my-2 overflow-x-auto text-[11px] mono" style={{ background: '#0F172A', border: '1px solid #1E293B', color: '#94A3B8' }}><code {...props}>{children}</code></pre>,
  blockquote: (props: any) => (
    <blockquote className="border-l-2 pl-3 my-2 italic" style={{ borderColor: '#8B5CF6', color: '#94A3B8' }} {...props} />
  ),
}

/* ─── Intent Badge ──────────────────────────────────────────── */
function IntentBadge({ intent }: { intent?: string }) {
  if (!intent) return null
  const colors: Record<string, string> = {
    churn: '#EF4444', revenue: '#10B981', campaign: '#8B5CF6',
    customer_lookup: '#3B82F6', trust: '#F59E0B', emotion: '#EC4899',
    product: '#06B6D4', fairness: '#8B5CF6', nba: '#F97316',
    cart: '#F59E0B', session: '#10B981', general: '#64748B',
  }
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-medium"
      style={{ background: `${colors[intent] || '#64748B'}15`, color: colors[intent] || '#64748B', border: `1px solid ${colors[intent] || '#64748B'}30` }}>
      <Database size={8} /> {intent.replace('_', ' ')}
    </span>
  )
}

/* ═══ MAIN COMPONENT ════════════════════════════════════════════ */
export default function MarketerCopilot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I'm your **OmniPulse AI Copilot** — connected live to your customer database.\n\nI can analyze churn risks, revenue trends, campaign performance, customer profiles, and more. All my answers are grounded in your real platform data.\n\n**Try asking me:**\n- \"Which customers are likely to churn?\"\n- \"Show me revenue at risk\"\n- \"Tell me about CUST-001000\"",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [conversationId, setConversationId] = useState<string>(() => crypto.randomUUID())
  const chatEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /* ── Send Message (SSE Streaming) ─────────────────────────── */
  const handleSend = useCallback(async (questionText: string) => {
    if (!questionText.trim() || isStreaming) return

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: questionText,
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsStreaming(true)

    // Create placeholder for assistant response
    const assistantId = (Date.now() + 1).toString()
    const placeholder: Message = {
      id: assistantId,
      sender: 'assistant',
      text: '',
      timestamp: new Date(),
    }
    setMessages(prev => [...prev, placeholder])

    try {
      const response = await fetch('/api/copilot/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: questionText, conversation_id: conversationId }),
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullText = ''
      let refs: Reference[] = []
      let intent: string | undefined

      if (!reader) throw new Error('No reader available')

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const jsonStr = line.slice(6).trim()
          if (!jsonStr) continue

          try {
            const event = JSON.parse(jsonStr)

            if (event.type === 'intent') {
              intent = event.intent
            } else if (event.type === 'chunk') {
              fullText += event.content
              setMessages(prev =>
                prev.map(m =>
                  m.id === assistantId
                    ? { ...m, text: fullText, intent }
                    : m
                )
              )
            } else if (event.type === 'done') {
              refs = event.references || []
              if (event.conversation_id) {
                setConversationId(event.conversation_id)
              }
            }
          } catch {
            // skip malformed JSON
          }
        }
      }

      // Final update with references
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId
            ? { ...m, text: fullText || 'No response received.', references: refs, intent }
            : m
        )
      )
    } catch (err) {
      // Fallback to non-streaming
      try {
        const res = await api.post('/copilot/chat', { message: questionText, conversation_id: conversationId })
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId
              ? {
                ...m,
                text: res.data.answer || 'Sorry, something went wrong.',
                references: res.data.references,
                intent: res.data.intent,
              }
              : m
          )
        )
        if (res.data.conversation_id) setConversationId(res.data.conversation_id)
      } catch {
        setMessages(prev =>
          prev.map(m =>
            m.id === assistantId
              ? { ...m, text: 'Sorry, I had trouble connecting to the AI service. Please check that the backend is running and the Gemini API key is configured.' }
              : m
          )
        )
      }
    } finally {
      setIsStreaming(false)
      inputRef.current?.focus()
    }
  }, [isStreaming, conversationId])

  /* ── Regenerate Last Response ─────────────────────────────── */
  const handleRegenerate = () => {
    const lastUser = [...messages].reverse().find(m => m.sender === 'user')
    if (!lastUser) return
    // Remove last assistant message
    setMessages(prev => {
      const idx = prev.findLastIndex(m => m.sender === 'assistant')
      return idx > 0 ? prev.slice(0, idx) : prev
    })
    handleSend(lastUser.text)
  }

  /* ── Clear Chat ───────────────────────────────────────────── */
  const handleClearChat = async () => {
    try {
      await api.delete(`/copilot/conversations/${conversationId}`)
    } catch { /* ignore */ }
    const newId = crypto.randomUUID()
    setConversationId(newId)
    setMessages([
      {
        id: 'welcome',
        sender: 'assistant',
        text: "Chat cleared. I'm ready for new questions — ask me anything about your customers, campaigns, or revenue.",
        timestamp: new Date(),
      },
    ])
  }

  /* ── Navigate to Reference ────────────────────────────────── */
  const navigateToReference = (refType: string) => {
    const path = ROUTE_MAP[refType] || '/admin'
    navigate(path)
  }

  return (
    <div className="flex gap-5 h-[calc(100vh-140px)]">
      {/* ─── Sidebar ─────────────────────────────────────────── */}
      <div className="w-80 flex-shrink-0 flex flex-col gap-4">
        <div className="card p-5 flex flex-col justify-between flex-1">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Compass className="text-purple-400" size={18} />
              <h2 className="text-sm font-semibold text-white uppercase tracking-wider">Suggested Queries</h2>
            </div>
            <p className="text-xs mb-5 leading-relaxed" style={{ color: '#64748B' }}>
              Ask any question about your platform. The AI queries your live database and responds with real data.
            </p>
            <div className="space-y-2.5">
              {SUGGESTIONS.map((s, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(s.question)}
                  disabled={isStreaming}
                  className="w-full text-left p-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 hover:border-purple-500/30 transition-all flex gap-3 items-start group disabled:opacity-50"
                >
                  <s.icon size={15} style={{ color: s.color }} className="mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-xs font-medium text-slate-300 group-hover:text-white transition-colors">{s.question}</p>
                  </div>
                  <ArrowRight size={12} className="opacity-0 group-hover:opacity-100 transition-opacity mt-0.5 text-purple-400" />
                </button>
              ))}
            </div>
          </div>

          <div className="pt-4 border-t border-white/5 space-y-2">
            <button
              onClick={handleClearChat}
              disabled={isStreaming}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs hover:bg-white/5 transition-colors disabled:opacity-50"
              style={{ color: '#64748B' }}
            >
              <Trash2 size={12} /> Clear Chat
            </button>
            <div className="flex items-center gap-2 text-xs" style={{ color: '#475569' }}>
              <Terminal size={12} />
              <span>Powered by Gemini 2.5 Flash</span>
            </div>
          </div>
        </div>
      </div>

      {/* ─── Main Chat ───────────────────────────────────────── */}
      <div className="flex-1 card flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 flex items-center justify-between" style={{ borderBottom: '1px solid #2A2D3A' }}>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #8B5CF620, #6366F120)', border: '1px solid #8B5CF630' }}>
              <Sparkles size={17} className="text-purple-400" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">Marketer Agent Copilot</h2>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-[10px]" style={{ color: '#10B981' }}>Live — Connected to Database</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {messages.length > 2 && (
              <button
                onClick={handleRegenerate}
                disabled={isStreaming}
                className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] hover:bg-white/5 transition-colors disabled:opacity-50"
                style={{ color: '#64748B', border: '1px solid #2A2D3A' }}
              >
                <RefreshCw size={11} /> Regenerate
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          <AnimatePresence initial={false}>
            {messages.map((m) => (
              <motion.div
                key={m.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className={`flex gap-3 ${m.sender === 'user' ? 'flex-row-reverse' : ''}`}
              >
                {/* Avatar */}
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${m.sender === 'user'
                  ? 'bg-blue-600/20 border border-blue-500/30'
                  : 'border border-purple-500/30'
                  }`}
                  style={m.sender === 'assistant' ? { background: 'linear-gradient(135deg, #8B5CF615, #6366F115)' } : undefined}
                >
                  {m.sender === 'user'
                    ? <User size={14} className="text-blue-400" />
                    : <Bot size={14} className="text-purple-400" />}
                </div>

                {/* Bubble */}
                <div className={`max-w-[80%] space-y-2 ${m.sender === 'user' ? 'items-end' : ''}`}>
                  {/* Intent badge for assistant */}
                  {m.sender === 'assistant' && m.intent && (
                    <div className="flex items-center gap-2">
                      <IntentBadge intent={m.intent} />
                    </div>
                  )}

                  <div className={`p-4 rounded-xl text-sm leading-relaxed ${m.sender === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm'
                    : 'rounded-tl-sm'
                    }`}
                    style={m.sender === 'assistant'
                      ? { background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)', color: '#CBD5E1' }
                      : undefined}
                  >
                    {m.sender === 'user' ? (
                      <span>{m.text}</span>
                    ) : (
                      <div className="prose-sm">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                          {m.text || ''}
                        </ReactMarkdown>
                        {/* Blinking cursor while streaming */}
                        {isStreaming && m.id === messages[messages.length - 1]?.id && m.sender === 'assistant' && (
                          <span className="inline-block w-2 h-4 ml-0.5 animate-pulse rounded-sm" style={{ background: '#8B5CF6' }} />
                        )}
                      </div>
                    )}
                  </div>

                  {/* Copy button for assistant messages */}
                  {m.sender === 'assistant' && m.text && m.id !== 'welcome' && !isStreaming && (
                    <div className="flex items-center gap-1 pl-1">
                      <CopyButton text={m.text} />
                    </div>
                  )}

                  {/* Reference quick-links */}
                  {m.references && m.references.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {m.references.map((ref, rIdx) => (
                        <button
                          key={rIdx}
                          onClick={() => navigateToReference(ref.type)}
                          className="px-3 py-1.5 rounded-full text-[11px] font-semibold transition-colors flex items-center gap-1.5"
                          style={{ background: '#8B5CF610', border: '1px solid #8B5CF625', color: '#A78BFA' }}
                        >
                          <Compass size={10} />
                          {ref.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Streaming indicator */}
          {isStreaming && messages[messages.length - 1]?.text === '' && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 border border-purple-500/30"
                style={{ background: 'linear-gradient(135deg, #8B5CF615, #6366F115)' }}>
                <Bot size={14} className="text-purple-400" />
              </div>
              <div className="p-4 rounded-xl rounded-tl-sm flex items-center gap-2"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                <Database size={12} className="text-purple-400 animate-pulse" />
                <span className="text-xs" style={{ color: '#94A3B8' }}>Querying database & analyzing...</span>
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4" style={{ background: 'rgba(255,255,255,0.01)', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend(input)
            }}
            className="flex gap-2"
          >
            <div className="relative flex-1">
              <input
                ref={inputRef}
                type="text"
                placeholder="Ask your customer intelligence assistant..."
                className="input pr-14 text-sm h-12"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isStreaming}
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[9px] bg-white/5 border border-white/10 px-1.5 py-0.5 rounded text-slate-500 flex items-center gap-1 select-none">
                Enter <CornerDownLeft size={8} />
              </span>
            </div>
            <button
              type="submit"
              disabled={isStreaming || !input.trim()}
              className="btn btn-primary h-12 px-6 flex items-center justify-center gap-2 disabled:opacity-50 transition-opacity"
            >
              <Send size={15} />
              <span>{isStreaming ? 'Thinking...' : 'Send'}</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
