import { useRef, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { motion, useScroll, useTransform } from 'framer-motion'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Zap, Activity, Shield, Target, BarChart3, Brain, Users, TrendingUp, ArrowRight } from 'lucide-react'
import * as THREE from 'three'

/* ── 3D Customer Network ──────────────────────────── */
function NetworkNode({ position, color, size }: { position: [number, number, number]; color: string; size: number }) {
  const ref = useRef<THREE.Mesh>(null!)
  const offset = useMemo(() => Math.random() * Math.PI * 2, [])
  
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    ref.current.position.y = position[1] + Math.sin(t * 0.5 + offset) * 0.3
    ref.current.position.x = position[0] + Math.cos(t * 0.3 + offset) * 0.15
  })

  return (
    <mesh ref={ref} position={position}>
      <sphereGeometry args={[size, 16, 16]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} transparent opacity={0.85} />
    </mesh>
  )
}

function NetworkEdge({ start, end, color }: { start: [number, number, number]; end: [number, number, number]; color: string }) {
  const points = useMemo(() => [new THREE.Vector3(...start), new THREE.Vector3(...end)], [start, end])
  const geometry = useMemo(() => new THREE.BufferGeometry().setFromPoints(points), [points])
  
  return (
    <line>
      <bufferGeometry attach="geometry" {...geometry} />
      <lineBasicMaterial attach="material" color={color} transparent opacity={0.2} />
    </line>
  )
}

function CustomerNetwork() {
  const nodes = useMemo(() => {
    const n: { pos: [number, number, number]; color: string; size: number }[] = []
    for (let i = 0; i < 60; i++) {
      n.push({
        pos: [(Math.random() - 0.5) * 12, (Math.random() - 0.5) * 8, (Math.random() - 0.5) * 6],
        color: ['#3B82F6', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B'][Math.floor(Math.random() * 5)],
        size: 0.06 + Math.random() * 0.12,
      })
    }
    return n
  }, [])

  const edges = useMemo(() => {
    const e: { start: [number, number, number]; end: [number, number, number] }[] = []
    for (let i = 0; i < nodes.length; i++) {
      const connections = 1 + Math.floor(Math.random() * 2)
      for (let c = 0; c < connections; c++) {
        const j = Math.floor(Math.random() * nodes.length)
        if (j !== i) {
          const dist = Math.sqrt(
            (nodes[i].pos[0] - nodes[j].pos[0]) ** 2 +
            (nodes[i].pos[1] - nodes[j].pos[1]) ** 2 +
            (nodes[i].pos[2] - nodes[j].pos[2]) ** 2
          )
          if (dist < 5) {
            e.push({ start: nodes[i].pos, end: nodes[j].pos })
          }
        }
      }
    }
    return e
  }, [nodes])

  return (
    <>
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 10, 10]} intensity={0.6} />
      {nodes.map((n, i) => (
        <NetworkNode key={i} position={n.pos} color={n.color} size={n.size} />
      ))}
      {edges.map((e, i) => (
        <NetworkEdge key={i} start={e.start} end={e.end} color="#3B82F6" />
      ))}
      <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} enablePan={false} />
    </>
  )
}

/* ── Animated Counter ──────────────────────────────── */
function Counter({ value, suffix = '' }: { value: string; suffix?: string }) {
  return (
    <motion.span
      className="mono text-3xl font-bold text-white"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
    >
      {value}{suffix}
    </motion.span>
  )
}

/* ── Feature Card ──────────────────────────────────── */
function FeatureCard({ icon: Icon, title, desc, delay }: { icon: any; title: string; desc: string; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay }}
      className="card p-6 hover:border-blue-500/30 group cursor-default"
    >
      <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"
           style={{ background: 'linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15))' }}>
        <Icon size={20} className="text-blue-400" />
      </div>
      <h3 className="text-white font-semibold mb-2">{title}</h3>
      <p className="text-sm leading-relaxed" style={{ color: '#94A3B8' }}>{desc}</p>
    </motion.div>
  )
}

