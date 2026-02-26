import { useState } from 'react'

const steps = [
  {
    step: '01',
    title: 'Install with pip',
    code: 'pip install mdir-tui',
    comment: '# Or with uv for faster installs',
    alt: 'uv pip install mdir-tui',
  },
  {
    step: '02',
    title: 'Or clone & run',
    code: 'git clone https://github.com/BogKim2/mdir_project.git',
    comment: '# Then install deps',
    alt: 'cd mdir_project && uv sync',
  },
  {
    step: '03',
    title: 'Launch',
    code: 'mdir',
    comment: '# Or python -m mdir',
    alt: 'python -m mdir',
  },
]

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)

  const copy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  return (
    <button
      onClick={copy}
      className="flex-shrink-0 flex items-center gap-1.5 font-mono text-xs px-3 py-1 rounded border border-[#1e3525] text-[#4a6b52] hover:text-[#00ff9d] hover:border-[#00ff9d]/30 transition-all duration-200"
    >
      {copied ? (
        <>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M2 6l3 3 5-5" stroke="#00ff9d" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Copied
        </>
      ) : (
        <>
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <rect x="1" y="3" width="7" height="8" rx="1" stroke="currentColor" strokeWidth="1.2"/>
            <path d="M3 3V2a1 1 0 011-1h5a1 1 0 011 1v7a1 1 0 01-1 1H8" stroke="currentColor" strokeWidth="1.2"/>
          </svg>
          Copy
        </>
      )}
    </button>
  )
}

export default function Install() {
  return (
    <section id="install" className="py-24 px-6 relative">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 60% at 50% 50%, rgba(0,255,157,0.04) 0%, transparent 70%)',
        }}
      />

      <div className="max-w-3xl mx-auto">
        <div className="reveal text-center mb-14">
          <p className="font-mono text-[#4a6b52] text-xs tracking-[0.3em] uppercase mb-4">Get Started</p>
          <h2 className="font-display font-bold text-4xl md:text-5xl text-[#c8d8cc]">
            Up & Running in <span className="text-[#00ff9d] glow-text">30 Seconds</span>
          </h2>
          <p className="mt-4 text-[#4a6b52]">
            Requires Python 3.11+ · Windows, Linux, macOS
          </p>
        </div>

        <div className="space-y-4">
          {steps.map((step, i) => (
            <div
              key={step.step}
              className="reveal rounded-xl overflow-hidden border border-[#1e3525]"
              style={{
                background: 'rgba(13,20,16,0.8)',
                transitionDelay: `${i * 100}ms`,
              }}
            >
              {/* Step header */}
              <div className="flex items-center gap-3 px-5 py-3 border-b border-[#1e3525]/60">
                <span className="font-mono text-xs text-[#2a4530]">{step.step}</span>
                <span className="font-display text-sm font-medium text-[#c8d8cc]">{step.title}</span>
              </div>

              {/* Code block */}
              <div className="p-5 space-y-2">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="font-mono text-sm text-[#4a6b52] mb-1">{step.comment}</div>
                    <div className="font-mono text-sm text-[#00ff9d] truncate">
                      <span className="text-[#2a4530] select-none">$ </span>
                      {step.code}
                    </div>
                    {step.alt && (
                      <div className="font-mono text-sm text-[#c8d8cc]/40 truncate mt-1">
                        <span className="text-[#2a4530] select-none">$ </span>
                        {step.alt}
                      </div>
                    )}
                  </div>
                  <CopyButton text={step.code} />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Requirements */}
        <div
          className="reveal mt-6 p-4 rounded-xl border border-[#1e3525]/60 bg-[#0d1410]/40"
        >
          <div className="flex flex-wrap gap-3 justify-center">
            {[
              'Python ≥ 3.11',
              'Textual ≥ 0.50',
              'send2trash',
              'Windows / Linux / macOS',
            ].map((req) => (
              <span key={req} className="font-mono text-xs text-[#4a6b52] flex items-center gap-1.5">
                <span className="w-1 h-1 rounded-full bg-[#1e3525]" />
                {req}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
