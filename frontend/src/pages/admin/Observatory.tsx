import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Activity, Users, ShoppingCart, DollarSign, TrendingUp, Shield, Heart, AlertTriangle, Zap, BarChart3 } from 'lucide-react'
import { AreaChart, Area, BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from 'recharts'
import api from '../../services/api'

export default function Observatory() {
  const { data: overview } = useQuery({
    queryKey: ['overview'],
    queryFn: () => api.get('/analytics/overview').then(r => r.data),
    refetchInterval: 5000,
  })

  const { data: platform } = useQuery({
    queryKey: ['platform-intelligence'],
    queryFn: () => api.get('/ai/platform-intelligence').then(r => r.data),
    refetchInterval: 5000,
  })

  const { data: events } = useQuery({
    queryKey: ['events'],
    queryFn: () => api.get('/events?limit=20').then(r => r.data),
    refetchInterval: 3000,
  })

  const churnDist = platform?.churn_distribution || {}
  const trustDist = platform?.trust_distribution || {}
  const roi = platform?.roi || {}
  const revenueTrend = overview?.revenue_trend || []
  const eventList = Array.isArray(events) ? events : []

  const eventIcons: Record<string, string> = {
    'PRODUCT_VIEW': '👁️', 'SEARCH': '🔍', 'ADD_TO_CART': '🛒', 'REMOVE_FROM_CART': '🗑️',
    'PURCHASE_COMPLETED': '💰', 'CHECKOUT_STARTED': '🧾', 'ADD_TO_WISHLIST': '❤️',
    'REVIEW_SUBMITTED': '⭐', 'REFUND_REQUESTED': '↩️', 'LOGIN': '🔑',
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">Live Business Observatory</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>
        Real-time operational metrics — all live, no refresh needed
        <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px]"
              style={{ background: '#10B98120', color: '#10B981' }}>● LIVE</span>
      </p>

      {/* Top KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-3 mb-6">
        {[
          { icon: Users, label: 'Active Sessions', value: platform?.active_sessions || 0, color: '#10B981', sub: 'Live now' },
          { icon: DollarSign, label: 'Revenue', value: `₹${((overview?.total_revenue || 0) / 1000).toFixed(0)}K`, color: '#3B82F6', sub: 'Total' },
          { icon: ShoppingCart, label: 'Orders', value: overview?.total_orders || 0, color: '#8B5CF6', sub: 'Total' },
          { icon: AlertTriangle, label: 'Cart Abandonment', value: platform?.cart_abandonment_count || 0, color: '#F97316', sub: 'Abandoned carts' },
          { icon: Zap, label: 'Events (Recent)', value: platform?.recent_events_24h || 0, color: '#06B6D4', sub: `${(platform?.total_events || 0).toLocaleString()} total` },
        ].map((kpi, i) => (
          <motion.div key={i} className="card p-3" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
            <kpi.icon size={14} style={{ color: kpi.color }} className="mb-1.5" />
            <p className="text-xl font-bold mono text-white">{typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}</p>
            <p className="text-[10px]" style={{ color: '#64748B' }}>{kpi.label}</p>
            <p className="text-[9px]" style={{ color: kpi.color }}>{kpi.sub}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-5 gap-5 mb-6">
        {/* Score Gauges */}
        <motion.div className="card p-4 lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Platform Health</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: 'Avg Trust', value: overview?.avg_trust_score || 0, max: 100, color: '#8B5CF6' },
              { label: 'Avg Happiness', value: overview?.avg_happiness_score || 0, max: 100, color: '#EC4899' },
              { label: 'Churn Risk', value: overview?.avg_churn_risk || 0, max: 100, color: '#EF4444' },
              { label: 'Retention', value: overview?.retention_rate || 0, max: 100, color: '#10B981' },
            ].map((g, i) => (
              <div key={i} className="text-center">
                <div className="relative w-16 h-16 mx-auto mb-2">
                  <svg viewBox="0 0 36 36" className="w-full h-full">
                    <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none" stroke="#1E293B" strokeWidth="3" />
                    <motion.path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none" stroke={g.color} strokeWidth="3" strokeLinecap="round"
                      strokeDasharray={`${(g.value / g.max) * 100}, 100`}
                      initial={{ strokeDasharray: '0, 100' }}
                      animate={{ strokeDasharray: `${(g.value / g.max) * 100}, 100` }}
                      transition={{ duration: 1, delay: i * 0.15 }} />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xs mono font-bold text-white">{g.value.toFixed(0)}</span>
                  </div>
                </div>
                <p className="text-[10px]" style={{ color: '#64748B' }}>{g.label}</p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Revenue Trend */}
        <motion.div className="card p-4 lg:col-span-3" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <h3 className="text-sm font-semibold text-white mb-3">Revenue Trend</h3>
          <div className="h-44">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueTrend}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="date" tick={{ fill: '#64748B', fontSize: 9 }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 9 }} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 11 }}
                  formatter={(v: number) => [`₹${v.toLocaleString('en-IN')}`, 'Revenue']} />
                <Area type="monotone" dataKey="revenue" stroke="#3B82F6" fill="url(#revGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      <div className="grid lg:grid-cols-2 gap-5 mb-6">
        {/* Risk Distribution */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Churn Risk Distribution</h3>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[
                { name: 'Low', value: churnDist.low || 0, fill: '#10B981' },
                { name: 'Medium', value: churnDist.medium || 0, fill: '#F59E0B' },
                { name: 'High', value: churnDist.high || 0, fill: '#F97316' },
                { name: 'Critical', value: churnDist.critical || 0, fill: '#EF4444' },
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {[{ fill: '#10B981' }, { fill: '#F59E0B' }, { fill: '#F97316' }, { fill: '#EF4444' }].map((e, i) => (
                    <motion.rect key={i} fill={e.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Trust Distribution */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Trust Distribution</h3>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[
                { name: 'Excellent', value: trustDist.excellent || 0, fill: '#10B981' },
                { name: 'Good', value: trustDist.good || 0, fill: '#3B82F6' },
                { name: 'Fair', value: trustDist.fair || 0, fill: '#F59E0B' },
                { name: 'Poor', value: trustDist.poor || 0, fill: '#F97316' },
                { name: 'Critical', value: trustDist.critical || 0, fill: '#EF4444' },
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="name" tick={{ fill: '#64748B', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {[{ fill: '#10B981' }, { fill: '#3B82F6' }, { fill: '#F59E0B' }, { fill: '#F97316' }, { fill: '#EF4444' }].map((e, i) => (
                    <motion.rect key={i} fill={e.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Live Event Stream */}
      <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <Activity size={14} style={{ color: '#10B981' }} />
          Live Event Stream
          <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: '#10B98120', color: '#10B981' }}>
            {eventList.length} recent
          </span>
        </h3>
        <div className="space-y-1.5 max-h-72 overflow-y-auto">
          {eventList.slice(0, 15).map((ev: any, i: number) => (
            <motion.div key={ev.event_id || i}
              className="flex items-center gap-3 p-2 rounded-lg"
              style={{ background: 'rgba(255,255,255,0.02)' }}
              initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.03 }}>
              <span className="text-sm">{eventIcons[ev.event_type] || '📌'}</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white truncate">
                  <span className="font-medium">{ev.customer_name}</span>
                  <span style={{ color: '#64748B' }}> — </span>
                  <span style={{ color: '#94A3B8' }}>{(ev.event_type || '').replace(/_/g, ' ')}</span>
                </p>
                {ev.event_value && <p className="text-[10px] truncate" style={{ color: '#475569' }}>{ev.event_value}</p>}
              </div>
              <span className="text-[10px] mono" style={{ color: '#475569' }}>
                {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : ''}
              </span>
            </motion.div>
          ))}
          {eventList.length === 0 && <p className="text-xs text-center py-4" style={{ color: '#475569' }}>No events yet — waiting for customer activity</p>}
        </div>
      </motion.div>
    </div>
  )
}
