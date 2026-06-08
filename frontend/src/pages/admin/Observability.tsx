/**
 * PLATFORM OBSERVABILITY - COMPLETE REBUILD
 * ==========================================
 * 
 * ALL METRICS NOW COME FROM REAL BACKEND TELEMETRY
 * 
 * Features:
 * - Real CPU & Memory metrics (via psutil)
 * - Real API latency tracking (via middleware)
 * - Real WebSocket connection count
 * - Real database statistics
 * - Real service health checks
 * - Real log streaming
 * 
 * NO hardcoded values
 * NO Math.random() simulations
 * NO fake data
 */

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Activity, ShieldCheck, Terminal, Cpu, Database, Wifi, Clock, Server, AlertTriangle, CheckCircle } from 'lucide-react'
import { BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import api from '../../services/api'

interface LogEntry {
  timestamp: string
  level: 'INFO' | 'WARN' | 'ERROR'
  service: string
  message: string
}

interface LatencyData {
  endpoint: string
  avg: number
  min: number
  max: number
  p50: number
  p95: number
  p99: number
  samples: number
}

interface HealthCheck {
  name: string
  status: string
  healthy: boolean
  description: string
  response_time_ms: number
}

export default function Observability() {
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: { current: 0, cores: 0 },
    memory: { used_percent: 0, used_mb: 0, available_mb: 0, total_mb: 0 },
    psutil_available: false
  })

  const [latencyData, setLatencyData] = useState<LatencyData[]>([])
  const [healthChecks, setHealthChecks] = useState<HealthCheck[]>([])
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [websocketStats, setWebsocketStats] = useState({
    active_connections: 0,
    rooms: 0
  })
  const [databaseStats, setDatabaseStats] = useState({
    file_size_mb: 0,
    query_latency_ms: 0,
    sqlite_version: 'unknown'
  })
  
  const [loading, setLoading] = useState(true)

  // Fetch system metrics every 2 seconds
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const { data } = await api.get('/telemetry/metrics')
        setSystemMetrics(data)
      } catch (error) {
        console.error('Failed to fetch system metrics:', error)
      }
    }

    fetchMetrics()
    const interval = setInterval(fetchMetrics, 2000)
    return () => clearInterval(interval)
  }, [])

  // Fetch latency data every 5 seconds
  useEffect(() => {
    const fetchLatency = async () => {
      try {
        const { data } = await api.get('/telemetry/latency')
        // Get top 6 endpoints by p95 latency
        setLatencyData(data.latencies.slice(0, 6))
      } catch (error) {
        console.error('Failed to fetch latency data:', error)
      }
    }

    fetchLatency()
    const interval = setInterval(fetchLatency, 5000)
    return () => clearInterval(interval)
  }, [])

  // Fetch health checks every 10 seconds
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const { data } = await api.get('/telemetry/health')
        setHealthChecks(data.checks)
      } catch (error) {
        console.error('Failed to fetch health checks:', error)
      }
    }

    fetchHealth()
    const interval = setInterval(fetchHealth, 10000)
    return () => clearInterval(interval)
  }, [])

  // Fetch logs every 3 seconds
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const { data } = await api.get('/telemetry/logs?limit=50')
        setLogs(data.logs)
        setLoading(false)
      } catch (error) {
        console.error('Failed to fetch logs:', error)
        setLoading(false)
      }
    }

    fetchLogs()
    const interval = setInterval(fetchLogs, 3000)
    return () => clearInterval(interval)
  }, [])

  // Fetch WebSocket stats every 5 seconds
  useEffect(() => {
    const fetchWsStats = async () => {
      try {
        const { data } = await api.get('/telemetry/websocket')
        setWebsocketStats(data)
      } catch (error) {
        console.error('Failed to fetch WebSocket stats:', error)
      }
    }

    fetchWsStats()
    const interval = setInterval(fetchWsStats, 5000)
    return () => clearInterval(interval)
  }, [])

  // Fetch database stats every 10 seconds
  useEffect(() => {
    const fetchDbStats = async () => {
      try {
        const { data } = await api.get('/telemetry/database')
        setDatabaseStats(data)
      } catch (error) {
        console.error('Failed to fetch database stats:', error)
      }
    }

    fetchDbStats()
    const interval = setInterval(fetchDbStats, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">Loading telemetry data...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
          <Server className="text-emerald-400" size={24} />
          Platform Observability
        </h1>
        <p className="text-sm" style={{ color: '#64748B' }}>
          Real-time system metrics via psutil | Middleware latency tracking | Live service health | {systemMetrics.psutil_available ? '✅ psutil enabled' : '⚠️ psutil not available'}
        </p>
      </div>

      {/* System Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { 
            icon: Cpu, 
            label: 'CPU Utilization', 
            value: `${systemMetrics.cpu.current}%`, 
            sublabel: `${systemMetrics.cpu.cores} cores`,
            color: '#10B981', 
            barVal: systemMetrics.cpu.current 
          },
          { 
            icon: Clock, 
            label: 'Memory Allocation', 
            value: `${systemMetrics.memory.used_percent}%`, 
            sublabel: `${Math.round(systemMetrics.memory.used_mb)} MB used`,
            color: '#3B82F6', 
            barVal: systemMetrics.memory.used_percent 
          },
          { 
            icon: Wifi, 
            label: 'WebSocket Connections', 
            value: `${websocketStats.active_connections} active`,
            sublabel: `${websocketStats.rooms} rooms`,
            color: '#8B5CF6' 
          },
          { 
            icon: Database, 
            label: 'Database Size', 
            value: `${databaseStats.file_size_mb} MB`,
            sublabel: `${databaseStats.query_latency_ms}ms query latency`,
            color: '#F59E0B'
          },
        ].map((item, idx) => (
          <motion.div
            key={idx}
            className="card p-5 flex flex-col justify-between"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{item.label}</span>
              <item.icon size={16} style={{ color: item.color }} />
            </div>
            <div>
              <p className="text-2xl font-bold text-white font-mono">{item.value}</p>
              {item.sublabel && (
                <p className="text-xs text-slate-500 mt-1">{item.sublabel}</p>
              )}
              {item.barVal !== undefined && (
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-1000"
                    style={{ background: item.color, width: `${Math.min(item.barVal, 100)}%` }}
                  />
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* API Latency Chart */}
        <motion.div
          className="lg:col-span-2 card p-6 flex flex-col"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
            API Endpoints Response Latency (P95)
            <span className="text-xs text-slate-500 font-normal">via middleware tracking</span>
          </h2>
          
          {latencyData.length > 0 ? (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={latencyData.map(d => ({ endpoint: d.endpoint, latency: d.p95 }))} layout="vertical">
                  <XAxis type="number" stroke="#475569" fontSize={9} tickLine={false} />
                  <YAxis dataKey="endpoint" type="category" stroke="#475569" fontSize={9} tickLine={false} width={110} />
                  <Tooltip 
                    contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: '8px' }}
                    formatter={(value: any, name: any, props: any) => {
                      const item = latencyData.find(d => d.endpoint === props.payload.endpoint)
                      if (item) {
                        return [
                          `P95: ${item.p95}ms | P50: ${item.p50}ms | Avg: ${item.avg}ms | Samples: ${item.samples}`,
                          'Latency'
                        ]
                      }
                      return [value, name]
                    }}
                  />
                  <Bar dataKey="latency" name="P95 Latency (ms)" fill="#10B981" radius={[0, 4, 4, 0]} barSize={12} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
              No API latency data yet. Make some API calls to see statistics.
            </div>
          )}
        </motion.div>

        {/* Health Checks */}
        <motion.div
          className="card p-6"
          initial={{ opacity: 0, x: 15 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
            Health Check Status
          </h2>
          <div className="space-y-4">
            {healthChecks.map((check, idx) => (
              <div key={idx} className="flex gap-3 p-3 rounded-lg bg-white/5 border border-white/5">
                {check.healthy ? (
                  <CheckCircle className="text-emerald-400 mt-0.5 flex-shrink-0" size={16} />
                ) : (
                  <AlertTriangle className="text-red-400 mt-0.5 flex-shrink-0" size={16} />
                )}
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-xs font-semibold text-white">{check.name}</h4>
                    <span 
                      className={`text-[9px] px-1.5 py-0.2 rounded border font-mono ${
                        check.healthy 
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-red-500/10 text-red-400 border-red-500/20'
                      }`}
                    >
                      {check.status}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-500 mt-0.5">{check.description}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Live Trace Logs */}
      <motion.div
        className="card p-6 flex flex-col h-[280px]"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <Terminal size={15} className="text-emerald-400" />
          Live System Logs
          <span className="text-xs text-slate-500 font-normal">({logs.length} entries)</span>
        </h2>
        <div className="flex-1 bg-black/60 border border-white/5 rounded-lg p-4 font-mono text-xs text-emerald-400 overflow-y-auto space-y-1">
          {logs.length > 0 ? (
            logs.map((log, idx) => (
              <div key={idx} className="flex gap-2 leading-relaxed">
                <span className="text-slate-600">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                <span className={
                  log.level === 'ERROR' ? 'text-red-500' :
                  log.level === 'WARN' ? 'text-yellow-500' : 
                  'text-emerald-500'
                }>
                  [{log.level}]
                </span>
                <span className="text-cyan-400 font-semibold">[{log.service}]</span>
                <span className="text-slate-300">{log.message}</span>
              </div>
            ))
          ) : (
            <div className="text-slate-500 text-center py-8">
              No logs yet. System events will appear here in real-time.
            </div>
          )}
        </div>
      </motion.div>
    </div>
  )
}