/* ── Landing Page ──────────────────────────────────── */
export default function Landing() {
  const { scrollYProgress } = useScroll()
  const networkScale = useTransform(scrollYProgress, [0, 0.3], [1, 1.2])

  const features = [
    { icon: Users, title: 'Unified Identity Engine', desc: 'Merge anonymous visitors, known customers, and campaign users into a single profile with real-time identity resolution.' },
    { icon: Activity, title: 'Real-Time Event Streaming', desc: 'Every customer action captured, streamed, analyzed, and visualized — as it happens.' },
    { icon: Shield, title: 'Trust Intelligence', desc: 'Continuous trust scoring based on purchase patterns, complaints, and engagement signals.' },
    { icon: Brain, title: 'Hierarchical Inference Router', desc: 'Rules → ML → Gemini. Three-tier intelligence that minimizes cost while maximizing accuracy.' },
    { icon: Target, title: 'Next Best Action Engine', desc: 'Determine the optimal channel, offer, timing, and tone for every customer interaction.' },
    { icon: TrendingUp, title: 'Revenue Attribution', desc: 'Measure every dollar saved, protected, and generated across campaigns and interventions.' },
  ]

  const stats = [
    { value: '50K+', label: 'Customer Profiles' },
    { value: '1M+', label: 'Events Processed' },
    { value: '95%', label: 'Prediction Accuracy' },
    { value: '<200ms', label: 'Decision Latency' },
  ]

  return (
    <div className="min-h-screen overflow-hidden" style={{ background: '#0B0F14' }}>
      {/* ── Navigation ─────────────────────── */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass-strong">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                 style={{ background: 'linear-gradient(135deg, #3B82F6, #8B5CF6)' }}>
              <Zap size={18} color="white" />
            </div>
            <span className="text-white font-bold text-lg">OmniPulse AI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-secondary text-sm py-2 px-4">Sign In</Link>
            <Link to="/register" className="btn-primary text-sm py-2 px-4">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* ── Hero Section ───────────────────── */}
      <section className="relative min-h-screen flex items-center pt-16">
        {/* 3D Background */}
        <div className="absolute inset-0 z-0">
          <Canvas camera={{ position: [0, 0, 8], fov: 50 }}>
            <CustomerNetwork />
          </Canvas>
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 z-10"
             style={{ background: 'radial-gradient(ellipse at center, transparent 30%, #0B0F14 80%)' }} />

        <div className="relative z-20 max-w-7xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-6"
                 style={{ background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.2)' }}>
              <div className="live-indicator" />
              <span className="text-sm font-medium text-blue-400">Enterprise Customer Intelligence</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-extrabold text-white leading-tight mb-6">
              Real-Time Customer
              <br />
              <span className="gradient-text">Intelligence OS</span>
            </h1>

            <p className="text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed" style={{ color: '#94A3B8' }}>
              Observe. Understand. Predict. Act. The unified operating system for customer intelligence,
              adaptive journey orchestration, and measurable business impact.
            </p>

            <div className="flex items-center justify-center gap-4">
              <Link to="/register">
                <motion.button className="btn-primary text-base py-3 px-8 flex items-center gap-2" whileHover={{ scale: 1.03 }}>
                  Launch Platform <ArrowRight size={18} />
                </motion.button>
              </Link>
              <Link to="/login">
                <motion.button className="btn-secondary text-base py-3 px-8" whileHover={{ scale: 1.03 }}>
                  Admin Demo
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── Stats ──────────────────────────── */}
      <section className="relative z-20 py-20" style={{ background: 'linear-gradient(180deg, transparent, rgba(17,24,39,0.8))' }}>
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((s, i) => (
              <motion.div
                key={i}
                className="text-center"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <Counter value={s.value} />
                <p className="text-sm mt-1" style={{ color: '#64748B' }}>{s.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ───────────────────────── */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Platform Capabilities</h2>
            <p className="text-lg max-w-xl mx-auto" style={{ color: '#94A3B8' }}>
              Enterprise-grade intelligence architecture designed for Fortune 500 scale.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <FeatureCard key={i} {...f} delay={i * 0.1} />
            ))}
          </div>
        </div>
      </section>

      {/* ── Architecture ───────────────────── */}
      <section className="py-24 px-6" style={{ background: 'rgba(17,24,39,0.5)' }}>
        <div className="max-w-4xl mx-auto text-center">
          <motion.h2
            className="text-3xl font-bold text-white mb-12"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            Meridian Intelligence Architecture
          </motion.h2>
          
          <div className="space-y-3">
            {['Customer Actions', 'Event Streaming', 'Identity Resolution', 'Unified Profile',
              'Behavior Analysis', 'Trust Analysis', 'Hierarchical Inference Router',
              'Decision Cache', 'Next Best Action', 'Journey Orchestration', 'Business Impact'].map((step, i) => (
              <motion.div
                key={i}
                className="glass rounded-lg py-3 px-6 inline-block"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
              >
                <span className="text-sm font-medium text-white">{step}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ────────────────────────────── */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Intelligence That Drives <span className="gradient-text">Revenue</span>
            </h2>
            <p className="text-lg mb-8" style={{ color: '#94A3B8' }}>
              Every customer action creates intelligence. Every intelligence signal drives decisions.
              Every decision creates measurable business impact.
            </p>
            <Link to="/register">
              <motion.button className="btn-primary text-lg py-4 px-10" whileHover={{ scale: 1.03 }}>
                Start Building Intelligence
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────── */}
      <footer className="py-8 px-6" style={{ borderTop: '1px solid #1E293B' }}>
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Zap size={16} className="text-blue-400" />
            <span className="text-sm font-medium text-white">OmniPulse AI</span>
          </div>
          <p className="text-xs" style={{ color: '#64748B' }}>
            Built for Epsilon Hackathon 2026 • Customer Intelligence Operating System
          </p>
        </div>
      </footer>
    </div>
  )
}
