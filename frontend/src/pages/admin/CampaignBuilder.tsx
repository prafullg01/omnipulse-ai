import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Megaphone, Wand2, Plus, Play, BarChart3 } from 'lucide-react'
import api from '../../services/api'

export default function CampaignBuilder() {
  const [nlInput, setNlInput] = useState('')
  const [generatedCampaign, setGeneratedCampaign] = useState<any>(null)
  const [generating, setGenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [savedMsg, setSavedMsg] = useState('')

  const { data: campaigns, refetch: refetchCampaigns } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => api.get('/campaigns').then(r => r.data),
  })

  const generateFromNL = async () => {
    if (!nlInput.trim()) return
    setGenerating(true)
    setTimeout(() => {
      setGeneratedCampaign({
        campaign_name: nlInput.slice(0, 80),
        audience: { segment: 'at_risk', recency: '>30 days' },
        channel: 'email',
        offer: '20% discount on next purchase',
        discount_pct: 20,
        journey: [
          { id: '1', type: 'trigger', label: 'Customer Inactive 30+ Days' },
          { id: '2', type: 'action', label: 'Send Email: Personal Offer' },
          { id: '3', type: 'wait', label: 'Wait 3 Days' },
          { id: '4', type: 'condition', label: 'Opened Email?' },
          { id: '5', type: 'action', label: 'Yes: Send Follow-Up SMS' },
          { id: '6', type: 'action', label: 'No: Send Push Notification' },
        ],
      })
      setGenerating(false)
    }, 1500)
  }

  const saveCampaign = async () => {
    if (!generatedCampaign) return
    setSaving(true)
    try {
      await api.post('/campaigns', {
        campaign_name: generatedCampaign.campaign_name,
        description: `Auto-generated from: "${nlInput}"`,
        channel: generatedCampaign.channel,
        offer: generatedCampaign.offer,
        discount_pct: generatedCampaign.discount_pct || 0,
        audience: generatedCampaign.audience,
      })
      setSavedMsg('Campaign saved to database!')
      refetchCampaigns()
      setTimeout(() => setSavedMsg(''), 3000)
    } catch (e) {
      setSavedMsg('Save failed. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const launchCampaign = async (campaignId: string) => {
    await api.post(`/campaigns/${campaignId}/launch`)
    refetchCampaigns()
  }

  const statusColors: Record<string, string> = {
    active: '#10B981', completed: '#3B82F6', draft: '#64748B', paused: '#F59E0B',
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">Campaign Intelligence</h1>
      <p className="text-sm mb-6" style={{ color: '#64748B' }}>Natural language campaign builder & management</p>

      {/* NL Builder */}
      <motion.div className="card p-5 mb-6" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-2 mb-3">
          <Wand2 size={16} className="text-purple-400" />
          <h3 className="text-sm font-semibold text-white">Build Campaign from Natural Language</h3>
        </div>
        <div className="flex gap-3">
          <input
            className="input flex-1"
            placeholder="e.g., Re-engage customers inactive for 30 days with a personalized discount..."
            value={nlInput}
            onChange={e => setNlInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && generateFromNL()}
          />
          <motion.button
            className="btn-primary flex items-center gap-2 whitespace-nowrap"
            onClick={generateFromNL}
            whileTap={{ scale: 0.97 }}
            disabled={generating}
          >
            {generating ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Wand2 size={16} />}
            Generate
          </motion.button>
        </div>

        {/* Generated Campaign */}
        {generatedCampaign && (
          <motion.div className="mt-5 p-4 rounded-lg" style={{ background: 'rgba(139,92,246,0.05)', border: '1px solid rgba(139,92,246,0.1)' }}
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <h4 className="text-sm font-semibold text-purple-400 mb-3">Generated Journey Flow</h4>
            <div className="flex flex-wrap gap-2">
              {generatedCampaign.journey.map((step: any, i: number) => (
                <motion.div
                  key={step.id}
                  className="flex items-center gap-2"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.15 }}
                >
                  <div className="px-3 py-2 rounded-lg text-xs font-medium" style={{
                    background: step.type === 'trigger' ? 'rgba(59,130,246,0.1)' : step.type === 'condition' ? 'rgba(245,158,11,0.1)' : 'rgba(16,185,129,0.1)',
                    color: step.type === 'trigger' ? '#60A5FA' : step.type === 'condition' ? '#FBBF24' : '#34D399',
                    border: `1px solid ${step.type === 'trigger' ? 'rgba(59,130,246,0.2)' : step.type === 'condition' ? 'rgba(245,158,11,0.2)' : 'rgba(16,185,129,0.2)'}`,
                  }}>
                    {step.label}
                  </div>
                  {i < generatedCampaign.journey.length - 1 && (
                    <span style={{ color: '#64748B' }}>→</span>
                  )}
                </motion.div>
              ))}
            </div>
            <div className="mt-3 flex gap-3">
              <span className="badge badge-info">Channel: {generatedCampaign.channel}</span>
              <span className="badge badge-success">Offer: {generatedCampaign.offer}</span>
              <motion.button
                className="btn-primary flex items-center gap-2 text-xs px-3 py-1.5 ml-auto"
                onClick={saveCampaign}
                disabled={saving}
                whileTap={{ scale: 0.97 }}
              >
                {saving ? <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Plus size={13} />}
                {saving ? 'Saving...' : 'Save to Database'}
              </motion.button>
            </div>
            {savedMsg && (
              <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-xs mt-2 text-green-400">{savedMsg}</motion.p>
            )}
          </motion.div>
        )}
      </motion.div>

      {/* Campaign List */}
      <motion.div className="card p-5" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white">Active Campaigns</h3>
          <span className="badge badge-info">{(campaigns || []).length} total</span>
        </div>
        <div className="space-y-2">
          {(campaigns || []).map((c: any, i: number) => (
            <motion.div
              key={c.campaign_id}
              className="flex items-center gap-4 p-3 rounded-lg"
              style={{ background: 'rgba(255,255,255,0.02)' }}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Megaphone size={16} style={{ color: statusColors[c.status] || '#64748B' }} />
              <div className="flex-1">
                <p className="text-sm font-medium text-white">{c.campaign_name}</p>
                <p className="text-[11px]" style={{ color: '#64748B' }}>{c.channel} · {c.offer}</p>
              </div>
              <span className="badge text-[9px]" style={{
                background: `${statusColors[c.status]}20`,
                color: statusColors[c.status],
              }}>{c.status}</span>
              {c.status === 'draft' && (
                <button
                  onClick={() => launchCampaign(c.campaign_id)}
                  className="flex items-center gap-1 text-[10px] text-green-400 hover:text-green-300 px-2 py-1 rounded bg-green-500/10 border border-green-500/20 transition-colors"
                >
                  <Play size={10} />
                  Launch
                </button>
              )}
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
