/**
 * ADMIN LAYOUT — Real-Time Intelligence Command Center
 * =====================================================
 * 
 * Features:
 * - Shared WebSocket connection across all admin pages
 * - Toast notification system for every customer event
 * - Clickable notifications → Customer 360 deep-link
 * - Bell icon with unread count and dropdown
 * - Auto-dismiss after 6 seconds
 */

import { useState, useEffect, useRef, useCallback, createContext, useContext } from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuthStore } from '../store/authStore'
import { useQueryClient } from '@tanstack/react-query'
import {
  Zap, LayoutDashboard, Users, AlertTriangle, Heart, Target,
  Megaphone, GitBranch, LogOut, Search, Bell, Activity,
  Shield, DollarSign, Scale, FileText, Bot, PlayCircle,
  MonitorDot, Gauge, ChevronDown, X, ShoppingCart, Eye,
  UserPlus, LogIn, Package, MessageSquare, RotateCcw, Star
} from 'lucide-react'

/* ── WebSocket Context ────────────────── */
interface WsEvent {
  id: string
  type: string
  event_type: string
  customer_id: string
  customer_name: string
  event_value: string
  message: string
  timestamp: string
  metadata: Record<string, any>
}

interface WsContextType {
  events: WsEvent[]
  notifications: WsEvent[]
  unreadCount: number
  clearUnread: () => void
  dismissNotification: (id: string) => void
}

const WsContext = createContext<WsContextType>({
  events: [],
  notifications: [],
  unreadCount: 0,
  clearUnread: () => {},
  dismissNotification: () => {},
})

export const useWsContext = () => useContext(WsContext)

/* ── Event Icon Map ──────────────────── */
function getEventIcon(eventType: string) {
  const map: Record<string, { icon: any; color: string; bg: string }> = {
    'USER_REGISTERED': { icon: UserPlus, color: '#10B981', bg: 'rgba(16,185,129,0.12)' },
    'USER_LOGIN': { icon: LogIn, color: '#3B82F6', bg: 'rgba(59,130,246,0.12)' },
    'USER_LOGOUT': { icon: LogOut, color: '#64748B', bg: 'rgba(100,116,139,0.12)' },
    'PRODUCT_VIEW': { icon: Eye, color: '#8B5CF6', bg: 'rgba(139,92,246,0.12)' },
    'ADD_TO_CART': { icon: ShoppingCart, color: '#F59E0B', bg: 'rgba(245,158,11,0.12)' },
    'REMOVE_FROM_CART': { icon: ShoppingCart, color: '#6B7280', bg: 'rgba(107,114,128,0.12)' },
    'ADD_TO_WISHLIST': { icon: Heart, color: '#EF4444', bg: 'rgba(239,68,68,0.12)' },
    'REMOVE_FROM_WISHLIST': { icon: Heart, color: '#6B7280', bg: 'rgba(107,114,128,0.12)' },
    'SEARCH': { icon: Search, color: '#06B6D4', bg: 'rgba(6,182,212,0.12)' },
    'CHECKOUT_STARTED': { icon: Package, color: '#F97316', bg: 'rgba(249,115,22,0.12)' },
    'PURCHASE_COMPLETED': { icon: DollarSign, color: '#10B981', bg: 'rgba(16,185,129,0.12)' },
    'SUPPORT_TICKET_CREATED': { icon: MessageSquare, color: '#EF4444', bg: 'rgba(239,68,68,0.12)' },
    'REVIEW_SUBMITTED': { icon: Star, color: '#F59E0B', bg: 'rgba(245,158,11,0.12)' },
    'REFUND_REQUESTED': { icon: RotateCcw, color: '#EF4444', bg: 'rgba(239,68,68,0.12)' },
  }
  return map[eventType] || { icon: Activity, color: '#64748B', bg: 'rgba(100,116,139,0.12)' }
}

