const vulns = [
  {
    id: 'VULN-01',
    severity: 'CRITICAL',
    title: 'Path Traversal',
    desc: 'mkdir / rename accepted "../escaped" names allowing escape from working directory.',
    fix: '_validate_filename() + resolved parent check blocks all traversal attempts',
    severityColor: '#ff4444',
  },
  {
    id: 'VULN-02',
    severity: 'HIGH',
    title: 'Symlink Escape',
    desc: 'shutil.copytree() followed symlinks by default, enabling escape outside destination.',
    fix: 'symlinks=True preserves symlinks as-is without following them',
    severityColor: '#ff6b35',
  },
  {
    id: 'VULN-04',
    severity: 'HIGH',
    title: 'TOCTOU Race',
    desc: 'Pre-existence check before mkdir/rename created a race condition window.',
    fix: 'Removed pre-checks; rely solely on OS-level FileExistsError',
    severityColor: '#ff6b35',
  },
  {
    id: 'VULN-05',
    severity: 'MEDIUM',
    title: 'Infinite Conflict Loop',
    desc: 'resolve_conflict() had no upper bound — could run forever in adversarial scenarios.',
    fix: '_MAX_CONFLICT_RETRIES = 999 raises FileOperationError on limit',
    severityColor: '#febc2e',
  },
  {
    id: 'VULN-07',
    severity: 'MEDIUM',
    title: 'Invalid Filename',
    desc: 'No validation of Windows reserved names (CON, NUL) or illegal characters (:, |, etc).',
    fix: 'Regex _INVALID_CHARS_RE + _WINDOWS_RESERVED enforced on all inputs',
    severityColor: '#febc2e',
  },
  {
    id: 'VULN-08',
    severity: 'MEDIUM',
    title: 'Symlink stat() Leak',
    desc: 'stat() follows symlinks, exposing target metadata and enabling TOCTOU via symlinks.',
    fix: 'lstat() used for symlinks — reads symlink own metadata only',
    severityColor: '#febc2e',
  },
  {
    id: 'VULN-10',
    severity: 'LOW',
    title: 'select_all() Freeze',
    desc: 'select_all() on a directory with 100K+ files could freeze the UI indefinitely.',
    fix: 'MAX_SELECT_ALL = 10,000 hard cap prevents UI lockup',
    severityColor: '#4a6b52',
  },
]

const severityOrder = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }

export default function Security() {
  return (
    <section id="security" className="py-24 px-6 relative">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 70% 60% at 20% 60%, rgba(255,107,53,0.04) 0%, transparent 60%)',
        }}
      />

      <div className="max-w-6xl mx-auto">
        <div className="reveal text-center mb-6">
          <p className="font-mono text-[#4a6b52] text-xs tracking-[0.3em] uppercase mb-4">Security Audit</p>
          <h2 className="font-display font-bold text-4xl md:text-5xl text-[#c8d8cc]">
            7 Vulnerabilities <span className="text-[#ff6b35]">Patched</span>
          </h2>
          <p className="mt-4 text-[#4a6b52] max-w-lg mx-auto">
            Full PDCA security review identified and resolved every issue. 11 regression tests added to prevent regressions.
          </p>
        </div>

        {/* Stats row */}
        <div className="reveal flex flex-wrap justify-center gap-6 mb-14">
          {[
            { label: 'Critical', count: 1, color: '#ff4444' },
            { label: 'High', count: 2, color: '#ff6b35' },
            { label: 'Medium', count: 3, color: '#febc2e' },
            { label: 'Low', count: 1, color: '#4a6b52' },
          ].map(({ label, count, color }) => (
            <div
              key={label}
              className="flex flex-col items-center px-8 py-4 rounded-xl border"
              style={{
                borderColor: `${color}30`,
                background: `${color}08`,
              }}
            >
              <span className="font-display font-bold text-3xl" style={{ color }}>{count}</span>
              <span className="font-mono text-xs mt-1" style={{ color: `${color}80` }}>{label}</span>
            </div>
          ))}
          <div
            className="flex flex-col items-center px-8 py-4 rounded-xl border border-[#00ff9d]/20 bg-[#00ff9d]/05"
          >
            <span className="font-display font-bold text-3xl text-[#00ff9d]">46</span>
            <span className="font-mono text-xs mt-1 text-[#00ff9d]/50">Tests Passing</span>
          </div>
        </div>

        {/* Vulnerability list */}
        <div className="space-y-3">
          {vulns.map((vuln, i) => (
            <div
              key={vuln.id}
              className="reveal group rounded-xl border border-[#1e3525] hover:border-[#2a4530] overflow-hidden transition-all duration-300"
              style={{
                background: 'rgba(13,20,16,0.6)',
                transitionDelay: `${i * 60}ms`,
              }}
            >
              <div className="flex items-start gap-4 p-5">
                {/* Severity badge */}
                <div className="flex-shrink-0 flex flex-col items-center gap-1 w-20">
                  <span
                    className="font-mono text-[10px] font-bold px-2 py-0.5 rounded"
                    style={{
                      color: vuln.severityColor,
                      background: `${vuln.severityColor}15`,
                      border: `1px solid ${vuln.severityColor}30`,
                    }}
                  >
                    {vuln.severity}
                  </span>
                  <span className="font-mono text-[10px] text-[#2a4530]">{vuln.id}</span>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <h3 className="font-display font-semibold text-[#c8d8cc] mb-1">{vuln.title}</h3>
                  <p className="font-mono text-xs text-[#4a6b52] mb-3 leading-relaxed">{vuln.desc}</p>

                  {/* Fix */}
                  <div className="flex items-start gap-2 p-3 rounded-lg bg-[#00ff9d]/04 border border-[#00ff9d]/10">
                    <span className="font-mono text-[10px] text-[#00ff9d] flex-shrink-0 mt-0.5">FIX</span>
                    <span className="font-mono text-xs text-[#00ff9d]/70 leading-relaxed">{vuln.fix}</span>
                  </div>
                </div>

                {/* Resolved mark */}
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-[#00ff9d]/10 border border-[#00ff9d]/30 flex items-center justify-center">
                  <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6l3 3 5-5" stroke="#00ff9d" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
