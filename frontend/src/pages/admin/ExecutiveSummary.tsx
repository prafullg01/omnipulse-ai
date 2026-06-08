import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Brain, TrendingUp, AlertTriangle, Shield, Heart, Target, DollarSign, Users, Zap, Info } from 'lucide-react'
import { BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts'
import api from '../../services/api'
import { useState } from 'react'

function MetricTooltip({ text }: { text: string }) {
  const [show, setShow] = useState(false)
  return (
    <span className="relative inline-block ml-0.5">
      <Info size={10} className="cursor-help opacity-40 hover:opacity-100 transition-opacity"
            style={{ color: '#64748B' }}
            onMouseEnter={() => setShow(true)}
            onMouseLeave={() => setShow(false)} />
      {show && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-52 p-2 rounded-lg text-[10px] leading-relaxed"
          style={{ background: '#1E293B', border: '1px solid #374151', color: '#94A3B8', boxShadow: '0 8px 32px rgba(0,0,0,0.4)' }}>
          {text}
        </motion.div>
      )}
    </span>
  )
}

export default function ExecutiveSummary() {
  const { data: exec } = useQuery({
    queryKey: ['executive-summary'],
    queryFn: () => api.get('/ai/executive-summary').then(r => r.data),
    refetchInterval: 8000,
  })

  const { data: platform } = useQuery({
    queryKey: ['platform-intelligence'],
    queryFn: () => api.get('/ai/platform-intelligence').then(r => r.data),
    refetchInterval: 8000,
  })

  const metrics = exec?.metrics || {}
  const highlights = exec?.highlights || []
  const risks = exec?.risks || []
  const recommendations = exec?.recommendations || []

  const churnDist = platform?.churn_distribution || {}
  const trustDist = platform?.trust_distribution || {}
  const clvDist = platform?.clv_distribution || {}

  const churnChartData = [
    { name: 'Low', value: churnDist.low || 0, fill: '#10B981' },
    { name: 'Medium', value: churnDist.medium || 0, fill: '#F59E0B' },
    { name: 'High', value: churnDist.high || 0, fill: '#F97316' },
    { name: 'Critical', value: churnDist.critical || 0, fill: '#EF4444' },
  ]

  const trustChartData = [
    { name: 'Excellent', value: trustDist.excellent || 0, fill: '#10B981' },
    { name: 'Good', value: trustDist.good || 0, fill: '#3B82F6' },
    { name: 'Fair', value: trustDist.fair || 0, fill: '#F59E0B' },
    { name: 'Poor', value: trustDist.poor || 0, fill: '#F97316' },
    { name: 'Critical', value: trustDist.critical || 0, fill: '#EF4444' },
  ]

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">Executive Intelligence</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>
        Live platform briefing — generated from real-time data
        <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px]"
              style={{ background: '#10B98120', color: '#10B981' }}>● LIVE</span>
      </p>

      {/* Top KPIs */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        {[
          { icon: Users, label: 'Customers', value: (metrics.customers || platform?.total_customers || 0).toLocaleString(), color: '#3B82F6', tooltip: 'Total registered customers (role=customer)' },
          { icon: DollarSign, label: 'Revenue', value: `₹${((metrics.revenue || platform?.total_revenue || 0) / 1000).toFixed(0)}K`, color: '#10B981', tooltip: 'Total delivered order revenue — SUM(orders.total_amount)' },
          { icon: AlertTriangle, label: 'High Risk', value: metrics.high_risk || (churnDist.high || 0) + (churnDist.critical || 0), color: '#EF4444', sub: '> 70% churn', tooltip: 'Customers exceeding 70% churn probability threshold' },
          { icon: Shield, label: 'Avg Trust', value: `${(metrics.avg_trust || 0).toFixed(0)}`, color: '#8B5CF6', sub: '/ 100', tooltip: 'Average trust score across all customer profiles' },
          { icon: Heart, label: 'Happiness', value: `${(metrics.avg_happiness || 0).toFixed(0)}`, color: '#EC4899', sub: '/ 100', tooltip: 'Average happiness score from customer profiles' },
          { icon: Zap, label: 'Campaigns', value: metrics.active_campaigns || 0, color: '#F59E0B', sub: 'active', tooltip: 'Currently active marketing campaigns' },
        ].map((kpi, i) => (
          <motion.div key={i} className="card p-3 text-center" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
            <kpi.icon size={14} className="mx-auto mb-1" style={{ color: kpi.color }} />
            <p className="text-lg font-bold mono text-white">{kpi.value}</p>
            <p className="text-[9px] flex items-center justify-center gap-0.5" style={{ color: '#64748B' }}>
              {kpi.label}
              {kpi.tooltip && <MetricTooltip text={kpi.tooltip} />}
            </p>
            {kpi.sub && <p className="text-[8px] mt-0.5" style={{ color: '#475569' }}>{kpi.sub}</p>}
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-5 mb-6">
        {/* Executive Briefing */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <div className="flex items-center gap-2 mb-4">
            <Brain size={16} style={{ color: '#8B5CF6' }} />
            <h3 className="text-sm font-semibold text-white">Executive Briefing</h3>
          </div>
          <div className="prose prose-sm prose-invert max-w-none">
            <p className="text-xs leading-relaxed whitespace-pre-wrap" style={{ color: '#CBD5E1' }}>
              {exec?.summary || 'Loading executive briefing...'}
            </p>
          </div>
        </motion.div>

        {/* Highlights + Risks */}
        <div className="space-y-5">
          <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <TrendingUp size={14} style={{ color: '#10B981' }} /> Highlights
            </h3>
            <div className="space-y-2">
              {highlights.map((h: string, i: number) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-[10px] mt-0.5" style={{ color: '#10B981' }}>●</span>
                  <p className="text-xs" style={{ color: '#94A3B8' }}>{h}</p>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <AlertTriangle size={14} style={{ color: '#EF4444' }} /> Risks
            </h3>
            <div className="space-y-2">
              {risks.map((r: string, i: number) => (
                <div key={i} className="flex items-start gap-2">
                  <span className="text-[10px] mt-0.5" style={{ color: '#EF4444' }}>▲</span>
                  <p className="text-xs" style={{ color: '#94A3B8' }}>{r}</p>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-5 mb-6">
        {/* Churn Distribution Chart */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Churn Risk Distribution</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={churnChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {churnChartData.map((entry, i) => (
                    <motion.rect key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Trust Distribution Chart */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Trust Score Distribution</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trustChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {trustChartData.map((entry, i) => (
                    <motion.rect key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Recommendations */}
      <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
        <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Target size={14} style={{ color: '#3B82F6' }} /> AI Recommendations
        </h3>
        <div className="grid sm:grid-cols-2 gap-3">
          {recommendations.map((r: string, i: number) => (
            <div key={i} className="p-3 rounded-lg flex items-start gap-3" style={{ background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.15)' }}>
              <span className="text-sm font-bold mono" style={{ color: '#3B82F6' }}>{i + 1}</span>
              <p className="text-xs" style={{ color: '#94A3B8' }}>{r}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
