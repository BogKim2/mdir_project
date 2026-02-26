const features = [
  {
    icon: '⬛',
    title: 'Dual-Panel Layout',
    desc: 'Side-by-side panels with independent navigation. Copy and move files between panels with a single keystroke.',
    accent: '#00ff9d',
    tag: 'FR-01',
  },
  {
    icon: '🔐',
    title: 'Safe Operations',
    desc: 'Delete sends files to the system recycle bin via send2trash. No accidental permanent deletions.',
    accent: '#00e5ff',
    tag: 'FR-06',
  },
  {
    icon: '🔍',
    title: 'Text Preview',
    desc: 'Inline file viewer with scroll support. Preview any text file without leaving the manager.',
    accent: '#ff6b35',
    tag: 'FR-09',
  },
  {
    icon: '⚡',
    title: 'Column Sorting',
    desc: 'Sort by name, size, or modified date. Click column headers or use Ctrl+S to cycle through sort modes.',
    accent: '#00ff9d',
    tag: 'FR-13',
  },
  {
    icon: '✓',
    title: 'Multi-Selection',
    desc: 'Select multiple files with Space, select all with Ctrl+A. Operate on entire groups at once.',
    accent: '#00e5ff',
    tag: 'FR-10',
  },
  {
    icon: '🛡️',
    title: 'Security Hardened',
    desc: '7 CVEs patched. Path traversal blocked, filename validation enforced, symlink escape prevented.',
    accent: '#ff6b35',
    tag: 'v0.1.1',
  },
]

export default function Features() {
  return (
    <section id="features-detail" className="py-24 px-6 relative">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 80% 50% at 50% 50%, rgba(0,255,157,0.03) 0%, transparent 70%)',
        }}
      />

      <div className="max-w-6xl mx-auto">
        <div className="reveal text-center mb-16">
          <p className="font-mono text-[#4a6b52] text-xs tracking-[0.3em] uppercase mb-4">What You Get</p>
          <h2 className="font-display font-bold text-4xl md:text-5xl text-[#c8d8cc]">
            Every Feature <span className="text-[#00ff9d] glow-text">Matters</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature, i) => (
            <div
              key={feature.title}
              className="reveal group relative rounded-xl p-6 border border-[#1e3525] hover:border-[#2a4530] transition-all duration-300"
              style={{
                background: 'rgba(13,20,16,0.6)',
                transitionDelay: `${i * 80}ms`,
                boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
              }}
            >
              {/* Hover glow */}
              <div
                className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                style={{
                  background: `radial-gradient(ellipse 80% 60% at 30% 30%, ${feature.accent}08 0%, transparent 70%)`,
                }}
              />

              <div className="relative">
                {/* Tag */}
                <span
                  className="inline-block font-mono text-[10px] px-2 py-0.5 rounded mb-4 border"
                  style={{
                    color: feature.accent,
                    borderColor: `${feature.accent}30`,
                    background: `${feature.accent}08`,
                  }}
                >
                  {feature.tag}
                </span>

                <div className="text-2xl mb-3">{feature.icon}</div>
                <h3 className="font-display font-semibold text-lg text-[#c8d8cc] mb-2">
                  {feature.title}
                </h3>
                <p className="text-[#4a6b52] text-sm leading-relaxed">{feature.desc}</p>
              </div>

              {/* Bottom accent line */}
              <div
                className="absolute bottom-0 left-6 right-6 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                style={{ background: `linear-gradient(90deg, transparent, ${feature.accent}40, transparent)` }}
              />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
