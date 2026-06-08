import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Target, Zap, Mail, MessageSquare, Gift, Clock, ChevronRight } from 'lucide-react'
import api from '../../services/api'

export default function NBACenter() {
  const [selectedCustomer, setSelectedCustomer] = useState<string | null>(null)
  const [nbaResult, setNbaResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState<'generate' | 'overview'>('generate')

  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: () => api.get('/customers').then(r => r.data),
  })

  const { data: nbaOverview } = useQuery({
    queryKey: ['nbaOverview'],
    queryFn: () => api.get('/analytics/nba').then(r => r.data),
    enabled: viewMode === 'overview',
    refetchInterval: 15000,
  })

  const generateNBA = async (customerId: string) => {
    setLoading(true)
    setSelectedCustomer(customerId)
    try {
      const { data } = await api.get(`/ai/nba/${customerId}`)
      setNbaResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const tierColors: Record<string, string> = { rules: '#10B981', ml: '#3B82F6', gemini: '#8B5CF6' }
  const channelIcons: Record<string, any> = { email: Mail, sms: MessageSquare, push: Zap }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Next Best Action Center</h1>
          <p className="text-sm" style={{ color: '#64748B' }}>Hierarchical Inference Router: Rules → ML → Gemini</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('generate')}
            className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'generate'
                ? 'bg-purple-600 text-white'
                : 'bg-white/5 text-slate-400 hover:bg-white/10'
            }`}
          >
            Generate NBA
          </button>
          <button
            onClick={() => setViewMode('overview')}
            className={`px-4 py-2 rounded-lg text-xs font-medium transition-all ${
              viewMode === 'overview'
                ? 'bg-purple-600 text-white'
                : 'bg-white/5 text-slate-400 hover:bg-white/10'
            }`}
          >
            NBA Overview
          </button>
        </div>
      </div>

      {viewMode === 'generate' ? (
        <div className="grid lg:grid-cols-3 gap-5">{/* existing generate UI */}
        {/* Customer Selection */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <h3 className="text-sm font-semibold text-white mb-3">Select Customer</h3>
          <div className="space-y-1.5 max-h-[500px] overflow-y-auto">
            {(customers || []).slice(0, 20).map((c: any, i: number) => (
              <motion.button
                key={c.customer_id}
                className="w-full flex items-center gap-3 p-2.5 rounded-lg text-left transition-colors"
                style={{
                  background: selectedCustomer === c.customer_id ? 'rgba(59,130,246,0.1)' : 'transparent',
                  border: selectedCustomer === c.customer_id ? '1px solid rgba(59,130,246,0.2)' : '1px solid transparent',
                }}
                onClick={() => generateNBA(c.customer_id)}
                whileHover={{ background: 'rgba(59,130,246,0.05)' }}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <div className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
                     style={{ background: `hsl(${(c.name.charCodeAt(0) * 7) % 360}, 60%, 50%)` }}>
                  {c.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-white truncate">{c.name}</p>
                  <p className="text-[10px] truncate" style={{ color: '#64748B' }}>Risk: {(c.churn_probability * 100).toFixed(0)}%</p>
                </div>
                <ChevronRight size={14} style={{ color: '#64748B' }} />
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* NBA Result */}
        <motion.div className="card p-5 lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="w-8 h-8 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
            </div>
          ) : nbaResult ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
              {/* Decision Header */}
              <div className="flex items-center justify-between mb-5">
                <div>
                  <h3 className="text-lg font-bold text-white">Recommendation Generated</h3>
                  <p className="text-xs" style={{ color: '#64748B' }}>Inference Tier: <span className="font-medium" style={{ color: tierColors[nbaResult.inference_tier] }}>{nbaResult.inference_tier.toUpperCase()}</span></p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-right">
                    <p className="text-xs" style={{ color: '#64748B' }}>Confidence</p>
                    <p className="text-xl font-bold mono" style={{ color: nbaResult.confidence > 0.7 ? '#10B981' : '#F59E0B' }}>
                      {(nbaResult.confidence * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Customer Profile Signals */}
              <div className="grid grid-cols-4 gap-3 mb-5 p-4 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid #2A2D3A' }}>
                <div>
                  <p className="text-[10px] font-medium mb-1" style={{ color: '#64748B' }}>CHURN RISK</p>
                  <p className="text-lg font-bold mono" style={{ color: nbaResult.customer_churn > 0.7 ? '#EF4444' : nbaResult.customer_churn > 0.5 ? '#F59E0B' : '#10B981' }}>
                    {(nbaResult.customer_churn * 100).toFixed(0)}%
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-medium mb-1" style={{ color: '#64748B' }}>TRUST SCORE</p>
                  <p className="text-lg font-bold text-white mono">{nbaResult.customer_trust?.toFixed(0)}</p>
                </div>
                <div>
                  <p className="text-[10px] font-medium mb-1" style={{ color: '#64748B' }}>ENGAGEMENT</p>
                  <p className="text-lg font-bold text-white mono">{nbaResult.customer_engagement?.toFixed(0)}</p>
                </div>
                <div>
                  <p className="text-[10px] font-medium mb-1" style={{ color: '#64748B' }}>{nbaResult.clv_label?.toUpperCase() || 'CLV'}</p>
                  <p className="text-lg font-bold text-white mono">₹{nbaResult.customer_clv?.toLocaleString() || '0'}</p>
                </div>
              </div>

              {/* Decision Cards */}
              <div className="grid grid-cols-2 gap-3 mb-5">
                {[
                  { label: 'Action', value: nbaResult.recommended_action?.replace(/_/g, ' '), color: '#3B82F6' },
                  { label: 'Channel', value: nbaResult.channel, color: '#8B5CF6' },
                  { label: 'Tone', value: nbaResult.tone, color: '#10B981' },
                  { label: 'Timing', value: nbaResult.timing, color: '#F59E0B' },
                ].map((d, i) => (
                  <motion.div key={i} className="p-3 rounded-lg" style={{ background: `${d.color}08`, border: `1px solid ${d.color}15` }}
                    initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 + i * 0.1 }}>
                    <p className="text-[10px] font-medium uppercase" style={{ color: d.color }}>{d.label}</p>
                    <p className="text-sm font-semibold text-white mt-1 capitalize">{d.value}</p>
                  </motion.div>
                ))}
              </div>

              {/* Offer */}
              <div className="p-4 rounded-lg mb-4" style={{ background: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.1)' }}>
                <div className="flex items-center gap-2 mb-1">
                  <Gift size={14} className="text-green-400" />
                  <span className="text-xs font-medium text-green-400">RECOMMENDED OFFER</span>
                </div>
                <p className="text-sm text-white">{nbaResult.offer}</p>
              </div>

              {/* Reasoning */}
              <div className="p-4 rounded-lg mb-4" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid #2A2D3A' }}>
                <p className="text-xs font-medium text-blue-400 mb-2">REASONING</p>
                <p className="text-sm" style={{ color: '#94A3B8' }}>{nbaResult.reason}</p>
              </div>

              {/* Signals */}
              <div>
                <p className="text-xs font-medium mb-2" style={{ color: '#64748B' }}>SIGNALS USED</p>
                <div className="flex flex-wrap gap-2">
                  {(nbaResult.signals_used || []).map((s: string, i: number) => (
                    <span key={i} className="badge badge-info">{s.replace(/_/g, ' ')}</span>
                  ))}
                </div>
              </div>

              {/* Generated Message */}
              {nbaResult.message && (
                <div className="mt-4 p-4 rounded-lg" style={{ background: 'rgba(139,92,246,0.05)', border: '1px solid rgba(139,92,246,0.1)' }}>
                  <p className="text-xs font-medium text-purple-400 mb-2">GENERATED MESSAGE</p>
                  <p className="text-sm italic" style={{ color: '#94A3B8' }}>"{nbaResult.message}"</p>
                </div>
              )}
            </motion.div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <Target size={48} style={{ color: '#2A2D3A' }} className="mx-auto mb-3" />
                <p className="text-sm" style={{ color: '#64748B' }}>Select a customer to generate a recommendation</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>
      ) : (
        <div className="space-y-5">
          {/* NBA Statistics with NEW ANALYTICS CARDS */}
          <div className="grid grid-cols-5 gap-4">
            <motion.div className="card p-4" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
              <p className="text-xs mb-1" style={{ color: '#64748B' }}>Total Decisions</p>
              <p className="text-2xl font-bold text-white mono">{nbaOverview?.total_decisions || 0}</p>
            </motion.div>
            
            <motion.div className="card p-4" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
              <p className="text-xs mb-1" style={{ color: '#64748B' }}>Avg Confidence</p>
              <p className="text-2xl font-bold mono" style={{ color: '#10B981' }}>{((nbaOverview?.avg_confidence || 0) * 100).toFixed(0)}%</p>
            </motion.div>
            
            <motion.div className="card p-4" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <p className="text-xs mb-1" style={{ color: '#64748B' }}>High Confidence</p>
              <p className="text-2xl font-bold text-white mono">{nbaOverview?.high_confidence_decisions || 0}</p>
              <p className="text-[10px] mt-0.5" style={{ color: '#64748B' }}>&gt;70% confidence</p>
            </motion.div>
            
            {Object.entries(nbaOverview?.tier_distribution || {}).map(([tier, count], i) => (
              <motion.div key={tier} className="card p-4" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + (i * 0.05) }}>
                <p className="text-xs mb-1 uppercase" style={{ color: tierColors[tier] || '#64748B' }}>{tier} Tier</p>
                <p className="text-2xl font-bold text-white mono">{count as number}</p>
              </motion.div>
            ))}
          </div>

          {/* Action & Channel Distribution Cards */}
          <div className="grid grid-cols-2 gap-5">
            <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
              <h3 className="text-sm font-semibold text-white mb-4">Actions by Type</h3>
              <div className="space-y-2">
                {Object.entries(nbaOverview?.action_distribution || {}).map(([action, count]) => (
                  <div key={action} className="flex items-center justify-between p-2 rounded-lg border border-white/5 bg-white/[0.02]">
                    <span className="text-xs capitalize" style={{ color: '#94A3B8' }}>{action.replace(/_/g, ' ')}</span>
                    <span className="text-sm font-bold text-white mono">{count as number}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <h3 className="text-sm font-semibold text-white mb-4">Channels by Type</h3>
              <div className="space-y-2">
                {Object.entries(nbaOverview?.channel_distribution || {}).map(([channel, count]) => (
                  <div key={channel} className="flex items-center justify-between p-2 rounded-lg border border-white/5 bg-white/[0.02]">
                    <span className="text-xs capitalize" style={{ color: '#94A3B8' }}>{channel}</span>
                    <span className="text-sm font-bold text-white mono">{count as number}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* NBA Decision Table with REAL DATABASE VALUES */}
          <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <h3 className="text-sm font-semibold text-white mb-4">Recent NBA Decisions (Highest Risk First)</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="text-left text-xs font-medium py-2 px-3" style={{ color: '#64748B' }}>Customer</th>
                    <th className="text-left text-xs font-medium py-2 px-3" style={{ color: '#64748B' }}>Risk</th>
                    <th className="text-left text-xs font-medium py-2 px-3" style={{ color: '#64748B' }}>Trust</th>
                    <th className="text-left text-xs font-medium py-2 px-3" style={{ color: '#64748B' }}>Engagement</th>
                    <th className="text-left text-xs font-medium py-2 px-3" style={{ color: '#64748B' }}>CLV</th>
                    <th className="text-left text-xs font-medium py-2 px-3" style={{ color: '#64748B' }}>Action</th>
                    <th className="text-left text-xs font-medium py-2 px-3" style={{ color: '#64748B' }}>Channel</th>
                    <th className="text-left text-xs font-medium py-2 px-3" style={{ color: '#64748B' }}>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {(nbaOverview?.decisions || []).map((d: any) => (
                    <tr key={d.decision_id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                      <td className="py-3 px-3">
                        <p className="text-xs font-medium text-white">{d.customer_name}</p>
                        <p className="text-[10px]" style={{ color: '#64748B' }}>{d.customer_id.slice(0, 12)}</p>
                      </td>
                      <td className="py-3 px-3">
                        <span className="text-xs font-medium mono" style={{ color: d.churn_probability > 0.7 ? '#EF4444' : d.churn_probability > 0.5 ? '#F59E0B' : '#10B981' }}>
                          {(d.churn_probability * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="text-xs mono" style={{ color: '#94A3B8' }}>{d.trust_score?.toFixed(0) || 'N/A'}</span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="text-xs mono" style={{ color: '#94A3B8' }}>{d.engagement_score?.toFixed(0) || 'N/A'}</span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="text-xs mono" style={{ color: '#94A3B8' }}>₹{d.clv?.toLocaleString() || '0'}</span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="badge badge-info text-[10px]">{d.recommended_action?.replace(/_/g, ' ')}</span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="text-xs text-slate-300 capitalize">{d.channel}</span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="text-xs font-medium mono" style={{ color: d.confidence > 0.7 ? '#10B981' : '#F59E0B' }}>
                          {(d.confidence * 100).toFixed(0)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
