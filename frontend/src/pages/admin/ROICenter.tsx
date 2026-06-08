import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { DollarSign, TrendingUp, Shield, Percent, BarChart3, Target, Info, AlertTriangle } from 'lucide-react'
import { BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, Cell } from 'recharts'
import api from '../../services/api'
import { useState } from 'react'

function AttributionBadge({ confidence }: { confidence?: string }) {
  const color = confidence === 'High' ? '#10B981' : confidence === 'Medium' ? '#F59E0B' : '#EF4444'
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-medium"
          style={{ background: `${color}15`, color, border: `1px solid ${color}30` }}>
      {confidence || 'Medium'} Confidence
    </span>
  )
}

function InfoTooltip({ text }: { text: string }) {
  const [show, setShow] = useState(false)
  return (
    <span className="relative inline-block ml-1">
      <Info size={11} className="cursor-help opacity-50 hover:opacity-100 transition-opacity"
            style={{ color: '#64748B' }}
            onMouseEnter={() => setShow(true)}
            onMouseLeave={() => setShow(false)} />
      {show && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-56 p-2.5 rounded-lg text-[10px] leading-relaxed"
          style={{ background: '#1E293B', border: '1px solid #374151', color: '#94A3B8', boxShadow: '0 8px 32px rgba(0,0,0,0.4)' }}>
          {text}
          <div className="absolute top-full left-1/2 -translate-x-1/2 w-2 h-2 rotate-45"
               style={{ background: '#1E293B', border: '1px solid #374151', borderTop: 'none', borderLeft: 'none' }} />
        </motion.div>
      )}
    </span>
  )
}

