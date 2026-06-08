import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Scale, Users, MapPin, AlertTriangle, ShieldCheck, Info } from 'lucide-react'
import { BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts'
import api from '../../services/api'
import { useState } from 'react'

function FairnessTooltip({ text }: { text: string }) {
  const [show, setShow] = useState(false)
  return (
    <span className="relative inline-block ml-1">
      <Info size={12} className="cursor-help opacity-40 hover:opacity-100 transition-opacity"
            style={{ color: '#64748B' }}
            onMouseEnter={() => setShow(true)}
            onMouseLeave={() => setShow(false)} />
      {show && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 rounded-lg text-[10px] leading-relaxed"
          style={{ background: '#1E293B', border: '1px solid #374151', color: '#94A3B8', boxShadow: '0 8px 32px rgba(0,0,0,0.4)' }}>
          {text}
        </motion.div>
      )}
    </span>
  )
}

const COLORS = ['#3B82F6', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B', '#EF4444', '#06B6D4', '#F97316']

export default function FairnessCenter() {
  const { data } = useQuery({
    queryKey: ['platform-intelligence'],
    queryFn: () => api.get('/ai/platform-intelligence').then(r => r.data),
    refetchInterval: 8000,
  })

  const fairness = data?.fairness || {}
  const genderCoverage = fairness.gender_coverage || {}
  const ageCoverage = fairness.age_coverage || {}
  const locationCoverage = fairness.location_coverage || {}
  const trustEquity = fairness.trust_equity || {}
  const biasAlerts = fairness.bias_alerts || []

  const genderData = Object.entries(genderCoverage).map(([k, v]) => ({ name: k || 'Unknown', value: v as number }))
  const ageData = Object.entries(ageCoverage).map(([k, v]) => ({ name: k, value: v as number }))
  const locationData = Object.entries(locationCoverage).slice(0, 8).map(([k, v]) => ({ name: k || 'Unknown', value: v as number }))

  const trustEquityData = Object.entries(trustEquity).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1),
    value: v as number,
    fill: k === 'excellent' ? '#10B981' : k === 'good' ? '#3B82F6' : k === 'fair' ? '#F59E0B' : k === 'poor' ? '#F97316' : '#EF4444',
  }))

  const churnDist = data?.churn_distribution || {}
  const clvDist = data?.clv_distribution || {}

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">Fairness Observatory</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>
        Coverage, equity, and bias monitoring — updates when new customers join
        <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px]"
              style={{ background: '#10B98120', color: '#10B981' }}>● LIVE</span>
      </p>

      {/* Bias Alerts */}
      {biasAlerts.length > 0 && (
        <motion.div className="mb-6 p-4 rounded-xl" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)' }}
          initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={16} style={{ color: '#EF4444' }} />
            <h3 className="text-sm font-semibold" style={{ color: '#EF4444' }}>Bias Alerts Detected</h3>
          </div>
          {biasAlerts.map((a: string, i: number) => (
            <p key={i} className="text-xs ml-6" style={{ color: '#FCA5A5' }}>• {a}</p>
          ))}
        </motion.div>
      )}

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { icon: Users, label: 'Total Customers', value: data?.total_customers || 0, color: '#3B82F6' },
          { icon: Scale, label: 'Recommendation Equity', value: `${(fairness.recommendation_equity || 0).toFixed(0)}%`, color: '#8B5CF6', tooltip: 'Measures how evenly NBA recommendations are distributed across gender, age, action types, and channels. A score below 100% indicates some demographic groups or channels receive disproportionate recommendations. Coverage (100%) means all customers GET recommendations; Equity measures whether the DISTRIBUTION is balanced.' },

          { icon: ShieldCheck, label: 'Campaign Equity', value: `${(fairness.campaign_equity || 0).toFixed(0)}%`, color: '#10B981' },
          { icon: AlertTriangle, label: 'Bias Alerts', value: biasAlerts.length, color: biasAlerts.length > 0 ? '#EF4444' : '#10B981' },
        ].map((kpi, i) => (
          <motion.div key={i} className="card p-4" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
            <kpi.icon size={16} style={{ color: kpi.color }} className="mb-2" />
            <p className="text-2xl font-bold mono text-white">{typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}</p>
            <p className="text-[10px] flex items-center justify-center gap-0.5" style={{ color: '#64748B' }}>
              {kpi.label}
              {kpi.tooltip && <FairnessTooltip text={kpi.tooltip} />}
            </p>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-5 mb-6">
        {/* Gender Coverage */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Gender Coverage</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={genderData} cx="50%" cy="50%" innerRadius={35} outerRadius={65} paddingAngle={3} dataKey="value">
                  {genderData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-1 mt-2">
            {genderData.map((d, i) => (
              <div key={d.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
                  <span className="text-[11px]" style={{ color: '#94A3B8' }}>{d.name}</span>
                </div>
                <span className="text-[11px] mono" style={{ color: '#CBD5E1' }}>{d.value}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Age Coverage */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Age Coverage</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ageData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis type="number" tick={{ fill: '#64748B', fontSize: 10 }} />
                <YAxis dataKey="name" type="category" tick={{ fill: '#64748B', fontSize: 10 }} width={45} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="value" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Location Coverage */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <MapPin size={14} style={{ color: '#06B6D4' }} /> Location Coverage
          </h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {locationData.map((d, i) => {
              const maxVal = Math.max(...locationData.map(l => l.value), 1)
              return (
                <div key={d.name}>
                  <div className="flex items-center justify-between mb-0.5">
                    <span className="text-[11px]" style={{ color: '#94A3B8' }}>{d.name}</span>
                    <span className="text-[11px] mono" style={{ color: '#CBD5E1' }}>{d.value}</span>
                  </div>
                  <div className="w-full h-1 rounded-full" style={{ background: '#1E293B' }}>
                    <motion.div className="h-full rounded-full" style={{ background: COLORS[i % COLORS.length] }}
                      initial={{ width: 0 }} animate={{ width: `${(d.value / maxVal) * 100}%` }}
                      transition={{ duration: 0.6, delay: i * 0.05 }} />
                  </div>
                </div>
              )
            })}
          </div>
        </motion.div>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Trust Equity */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Trust Equity Distribution</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trustEquityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {trustEquityData.map((entry, i) => (
                    <Cell key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* CLV Tier Distribution */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <h3 className="text-sm font-semibold text-white mb-4">CLV Tier Equity</h3>
          <div className="space-y-3">
            {[
              { name: 'Diamond', value: clvDist.diamond || 0, color: '#06B6D4', label: '≥₹100K' },
              { name: 'Platinum', value: clvDist.platinum || 0, color: '#8B5CF6', label: '₹50K–100K' },
              { name: 'Gold', value: clvDist.gold || 0, color: '#F59E0B', label: '₹20K–50K' },
              { name: 'Silver', value: clvDist.silver || 0, color: '#94A3B8', label: '₹5K–20K' },
              { name: 'Bronze', value: clvDist.bronze || 0, color: '#78716C', label: '<₹5K' },
            ].map((tier, i) => {
              const total = Object.values(clvDist as Record<string, number>).reduce((a, b) => a + b, 0) || 1
              const pct = ((tier.value / total) * 100).toFixed(1)
              return (
                <div key={tier.name}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full" style={{ background: tier.color }} />
                      <span className="text-xs" style={{ color: '#94A3B8' }}>{tier.name}</span>
                      <span className="text-[10px]" style={{ color: '#475569' }}>{tier.label}</span>
                    </div>
                    <span className="text-xs mono" style={{ color: '#CBD5E1' }}>{tier.value} ({pct}%)</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full" style={{ background: '#1E293B' }}>
                    <motion.div className="h-full rounded-full" style={{ background: tier.color }}
                      initial={{ width: 0 }} animate={{ width: `${Math.min(100, parseFloat(pct))}%` }}
                      transition={{ duration: 0.8, delay: i * 0.1 }} />
                  </div>
                </div>
              )
            })}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
