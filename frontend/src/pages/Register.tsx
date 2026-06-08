import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { UserPlus, Zap } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'

export default function Register() {
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', password: '', city: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/auth/register', form)
      setAuth(data.access_token, data.user)
      navigate('/shop')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const update = (key: string, val: string) => setForm({ ...form, [key]: val })

  return (
    <div className="min-h-screen flex items-center justify-center"
         style={{ background: 'linear-gradient(135deg, #0B0F14 0%, #111827 50%, #0B0F14 100%)' }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="glass-strong rounded-2xl p-8 w-full max-w-md"
      >
        <div className="text-center mb-6">
          <motion.div
            className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4"
            style={{ background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)' }}
          >
            <Zap size={28} color="white" />
          </motion.div>
          <h1 className="text-2xl font-bold text-white">Create Account</h1>
          <p className="text-sm mt-1" style={{ color: '#94A3B8' }}>Join the OmniPulse experience</p>
        </div>

        <form onSubmit={handleRegister} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: '#94A3B8' }}>First Name</label>
              <input className="input" placeholder="Priya" value={form.first_name} onChange={(e) => update('first_name', e.target.value)} required />
            </div>
            <div>
              <label className="block text-xs font-medium mb-1" style={{ color: '#94A3B8' }}>Last Name</label>
              <input className="input" placeholder="Sharma" value={form.last_name} onChange={(e) => update('last_name', e.target.value)} required />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: '#94A3B8' }}>Email</label>
            <input type="email" className="input" placeholder="priya@email.com" value={form.email} onChange={(e) => update('email', e.target.value)} required />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: '#94A3B8' }}>Password</label>
            <input type="password" className="input" placeholder="••••••••" value={form.password} onChange={(e) => update('password', e.target.value)} required />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" style={{ color: '#94A3B8' }}>City</label>
            <input className="input" placeholder="Mumbai" value={form.city} onChange={(e) => update('city', e.target.value)} />
          </div>

          {error && <p className="text-sm text-red-400 bg-red-400/10 rounded-lg p-2 text-center">{error}</p>}

          <motion.button type="submit" className="btn-primary w-full flex items-center justify-center gap-2 py-3" whileTap={{ scale: 0.99 }} disabled={loading}>
            {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <><UserPlus size={18} />Create Account</>}
          </motion.button>
        </form>

        <p className="mt-4 text-center text-sm" style={{ color: '#64748B' }}>
          Already have an account? <Link to="/login" className="text-blue-400 hover:text-blue-300 font-medium">Sign in</Link>
        </p>
      </motion.div>
    </div>
  )
}
