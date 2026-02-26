import { useState } from 'react'

const LEFT_FILES = [
  { name: '..', type: 'dir', size: '<DIR>', date: '2026-02-26 10:00' },
  { name: 'src', type: 'dir', size: '<DIR>', date: '2026-02-26 09:15' },
  { name: 'docs', type: 'dir', size: '<DIR>', date: '2026-02-25 22:00' },
  { name: 'tests', type: 'dir', size: '<DIR>', date: '2026-02-25 18:30' },
  { name: 'pyproject.toml', type: 'file', size: '1.2K', date: '2026-02-26 08:00' },
  { name: 'README.md', type: 'file', size: '4.8K', date: '2026-02-26 07:45' },
  { name: '.gitignore', type: 'file', size: '0.3K', date: '2026-02-24 12:00' },
  { name: 'CHANGELOG.md', type: 'file', size: '2.1K', date: '2026-02-26 09:30' },
]

const RIGHT_FILES = [
  { name: '..', type: 'dir', size: '<DIR>', date: '2026-02-26 10:00' },
  { name: 'mdir', type: 'dir', size: '<DIR>', date: '2026-02-26 09:00' },
  { name: 'app.py', type: 'file', size: '12.4K', date: '2026-02-26 09:00' },
  { name: 'models', type: 'dir', size: '<DIR>', date: '2026-02-25 20:00' },
  { name: 'operations', type: 'dir', size: '<DIR>', date: '2026-02-26 01:00' },
  { name: 'panels', type: 'dir', size: '<DIR>', date: '2026-02-25 22:00' },
  { name: 'styles', type: 'dir', size: '<DIR>', date: '2026-02-25 14:00' },
  { name: '__init__.py', type: 'file', size: '0.1K', date: '2026-02-24 10:00' },
]

function FileRow({ file, active, isActive }) {
  const isDir = file.type === 'dir'
  return (
    <div
      className={`flex items-center font-mono text-xs px-2 py-0.5 rounded-sm transition-colors ${
        active
          ? isActive
            ? 'bg-[#1155bb] text-white'
            : 'bg-[#252535] text-[#888899]'
          : 'hover:bg-[#1a2e1f]/40'
      }`}
    >
      <span className={`flex-1 truncate ${isDir ? 'text-[#00e5ff]' : 'text-[#c8d8cc]'}`}>
        {isDir && file.name !== '..' ? '  ' : ''}{file.name}
      </span>
      <span className="w-16 text-right text-[#4a6b52]">{file.size}</span>
      <span className="w-32 text-right text-[#4a6b52] hidden lg:block">{file.date}</span>
    </div>
  )
}

function Panel({ title, path, files, isActive, cursorIdx }) {
  return (
    <div
      className={`flex-1 flex flex-col rounded-lg overflow-hidden font-mono text-xs transition-all duration-300 ${
        isActive ? 'panel-active' : 'panel-inactive'
      }`}
      style={{ background: '#0d1410', minWidth: 0 }}
    >
      {/* Path bar */}
      <div
        className={`px-3 py-1.5 text-xs font-mono border-b flex items-center gap-2 transition-colors ${
          isActive
            ? 'bg-[#0f3460] border-[#1a4570] text-white'
            : 'bg-[#0d1a10] border-[#1e3525] text-[#555577]'
        }`}
      >
        {isActive && <span className="text-[#00ff9d] font-bold">▶</span>}
        <span className="truncate">{path}</span>
      </div>

      {/* Column headers */}
      <div className="flex items-center px-2 py-0.5 border-b border-[#1e3525]/60 text-[#2a4530] text-[10px]">
        <span className="flex-1">Name</span>
        <span className="w-16 text-right">Size</span>
        <span className="w-32 text-right hidden lg:block">Modified</span>
      </div>

      {/* Files */}
      <div className="flex-1 overflow-hidden p-1 space-y-0.5">
        {files.map((file, i) => (
          <FileRow
            key={file.name}
            file={file}
            active={i === cursorIdx}
            isActive={isActive}
          />
        ))}
      </div>

      {/* Status line */}
      <div className="px-3 py-1 border-t border-[#1e3525]/60 text-[#2a4530] text-[10px] flex justify-between">
        <span>{files.length - 1} items</span>
        <span>sort: name ↑</span>
      </div>
    </div>
  )
}