/* ── Toast Notification ──────────────── */
function LiveToast({ notification, onDismiss, onViewCustomer }: {
  notification: WsEvent; onDismiss: () => void; onViewCustomer: () => void
}) {
  const { icon: Icon, color, bg } = getEventIcon(notification.event_type)

  useEffect(() => {
    const timer = setTimeout(onDismiss, 6000)
    return () => clearTimeout(timer)
  }, [onDismiss])

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: 400, scale: 0.8 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 400, scale: 0.8 }}
      transition={{ type: 'spring', damping: 25, stiffness: 300 }}
      className="w-96 rounded-xl overflow-hidden shadow-2xl border border-slate-700/50"
      style={{ background: 'rgba(15, 23, 42, 0.95)', backdropFilter: 'blur(20px)' }}
    >
      {/* Progress bar */}
      <motion.div className="h-0.5" style={{ background: color }} initial={{ width: '100%' }}
        animate={{ width: '0%' }} transition={{ duration: 6, ease: 'linear' }} />
      
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: bg }}>
            <Icon size={20} style={{ color }} />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-white font-medium leading-tight">{notification.message || `${notification.customer_name} — ${notification.event_type.replace(/_/g, ' ')}`}</p>
            {notification.event_value && notification.event_type !== notification.event_value && (
              <p className="text-xs mt-0.5 truncate" style={{ color }}>{notification.event_value}</p>
            )}
            <p className="text-[10px] text-slate-500 mt-1">
              {new Date(notification.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </p>
          </div>
          <button onClick={onDismiss} className="text-slate-600 hover:text-slate-400 transition flex-shrink-0">
            <X size={14} />
          </button>
        </div>
        <button onClick={onViewCustomer}
          className="mt-3 w-full py-1.5 rounded-lg text-[11px] font-medium text-blue-400 hover:text-white hover:bg-blue-600/20 transition text-center border border-blue-500/20"
        >
          View Customer 360 →
        </button>
      </div>
    </motion.div>
  )
}

