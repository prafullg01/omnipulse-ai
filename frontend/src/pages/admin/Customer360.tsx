import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { Users, Search, ChevronRight, Shield, Heart, AlertTriangle, TrendingUp, ShoppingBag, ShoppingCart, Target, Brain, Zap, DollarSign, BarChart3, Eye } from 'lucide-react'
import api from '../../services/api'

function RiskBadge({ value }: { value: number }) {
  const color = value > 0.7 ? '#EF4444' : value > 0.4 ? '#F59E0B' : '#10B981'
  const label = value > 0.7 ? 'Critical' : value > 0.4 ? 'Medium' : 'Low'
  return <span className="badge text-[10px]" style={{ background: `${color}20`, color }}>{label} {(value * 100).toFixed(0)}%</span>
}

function EmotionBadge({ emotion }: { emotion: string }) {
  const colors: Record<string, string> = { happy: '#10B981', excited: '#8B5CF6', neutral: '#64748B', frustrated: '#F59E0B', angry: '#EF4444' }
  return <span className="badge text-[10px]" style={{ background: `${colors[emotion] || '#64748B'}20`, color: colors[emotion] || '#64748B' }}>{emotion}</span>
}

function ScoreGauge({ label, value, max = 100, color, sub }: { label: string; value: number; max?: number; color: string; sub?: string }) {
  const pct = (value / max) * 100
  return (
    <div className="text-center">
      <div className="relative w-14 h-14 mx-auto mb-1">
        <svg viewBox="0 0 36 36" className="w-full h-full">
          <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none" stroke="#1E293B" strokeWidth="3" />
          <motion.path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none" stroke={color} strokeWidth="3" strokeLinecap="round"
            strokeDasharray={`${pct}, 100`}
            initial={{ strokeDasharray: '0, 100' }}
            animate={{ strokeDasharray: `${pct}, 100` }}
            transition={{ duration: 0.8 }} />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs mono font-bold text-white">{typeof value === 'number' ? value.toFixed(0) : value}</span>
        </div>
      </div>
      <p className="text-[10px]" style={{ color: '#64748B' }}>{label}</p>
      {sub && <p className="text-[9px]" style={{ color }}>{sub}</p>}
    </div>
  )
}