export default function TUIPreview() {
  const [activePanel, setActivePanel] = useState('left')
  const [leftCursor, setLeftCursor] = useState(1)
  const [rightCursor, setRightCursor] = useState(2)

  return (
    <section id="features" className="py-32 px-6 relative">
      {/* Section label */}
      <div className="max-w-6xl mx-auto">
        <div className="reveal text-center mb-16">
          <p className="font-mono text-[#4a6b52] text-xs tracking-[0.3em] uppercase mb-4">Live Preview</p>
          <h2 className="font-display font-bold text-4xl md:text-5xl text-[#c8d8cc]">
            Dual-Panel <span className="text-[#00ff9d] glow-text">Interface</span>
          </h2>
          <p className="mt-4 text-[#4a6b52] text-base max-w-xl mx-auto">
            Two panels, total keyboard control. Switch with Tab. Navigate like a pro.
          </p>
        </div>

        {/* TUI mockup */}
        <div className="reveal">
          <div
            className="rounded-2xl overflow-hidden scanlines"
            style={{
              background: '#080c0a',
              border: '1px solid #1e3525',
              boxShadow: '0 40px 100px rgba(0,0,0,0.7), 0 0 80px rgba(0,255,157,0.06)',
            }}
          >
            {/* Window chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-[#1e3525]/60 bg-[#0d1410]">
              <span className="w-3 h-3 rounded-full bg-[#ff5f57]" />
              <span className="w-3 h-3 rounded-full bg-[#febc2e]" />
              <span className="w-3 h-3 rounded-full bg-[#28c840]" />
              <span className="font-mono text-xs text-[#2a4530] ml-3">
                mdir — Python 3.13 · Textual
              </span>
              <div className="ml-auto flex gap-3">
                <span className="font-mono text-[10px] text-[#2a4530]">46 tests ✓</span>
                <span className="font-mono text-[10px] text-[#00e5ff]">v0.1.1</span>
              </div>
            </div>

            {/* Panels */}
            <div className="flex gap-1 p-2" style={{ minHeight: '360px' }}>
              <div
                className="cursor-pointer flex-1"
                onClick={() => setActivePanel('left')}
              >
                <Panel
                  title="left"
                  path="E:\projects\bkit_mdirproject"
                  files={LEFT_FILES}
                  isActive={activePanel === 'left'}
                  cursorIdx={activePanel === 'left' ? leftCursor : leftCursor}
                />
              </div>
              <div
                className="cursor-pointer flex-1"
                onClick={() => setActivePanel('right')}
              >
                <Panel
                  title="right"
                  path="E:\projects\bkit_mdirproject\src"
                  files={RIGHT_FILES}
                  isActive={activePanel === 'right'}
                  cursorIdx={activePanel === 'right' ? rightCursor : rightCursor}
                />
              </div>
            </div>

            {/* Status bar */}
            <div className="px-4 py-1.5 border-t border-[#1e3525]/60 bg-[#0d1410] flex justify-between items-center">
              <span className="font-mono text-[10px] text-[#2a4530]">
                8 items · sort: name ↑ · disk: 234G free / 512G
              </span>
              <span className="font-mono text-[10px] text-[#00ff9d]">READY</span>
            </div>

            {/* Function bar */}
            <div className="px-2 py-1 bg-[#080c0a] border-t border-[#1e3525]/40 flex items-center gap-1 flex-wrap">
              {[
                ['F2','Rename'],['F3','View'],['F5','Copy'],['F6','Move'],
                ['F7','MkDir'],['F8','Delete'],['F10','Quit'],
              ].map(([key, label]) => (
                <span key={key} className="flex items-center font-mono text-[10px] px-1.5">
                  <span className="text-[#080c0a] bg-[#4a6b52] rounded px-1 mr-0.5">{key}</span>
                  <span className="text-[#4a6b52]">{label}</span>
                </span>
              ))}
            </div>
          </div>

          {/* Interactive hint */}
          <p className="text-center font-mono text-xs text-[#2a4530] mt-4">
            Click panels to switch focus · <span className="text-[#4a6b52]">Tab</span> to switch in real app
          </p>
        </div>
      </div>
    </section>
  )
}
