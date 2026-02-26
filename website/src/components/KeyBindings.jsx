const keys = [
  { key: 'Tab', action: 'Switch panel', category: 'Navigation' },
  { key: '↑ ↓', action: 'Move cursor', category: 'Navigation' },
  { key: '↵ Enter', action: 'Enter directory', category: 'Navigation' },
  { key: '⌫ Back', action: 'Parent directory', category: 'Navigation' },
  { key: 'Ctrl+G', action: 'Go to path', category: 'Navigation' },
  { key: 'F2', action: 'Rename file', category: 'File Ops' },
  { key: 'F3', action: 'Preview text', category: 'File Ops' },
  { key: 'F5', action: 'Copy to opposite', category: 'File Ops' },
  { key: 'F6', action: 'Move to opposite', category: 'File Ops' },
  { key: 'F7', action: 'New folder', category: 'File Ops' },
  { key: 'F8', action: 'Delete (trash)', category: 'File Ops' },
  { key: 'Space', action: 'Toggle select', category: 'Selection' },
  { key: 'Ctrl+A', action: 'Select all', category: 'Selection' },
  { key: 'Ctrl+H', action: 'Toggle hidden', category: 'View' },
  { key: 'Ctrl+S', action: 'Cycle sort', category: 'View' },
  { key: 'F10 / Q', action: 'Quit', category: 'App' },
]

const categories = ['Navigation', 'File Ops', 'Selection', 'View', 'App']
const categoryColors = {
  Navigation: '#00ff9d',
  'File Ops': '#00e5ff',
  Selection: '#ff6b35',
  View: '#a78bfa',
  App: '#f87171',
}

export default function KeyBindings() {
  return (
    <section id="keys" className="py-24 px-6 relative">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 80% at 80% 50%, rgba(0,229,255,0.03) 0%, transparent 60%)',
        }}
      />

      <div className="max-w-6xl mx-auto">
        <div className="reveal text-center mb-16">
          <p className="font-mono text-[#4a6b52] text-xs tracking-[0.3em] uppercase mb-4">Keyboard First</p>
          <h2 className="font-display font-bold text-4xl md:text-5xl text-[#c8d8cc]">
            16 Key <span className="text-[#00e5ff] glow-cyan">Bindings</span>
          </h2>
          <p className="mt-4 text-[#4a6b52] max-w-md mx-auto">
            Complete keyboard control. Every operation accessible without touching the mouse.
          </p>
        </div>

        {/* Category legend */}
        <div className="reveal flex flex-wrap justify-center gap-3 mb-10">
          {categories.map((cat) => (
            <span
              key={cat}
              className="flex items-center gap-1.5 font-mono text-xs px-3 py-1 rounded-full border"
              style={{
                color: categoryColors[cat],
                borderColor: `${categoryColors[cat]}30`,
                background: `${categoryColors[cat]}08`,
              }}
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ background: categoryColors[cat] }}
              />
              {cat}
            </span>
          ))}
        </div>

        {/* Key grid */}
        <div className="reveal grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
          {keys.map((item, i) => (
            <div
              key={item.key}
              className="group flex items-center gap-3 px-4 py-3 rounded-lg border border-[#1e3525] hover:border-[#2a4530] transition-all duration-200"
              style={{
                background: 'rgba(13,20,16,0.5)',
                transitionDelay: `${i * 30}ms`,
              }}
            >
              {/* Category dot */}
              <span
                className="w-1 h-6 rounded-full flex-shrink-0"
                style={{ background: categoryColors[item.category] }}
              />
              {/* Key */}
              <span className="key-badge flex-shrink-0" style={{ color: categoryColors[item.category] }}>
                {item.key}
              </span>
              {/* Action */}
              <span className="font-mono text-xs text-[#4a6b52] group-hover:text-[#c8d8cc] transition-colors truncate">
                {item.action}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
