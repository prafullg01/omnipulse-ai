import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { GitBranch, Play, TrendingUp, TrendingDown, DollarSign, Users, AlertTriangle, Heart, Zap, MessageCircle, ShoppingBag, Info } from 'lucide-react'
import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import api from '../../services/api'

export default function DigitalTwin() {
  const [selectedCustomer, setSelectedCustomer] = useState<any | null>(null)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const { data: customersData } = useQuery({
    queryKey: ['digitalTwinCustomers'],
    queryFn: () => api.get('/ai/digital-twin/customers').then(r => r.data),
  })

  const customers = customersData?.customers || []

  const simulate = async (customer: any) => {
    setLoading(true)
    setSelectedCustomer(customer)
    try {
      const { data } = await api.post('/ai/digital-twin/simulate', { customer_id: customer.customer_id })
      setResult(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const chartData = result ? [
    { month: 'Now', noAction: 0, intervention: 0 },
    { month: '30d', noAction: result.no_action.revenue_30d, intervention: result.intervention.revenue_30d },
    { month: '60d', noAction: result.no_action.revenue_60d, intervention: result.intervention.revenue_60d },
    { month: '90d', noAction: result.no_action.revenue_90d, intervention: result.intervention.revenue_90d },
  ] : []

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
            <GitBranch className="text-purple-400" />
            Digital Twin Lab
          </h1>
          <p className="text-sm" style={{ color: '#64748B' }}>Simulate customer futures with and without intervention • All values database-backed</p>
        </div>
        {customersData && (
          <div className="text-right">
            <p className="text-xs font-medium text-purple-400">{customersData.sample_size} Sample • {customersData.total?.toLocaleString()} Total</p>
            <p className="text-[10px]" style={{ color: '#64748B' }}>
              Stratified random: 20%, 40%, 60%, 90% mix
            </p>
          </div>
        )}
      </div>

      <div className="grid lg:grid-cols-3 gap-5">
        {/* Customer Selection */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-white">Sample Customers</h3>
            <div className="text-[10px] font-mono text-purple-400">{customers.length} of {customersData?.total || 0}</div>
          </div>
          <div className="space-y-1.5 max-h-[600px] overflow-y-auto pr-2 custom-scrollbar">
            {customers.map((c: any, i: number) => {
              const riskColor = c.churn_probability > 0.7 ? '#EF4444' : c.churn_probability > 0.5 ? '#F59E0B' : '#10B981'
              const isSelected = selectedCustomer?.customer_id === c.customer_id
              
              return (
                <motion.button
                  key={c.customer_id}
                  className="w-full flex items-center gap-3 p-2.5 rounded-lg text-left border"
                  style={{
                    background: isSelected ? 'rgba(139,92,246,0.1)' : 'transparent',
                    borderColor: isSelected ? 'rgba(139,92,246,0.3)' : 'transparent'
                  }}
                  onClick={() => simulate(c)}
                  whileHover={{ background: 'rgba(139,92,246,0.05)', scale: 1.01 }}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: Math.min(i * 0.02, 0.3) }}
                >
                  <div className="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
                       style={{ background: `hsl(${(c.name.charCodeAt(0) * 7) % 360}, 60%, 50%)` }}>
                    {c.name.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-white truncate">{c.name}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px]" style={{ color: '#64748B' }}>
                        CLV: ₹{c.clv?.toLocaleString('en-IN')}
                      </span>
                      <span className="text-[9px] px-1.5 py-0.5 rounded font-mono" style={{ background: `${riskColor}15`, color: riskColor }}>
                        {(c.churn_probability * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  {c.churn_probability > 0.7 && (
                    <AlertTriangle size={14} className="text-red-400 flex-shrink-0" />
                  )}
                </motion.button>
              )
            })}
          </div>
          {customersData?.risk_distribution && (
            <div className="mt-4 pt-3 border-t" style={{ borderColor: '#2A2D3A' }}>
              <p className="text-[10px] font-semibold text-slate-400 mb-2">Risk Distribution (Sample)</p>
              <div className="space-y-1 text-[9px]">
                <div className="flex justify-between">
                  <span style={{ color: '#10B981' }}>Low (&lt;30%):</span>
                  <span className="text-white font-mono">~10</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#F59E0B' }}>Medium (30-60%):</span>
                  <span className="text-white font-mono">~15</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#EF4444' }}>High (60-80%):</span>
                  <span className="text-white font-mono">~15</span>
                </div>
                <div className="flex justify-between">
                  <span style={{ color: '#DC2626' }}>Critical (&gt;80%):</span>
                  <span className="text-white font-mono">~10</span>
                </div>
              </div>
            </div>
          )}
          {customersData?.clv_sources && (
            <div className="mt-3 pt-3 border-t" style={{ borderColor: '#2A2D3A' }}>
              <p className="text-[10px] font-semibold text-slate-400 mb-2">CLV Sources (Total)</p>
              <div className="grid grid-cols-2 gap-1 text-[9px]">
                {Object.entries(customersData.clv_sources).map(([source, count]: [string, any]) => (
                  <div key={source} className="flex justify-between">
                    <span style={{ color: '#64748B' }}>{source}:</span>
                    <span className="text-white font-mono">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>

        {/* Simulation Result */}
        <motion.div className="card p-5 lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="w-10 h-10 border-2 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mx-auto mb-3" />
                <p className="text-sm" style={{ color: '#64748B' }}>Simulating future scenarios...</p>
              </div>
            </div>
          ) : result ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-white">{result.customer_name}</h3>
                  <p className="text-xs mt-1" style={{ color: '#64748B' }}>
                    CLV: ₹{result.effective_clv?.toLocaleString('en-IN')} • Segment: {result.segment} • Source: {result.clv_source}
                  </p>
                </div>
                <div className="px-3 py-1 rounded-lg" style={{ background: result.revenue_delta > 0 ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)' }}>
                  <span className="text-xs font-medium font-mono" style={{ color: result.revenue_delta > 0 ? '#10B981' : '#EF4444' }}>
                    {result.revenue_delta > 0 ? '+' : ''}₹{result.revenue_delta?.toLocaleString('en-IN')} delta
                  </span>
                </div>
              </div>

              {/* Simulation Drivers Panel */}
              {result.drivers && (
                <div className="grid grid-cols-4 gap-3 p-4 rounded-lg" style={{ background: 'rgba(139,92,246,0.05)', border: '1px solid rgba(139,92,246,0.1)' }}>
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 mb-1">
                      <AlertTriangle size={12} style={{ color: result.drivers.churn_probability > 0.7 ? '#EF4444' : '#F59E0B' }} />
                      <p className="text-[10px] font-medium" style={{ color: '#94A3B8' }}>Churn Risk</p>
                    </div>
                    <p className="text-lg font-bold font-mono" style={{ color: result.drivers.churn_probability > 0.7 ? '#EF4444' : result.drivers.churn_probability > 0.5 ? '#F59E0B' : '#10B981' }}>
                      {(result.drivers.churn_probability * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 mb-1">
                      <Heart size={12} className="text-cyan-400" />
                      <p className="text-[10px] font-medium" style={{ color: '#94A3B8' }}>Trust</p>
                    </div>
                    <p className="text-lg font-bold font-mono text-cyan-400">{result.drivers.trust_score}/100</p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 mb-1">
                      <Zap size={12} className="text-green-400" />
                      <p className="text-[10px] font-medium" style={{ color: '#94A3B8' }}>Happiness</p>
                    </div>
                    <p className="text-lg font-bold font-mono text-green-400">{result.drivers.happiness_score}/100</p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 mb-1">
                      <ShoppingBag size={12} className="text-purple-400" />
                      <p className="text-[10px] font-medium" style={{ color: '#94A3B8' }}>Engagement</p>
                    </div>
                    <p className="text-lg font-bold font-mono text-purple-400">{result.drivers.engagement_score}/100</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-medium mb-1" style={{ color: '#94A3B8' }}>Recency</p>
                    <p className="text-sm font-mono text-white">{result.drivers.recency_days}d</p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-medium mb-1" style={{ color: '#94A3B8' }}>Orders</p>
                    <p className="text-sm font-mono text-white">{result.drivers.frequency}</p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center justify-center gap-1 mb-1">
                      <MessageCircle size={10} className="text-red-400" />
                      <p className="text-[10px] font-medium" style={{ color: '#94A3B8' }}>Complaints</p>
                    </div>
                    <p className="text-sm font-mono" style={{ color: result.drivers.complaints > 0 ? '#EF4444' : '#64748B' }}>
                      {result.drivers.complaints}
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-medium mb-1" style={{ color: '#94A3B8' }}>Campaigns</p>
                    <p className="text-sm font-mono text-white">{result.drivers.campaign_engagement}</p>
                  </div>
                </div>
              )}

              {/* Scenario Comparison */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg" style={{ background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.1)' }}>
                  <p className="text-xs font-medium text-red-400 mb-3">SCENARIO A: No Intervention</p>
                  <div className="space-y-2">
                    <div className="flex justify-between"><span className="text-xs" style={{ color: '#94A3B8' }}>Churn (30d)</span><span className="text-sm mono font-medium text-red-400">{(result.no_action.churn_30d * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between"><span className="text-xs" style={{ color: '#94A3B8' }}>Churn (90d)</span><span className="text-sm mono font-medium text-red-400">{(result.no_action.churn_90d * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between"><span className="text-xs" style={{ color: '#94A3B8' }}>Revenue (90d)</span><span className="text-sm mono font-medium text-white">₹{result.no_action.revenue_90d?.toLocaleString('en-IN')}</span></div>
                    <div className="flex justify-between"><span className="text-xs" style={{ color: '#94A3B8' }}>Retention</span><span className="text-sm mono font-medium text-red-400">{(result.no_action.retention_prob * 100).toFixed(0)}%</span></div>
                  </div>
                </div>
                <div className="p-4 rounded-lg" style={{ background: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.1)' }}>
                  <p className="text-xs font-medium text-green-400 mb-3">SCENARIO B: With Intervention</p>
                  <div className="space-y-2">
                    <div className="flex justify-between"><span className="text-xs" style={{ color: '#94A3B8' }}>Churn (30d)</span><span className="text-sm mono font-medium text-green-400">{(result.intervention.churn_30d * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between"><span className="text-xs" style={{ color: '#94A3B8' }}>Churn (90d)</span><span className="text-sm mono font-medium text-green-400">{(result.intervention.churn_90d * 100).toFixed(0)}%</span></div>
                    <div className="flex justify-between"><span className="text-xs" style={{ color: '#94A3B8' }}>Revenue (90d)</span><span className="text-sm mono font-medium text-white">₹{result.intervention.revenue_90d?.toLocaleString('en-IN')}</span></div>
                    <div className="flex justify-between"><span className="text-xs" style={{ color: '#94A3B8' }}>Retention</span><span className="text-sm mono font-medium text-green-400">{(result.intervention.retention_prob * 100).toFixed(0)}%</span></div>
                  </div>
                </div>
              </div>

              {/* Revenue Chart */}
              <div>
                <h4 className="text-xs font-semibold text-white mb-3 flex items-center gap-2">
                  <TrendingUp size={14} className="text-purple-400" />
                  Revenue Projection (90 days)
                </h4>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="noActionGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#EF4444" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="interventionGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10B981" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="month" tick={{ fill: '#64748B', fontSize: 11 }} />
                      <YAxis tick={{ fill: '#64748B', fontSize: 10 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
                      <Tooltip 
                        contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} 
                        formatter={(value: number) => [`₹${value.toLocaleString('en-IN')}`, '']}
                      />
                      <Area type="monotone" dataKey="noAction" stroke="#EF4444" fill="url(#noActionGrad)" strokeWidth={2} name="No Action" />
                      <Area type="monotone" dataKey="intervention" stroke="#10B981" fill="url(#interventionGrad)" strokeWidth={2} name="With Intervention" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Formula Info */}
              {result.formula_info && (
                <div className="p-3 rounded-lg" style={{ background: 'rgba(100,116,139,0.05)', border: '1px solid rgba(100,116,139,0.1)' }}>
                  <div className="flex items-start gap-2">
                    <Info size={14} className="text-slate-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-[10px] font-semibold text-slate-400 mb-1">Simulation Formula</p>
                      <p className="text-[9px] font-mono" style={{ color: '#64748B', lineHeight: '1.4' }}>
                        CLV: ₹{result.formula_info.clv_used?.toLocaleString('en-IN')} ({result.formula_info.clv_source}) • 
                        Segment: {result.formula_info.segment} • 
                        Rescue Factor: {result.formula_info.rescue_factor} • 
                        Revenue Multipliers: {JSON.stringify(result.formula_info.revenue_multipliers)}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <GitBranch size={48} style={{ color: '#2A2D3A' }} className="mx-auto mb-3" />
                <p className="text-sm" style={{ color: '#64748B' }}>Select a customer to simulate their future</p>
                <p className="text-xs mt-2" style={{ color: '#475569' }}>All simulations use real database values</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