export default function ROICenter() {
  const { data } = useQuery({
    queryKey: ['roi'],
    queryFn: () => api.get('/analytics/roi').then(r => r.data),
    refetchInterval: 8000,
  })

  const fmt = (v: number) => `₹${(v / 1000).toFixed(0)}K`
  const attribution = data?.attribution || {}

  const waterfall = data?.waterfall_data || []
  const waterfallColors = ['#3B82F6', '#10B981', '#8B5CF6', '#EF4444', '#F59E0B']
  const monthly = data?.monthly_revenue || []
  const campaigns = data?.campaign_comparison || []

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">ROI Attribution Center</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>
        Revenue attribution — Campaign → Click → Purchase → Revenue
        <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px]"
              style={{ background: '#10B98120', color: '#10B981' }}>● LIVE</span>
      </p>

      {/* KPI Row */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
        {[
          {
            icon: DollarSign,
            label: 'Total Revenue',
            value: fmt(data?.total_revenue || 0),
            color: '#3B82F6',
            confidence: 'High',
            tooltip: 'Direct SUM of all delivered orders — 100% database-verified'
          },
          {
            icon: TrendingUp,
            label: 'Direct Conversions',
            value: fmt(data?.campaign_revenue || 0),
            color: '#10B981',
            confidence: attribution.confidence || 'Medium',
            tooltip: `${attribution.campaign_revenue_note || 'Campaign revenue from confirmed conversions'}. Match rate: ${attribution.match_rate || '~35'}%`
          },
          {
            icon: Shield,
            label: 'Revenue Protected',
            value: fmt(data?.revenue_protected || 0),
            color: '#8B5CF6',
            confidence: 'High',
            tooltip: 'Revenue from customers who received churn rescue or retention interventions via NBA engine'
          },
          {
            icon: Target,
            label: 'Revenue At Risk',
            value: fmt(data?.revenue_at_risk || 0),
            color: '#EF4444',
            confidence: 'High',
            tooltip: 'Historical orders from high-risk (>70% churn) customers. If zero, all high-risk customers are non-purchasers'
          },
          {
            icon: Percent,
            label: 'Campaign ROI',
            value: `${(data?.campaign_roi || 0).toFixed(0)}%`,
            color: '#F59E0B',
            confidence: attribution.confidence || 'Medium',
            tooltip: 'Formula: ((campaign_revenue - campaign_cost) / campaign_cost) × 100'
          },
          {
            icon: BarChart3,
            label: 'Conversion Rate',
            value: `${(data?.conversion_rate || 0).toFixed(1)}%`,
            color: '#06B6D4',
            confidence: 'High',
            tooltip: 'Confirmed conversions from campaign_responses / total campaign sends'
          },
        ].map((kpi, i) => (
          <motion.div key={i} className="card p-3 text-center" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
            <kpi.icon size={14} className="mx-auto mb-1" style={{ color: kpi.color }} />
            <p className="text-lg font-bold mono text-white">{kpi.value}</p>
            <p className="text-[9px] flex items-center justify-center gap-0.5" style={{ color: '#64748B' }}>
              {kpi.label}
              <InfoTooltip text={kpi.tooltip} />
            </p>
            {kpi.confidence && (
              <div className="mt-1">
                <AttributionBadge confidence={kpi.confidence} />
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Attribution Notice */}
      {attribution.method && (
        <motion.div
          className="mb-5 p-3 rounded-xl flex items-start gap-3"
          style={{ background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)' }}
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
        >
          <AlertTriangle size={14} className="mt-0.5 flex-shrink-0" style={{ color: '#F59E0B' }} />
          <div>
            <p className="text-xs font-medium" style={{ color: '#F59E0B' }}>Attribution Notice</p>
            <p className="text-[11px] mt-0.5" style={{ color: '#94A3B8' }}>
              Campaign revenue shows <strong style={{ color: '#CBD5E1' }}>confirmed direct conversions only</strong> ({attribution.match_rate || '~35'}% match rate).
              Actual campaign influence may be higher but cannot be directly measured due to customer ID segmentation across data sources.
            </p>
          </div>
        </motion.div>
      )}

      <div className="grid lg:grid-cols-2 gap-5 mb-6">
        {/* Revenue Waterfall */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Revenue Waterfall</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={waterfall}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="stage" tick={{ fill: '#64748B', fontSize: 9 }} angle={-15} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }}
                  tickFormatter={(v: number) => `₹${(v / 1000).toFixed(0)}K`} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`₹${v.toLocaleString('en-IN')}`, 'Amount']} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {waterfall.map((_: any, i: number) => (
                    <Cell key={i} fill={waterfallColors[i % waterfallColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Monthly Revenue Trend */}
        <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <h3 className="text-sm font-semibold text-white mb-4">Monthly Revenue vs Protected</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                <XAxis dataKey="month" tick={{ fill: '#64748B', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748B', fontSize: 10 }}
                  tickFormatter={(v: number) => `₹${(v / 1000).toFixed(0)}K`} />
                <Tooltip contentStyle={{ background: '#1E293B', border: '1px solid #374151', borderRadius: 8, fontSize: 12 }}
                  formatter={(v: number) => [`₹${v.toLocaleString('en-IN')}`, '']} />
                <Bar dataKey="revenue" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Revenue" />
                <Bar dataKey="protected" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="Protected" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Attribution Summary */}
      <motion.div className="card p-5 mb-6" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <h3 className="text-sm font-semibold text-white mb-4">Attribution Path</h3>
        <div className="flex items-center justify-center gap-2 flex-wrap">
          {[
            { label: 'Campaign', value: data?.total_campaigns || 0, color: '#3B82F6' },
            { label: '→', color: '#475569' },
            { label: 'Sends', value: data?.total_campaign_sends || 0, color: '#8B5CF6' },
            { label: '→', color: '#475569' },
            { label: 'Influenced', value: data?.campaign_influenced_customers || 0, color: '#06B6D4' },
            { label: '→', color: '#475569' },
            { label: 'Confirmed', value: fmt(data?.campaign_revenue || 0), color: '#10B981' },
          ].map((step, i) => (
            step.value !== undefined ? (
              <div key={i} className="text-center px-4 py-2 rounded-lg" style={{ background: `${step.color}10`, border: `1px solid ${step.color}30` }}>
                <p className="text-lg font-bold mono" style={{ color: step.color }}>{step.value}</p>
                <p className="text-[9px]" style={{ color: '#64748B' }}>{step.label}</p>
              </div>
            ) : (
              <span key={i} className="text-lg" style={{ color: step.color }}>{step.label}</span>
            )
          ))}
        </div>
      </motion.div>

      {/* Campaign Performance Table */}
      <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}>
        <h3 className="text-sm font-semibold text-white mb-4">Campaign ROI Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr style={{ color: '#64748B' }}>
                <th className="text-left py-2 px-3">Campaign</th>
                <th className="text-right py-2 px-3">Sends</th>
                <th className="text-right py-2 px-3">Open Rate</th>
                <th className="text-right py-2 px-3">Click Rate</th>
                <th className="text-right py-2 px-3">Conv. Rate</th>
                <th className="text-right py-2 px-3">Revenue</th>
                <th className="text-right py-2 px-3">ROI</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((c: any, i: number) => (
                <motion.tr key={i} className="border-t" style={{ borderColor: '#1E293B' }}
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }}>
                  <td className="py-2 px-3 text-white font-medium">{c.name}</td>
                  <td className="py-2 px-3 text-right mono" style={{ color: '#94A3B8' }}>{c.sends}</td>
                  <td className="py-2 px-3 text-right mono" style={{ color: '#3B82F6' }}>{c.open_rate}%</td>
                  <td className="py-2 px-3 text-right mono" style={{ color: '#8B5CF6' }}>{c.click_rate}%</td>
                  <td className="py-2 px-3 text-right mono" style={{ color: '#10B981' }}>{c.conversion_rate}%</td>
                  <td className="py-2 px-3 text-right mono" style={{ color: '#F59E0B' }}>₹{(c.revenue || 0).toLocaleString('en-IN')}</td>
                  <td className="py-2 px-3 text-right mono font-bold" style={{ color: c.roi > 0 ? '#10B981' : '#EF4444' }}>{c.roi}%</td>
                </motion.tr>
              ))}
              {campaigns.length === 0 && (
                <tr><td colSpan={7} className="py-4 text-center" style={{ color: '#475569' }}>No campaign data</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  )
}
