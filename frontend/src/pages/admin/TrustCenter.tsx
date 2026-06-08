import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Shield, TrendingUp, TrendingDown, AlertTriangle, ChevronRight } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts'
import { useNavigate } from 'react-router-dom'
import api from '../../services/api'

export default function TrustCenter() {
  const navigate = useNavigate()
  const { data } = useQuery({
    queryKey: ['trust'],
    queryFn: () => api.get('/analytics/trust').then(r => r.data),
    refetchInterval: 5000,
  })

  const avgTrust = data?.avg_trust || 50
  const dist = data?.distribution || { low: 0, medium: 0, high: 0 }
  const drivers = data?.trust_drivers || []
  const trend = data?.trust_trend || []
  const lowTrust = data?.low_trust_customers || []

  const pieData = [
    { name: 'High Trust', value: dist.high, color: '#10B981' },
    { name: 'Medium', value: dist.medium, color: '#F59E0B' },
    { name: 'Low Trust', value: dist.low, color: '#EF4444' },
  ].filter(d => d.value > 0)

  const trustColor = avgTrust >= 70 ? '#10B981' : avgTrust >= 45 ? '#F59E0B' : '#EF4444'
  const trustLevel = avgTrust >= 70 ? 'Excellent' : avgTrust >= 45 ? 'Fair' : 'Critical'

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">Real-Time Trust Center</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>
        Trust scores update after every customer interaction
        <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px]"
              style={{ background: '#10B98120', color: '#10B981' }}>● LIVE</span>
      </p>

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { icon: Shield, label: 'Avg Trust Score', value: `${avgTrust.toFixed(0)}/100`, sub: trustLevel, color: trustColor },
          { icon: TrendingUp, label: 'High Trust', value: dist.high, sub: 'Score ≥ 80', color: '#10B981' },
          { icon: TrendingDown, label: 'Low Trust', value: dist.low, sub: 'Score < 50', color: '#EF4444' },
          { icon: AlertTriangle, label: 'Total Customers', value: data?.total_customers || 0, sub: 'Platform-wide', color: '#3B82F6' },
        ].map((kpi, i) => (
          <motion.div key={i} className="card p-4" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
            <kpi.icon size={16} style={{ color: kpi.color }} className="mb-2" />
            <p className="text-2xl font-bold mono text-white">{typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}</p>
            <p className="text-[10px]" style={{ color: '#64748B' }}>{kpi.label}</p>
            <p className="text-[9px] mt-0.5" style={{ color: kpi.color }}>{kpi.sub}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-5 mb-6">
        {/* Trust Distribution */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Trust Distribution</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={3} dataKey="value">
                  {pieData.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-1.5 mt-2">
            {pieData.map(d => (
              <div key={d.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
                  <span className="text-xs" style={{ color: '#94A3B8' }}>{d.name}</span>
                </div>
                <span className="text-xs mono font-medium" style={{ color: d.color }}>{d.value}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Trust Drivers */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Trust Drivers</h3>
          <div className="space-y-3">
            {drivers.map((d: any, i: number) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs" style={{ color: '#94A3B8' }}>{d.label}</span>
                  <span className="text-xs mono font-medium" style={{ color: d.color }}>{d.value.toFixed(1)}%</span>
                </div>
                <div className="w-full h-1.5 rounded-full" style={{ background: '#1E293B' }}>
                  <motion.div className="h-full rounded-full" style={{ background: d.color }}
                    initial={{ width: 0 }} animate={{ width: `${Math.min(d.value, 100)}%` }}
                    transition={{ duration: 0.8, delay: i * 0.1 }} />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Trust Trend */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Trust Trend</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend.slice(-14)}>
                <defs>
                  <linearGradient id="trustGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 10 }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#64748B', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
                <Area type="monotone" dataKey="trust" stroke="#3B82F6" fill="url(#trustGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Low Trust Customers */}
      <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
        <h3 className="text-sm font-semibold text-white mb-4">Low Trust Customers — Intervention Required</h3>
        <div className="space-y-2 max-h-72 overflow-y-auto">
          {lowTrust.map((c: any, i: number) => (
            <motion.div key={c.customer_id}
              className="flex items-center gap-4 p-3 rounded-lg cursor-pointer hover:scale-[1.01] transition-transform"
              style={{ background: 'rgba(255,255,255,0.02)' }}
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.04 }}
              onClick={() => navigate(`/admin/customer360?id=${c.customer_id}`)}
            >
              <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                   style={{ background: c.trust_score < 30 ? '#EF4444' : '#F59E0B' }}>
                {c.name?.charAt(0)}
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-white">{c.name}</p>
                <p className="text-[11px]" style={{ color: '#64748B' }}>Churn: {(c.churn_probability * 100).toFixed(0)}%</p>
              </div>
              <div className="w-20">
                <p className="text-xs mono font-bold" style={{ color: c.trust_score < 30 ? '#EF4444' : '#F59E0B' }}>
                  {c.trust_score.toFixed(0)}/100
                </p>
                <div className="w-full h-1 rounded-full mt-1" style={{ background: '#1E293B' }}>
                  <div className="h-full rounded-full" style={{ background: c.trust_score < 30 ? '#EF4444' : '#F59E0B', width: `${c.trust_score}%` }} />
                </div>
              </div>
              <ChevronRight size={14} style={{ color: '#475569' }} />
            </motion.div>
          ))}
          {lowTrust.length === 0 && <p className="text-xs text-center py-4" style={{ color: '#475569' }}>No low-trust customers detected</p>}
        </div>
      </motion.div>
    </div>
  )
}
