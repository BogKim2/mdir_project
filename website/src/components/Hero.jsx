import { useEffect, useRef, useState } from 'react'

const TYPING_LINES = [
  { text: '$ mdir', delay: 0, color: '#00ff9d' },
  { text: '> Loading dual-panel file manager...', delay: 800, color: '#4a6b52' },
  { text: '> Initializing Textual TUI engine', delay: 1600, color: '#4a6b52' },
  { text: '> Security hardened. 7 CVEs patched.', delay: 2400, color: '#00e5ff' },
  { text: '> Ready.', delay: 3200, color: '#00ff9d' },
]

function TypingLine({ text, delay, color }) {
  const [displayed, setDisplayed] = useState('')
  const [started, setStarted] = useState(false)

  useEffect(() => {
    const startTimer = setTimeout(() => {
      setStarted(true)
      let i = 0
      const interval = setInterval(() => {
        i++
        setDisplayed(text.slice(0, i))
        if (i >= text.length) clearInterval(interval)
      }, 28)
      return () => clearInterval(interval)
    }, delay)
    return () => clearTimeout(startTimer)
  }, [text, delay])

  if (!started) return null

  return (
    <div style={{ color }} className="font-mono text-sm leading-7">
      {displayed}
      {displayed.length < text.length && (
        <span className="cursor-blink" />
      )}
    </div>
  )
}

// Particle background
function Particles() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    let animId

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    const particles = Array.from({ length: 80 }, () => ({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      size: Math.random() * 1.5 + 0.3,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.5 + 0.1,
      color: Math.random() > 0.7 ? '#00e5ff' : '#00ff9d',
    }))

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      particles.forEach((p) => {
        p.x += p.speedX
        p.y += p.speedY
        if (p.x < 0) p.x = canvas.width
        if (p.x > canvas.width) p.x = 0
        if (p.y < 0) p.y = canvas.height
        if (p.y > canvas.height) p.y = 0

        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fillStyle = p.color
        ctx.globalAlpha = p.opacity
        ctx.fill()
      })

      // Draw connections
      ctx.globalAlpha = 1
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < 120) {
            ctx.beginPath()
            ctx.strokeStyle = '#00ff9d'
            ctx.globalAlpha = (1 - dist / 120) * 0.06
            ctx.lineWidth = 0.5
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.stroke()
          }
        }
      }

      animId = requestAnimationFrame(draw)
    }

    draw()
    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('resize', resize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
      style={{ opacity: 0.6 }}
    />
  )
}

export default function Hero() {
  const [showContent, setShowContent] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setShowContent(true), 200)
    return () => clearTimeout(t)
  }, [])

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden mesh-bg scanlines">
      <Particles />

      {/* Grid overlay */}
      <div className="absolute inset-0 grid-bg opacity-40 pointer-events-none" />

      {/* Radial vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 70% 70% at 50% 50%, transparent 40%, #080c0a 100%)',
        }}
      />

      {/* Glowing orb */}
      <div
        className="absolute pointer-events-none"
        style={{
          width: '600px',
          height: '600px',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(0,255,157,0.08) 0%, transparent 70%)',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          animation: 'glowPulse 4s ease-in-out infinite',
        }}
      />

      {/* Content */}
      <div className="relative z-10 text-center px-6 max-w-5xl mx-auto">
        {/* Badge */}
        <div
          className="inline-flex items-center gap-2 mb-8 px-4 py-1.5 rounded-full border border-[#1e3525] bg-[#0d1410]/60 backdrop-blur-sm"
          style={{
            opacity: showContent ? 1 : 0,
            transform: showContent ? 'translateY(0)' : 'translateY(-10px)',
            transition: 'all 0.6s cubic-bezier(0.16,1,0.3,1)',
          }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-[#00ff9d]" style={{ animation: 'glowPulse 2s ease-in-out infinite' }} />
          <span className="font-mono text-xs text-[#4a6b52] tracking-widest uppercase">
            Python · Textual · v0.1.1
          </span>
        </div>

        {/* Main title */}
        <h1
          className="font-display font-bold tracking-tight mb-4"
          style={{
            fontSize: 'clamp(3.5rem, 10vw, 8rem)',
            lineHeight: 1,
            opacity: showContent ? 1 : 0,
            transform: showContent ? 'translateY(0)' : 'translateY(20px)',
            transition: 'all 0.7s cubic-bezier(0.16,1,0.3,1) 0.1s',
          }}
        >
          <span className="glow-text text-[#00ff9d]">m</span>
          <span className="text-[#c8d8cc]">dir</span>
        </h1>

        {/* Subtitle */}
        <p
          className="font-mono text-[#4a6b52] text-sm tracking-[0.3em] uppercase mb-8"
          style={{
            opacity: showContent ? 1 : 0,
            transition: 'all 0.7s cubic-bezier(0.16,1,0.3,1) 0.2s',
          }}
        >
          Modern Dual-Panel TUI File Manager
        </p>

        {/* Terminal card */}
        <div
          className="relative mx-auto max-w-lg text-left rounded-xl overflow-hidden mb-12"
          style={{
            background: 'rgba(13,20,16,0.8)',
            border: '1px solid #1e3525',
            boxShadow: '0 0 0 1px #1e3525, 0 40px 80px rgba(0,0,0,0.5), 0 0 60px rgba(0,255,157,0.08)',
            backdropFilter: 'blur(10px)',
            opacity: showContent ? 1 : 0,
            transform: showContent ? 'translateY(0)' : 'translateY(30px)',
            transition: 'all 0.8s cubic-bezier(0.16,1,0.3,1) 0.3s',
          }}
        >
          {/* Terminal header */}
          <div className="flex items-center gap-2 px-4 py-3 border-b border-[#1e3525]/60">
            <span className="w-3 h-3 rounded-full bg-[#ff5f57]" />
            <span className="w-3 h-3 rounded-full bg-[#febc2e]" />
            <span className="w-3 h-3 rounded-full bg-[#28c840]" />
            <span className="font-mono text-xs text-[#2a4530] ml-2">terminal</span>
          </div>
          {/* Terminal content */}
          <div className="p-5 space-y-0.5">
            {TYPING_LINES.map((line, i) => (
              <TypingLine key={i} {...line} />
            ))}
          </div>
        </div>

        {/* CTAs */}
        <div
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
          style={{
            opacity: showContent ? 1 : 0,
            transition: 'all 0.8s cubic-bezier(0.16,1,0.3,1) 0.5s',
          }}
        >
          <a
            href="#install"
            className="group flex items-center gap-2 px-8 py-3.5 rounded-lg font-mono text-sm font-medium bg-[#00ff9d] text-[#080c0a] hover:bg-[#00e88a] transition-all duration-200"
            style={{ boxShadow: '0 0 30px rgba(0,255,157,0.3)' }}
          >
            <span className="text-[#080c0a]/50">$</span> pip install mdir-tui
          </a>
          <a
            href="https://github.com/BogKim2/mdir_project"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-8 py-3.5 rounded-lg font-mono text-sm border border-[#1e3525] text-[#c8d8cc] hover:border-[#00ff9d]/40 hover:text-[#00ff9d] transition-all duration-200"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
            </svg>
            View on GitHub
          </a>
        </div>
      </div>

      {/* Scroll indicator */}
      <div
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        style={{ animation: 'float 3s ease-in-out infinite' }}
      >
        <span className="font-mono text-[10px] text-[#2a4530] tracking-widest">SCROLL</span>
        <div className="w-px h-12 bg-gradient-to-b from-[#1e3525] to-transparent" />
      </div>
    </section>
  )
}
