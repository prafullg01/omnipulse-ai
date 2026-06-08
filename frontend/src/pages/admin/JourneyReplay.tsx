import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Play, Pause, RotateCcw, FastForward, SkipForward, SkipBack, Search, User, Compass, HelpCircle, Activity, ShoppingBag, MessageSquare, AlertTriangle, Calendar, Star } from 'lucide-react'
import api from '../../services/api'

interface JourneyEvent {
  event_type: string
  event_value: string
  timestamp: string
}

export default function JourneyReplay() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [speed, setSpeed] = useState<1 | 2 | 5>(1)
  const [eventFilter, setEventFilter] = useState<string | null>(null)
  const timerRef = useRef<any>(null)

  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: () => api.get('/customers').then(r => r.data),
  })

  const { data: journey, isLoading: isProfileLoading } = useQuery({
    queryKey: ['customerJourney', selectedId],
    queryFn: () => api.get(`/analytics/journey/${selectedId}`).then(r => r.data),
    enabled: !!selectedId,
  })

  // Journey timeline already sorted by timestamp in backend
  const allEvents: JourneyEvent[] = journey?.timeline || []
  
  // Apply filter
  const sortedEvents = eventFilter 
    ? allEvents.filter(e => e.event_type.toLowerCase().includes(eventFilter.toLowerCase()))
    : allEvents

  const filteredCustomers = (customers || []).filter((c: any) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  )

  useEffect(() => {
    // Reset state on customer change
    setIsPlaying(false)
    setCurrentIndex(0)
  }, [selectedId])

  useEffect(() => {
    if (isPlaying) {
      const intervalDuration = 2000 / speed // Base 2 seconds per event
      timerRef.current = setInterval(() => {
        setCurrentIndex(prev => {
          if (prev >= sortedEvents.length - 1) {
            setIsPlaying(false)
            return prev
          }
          return prev + 1
        })
      }, intervalDuration)
    } else {
      if (timerRef.current) clearInterval(timerRef.current)
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isPlaying, speed, sortedEvents.length])

  const getEventIcon = (type: string) => {
    const t = type.toLowerCase()
    if (t.includes('purchase') || t.includes('checkout') || t.includes('order')) return ShoppingBag
    if (t.includes('support') || t.includes('ticket') || t.includes('complain')) return AlertTriangle
    if (t.includes('message') || t.includes('email') || t.includes('sms') || t.includes('campaign')) return MessageSquare
    if (t.includes('login') || t.includes('visit') || t.includes('view')) return Activity
    return Compass
  }

  const getEventColor = (type: string) => {
    const t = type.toLowerCase()
    if (t.includes('purchase') || t.includes('checkout') || t.includes('order')) return '#10B981' // Green
    if (t.includes('support') || t.includes('ticket') || t.includes('complain')) return '#EF4444' // Red
    if (t.includes('message') || t.includes('email') || t.includes('sms') || t.includes('campaign')) return '#8B5CF6' // Purple
    return '#3B82F6' // Blue
  }

  const handleNext = () => {
    if (currentIndex < sortedEvents.length - 1) {
      setCurrentIndex(prev => prev + 1)
    }
  }

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1)
    }
  }

  const handleReset = () => {
    setIsPlaying(false)
    setCurrentIndex(0)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">Customer Journey Replay</h1>
        <p className="text-sm" style={{ color: '#64748B' }}>
          Replay chronological touchpoints, purchase decisions, and campaign actions step-by-step
        </p>
      </div>

      <div className="flex gap-5 h-[calc(100vh-200px)]">
        {/* Customer Selector Sidebar */}
        <div className="w-80 flex-shrink-0 card flex flex-col">
          <div className="p-4" style={{ borderBottom: '1px solid #2A2D3A' }}>
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#64748B' }} />
              <input
                className="input pl-9 text-sm"
                placeholder="Search customers..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {filteredCustomers.map((c: any) => (
              <div
                key={c.customer_id}
                onClick={() => setSelectedId(c.customer_id)}
                className="flex items-center gap-3 px-4 py-3 cursor-pointer border-b border-white/5 transition-all hover:bg-white/[0.02]"
                style={{
                  background: selectedId === c.customer_id ? 'rgba(139,92,246,0.08)' : 'transparent',
                }}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                  style={{ background: `hsl(${(c.name.charCodeAt(0) * 11) % 360}, 60%, 55%)` }}
                >
                  {c.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-white truncate">{c.name}</p>
                  <p className="text-[10px]" style={{ color: '#64748B' }}>{c.persona} · {c.city}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Journey Player Panel */}
        <div className="flex-1 card flex flex-col overflow-hidden">
          {isProfileLoading ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : journey ? (
            <>
              {/* Player Controls Bar */}
              <div className="px-6 py-4 flex flex-col gap-4" style={{ borderBottom: '1px solid #2A2D3A' }}>
                {/* Customer Summary Panel */}
                {journey?.customer_summary && (
                  <div className="grid grid-cols-5 gap-3 p-4 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid #2A2D3A' }}>
                    <div>
                      <p className="text-[10px] mb-0.5" style={{ color: '#64748B' }}>CUSTOMER</p>
                      <p className="text-xs font-bold text-white">{journey.customer_summary.customer_name}</p>
                      <p className="text-[10px]" style={{ color: '#64748B' }}>{journey.customer_summary.persona} · {journey.customer_summary.city}</p>
                    </div>
                    <div>
                      <p className="text-[10px] mb-0.5" style={{ color: '#64748B' }}>RISK</p>
                      <p className="text-lg font-bold mono" style={{ color: journey.customer_summary.current_risk > 0.7 ? '#EF4444' : journey.customer_summary.current_risk > 0.5 ? '#F59E0B' : '#10B981' }}>
                        {(journey.customer_summary.current_risk * 100).toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] mb-0.5" style={{ color: '#64748B' }}>TRUST / ENGAGEMENT</p>
                      <p className="text-sm font-bold text-white mono">{journey.customer_summary.trust_score.toFixed(0)} / {journey.customer_summary.engagement_score.toFixed(0)}</p>
                    </div>
                    <div>
                      <p className="text-[10px] mb-0.5" style={{ color: '#64748B' }}>CLV</p>
                      <p className="text-sm font-bold text-white mono">₹{journey.customer_summary.clv.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-[10px] mb-0.5" style={{ color: '#64748B' }}>ACTIVITY</p>
                      <p className="text-xs text-white">{journey.customer_summary.total_orders} orders · {journey.customer_summary.total_complaints} complaints · {journey.customer_summary.total_refunds} refunds</p>
                    </div>
                  </div>
                )}
                
                {/* Replay Analytics */}
                {journey?.replay_analytics && (
                  <div className="grid grid-cols-6 gap-3">
                    {[
                      { label: 'Total Events', value: journey.replay_analytics.total_events, color: '#3B82F6' },
                      { label: 'Journey Days', value: journey.replay_analytics.journey_duration_days, color: '#8B5CF6' },
                      { label: 'Conversion %', value: `${journey.replay_analytics.conversion_rate.toFixed(1)}%`, color: '#10B981' },
                      { label: 'Retention %', value: `${journey.replay_analytics.retention_probability.toFixed(0)}%`, color: '#F59E0B' },
                      { label: 'Purchases', value: journey.replay_analytics.total_purchases, color: '#10B981' },
                      { label: 'Engagement', value: journey.replay_analytics.average_engagement.toFixed(0), color: '#3B82F6' },
                    ].map((metric, i) => (
                      <div key={i} className="p-2 rounded-lg text-center" style={{ background: `${metric.color}08`, border: `1px solid ${metric.color}15` }}>
                        <p className="text-[10px] mb-0.5" style={{ color: metric.color }}>{metric.label}</p>
                        <p className="text-sm font-bold text-white mono">{metric.value}</p>
                      </div>
                    ))}
                  </div>
                )}
                
                {/* Control Bar */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-purple-500/10 border border-purple-500/20">
                      <User size={18} className="text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-white">
                        Journey Replay
                      </h3>
                      <p className="text-[10px]" style={{ color: '#64748B' }}>
                        Step {sortedEvents.length > 0 ? currentIndex + 1 : 0} of {sortedEvents.length}
                      </p>
                    </div>
                  </div>

                  {/* Main Playback HUD */}
                  {sortedEvents.length > 0 && (
                    <div className="flex items-center gap-2 bg-white/5 border border-white/5 px-3 py-1.5 rounded-full">
                      <button
                        onClick={handleReset}
                        className="p-1.5 hover:bg-white/10 rounded-full text-slate-400 hover:text-white transition-colors"
                        title="Reset Player"
                      >
                        <RotateCcw size={14} />
                      </button>
                      <button
                        onClick={handlePrev}
                        disabled={currentIndex === 0}
                        className="p-1.5 hover:bg-white/10 rounded-full text-slate-400 hover:text-white disabled:opacity-30 transition-colors"
                      >
                        <SkipBack size={14} />
                      </button>
                      <button
                        onClick={() => setIsPlaying(!isPlaying)}
                        className="w-8 h-8 rounded-full bg-purple-600 hover:bg-purple-500 text-white flex items-center justify-center transition-colors"
                      >
                        {isPlaying ? <Pause size={14} fill="white" /> : <Play size={14} fill="white" className="ml-0.5" />}
                      </button>
                      <button
                        onClick={handleNext}
                        disabled={currentIndex === sortedEvents.length - 1}
                        className="p-1.5 hover:bg-white/10 rounded-full text-slate-400 hover:text-white disabled:opacity-30 transition-colors"
                      >
                        <SkipForward size={14} />
                      </button>

                      <div className="h-4 w-px bg-white/10 mx-1" />

                      <div className="flex items-center gap-1">
                        {([1, 2, 5] as const).map(s => (
                          <button
                            key={s}
                            onClick={() => setSpeed(s)}
                            className={`text-[9px] font-bold px-1.5 py-0.5 rounded transition-colors ${
                              speed === s ? 'bg-purple-600 text-white' : 'text-slate-400 hover:bg-white/5'
                            }`}
                          >
                            {s}x
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Event Filter */}
                  <div className="flex items-center gap-1">
                    {['purchase', 'complaint', 'refund', 'review', 'campaign'].map(filter => (
                      <button
                        key={filter}
                        onClick={() => setEventFilter(eventFilter === filter ? null : filter)}
                        className={`text-[10px] px-2 py-1 rounded transition-colors ${
                          eventFilter === filter ? 'bg-purple-600 text-white' : 'bg-white/5 text-slate-400 hover:bg-white/10'
                        }`}
                      >
                        {filter}
                      </button>
                    ))}
                    {eventFilter && (
                      <button
                        onClick={() => setEventFilter(null)}
                        className="text-[10px] px-2 py-1 rounded bg-red-600/20 text-red-400 hover:bg-red-600/30"
                      >
                        Clear
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* Main Timeline Viewport */}
              <div className="flex-1 flex overflow-hidden">
                {sortedEvents.length === 0 ? (
                  <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
                    <Activity size={48} className="text-slate-700 mb-2" />
                    <p className="text-sm" style={{ color: '#64748B' }}>No customer lifecycle events logged for replay.</p>
                  </div>
                ) : (
                  <>
                    {/* Left Scrollable Visual Flow */}
                    <div className="flex-1 overflow-y-auto p-6 space-y-6 relative">
                      {/* Timeline Line */}
                      <div className="absolute left-[38px] top-6 bottom-6 w-0.5 bg-slate-800 pointer-events-none" />

                      {sortedEvents.map((evt, idx) => {
                        const Icon = getEventIcon(evt.event_type)
                        const color = getEventColor(evt.event_type)
                        const isPast = idx <= currentIndex
                        const isActive = idx === currentIndex

                        return (
                          <motion.div
                            key={idx}
                            className={`flex gap-5 relative transition-opacity duration-300 ${
                              isPast ? 'opacity-100' : 'opacity-20'
                            }`}
                            onClick={() => setCurrentIndex(idx)}
                          >
                            {/* Step Indicator Dot */}
                            <div className="relative z-10 flex-shrink-0 flex items-center justify-center">
                              <motion.div
                                className="w-10 h-10 rounded-full flex items-center justify-center border cursor-pointer transition-all"
                                style={{
                                  background: isActive ? color : isPast ? `${color}15` : '#1A1C24',
                                  borderColor: isActive ? color : isPast ? `${color}40` : '#2A2D3A',
                                }}
                                animate={isActive ? { scale: [1, 1.15, 1] } : {}}
                                transition={{ repeat: Infinity, duration: 2 }}
                              >
                                <Icon size={16} style={{ color: isActive ? '#FFFFFF' : color }} />
                              </motion.div>
                            </div>

                            {/* Event Details Card */}
                            <div
                              className={`flex-1 p-4 rounded-xl border transition-all duration-300 cursor-pointer ${
                                isActive
                                  ? 'bg-white/5 border-purple-500/30 shadow-lg'
                                  : 'bg-transparent border-transparent hover:border-white/5 hover:bg-white/[0.01]'
                              }`}
                            >
                              <div className="flex items-center justify-between mb-1">
                                <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                                  {evt.event_type.replace(/_/g, ' ')}
                                </h4>
                                <span className="text-[10px] text-slate-500 font-mono">
                                  {new Date(evt.timestamp).toLocaleString()}
                                </span>
                              </div>
                              <p className="text-xs font-semibold text-slate-400 mt-1">
                                {evt.event_value || 'Touchpoint registered'}
                              </p>
                            </div>
                          </motion.div>
                        )
                      })}
                    </div>

                    {/* Right Interactive Drawer (Metadata HUD) */}
                    <div className="w-80 flex-shrink-0 border-l border-slate-800 bg-white/[0.01] p-6 space-y-6 overflow-y-auto">
                      <h4 className="text-xs font-semibold text-white uppercase tracking-wider">Touchpoint Telemetry</h4>

                      {/* Active Event Metrics */}
                      <div className="card p-4 space-y-4">
                        <div>
                          <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Selected Event</p>
                          <p className="text-xs font-bold text-purple-400 uppercase">
                            {sortedEvents[currentIndex]?.event_type.replace(/_/g, ' ') || 'None'}
                          </p>
                        </div>

                        <div>
                          <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Payload</p>
                          <p className="text-xs text-slate-200 break-words leading-relaxed font-mono">
                            {sortedEvents[currentIndex]?.event_value || 'None'}
                          </p>
                        </div>

                        <div>
                          <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-0.5">Captured At</p>
                          <p className="text-xs text-slate-200">
                            {sortedEvents[currentIndex] ? new Date(sortedEvents[currentIndex].timestamp).toLocaleString() : 'None'}
                          </p>
                        </div>
                      </div>

                      {/* Business Impact - DYNAMIC */}
                      {sortedEvents[currentIndex]?.business_impact && (
                        <div>
                          <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Business Impact</h4>
                          <div className="space-y-2">
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-slate-500">Churn Risk Impact</span>
                              <span className={`font-semibold ${sortedEvents[currentIndex].business_impact.churn_impact < 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                {sortedEvents[currentIndex].business_impact.churn_impact > 0 ? '+' : ''}{sortedEvents[currentIndex].business_impact.churn_impact}%
                              </span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-slate-500">Predicted CLV Lift</span>
                              <span className={`font-semibold ${sortedEvents[currentIndex].business_impact.clv_lift > 0 ? 'text-purple-400' : 'text-red-400'}`}>
                                {sortedEvents[currentIndex].business_impact.clv_lift > 0 ? '+' : ''}₹{sortedEvents[currentIndex].business_impact.clv_lift.toLocaleString()}
                              </span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-slate-500">Customer NPS Lift</span>
                              <span className={`font-semibold ${sortedEvents[currentIndex].business_impact.nps_lift > 0 ? 'text-blue-400' : 'text-red-400'}`}>
                                {sortedEvents[currentIndex].business_impact.nps_lift > 0 ? '+' : ''}{sortedEvents[currentIndex].business_impact.nps_lift} pts
                              </span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-slate-500">Trust Impact</span>
                              <span className={`font-semibold ${sortedEvents[currentIndex].business_impact.trust_impact > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                {sortedEvents[currentIndex].business_impact.trust_impact > 0 ? '+' : ''}{sortedEvents[currentIndex].business_impact.trust_impact}
                              </span>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-slate-500">Engagement Impact</span>
                              <span className={`font-semibold ${sortedEvents[currentIndex].business_impact.engagement_impact > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                {sortedEvents[currentIndex].business_impact.engagement_impact > 0 ? '+' : ''}{sortedEvents[currentIndex].business_impact.engagement_impact}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* NBA Triggered */}
                      {sortedEvents[currentIndex]?.nba_triggered && (
                        <div className="p-4 rounded-lg" style={{ background: 'rgba(139,92,246,0.05)', border: '1px solid rgba(139,92,246,0.2)' }}>
                          <h4 className="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2">NBA Triggered</h4>
                          <div className="space-y-2 text-xs">
                            <div>
                              <span className="text-slate-500">Action: </span>
                              <span className="text-white font-semibold">{sortedEvents[currentIndex].nba_triggered.action.replace(/_/g, ' ')}</span>
                            </div>
                            <div>
                              <span className="text-slate-500">Channel: </span>
                              <span className="text-white">{sortedEvents[currentIndex].nba_triggered.channel}</span>
                            </div>
                            <div>
                              <span className="text-slate-500">Confidence: </span>
                              <span className="text-emerald-400 font-semibold">{(sortedEvents[currentIndex].nba_triggered.confidence * 100).toFixed(0)}%</span>
                            </div>
                            <div>
                              <span className="text-slate-500">Reason: </span>
                              <span className="text-slate-300 text-[10px]">{sortedEvents[currentIndex].nba_triggered.reason}</span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Journey Insights */}
                      {journey?.journey_insights && (
                        <div>
                          <h4 className="text-xs font-semibold text-white uppercase tracking-wider mb-3">Journey Insights</h4>
                          <div className="space-y-3">
                            {journey.journey_insights.most_valuable_purchase && (
                              <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                                <p className="text-[10px] text-emerald-400 uppercase mb-1">Top Purchase</p>
                                <p className="text-xs text-white font-semibold">{journey.journey_insights.most_valuable_purchase.event_value}</p>
                              </div>
                            )}
                            {journey.journey_insights.most_recent_complaint && (
                              <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/20">
                                <p className="text-[10px] text-red-400 uppercase mb-1">Recent Complaint</p>
                                <p className="text-xs text-white">{new Date(journey.journey_insights.most_recent_complaint.timestamp).toLocaleDateString()}</p>
                              </div>
                            )}
                            <div className="p-3 rounded-lg bg-blue-500/5 border border-blue-500/20">
                              <p className="text-[10px] text-blue-400 uppercase mb-1">Retention Recommendation</p>
                              <p className="text-xs text-white">{journey.journey_insights.retention_recommendation}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
              <User size={48} className="text-slate-800 mb-3" />
              <h3 className="text-sm font-semibold text-white mb-1">No Customer Selected</h3>
              <p className="text-xs max-w-sm" style={{ color: '#64748B' }}>
                Select a customer from the left sidebar to load their lifecycle timeline and initialize the player HUD
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
