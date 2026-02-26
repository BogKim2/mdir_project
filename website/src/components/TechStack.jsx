const stack = [
  {
    name: 'Python 3.13',
    role: 'Language',
    desc: 'Latest Python with performance improvements and modern type system.',
    badge: 'py',
    color: '#3b82f6',
  },
  {
    name: 'Textual',
    role: 'TUI Framework',
    desc: 'Modern TUI framework with CSS styling, reactive state, and async support.',
    badge: 'tx',
    color: '#a78bfa',
  },
  {
    name: 'send2trash',
    role: 'Safe Delete',
    desc: 'Cross-platform recycle bin integration. Never accidentally lose files.',
    badge: 'st',
    color: '#34d399',
  },
  {
    name: 'pathlib',
    role: 'File System',
    desc: 'Cross-platform path handling with elegant, readable API.',
    badge: 'pl',
    color: '#fbbf24',
  },
  {
    name: 'pytest',
    role: 'Testing',
    desc: '46 tests across models and operations. Security regression suite included.',
    badge: 'pt',
    color: '#f87171',
  },
  {
    name: 'ruff',
    role: 'Linter + Formatter',
    desc: 'Ultra-fast Python linter written in Rust. Zero lint errors enforced.',
    badge: 'rf',
    color: '#fb923c',
  },
]

const metrics = [
  { label: 'Lines of Code', value: '~2,500', sub: 'src/' },
  { label: 'Test Cases', value: '46', sub: 'all passing' },
  { label: 'Match Rate', value: '94.4%', sub: 'design → impl' },
  { label: 'FR Coverage', value: '15/15', sub: '100%' },
]

export default function TechStack() {
  return (
    <section className="py-24 px-6 relative">
      <div
        className="absolute inset-0 pointer-events-none grid-bg"
        style={{ opacity: 0.15 }}
      />

      <div className="max-w-6xl mx-auto">
        <div className="reveal text-center mb-16">
          <p className="font-mono text-[#4a6b52] text-xs tracking-[0.3em] uppercase mb-4">Under the Hood</p>
          <h2 className="font-display font-bold text-4xl md:text-5xl text-[#c8d8cc]">
            Built With <span className="text-[#00ff9d] glow-text">Precision</span>
          </h2>
        </div>

        {/* Metrics */}
        <div className="reveal grid grid-cols-2 md:grid-cols-4 gap-4 mb-16">
          {metrics.map(({ label, value, sub }) => (
            <div
              key={label}
              className="text-center p-6 rounded-xl border border-[#1e3525]"
              style={{ background: 'rgba(13,20,16,0.6)' }}
            >
              <div className="font-display font-bold text-3xl text-[#00ff9d] glow-text mb-1">{value}</div>
              <div className="font-mono text-xs text-[#c8d8cc]">{label}</div>
              <div className="font-mono text-[10px] text-[#2a4530] mt-0.5">{sub}</div>
            </div>
          ))}
        </div>

        {/* Stack cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {stack.map((item, i) => (
            <div
              key={item.name}
              className="reveal group flex items-start gap-4 p-5 rounded-xl border border-[#1e3525] hover:border-[#2a4530] transition-all duration-300"
              style={{
                background: 'rgba(13,20,16,0.5)',
                transitionDelay: `${i * 60}ms`,
              }}
            >
              {/* Icon badge */}
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 font-mono text-sm font-bold"
                style={{
                  background: `${item.color}15`,
                  border: `1px solid ${item.color}30`,
                  color: item.color,
                }}
              >
                {item.badge}
              </div>

              <div className="min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-display font-semibold text-[#c8d8cc]">{item.name}</span>
                  <span
                    className="font-mono text-[10px] px-1.5 py-0.5 rounded"
                    style={{ color: item.color, background: `${item.color}10` }}
                  >
                    {item.role}
                  </span>
                </div>
                <p className="font-mono text-xs text-[#4a6b52] leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
