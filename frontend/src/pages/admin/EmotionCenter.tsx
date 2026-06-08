import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Heart, Smile, Meh, Frown, Angry, Sparkles } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts'
import api from '../../services/api'

const emotionConfig: Record<string, { icon: any; color: string }> = {
  happy: { icon: Smile, color: '#10B981' },
  excited: { icon: Sparkles, color: '#8B5CF6' },
  neutral: { icon: Meh, color: '#64748B' },
  frustrated: { icon: Frown, color: '#F59E0B' },
  angry: { icon: Angry, color: '#EF4444' },
}

export default function EmotionCenter() {
  const { data } = useQuery({
    queryKey: ['emotions'],
    queryFn: () => api.get('/analytics/emotions').then(r => r.data),
  })

  const dist = data?.emotion_distribution || {}
  const pieData = Object.entries(dist).map(([name, value]) => ({
    name, value: value as number, color: emotionConfig[name]?.color || '#64748B',
  }))

  const ticketSentiment = data?.ticket_sentiment || {}
  const barData = Object.entries(ticketSentiment).map(([name, value]) => ({
    name, count: value as number, fill: emotionConfig[name]?.color || '#64748B',
  }))

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">Emotion Intelligence Center</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>Customer emotion states and support ticket sentiment — from real database records</p>

      {/* Emotion KPIs */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        {Object.entries(emotionConfig).map(([emotion, config], i) => {
          const Icon = config.icon
          const profileCount = dist[emotion] || 0
          const ticketCount = ticketSentiment[emotion] || 0
          const totalCount = profileCount + ticketCount
          return (
            <motion.div key={emotion} className="card p-4 text-center" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
              <Icon size={20} style={{ color: config.color }} className="mx-auto mb-2" />
              <p className="text-xl font-bold mono text-white">{totalCount}</p>
              <p className="text-xs capitalize" style={{ color: '#64748B' }}>{emotion}</p>
              <p className="text-[9px] mt-0.5" style={{ color: '#475569' }}>
                {profileCount > 0 ? `${profileCount} profiles` : ''}
                {profileCount > 0 && ticketCount > 0 ? ' · ' : ''}
                {ticketCount > 0 ? `${ticketCount} tickets` : ''}
              </p>
            </motion.div>
          )
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        {/* Emotion Distribution */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <h3 className="text-sm font-semibold text-white mb-1">Customer Emotion State</h3>
          <p className="text-[10px] mb-3" style={{ color: '#64748B' }}>Source: customer_profiles.emotion</p>
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
          <div className="flex flex-wrap gap-3 justify-center mt-2">
            {pieData.map(d => (
              <div key={d.name} className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full" style={{ background: d.color }} />
                <span className="text-[11px] capitalize" style={{ color: '#94A3B8' }}>{d.name}: {d.value}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Ticket Sentiment */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <h3 className="text-sm font-semibold text-white mb-1">Support Ticket Sentiment</h3>
          <p className="text-[10px] mb-3" style={{ color: '#64748B' }}>Source: support_tickets.sentiment</p>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} layout="vertical">
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" tick={{ fill: '#94A3B8', fontSize: 12 }} width={80} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {barData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 p-3 rounded-lg" style={{ background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.1)' }}>
            <p className="text-xs" style={{ color: '#94A3B8' }}>
              <span className="font-medium text-red-400">{data?.open_tickets || 0} open tickets</span> requiring attention.
              Total tickets: {data?.total_tickets || 0}
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
