import { useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Users, DollarSign, TrendingUp, ShieldAlert, Heart, Activity,
  Zap, BarChart3, AlertTriangle, ArrowUpRight, ArrowDownRight, Megaphone,
  Eye, ShoppingCart, UserPlus, LogIn, Package, Search, Star, MessageSquare, RotateCcw
} from 'lucide-react'
import { AreaChart, Area, PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import api from '../../services/api'
import { useWsContext } from '../../layouts/AdminLayout'

/* ── Animated Counter ─────────────────────────────── */
function AnimatedValue({ value, prefix = '', suffix = '' }: { value: number; prefix?: string; suffix?: string }) {
  const [display, setDisplay] = useState(0)
  const ref = useRef<number>(0)

  useEffect(() => {
    const duration = 1200
    const start = ref.current
    const startTime = Date.now()
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = start + (value - start) * eased
      setDisplay(current)
      ref.current = current
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [value])

  return <span>{prefix}{typeof value === 'number' && value >= 1000 ? display.toLocaleString('en-IN', { maximumFractionDigits: 0 }) : display.toFixed(1)}{suffix}</span>
}

/* ── KPI Card ─────────────────────────────────────── */
function KPICard({ icon: Icon, label, value, prefix, suffix, trend, color, delay }: any) {
  return (
    <motion.div
      className="card p-5"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center"
             style={{ background: `${color}15` }}>
          <Icon size={18} style={{ color }} />
        </div>
        {trend && (
          <span className={`flex items-center gap-0.5 text-xs font-medium ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend > 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
      <div className="metric-value" style={{ color }}>
        <AnimatedValue value={value} prefix={prefix} suffix={suffix} />
      </div>
      <p className="text-xs mt-1" style={{ color: '#64748B' }}>{label}</p>
    </motion.div>
  )
}

/* ── Event Icon ───────────────────────────────────── */
function getEventConfig(eventType: string) {
  const configs: Record<string, { icon: any; color: string; label: string }> = {
    'PRODUCT_VIEW': { icon: Eye, color: '#8B5CF6', label: 'viewed' },
    'product_view': { icon: Eye, color: '#8B5CF6', label: 'viewed' },
    'ADD_TO_CART': { icon: ShoppingCart, color: '#F59E0B', label: 'added to cart' },
    'cart_add': { icon: ShoppingCart, color: '#F59E0B', label: 'added to cart' },
    'REMOVE_FROM_CART': { icon: ShoppingCart, color: '#6B7280', label: 'removed from cart' },
    'cart_remove': { icon: ShoppingCart, color: '#6B7280', label: 'removed from cart' },
    'PURCHASE_COMPLETED': { icon: DollarSign, color: '#10B981', label: 'purchased' },
    'purchase': { icon: DollarSign, color: '#10B981', label: 'purchased' },
    'USER_REGISTERED': { icon: UserPlus, color: '#10B981', label: 'registered' },
    'USER_LOGIN': { icon: LogIn, color: '#3B82F6', label: 'logged in' },
    'SUPPORT_TICKET_CREATED': { icon: MessageSquare, color: '#EF4444', label: 'submitted ticket' },
    'ticket_created': { icon: MessageSquare, color: '#EF4444', label: 'submitted ticket' },
    'SEARCH': { icon: Search, color: '#06B6D4', label: 'searched' },
    'search': { icon: Search, color: '#06B6D4', label: 'searched' },
    'ADD_TO_WISHLIST': { icon: Heart, color: '#EF4444', label: 'wishlisted' },
    'wishlist_add': { icon: Heart, color: '#EF4444', label: 'wishlisted' },
    'CHECKOUT_STARTED': { icon: Package, color: '#F97316', label: 'started checkout' },
    'REVIEW_SUBMITTED': { icon: Star, color: '#F59E0B', label: 'reviewed' },
    'REFUND_REQUESTED': { icon: RotateCcw, color: '#EF4444', label: 'requested refund' },
  }
  return configs[eventType] || { icon: Activity, color: '#64748B', label: eventType?.replace(/_/g, ' ').toLowerCase() || 'activity' }
}

/* ── Live Event Item ──────────────────────────────── */
function EventItem({ event, index, onClick }: { event: any; index: number; onClick: () => void }) {
  const config = getEventConfig(event.event_type)
  const Icon = config.icon

  return (
    <motion.button
      className="flex items-center gap-3 py-2.5 px-3 rounded-lg w-full text-left hover:bg-white/5 transition-colors"
      style={{ background: index % 2 === 0 ? 'rgba(255,255,255,0.02)' : 'transparent' }}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
      onClick={onClick}
    >
      <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${config.color}15` }}>
        <Icon size={14} style={{ color: config.color }} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-white truncate">
          <span className="font-medium">{event.customer_name || event.customer_id?.slice(0, 8)}</span>
          <span style={{ color: '#64748B' }}> {config.label} </span>
          {event.event_value && <span style={{ color: config.color }}>{event.event_value}</span>}
        </p>
      </div>
      <span className="text-[10px] mono flex-shrink-0" style={{ color: '#64748B' }}>
        {new Date(event.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
      </span>
    </motion.button>
  )
}

/* ── Dashboard ────────────────────────────────────── */
export default function Dashboard() {
  const navigate = useNavigate()
  const { events: wsEvents } = useWsContext()

  const { data: overview } = useQuery({
    queryKey: ['overview'],
    queryFn: () => api.get('/analytics/overview').then(r => r.data),
    refetchInterval: 10000,
  })

  const { data: churnDist } = useQuery({
    queryKey: ['churn-dist'],
    queryFn: () => api.get('/analytics/churn').then(r => r.data),
    refetchInterval: 30000,
  })

  const { data: recentEvents } = useQuery({
    queryKey: ['events'],
    queryFn: () => api.get('/events?limit=20').then(r => r.data),
  })

  // Merge WS events with DB events
  const allEvents = [...wsEvents, ...(recentEvents || [])].slice(0, 30)

  const churnData = [
    { name: 'Low', value: churnDist?.distribution?.low || 0, color: '#10B981' },
    { name: 'Medium', value: churnDist?.distribution?.medium || 0, color: '#F59E0B' },
    { name: 'High', value: churnDist?.distribution?.high || 0, color: '#F97316' },
    { name: 'Critical', value: churnDist?.distribution?.critical || 0, color: '#EF4444' },
  ]

  const trendData = overview?.revenue_trend || []

  const o = overview || {}

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Mission Control</h1>
          <p className="text-sm" style={{ color: '#64748B' }}>Real-time customer intelligence overview</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg" style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.15)' }}>
          <div className="live-indicator" />
          <span className="text-xs font-medium text-green-400">Live</span>
          <span className="text-[10px] text-green-400/60 ml-1">{wsEvents.length} events</span>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4 mb-6">
        <KPICard icon={Users} label="Total Customers" value={o.total_customers || 0} color="#3B82F6" trend={o.customer_trend} delay={0} />
        <KPICard icon={DollarSign} label="Total Revenue" value={o.total_revenue || 0} prefix="₹" color="#10B981" trend={o.revenue_trend_pct} delay={0.05} />
        <KPICard icon={TrendingUp} label="Retention Rate" value={o.retention_rate || 0} suffix="%" color="#8B5CF6" trend={o.retention_trend} delay={0.1} />
        <KPICard icon={ShieldAlert} label="Churn Risk" value={o.avg_churn_risk || 0} suffix="%" color="#EF4444" trend={o.churn_trend} delay={0.15} />
        <KPICard icon={Heart} label="Happiness" value={o.avg_happiness_score || 0} suffix="/100" color="#F59E0B" trend={o.happiness_trend} delay={0.2} />
        <KPICard icon={BarChart3} label="Avg CLV" value={o.avg_clv || 0} prefix="₹" color="#06B6D4" trend={o.clv_trend} delay={0.25} />
      </div>

      {/* Main Grid */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Revenue Trend */}
        <motion.div className="card p-5 lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Revenue Trend</h3>
            {o.revenue_trend_pct && <span className={`badge ${o.revenue_trend_pct > 0 ? 'badge-success' : 'badge-danger'}`}>{o.revenue_trend_pct > 0 ? '+' : ''}{o.revenue_trend_pct}%</span>}
          </div>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} formatter={(v: number) => [`₹${v.toLocaleString('en-IN')}`, 'Revenue']} />
                <Area type="monotone" dataKey="revenue" stroke="#3B82F6" fill="url(#revGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Churn Distribution */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Churn Risk Distribution</h3>
          <div className="h-40">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={churnData} cx="50%" cy="50%" innerRadius={35} outerRadius={60} paddingAngle={4} dataKey="value">
                  {churnData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {churnData.map(d => (
              <div key={d.name} className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                <span className="text-[11px]" style={{ color: '#94A3B8' }}>{d.name}: {d.value}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Live Events + Quick Stats */}
      <div className="grid lg:grid-cols-3 gap-5 mt-5">
        <motion.div className="card p-5 lg:col-span-2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Activity size={16} className="text-blue-400" />
              <h3 className="text-sm font-semibold text-white">Live Event Stream</h3>
            </div>
            <div className="flex items-center gap-1">
              <div className="live-indicator" />
              <span className="text-[10px] text-green-400 mono">{allEvents.length} events</span>
            </div>
          </div>
          <div className="space-y-0 max-h-72 overflow-y-auto">
            {allEvents.length > 0 ? (
              allEvents.map((e: any, i: number) => (
                <EventItem key={e.event_id || e.id || i} event={e} index={i}
                  onClick={() => e.customer_id && navigate(`/admin/customer360?id=${e.customer_id}`)}
                />
              ))
            ) : (
              <div className="text-center py-8">
                <p className="text-sm" style={{ color: '#64748B' }}>Waiting for customer activity...</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Quick Intelligence */}
        <motion.div className="card p-5 space-y-4" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}>
          <h3 className="text-sm font-semibold text-white">Intelligence Summary</h3>
          
          <div className="space-y-3">
            <div className="p-3 rounded-lg" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.12)' }}>
              <div className="flex items-center gap-2 mb-1">
                <AlertTriangle size={14} className="text-red-400" />
                <span className="text-xs font-semibold text-red-400">High Risk Customers</span>
              </div>
              <p className="text-2xl font-bold text-white mono">{o.high_risk_customers || 0}</p>
              <p className="text-[11px] mt-1" style={{ color: '#94A3B8' }}>Require immediate intervention</p>
            </div>

            <div className="p-3 rounded-lg" style={{ background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.12)' }}>
              <div className="flex items-center gap-2 mb-1">
                <DollarSign size={14} className="text-yellow-400" />
                <span className="text-xs font-semibold text-yellow-400">Revenue at Risk</span>
              </div>
              <p className="text-2xl font-bold text-white mono">₹{(o.revenue_at_risk || 0).toLocaleString('en-IN')}</p>
              <p className="text-[11px] mt-1" style={{ color: '#94A3B8' }}>From potential churn</p>
            </div>

            <div className="p-3 rounded-lg" style={{ background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.12)' }}>
              <div className="flex items-center gap-2 mb-1">
                <Megaphone size={14} className="text-blue-400" />
                <span className="text-xs font-semibold text-blue-400">Active Campaigns</span>
              </div>
              <p className="text-2xl font-bold text-white mono">{o.active_campaigns || 0}</p>
              <p className="text-[11px] mt-1" style={{ color: '#94A3B8' }}>Currently running</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
