import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, TrendingDown, DollarSign, Users, Eye, ChevronRight } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'

export default function ChurnCenter() {
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({
    queryKey: ['churn-dist'],
    queryFn: () => api.get('/analytics/churn').then(r => r.data),
    refetchInterval: 5000,
  })

  const dist = data?.distribution || { low: 0, medium: 0, high: 0, critical: 0 }
  const totalCustomers = data?.total_customers || 0
  const totalAtRisk = data?.total_at_risk || 0
  const atRisk = data?.at_risk_customers || []

  const pieData = [
    { name: 'Low', value: dist.low, color: '#10B981' },
    { name: 'Medium', value: dist.medium, color: '#F59E0B' },
    { name: 'High', value: dist.high, color: '#F97316' },
    { name: 'Critical', value: dist.critical, color: '#EF4444' },
  ].filter(d => d.value > 0)

  const riskPct = totalCustomers > 0 ? ((totalAtRisk / totalCustomers) * 100).toFixed(1) : '0'

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">Real-Time Churn Prediction</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>
        Live churn risk — updates after every customer action
        <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px]"
              style={{ background: '#10B98120', color: '#10B981' }}>
          ● LIVE
        </span>
      </p>

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { icon: Users, label: 'Total Customers', value: totalCustomers, sub: 'Platform-wide', color: '#3B82F6' },
          { icon: AlertTriangle, label: 'At Risk', value: totalAtRisk, sub: `${riskPct}% of total`, color: '#EF4444' },
          { icon: TrendingDown, label: 'Critical', value: dist.critical, sub: 'Immediate action', color: '#EF4444' },
          { icon: DollarSign, label: 'High Risk', value: dist.high, sub: 'Intervention needed', color: '#F97316' },
        ].map((kpi, i) => (
          <motion.div key={i} className="card p-4" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
            <kpi.icon size={16} style={{ color: kpi.color }} className="mb-2" />
            <p className="text-2xl font-bold mono text-white">{kpi.value.toLocaleString()}</p>
            <p className="text-[10px]" style={{ color: '#64748B' }}>{kpi.label}</p>
            <p className="text-[9px] mt-0.5" style={{ color: kpi.color }}>{kpi.sub}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-5">
        {/* Donut Chart */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Risk Distribution</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={75} paddingAngle={3} dataKey="value">
                  {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {[
              { name: 'Low', value: dist.low, color: '#10B981' },
              { name: 'Medium', value: dist.medium, color: '#F59E0B' },
              { name: 'High', value: dist.high, color: '#F97316' },
              { name: 'Critical', value: dist.critical, color: '#EF4444' },
            ].map(d => (
              <div key={d.name} className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
                <span className="text-xs" style={{ color: '#94A3B8' }}>{d.name}: {d.value}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* At-Risk Customer List */}
        <motion.div className="card p-5 lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Highest Risk Customers</h3>
          {isLoading && <p className="text-xs" style={{color: '#64748B'}}>Loading…</p>}
          <div className="space-y-2 max-h-[420px] overflow-y-auto">
            {atRisk.map((c: any, i: number) => {
              const riskColor = c.churn_probability >= 0.8 ? '#EF4444' : c.churn_probability >= 0.6 ? '#F97316' : '#F59E0B'
              return (
                <motion.div
                  key={c.customer_id}
                  className="flex items-center gap-4 p-3 rounded-lg cursor-pointer hover:scale-[1.01] transition-transform"
                  style={{ background: 'rgba(255,255,255,0.02)' }}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04 }}
                  onClick={() => navigate(`/admin/customer360?id=${c.customer_id}`)}
                >
                  <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                       style={{ background: riskColor }}>
                    {c.name?.charAt(0) || '?'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{c.name}</p>
                    <p className="text-[10px]" style={{ color: '#64748B' }}>
                      CLV: ₹{(c.clv || 0).toLocaleString('en-IN')} · {c.emotion || 'neutral'}
                    </p>
                    <p className="text-[9px]" style={{ color: '#94A3B8' }}>
                      Trust: {c.trust_score ?? 0} · Eng: {c.engagement_score ?? 0} · 
                      Recency: {c.recency_days ?? 0}d · 
                      {c.open_tickets > 0 ? <span style={{ color: '#EF4444' }}>🎫 {c.open_tickets} open</span> : 'No tickets'}
                    </p>
                    {(c.total_revenue || 0) > 0 && (
                      <p className="text-[9px]" style={{ color: '#F59E0B' }}>
                        Revenue: ₹{(c.total_revenue || 0).toLocaleString('en-IN')} · 
                        At Risk: ₹{((c.total_revenue || 0) * c.churn_probability).toFixed(0)}
                      </p>
                    )}
                  </div>
                  <div className="w-24">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] mono font-bold" style={{ color: riskColor }}>
                        {(c.churn_probability * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full h-1.5 rounded-full" style={{ background: '#1E293B' }}>
                      <motion.div
                        className="h-full rounded-full"
                        style={{ background: riskColor }}
                        initial={{ width: 0 }}
                        animate={{ width: `${c.churn_probability * 100}%` }}
                        transition={{ duration: 0.8, delay: i * 0.04 }}
                      />
                    </div>
                  </div>
                  <span className="badge text-[9px]" style={{
                    background: `${riskColor}20`,
                    color: riskColor,
                  }}>{c.risk_level}</span>
                  <ChevronRight size={14} style={{ color: '#475569' }} />
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      </div>
    </div>
  )
}