/* ── Notification Dropdown ───────────── */
function NotificationDropdown({ notifications, onViewCustomer, onClear }: {
  notifications: WsEvent[]; onViewCustomer: (id: string) => void; onClear: () => void
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      className="absolute right-0 top-full mt-2 w-96 rounded-xl border border-slate-700/50 shadow-2xl overflow-hidden z-[200]"
      style={{ background: 'rgba(15, 23, 42, 0.98)', backdropFilter: 'blur(20px)' }}
    >
      <div className="p-3 border-b border-slate-800 flex items-center justify-between">
        <span className="text-sm font-semibold text-white">Notifications</span>
        <button onClick={onClear} className="text-[10px] text-blue-400 hover:text-blue-300">Clear all</button>
      </div>
      <div className="max-h-80 overflow-y-auto">
        {notifications.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-sm">No notifications yet</div>
        ) : notifications.slice(0, 20).map(n => {
          const { icon: Icon, color, bg } = getEventIcon(n.event_type)
          return (
            <button key={n.id} onClick={() => onViewCustomer(n.customer_id)}
              className="w-full flex items-start gap-3 p-3 hover:bg-slate-800/50 transition text-left"
            >
              <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5" style={{ background: bg }}>
                <Icon size={14} style={{ color }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white leading-tight">{n.message}</p>
                <p className="text-[10px] text-slate-500 mt-0.5">
                  {new Date(n.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </button>
          )
        })}
      </div>
    </motion.div>
  )
}

/* ── Navigation ──────────────────────── */
interface NavSection {
  title: string
  items: { path: string; icon: any; label: string }[]
}

const navSections: NavSection[] = [
  {
    title: 'Command Center',
    items: [
      { path: '/admin', icon: LayoutDashboard, label: 'Mission Control' },
      { path: '/admin/customer360', icon: Users, label: 'Customer 360' },
    ],
  },
  {
    title: 'Intelligence',
    items: [
      { path: '/admin/churn', icon: AlertTriangle, label: 'Churn Center' },
      { path: '/admin/emotions', icon: Heart, label: 'Emotion Center' },
      { path: '/admin/trust', icon: Shield, label: 'Trust Center' },
      { path: '/admin/nba', icon: Target, label: 'NBA Center' },
      { path: '/admin/journey-replay', icon: PlayCircle, label: 'Journey Replay' },
    ],
  },
  {
    title: 'Campaigns & Revenue',
    items: [
      { path: '/admin/campaigns', icon: Megaphone, label: 'Campaign Builder' },
      { path: '/admin/roi', icon: DollarSign, label: 'ROI Center' },
      { path: '/admin/fairness', icon: Scale, label: 'Fairness Observatory' },
    ],
  },
  {
    title: 'Executive',
    items: [
      { path: '/admin/executive-summary', icon: FileText, label: 'Executive Summary' },
      { path: '/admin/copilot', icon: Bot, label: 'Marketer Copilot' },
      { path: '/admin/digital-twin', icon: GitBranch, label: 'Digital Twin Lab' },
    ],
  },
  {
    title: 'Operations',
    items: [
      { path: '/admin/observatory', icon: MonitorDot, label: 'Observatory' },
      { path: '/admin/observability', icon: Gauge, label: 'Observability' },
    ],
  },
]

function NavSectionGroup({ section }: { section: NavSection }) {
  const [open, setOpen] = useState(true)
  const location = useLocation()
  const hasActiveItem = section.items.some(item => location.pathname === item.path)

  return (
    <div className="mb-1">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider rounded transition-colors"
        style={{ color: hasActiveItem ? '#60A5FA' : '#475569' }}
      >
        {section.title}
        <motion.div animate={{ rotate: open ? 0 : -90 }} transition={{ duration: 0.2 }}>
          <ChevronDown size={12} />
        </motion.div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            {section.items.map((item) => {
              const active = location.pathname === item.path
              return (
                <Link key={item.path} to={item.path}>
                  <motion.div
                    className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium transition-colors relative ml-1"
                    style={{
                      color: active ? '#F1F5F9' : '#94A3B8',
                      background: active ? 'rgba(59,130,246,0.1)' : 'transparent',
                    }}
                    whileHover={{ x: 2, background: 'rgba(59,130,246,0.05)' }}
                  >
                    {active && (
                      <motion.div
                        layoutId="sidebar-indicator"
                        className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-4 rounded-r-full"
                        style={{ background: '#3B82F6' }}
                      />
                    )}
                    <item.icon size={16} className={active ? 'text-blue-400' : ''} />
                    {item.label}
                  </motion.div>
                </Link>
              )
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

/* ── Admin Layout ────────────────────── */
export default function AdminLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, logout } = useAuthStore()
  const wsRef = useRef<WebSocket | null>(null)
  
  // Notification state
  const [liveToasts, setLiveToasts] = useState<WsEvent[]>([])
  const [allNotifications, setAllNotifications] = useState<WsEvent[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [showDropdown, setShowDropdown] = useState(false)

  // Connect WebSocket
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const wsUrl = `${protocol}://${window.location.host}/ws/admin`
    
    let ws: WebSocket
    let reconnectTimer: any
    
    const connect = () => {
      ws = new WebSocket(wsUrl)
      wsRef.current = ws
      
      ws.onopen = () => {
        console.log('[WS] Connected to admin channel')
      }
      
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          
          // Intelligence event message generators
          const intelligenceMessages: Record<string, (d: any) => string> = {
            'churn_updated': (d) => `⚠️ ${d.customer_name} churn risk: ${d.churn_category} (${(d.churn_probability * 100).toFixed(0)}%)`,
            'clv_updated': (d) => `💎 ${d.customer_name} CLV: ₹${(d.predicted_clv || 0).toLocaleString('en-IN')} (${d.value_tier})`,
            'trust_updated': (d) => `🛡️ ${d.customer_name} trust: ${d.trust_level} (${d.trust_score?.toFixed(0)}/100)`,
            'happiness_updated': (d) => `😊 ${d.customer_name} mood: ${d.mood} (${d.happiness_score?.toFixed(0)}/100)`,
            'risk_updated': (d) => `🎯 ${d.customer_name} risk: ${d.risk_level} (${d.risk_score?.toFixed(0)}%)`,
            'nba_generated': (d) => `🏆 NBA for ${d.customer_name}: ${d.action}`,
            'campaign_generated': (d) => `📢 Campaign triggered: ${d.name} for ${d.customer_name}`,
            'digital_twin_updated': (d) => `🔮 Digital Twin updated for ${d.customer_name}`,
            'executive_update': (d) => d.insights?.[0] || `📊 Executive update for ${d.customer_name}`,
            'customer360_updated': (d) => `🔄 ${d.customer_name} profile updated`,
          }
          
          const isActivityEvent = msg.type === 'customer_activity' || msg.event_type
          const isIntelligenceEvent = msg.type && intelligenceMessages[msg.type]
          
          if (isActivityEvent || isIntelligenceEvent) {
            const data = msg.data || msg
            
            // Generate smart message
            let message = msg.message || ''
            if (!message && isIntelligenceEvent && intelligenceMessages[msg.type]) {
              message = intelligenceMessages[msg.type](data)
            }
            if (!message) {
              message = `${data.customer_name || 'Customer'} — ${(data.event_type || msg.type || '').replace(/_/g, ' ')}`
            }
            
            const notification: WsEvent = {
              id: `${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
              type: msg.type || 'customer_activity',
              event_type: msg.event_type || data.event_type || msg.type || 'UNKNOWN',
              customer_id: msg.customer_id || data.customer_id || '',
              customer_name: msg.customer_name || data.customer_name || 'Unknown',
              event_value: msg.event_value || data.event_value || '',
              message,
              timestamp: msg.timestamp || new Date().toISOString(),
              metadata: msg.metadata || data || {},
            }
            
            // Only show toasts for activity events (not every intelligence update)
            if (isActivityEvent) {
              setLiveToasts(prev => [notification, ...prev].slice(0, 4))
            }
            
            // Intelligence events that are significant enough for toasts
            if (msg.type === 'churn_updated' && data.churn_category === 'Critical') {
              setLiveToasts(prev => [notification, ...prev].slice(0, 4))
            }
            if (msg.type === 'campaign_generated') {
              setLiveToasts(prev => [notification, ...prev].slice(0, 4))
            }
            if (msg.type === 'nba_generated' && (data.confidence || 0) > 0.75) {
              setLiveToasts(prev => [notification, ...prev].slice(0, 4))
            }
            
            // Add to all notifications
            setAllNotifications(prev => [notification, ...prev].slice(0, 100))
            setUnreadCount(prev => prev + 1)
            
            // Invalidate ALL relevant queries across all admin modules
            queryClient.invalidateQueries({ queryKey: ['overview'] })
            queryClient.invalidateQueries({ queryKey: ['events'] })
            queryClient.invalidateQueries({ queryKey: ['customers'] })
            queryClient.invalidateQueries({ queryKey: ['churn-dist'] })
            queryClient.invalidateQueries({ queryKey: ['customer360'] })
            queryClient.invalidateQueries({ queryKey: ['platform-intelligence'] })
            queryClient.invalidateQueries({ queryKey: ['executive-summary'] })
          }
        } catch {}
      }
      
      ws.onclose = () => {
        console.log('[WS] Disconnected, reconnecting in 3s...')
        reconnectTimer = setTimeout(connect, 3000)
      }
      
      ws.onerror = () => {}
    }
    
    connect()
    
    return () => {
      clearTimeout(reconnectTimer)
      if (ws) ws.close()
    }
  }, [queryClient])

  const dismissToast = useCallback((id: string) => {
    setLiveToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const viewCustomer = useCallback((customerId: string) => {
    navigate(`/admin/customer360?id=${customerId}`)
    setShowDropdown(false)
  }, [navigate])

  const clearUnread = useCallback(() => {
    setUnreadCount(0)
    setShowDropdown(false)
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <WsContext.Provider value={{
      events: allNotifications,
      notifications: allNotifications,
      unreadCount,
      clearUnread,
      dismissNotification: dismissToast,
    }}>
      <div className="min-h-screen flex" style={{ background: '#0B0F14' }}>
        {/* ── Sidebar ─────────────────────── */}
        <aside className="w-60 flex-shrink-0 flex flex-col h-screen sticky top-0"
               style={{ background: '#0D1117', borderRight: '1px solid #1E293B' }}>
          <div className="h-14 flex items-center gap-3 px-4 flex-shrink-0" style={{ borderBottom: '1px solid #1E293B' }}>
            <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                 style={{ background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)' }}>
              <Zap size={14} color="white" />
            </div>
            <div>
              <span className="text-white font-bold text-sm">OmniPulse AI</span>
              <p className="text-[9px]" style={{ color: '#64748B' }}>Intelligence OS v2.0</p>
            </div>
          </div>

          <nav className="flex-1 py-3 px-2 space-y-0.5 overflow-y-auto">
            {navSections.map((section) => (
              <NavSectionGroup key={section.title} section={section} />
            ))}
          </nav>

          <div className="p-2 flex-shrink-0" style={{ borderTop: '1px solid #1E293B' }}>
            <div className="flex items-center gap-2.5 px-2 py-2">
              <div className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-white flex-shrink-0"
                   style={{ background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)' }}>
                {user?.name?.charAt(0) || 'A'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-white truncate">{user?.name || 'Admin'}</p>
                <p className="text-[10px] truncate" style={{ color: '#64748B' }}>{user?.email}</p>
              </div>
              <button onClick={handleLogout} className="text-gray-500 hover:text-red-400 transition">
                <LogOut size={14} />
              </button>
            </div>
          </div>
        </aside>

        {/* ── Main Content ────────────────── */}
        <div className="flex-1 flex flex-col min-h-screen">
          {/* Top Bar */}
          <header className="h-14 flex items-center justify-between px-6 flex-shrink-0"
                  style={{ background: '#0D1117', borderBottom: '1px solid #1E293B' }}>
            <div className="flex items-center gap-3">
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#64748B' }} />
                <input className="input pl-9 py-1.5 text-xs w-56" placeholder="Search customers, campaigns..." />
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg" style={{ background: 'rgba(16,185,129,0.1)' }}>
                <Activity size={12} className="text-green-400" />
                <span className="text-[10px] font-medium text-green-400">System Operational</span>
              </div>
              
              {/* Bell with notification count */}
              <div className="relative">
                <button
                  className="relative p-1.5 rounded-lg hover:bg-white/5 transition"
                  onClick={() => { setShowDropdown(!showDropdown); if (!showDropdown) setUnreadCount(0) }}
                >
                  <Bell size={16} style={{ color: unreadCount > 0 ? '#60A5FA' : '#94A3B8' }} />
                  {unreadCount > 0 && (
                    <motion.span
                      initial={{ scale: 0 }} animate={{ scale: 1 }}
                      className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 rounded-full bg-blue-500 text-[9px] font-bold text-white flex items-center justify-center"
                    >
                      {unreadCount > 99 ? '99+' : unreadCount}
                    </motion.span>
                  )}
                </button>

                <AnimatePresence>
                  {showDropdown && (
                    <NotificationDropdown
                      notifications={allNotifications}
                      onViewCustomer={viewCustomer}
                      onClear={() => { setAllNotifications([]); clearUnread() }}
                    />
                  )}
                </AnimatePresence>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 p-6 overflow-y-auto">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.3 }}
              >
                <Outlet />
              </motion.div>
            </AnimatePresence>
          </main>
        </div>

        {/* ── Live Toast Notifications ──── */}
        <div className="fixed top-16 right-4 z-[200] space-y-3">
          <AnimatePresence>
            {liveToasts.map(toast => (
              <LiveToast
                key={toast.id}
                notification={toast}
                onDismiss={() => dismissToast(toast.id)}
                onViewCustomer={() => { dismissToast(toast.id); viewCustomer(toast.customer_id) }}
              />
            ))}
          </AnimatePresence>
        </div>

        {/* Click outside dropdown */}
        {showDropdown && <div className="fixed inset-0 z-[150]" onClick={() => setShowDropdown(false)} />}
      </div>
    </WsContext.Provider>
  )
}