export default function Customer360() {
  const [searchParams] = useSearchParams()
  const deepLinkId = searchParams.get('id')
  const [selectedId, setSelectedId] = useState<string | null>(deepLinkId)
  const [search, setSearch] = useState('')

  useEffect(() => {
    if (deepLinkId) setSelectedId(deepLinkId)
  }, [deepLinkId])

  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: () => api.get('/customers').then(r => r.data),
  })

  const { data: profile } = useQuery({
    queryKey: ['customer360', selectedId],
    queryFn: () => api.get(`/customers/360/${selectedId}`).then(r => r.data),
    enabled: !!selectedId,
    refetchInterval: 5000,
  })

  // Live intelligence snapshot
  const { data: intel } = useQuery({
    queryKey: ['intelligence', selectedId],
    queryFn: () => api.get(`/ai/intelligence/${selectedId}`).then(r => r.data),
    enabled: !!selectedId,
    refetchInterval: 5000,
  })

  const filtered = (customers || []).filter((c: any) =>
    c.name.toLowerCase().includes(search.toLowerCase()) || c.email.toLowerCase().includes(search.toLowerCase())
  )

  const churn = intel?.churn || {}
  const clv = intel?.clv || {}
  const trust = intel?.trust || {}
  const happiness = intel?.happiness || {}
  const risk = intel?.risk || {}
  const nba = intel?.nba || {}
  const campaign = intel?.campaign || null
  const twin = intel?.digital_twin || {}
  const execInsights = intel?.executive_insights || []

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">Customer 360 Super Panel</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>
        Complete intelligence for every customer — live
        <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px]"
              style={{ background: '#10B98120', color: '#10B981' }}>● LIVE</span>
      </p>

      <div className="grid lg:grid-cols-4 gap-5">
        {/* Customer List */}
        <div className="card p-4">
          <div className="relative mb-3">
            <Search size={14} className="absolute left-3 top-2.5" style={{ color: '#64748B' }} />
            <input value={search} onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-lg text-xs text-white"
              style={{ background: '#0F172A', border: '1px solid #1E293B' }}
              placeholder="Search customers..." />
          </div>
          <div className="space-y-1 max-h-[70vh] overflow-y-auto">
            {filtered.slice(0, 50).map((c: any) => (
              <button key={c.customer_id}
                onClick={() => setSelectedId(c.customer_id)}
                className="w-full flex items-center gap-2 p-2 rounded-lg text-left transition-all"
                style={{
                  background: selectedId === c.customer_id ? 'rgba(59,130,246,0.1)' : 'transparent',
                  border: selectedId === c.customer_id ? '1px solid rgba(59,130,246,0.3)' : '1px solid transparent',
                }}>
                <div className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
                     style={{ background: '#1E293B' }}>{c.name.charAt(0)}</div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-white truncate">{c.name}</p>
                  <p className="text-[10px] truncate" style={{ color: '#64748B' }}>{c.email}</p>
                </div>
                <ChevronRight size={12} style={{ color: '#475569' }} />
              </button>
            ))}
          </div>
        </div>

        {/* Detail Panel */}
        <div className="lg:col-span-3 space-y-4">
          <AnimatePresence mode="wait">
            {selectedId && profile ? (
              <motion.div key={selectedId} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                {/* Profile Header */}
                <div className="card p-4 mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold"
                         style={{ background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)', color: '#fff' }}>
                      {profile.name?.charAt(0)}
                    </div>
                    <div className="flex-1">
                      <h2 className="text-lg font-bold text-white">{profile.name}</h2>
                      <p className="text-xs" style={{ color: '#64748B' }}>
                        {profile.email} · {profile.city} · {profile.segment || 'new'}
                      </p>
                    </div>
                    <RiskBadge value={profile.churn_probability || 0} />
                    <EmotionBadge emotion={happiness.emotion || profile.emotion || 'neutral'} />
                  </div>
                </div>

                {/* Intelligence Gauges */}
                <div className="card p-4 mb-4">
                  <h3 className="text-xs font-semibold text-white mb-3 flex items-center gap-2">
                    <Brain size={14} style={{ color: '#8B5CF6' }} /> Intelligence Scores
                  </h3>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                    <ScoreGauge label="Trust" value={trust.trust_score ?? profile.intelligence?.trust_score ?? profile.trust_score ?? 0} color="#8B5CF6" sub={trust.trust_level} />
                    <ScoreGauge label="Happiness" value={happiness.happiness_score ?? profile.intelligence?.happiness_score ?? profile.happiness_score ?? 0} color="#EC4899" sub={happiness.mood} />
                    <ScoreGauge label="Engagement" value={profile.intelligence?.engagement_score ?? profile.engagement_score ?? 0} color="#3B82F6" sub={profile.segment} />
                    <ScoreGauge label="Risk" value={risk.risk_score ?? profile.intelligence?.risk_score ?? 0} color="#EF4444" sub={risk.risk_level} />
                    <ScoreGauge label="Churn" value={(churn.churn_probability ?? profile.intelligence?.churn_probability ?? 0) * 100} color="#F97316" sub={churn.churn_category} />
                    <ScoreGauge label="CLV" value={Math.min(100, ((clv.predicted_clv ?? profile.intelligence?.predicted_clv ?? 0) / 1000))} color="#10B981" sub={clv.value_tier} />
                  </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-4 mb-4">
                  {/* Churn Detail */}
                  <div className="card p-4">
                    <h3 className="text-xs font-semibold text-white mb-2 flex items-center gap-2">
                      <AlertTriangle size={13} style={{ color: '#F97316' }} /> Churn Analysis
                    </h3>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl mono font-bold" style={{ color: churn.churn_probability > 0.6 ? '#EF4444' : churn.churn_probability > 0.3 ? '#F59E0B' : '#10B981' }}>
                        {((churn.churn_probability || 0) * 100).toFixed(0)}%
                      </span>
                      <span className="badge text-[10px]" style={{
                        background: churn.churn_category === 'Critical' ? '#EF444420' : churn.churn_category === 'High' ? '#F9731620' : '#F59E0B20',
                        color: churn.churn_category === 'Critical' ? '#EF4444' : churn.churn_category === 'High' ? '#F97316' : '#F59E0B',
                      }}>{churn.churn_category || 'Unknown'}</span>
                      <span className="text-[10px] mono" style={{ color: '#64748B' }}>conf: {((churn.churn_confidence || 0) * 100).toFixed(0)}%</span>
                    </div>
                    <div className="space-y-1 max-h-28 overflow-y-auto">
                      {(churn.churn_reasons || []).map((r: string, i: number) => (
                        <p key={i} className="text-[11px]" style={{ color: r.startsWith('✓') ? '#10B981' : '#94A3B8' }}>• {r}</p>
                      ))}
                    </div>
                  </div>

                  {/* Trust Detail */}
                  <div className="card p-4">
                    <h3 className="text-xs font-semibold text-white mb-2 flex items-center gap-2">
                      <Shield size={13} style={{ color: '#8B5CF6' }} /> Trust Analysis
                    </h3>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl mono font-bold" style={{ color: '#8B5CF6' }}>
                        {(trust.trust_score || 50).toFixed(0)}/100
                      </span>
                      <span className="badge text-[10px]" style={{ background: '#8B5CF620', color: '#8B5CF6' }}>
                        {trust.trust_level || 'Fair'}
                      </span>
                      <span className="text-[10px]" style={{ color: trust.trust_trend === 'declining' ? '#EF4444' : '#10B981' }}>
                        {trust.trust_trend === 'declining' ? '↘ Declining' : trust.trust_trend === 'improving' ? '↗ Improving' : '→ Stable'}
                      </span>
                    </div>
                    <div className="space-y-1 max-h-28 overflow-y-auto">
                      {(trust.trust_reasons || []).map((d: any, i: number) => (
                        <p key={i} className="text-[11px]" style={{ color: d.type === 'positive' ? '#10B981' : d.type === 'negative' ? '#EF4444' : '#94A3B8' }}>
                          {d.impact} — {d.signal}
                        </p>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-4 mb-4">
                  {/* NBA */}
                  <div className="card p-4">
                    <h3 className="text-xs font-semibold text-white mb-2 flex items-center gap-2">
                      <Target size={13} style={{ color: '#3B82F6' }} /> Next Best Action
                    </h3>
                    <p className="text-sm font-medium text-white mb-1">{nba.action || 'Computing...'}</p>
                    <p className="text-[11px] mb-2" style={{ color: '#94A3B8' }}>{nba.reason}</p>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] px-2 py-0.5 rounded" style={{ background: '#3B82F620', color: '#3B82F6' }}>
                        Confidence: {((nba.confidence || 0) * 100).toFixed(0)}%
                      </span>
                      <span className="text-[10px] px-2 py-0.5 rounded" style={{ background: '#10B98120', color: '#10B981' }}>
                        Channel: {nba.channel}
                      </span>
                    </div>
                    {nba.offer && (
                      <p className="text-[11px] mt-2 p-2 rounded" style={{ background: '#F59E0B10', color: '#F59E0B', border: '1px solid #F59E0B20' }}>
                        💡 {nba.offer}
                      </p>
                    )}
                  </div>

                  {/* Campaign */}
                  <div className="card p-4">
                    <h3 className="text-xs font-semibold text-white mb-2 flex items-center gap-2">
                      <Zap size={13} style={{ color: '#F59E0B' }} /> Auto Campaign
                    </h3>
                    {campaign ? (
                      <>
                        <p className="text-sm font-medium text-white mb-1">{campaign.name}</p>
                        <p className="text-[11px]" style={{ color: '#94A3B8' }}>Trigger: {campaign.trigger_reason}</p>
                        <div className="flex items-center gap-3 mt-2">
                          <span className="text-[10px] px-2 py-0.5 rounded" style={{ background: '#10B98120', color: '#10B981' }}>
                            Conv: {((campaign.predicted_conversion || 0) * 100).toFixed(0)}%
                          </span>
                          <span className="text-[10px] px-2 py-0.5 rounded" style={{ background: '#3B82F620', color: '#3B82F6' }}>
                            Rev: ₹{(campaign.predicted_revenue || 0).toLocaleString('en-IN')}
                          </span>
                          <span className="text-[10px] px-2 py-0.5 rounded" style={{ background: '#8B5CF620', color: '#8B5CF6' }}>
                            {campaign.channel}
                          </span>
                        </div>
                      </>
                    ) : (
                      <p className="text-[11px]" style={{ color: '#475569' }}>No campaign triggered — customer activity normal</p>
                    )}
                  </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-4 mb-4">
                  {/* Digital Twin */}
                  <div className="card p-4">
                    <h3 className="text-xs font-semibold text-white mb-3 flex items-center gap-2">
                      <Eye size={13} style={{ color: '#06B6D4' }} /> Digital Twin — Scenario Comparison
                    </h3>
                    {twin.scenario_a && twin.scenario_b ? (
                      <div className="grid grid-cols-2 gap-3">
                        <div className="p-2 rounded-lg" style={{ background: '#EF444410', border: '1px solid #EF444420' }}>
                          <p className="text-[10px] font-semibold" style={{ color: '#EF4444' }}>No Action</p>
                          <p className="text-xs mono mt-1 text-white">Rev: ₹{(twin.scenario_a.predicted_revenue || 0).toLocaleString('en-IN')}</p>
                          <p className="text-[10px] mono" style={{ color: '#94A3B8' }}>Churn: {((twin.scenario_a.predicted_churn || 0) * 100).toFixed(0)}%</p>
                          <p className="text-[10px] mono" style={{ color: '#94A3B8' }}>Retention: {((twin.scenario_a.predicted_retention || 0) * 100).toFixed(0)}%</p>
                        </div>
                        <div className="p-2 rounded-lg" style={{ background: '#10B98110', border: '1px solid #10B98120' }}>
                          <p className="text-[10px] font-semibold" style={{ color: '#10B981' }}>With Action</p>
                          <p className="text-xs mono mt-1 text-white">Rev: ₹{(twin.scenario_b.predicted_revenue || 0).toLocaleString('en-IN')}</p>
                          <p className="text-[10px] mono" style={{ color: '#94A3B8' }}>Churn: {((twin.scenario_b.predicted_churn || 0) * 100).toFixed(0)}%</p>
                          <p className="text-[10px] mono" style={{ color: '#94A3B8' }}>Retention: {((twin.scenario_b.predicted_retention || 0) * 100).toFixed(0)}%</p>
                        </div>
                      </div>
                    ) : (
                      <p className="text-[11px]" style={{ color: '#475569' }}>Computing scenarios...</p>
                    )}
                    {twin.uplift && (
                      <p className="text-[11px] mt-2 p-2 rounded" style={{ background: '#10B98110', color: '#10B981', border: '1px solid #10B98120' }}>
                        💰 Uplift: ₹{(twin.uplift.revenue || 0).toLocaleString('en-IN')} (+{(twin.uplift.revenue_pct || 0).toFixed(1)}%)
                      </p>
                    )}
                  </div>

                  {/* Risk Dimensions */}
                  <div className="card p-4">
                    <h3 className="text-xs font-semibold text-white mb-3 flex items-center gap-2">
                      <BarChart3 size={13} style={{ color: '#EF4444' }} /> Risk Dimensions
                    </h3>
                    <div className="space-y-2">
                      {Object.entries(risk.risk_dimensions || {}).map(([key, val]) => {
                        const v = val as number
                        const color = v > 60 ? '#EF4444' : v > 35 ? '#F59E0B' : '#10B981'
                        return (
                          <div key={key}>
                            <div className="flex items-center justify-between mb-0.5">
                              <span className="text-[11px] capitalize" style={{ color: '#94A3B8' }}>{key}</span>
                              <span className="text-[10px] mono" style={{ color }}>{v.toFixed(0)}%</span>
                            </div>
                            <div className="w-full h-1 rounded-full" style={{ background: '#1E293B' }}>
                              <motion.div className="h-full rounded-full" style={{ background: color }}
                                initial={{ width: 0 }} animate={{ width: `${v}%` }} transition={{ duration: 0.6 }} />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                    {(risk.risk_drivers || []).length > 0 && (
                      <div className="mt-2 space-y-1">
                        {(risk.risk_drivers || []).map((d: string, i: number) => (
                          <p key={i} className="text-[10px]" style={{ color: '#F97316' }}>⚠ {d}</p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Executive Insights */}
                {execInsights.length > 0 && (
                  <div className="card p-4 mb-4">
                    <h3 className="text-xs font-semibold text-white mb-2 flex items-center gap-2">
                      <Brain size={13} style={{ color: '#F59E0B' }} /> Executive Insights
                    </h3>
                    <div className="space-y-1">
                      {execInsights.map((insight: string, i: number) => (
                        <p key={i} className="text-[11px]" style={{ color: '#CBD5E1' }}>{insight}</p>
                      ))}
                    </div>
                  </div>
                )}

                {/* CLV & Orders Row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  {[
                    { label: 'Current CLV', value: `₹${(clv.clv || 0).toLocaleString('en-IN')}`, color: '#10B981' },
                    { label: 'Predicted CLV', value: `₹${(clv.predicted_clv || 0).toLocaleString('en-IN')}`, color: '#3B82F6' },
                    { label: 'Value Tier', value: clv.value_tier || 'Bronze', color: '#F59E0B' },
                    { label: 'Orders', value: profile.orders?.length || 0, color: '#8B5CF6' },
                  ].map((kpi, i) => (
                    <div key={i} className="card p-3 text-center">
                      <p className="text-sm font-bold mono" style={{ color: kpi.color }}>{kpi.value}</p>
                      <p className="text-[9px]" style={{ color: '#64748B' }}>{kpi.label}</p>
                    </div>
                  ))}
                </div>

                {/* Recent Activity */}
                <div className="card p-4">
                  <h3 className="text-xs font-semibold text-white mb-3">Recent Activity</h3>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto">
                    {(profile.events || profile.journey_timeline || []).slice(0, 20).map((ev: any, i: number) => {
                      const icons: Record<string, string> = {
                        'PRODUCT_VIEW': '👁️', 'product_view': '👁️',
                        'SEARCH': '🔍', 'search': '🔍',
                        'ADD_TO_CART': '🛒', 'cart_add': '🛒',
                        'REMOVE_FROM_CART': '🗑️', 'cart_remove': '🗑️',
                        'PURCHASE_COMPLETED': '💰', 'purchase': '💰',
                        'ADD_TO_WISHLIST': '❤️', 'wishlist_add': '❤️',
                        'REVIEW_SUBMITTED': '⭐', 'review_submit': '⭐', 'review_submitted': '⭐',
                        'REFUND_REQUESTED': '↩️', 'refund_request': '↩️',
                        'LOGIN': '🔑', 'USER_LOGIN': '🔑',
                        'CHECKOUT_STARTED': '🧾', 'checkout': '🧾',
                        'complaint': '😤', 'COMPLAINT': '😤',
                        'support_chat': '💬', 'support_ticket': '🎫', 'ticket_created': '🎫',
                        'campaign_opened': '📧', 'campaign_received': '📨',
                        'offer_clicked': '🔗', 'wishlist_remove': '💔',
                        'assistant_interaction': '🤖',
                      }
                      return (
                        <div key={i} className="flex items-center gap-2 text-[11px]">
                          <span>{icons[ev.event_type] || '📌'}</span>
                          <span className="text-white">{(ev.event_type || '').replace(/_/g, ' ')}</span>
                          <span style={{ color: '#64748B' }}>{ev.event_value}</span>
                          <span className="ml-auto mono text-[10px]" style={{ color: '#475569' }}>
                            {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : ''}
                          </span>
                        </div>
                      )
                    })}
                    {(!profile.events?.length && !profile.journey_timeline?.length) && (
                      <p className="text-xs text-center py-3" style={{ color: '#475569' }}>No activity yet</p>
                    )}
                  </div>
                </div>
              </motion.div>
            ) : (
              <div className="card p-12 text-center">
                <Users size={32} className="mx-auto mb-3" style={{ color: '#475569' }} />
                <p className="text-sm" style={{ color: '#64748B' }}>Select a customer to view their complete intelligence profile</p>
              </div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
