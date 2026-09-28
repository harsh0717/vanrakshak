import { getDashboard, isBackendOnline } from '../../api/client';
import { useApi } from '../../hooks/useApi';
import LoadingSpinner from '../Common/LoadingSpinner';

const villages = [
  { id: 'VLG001', name: 'Sasan Gir', x: 48, y: 42, risk: 'HIGH', incidents: 2 },
  { id: 'VLG002', name: 'Dhari', x: 22, y: 26, risk: 'MEDIUM', incidents: 1 },
  { id: 'VLG003', name: 'Khambha', x: 74, y: 32, risk: 'MEDIUM', incidents: 1 },
  { id: 'VLG004', name: 'Una', x: 80, y: 76, risk: 'MEDIUM', incidents: 1 },
  { id: 'VLG005', name: 'Rajula', x: 88, y: 50, risk: 'LOW', incidents: 0 },
  { id: 'VLG006', name: 'Talala', x: 64, y: 60, risk: 'HIGH', incidents: 2 },
  { id: 'VLG007', name: 'Mendarda', x: 34, y: 58, risk: 'LOW', incidents: 1 },
  { id: 'VLG008', name: 'Kodinar', x: 70, y: 88, risk: 'LOW', incidents: 0 },
];

const colors: Record<string, string> = {
  HIGH: '#ff3b3b',
  MEDIUM: '#ff8c00',
  LOW: '#00c896',
};

function ago(timestamp: string) {
  const minutes = Math.max(0, Math.floor((Date.now() - new Date(timestamp).getTime()) / 60000));
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function DashboardPage() {
  const { data, loading } = useApi(getDashboard, [], { refreshInterval: 30000 });

  if (loading && !data) return <LoadingSpinner label="Loading command center data..." />;
  if (!data) return <div style={{ padding: 30, color: 'var(--text-primary)' }}>Dashboard data unavailable.</div>;

  const s = data.stats;
  const confidence = Math.round((s.avg_ai_confidence || 0) * 100);

  return (
    <div style={{ maxWidth: 1700, margin: '0 auto', paddingBottom: 28 }}>
      <style>{`
        .vr-hero{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:18px;padding:20px 22px;border:1px solid var(--border);border-radius:14px;background:linear-gradient(135deg,#111c32,#0d1628 55%,#102b27);box-shadow:0 12px 40px rgba(0,0,0,.18)}
        .vr-title{font-size:28px;font-weight:800;letter-spacing:-.7px}.vr-sub{color:var(--text-secondary);font-size:12px;margin-top:5px}.vr-live{display:flex;align-items:center;gap:8px;color:var(--accent-green);font-size:11px;font-weight:800}.vr-live-dot{width:9px;height:9px;border-radius:50%;background:var(--accent-green);box-shadow:0 0 14px var(--accent-green)}
        .vr-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:16px}.vr-kpi{padding:18px;border:1px solid var(--border);border-radius:12px;background:var(--bg-card);min-height:145px}.vr-kpi-label{font-size:10px;color:var(--text-muted);font-weight:800;letter-spacing:1px;text-transform:uppercase}.vr-kpi-value{font-size:38px;line-height:1;font-weight:850;margin:12px 0}.vr-kpi-foot{font-size:11px;color:var(--text-secondary)}
        .vr-grid{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(350px,.85fr);gap:16px}.vr-card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;overflow:hidden}.vr-card-head{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid var(--border)}.vr-card-title{font-size:13px;font-weight:800}.vr-card-sub{font-size:10px;color:var(--text-muted);margin-top:2px}.vr-map{height:410px;background:#08120e;position:relative}.vr-map svg{width:100%;height:100%;display:block}.vr-legend{display:flex;gap:15px;padding:10px 16px;border-top:1px solid var(--border);font-size:10px;color:var(--text-secondary)}.vr-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px}.vr-list{padding:12px;display:flex;flex-direction:column;gap:9px;max-height:410px;overflow:auto}.vr-incident{padding:12px;border:1px solid var(--border);border-left:3px solid var(--accent-red);border-radius:9px;background:var(--bg-elevated)}.vr-row{display:flex;justify-content:space-between;gap:10px}.vr-id{font:700 11px monospace;color:var(--accent-blue)}.vr-badge{font-size:9px;font-weight:800;padding:3px 7px;border-radius:99px}.vr-meta{font-size:10px;color:var(--text-muted);margin-top:5px}.vr-lower{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}.vr-sighting{display:grid;grid-template-columns:38px 1fr auto;gap:10px;align-items:center;padding:10px;border:1px solid var(--border);border-radius:9px;background:var(--bg-elevated)}.vr-icon{width:38px;height:38px;border-radius:9px;background:var(--accent-blue-dim);display:grid;place-items:center;font-size:18px}.vr-agent-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;padding:12px}.vr-agent{padding:11px;border:1px solid var(--border);border-radius:9px;background:var(--bg-elevated)}.vr-progress{height:5px;background:var(--border);border-radius:99px;overflow:hidden;margin-top:8px}.vr-progress>div{height:100%;border-radius:99px}.vr-table{padding:12px}.vr-village{display:grid;grid-template-columns:1fr 90px 70px;gap:10px;align-items:center;padding:9px 4px;border-bottom:1px solid rgba(30,45,74,.65);font-size:11px}.vr-village:last-child{border-bottom:0}
        @media(max-width:1100px){.vr-kpis{grid-template-columns:repeat(2,1fr)}.vr-grid,.vr-lower{grid-template-columns:1fr}}@media(max-width:650px){.vr-hero{align-items:flex-start;flex-direction:column}.vr-title{font-size:22px}.vr-kpis{grid-template-columns:1fr}.vr-agent-grid{grid-template-columns:1fr}}
      `}</style>

      <section className="vr-hero">
        <div>
          <div className="vr-title">🐾 VanRakshak AI Command Center</div>
          <div className="vr-sub">Human–wildlife conflict intelligence · Gir Protected Area · Simulated Decision Support</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="vr-live" style={{ color: isBackendOnline() ? 'var(--accent-green)' : 'var(--accent-orange)' }}>
            <span className="vr-live-dot" style={{ background: isBackendOnline() ? 'var(--accent-green)' : 'var(--accent-orange)' }} />
            {isBackendOnline() ? 'BACKEND CONNECTED · DEMO MODE' : 'SIMULATION MODE · OFFLINE'}
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: 10, marginTop: 5 }}>Auto-refresh 30s · {new Date(data.last_updated).toLocaleTimeString()}</div>
        </div>
      </section>

      <section className="vr-kpis">
        <div className="vr-kpi" style={{ borderTop: '3px solid var(--accent-red)' }}>
          <div className="vr-kpi-label">Active Incidents</div>
          <div className="vr-kpi-value">{s.active_incidents}</div>
          <div style={{ display: 'flex', gap: 6 }}><span className="vr-badge" style={{ color: colors.HIGH, background: `${colors.HIGH}20` }}>{s.incidents_high} HIGH</span><span className="vr-badge" style={{ color: colors.MEDIUM, background: `${colors.MEDIUM}20` }}>{s.incidents_medium} MED</span><span className="vr-badge" style={{ color: colors.LOW, background: `${colors.LOW}20` }}>{s.incidents_low} LOW</span></div>
        </div>
        <div className="vr-kpi" style={{ borderTop: '3px solid var(--accent-blue)' }}>
          <div className="vr-kpi-label">Decision Confidence Indicator</div><div className="vr-kpi-value" style={{ color: confidence >= 80 ? 'var(--accent-green)' : 'var(--accent-orange)' }}>{confidence}%</div>
          <div className="vr-progress"><div style={{ width: `${confidence}%`, background: confidence >= 80 ? 'var(--accent-green)' : 'var(--accent-orange)' }} /></div>
        </div>
        <div className="vr-kpi" style={{ borderTop: '3px solid var(--accent-purple)' }}>
          <div className="vr-kpi-label">Sightings — Last 30 Days</div><div className="vr-kpi-value">{s.sightings_today}</div><div className="vr-kpi-foot">Across monitored villages</div>
        </div>
        <div className="vr-kpi" style={{ borderTop: '3px solid var(--accent-green)' }}>
          <div className="vr-kpi-label">Response Teams</div><div className="vr-kpi-value" style={{ color: 'var(--accent-green)' }}>{s.response_teams_available}<span style={{ color: 'var(--text-muted)', fontSize: 20 }}>/{s.response_teams_total}</span></div><div className="vr-kpi-foot">{s.pending_approvals} pending officer approvals</div>
        </div>
      </section>

      <section className="vr-grid">
        <div className="vr-card">
          <div className="vr-card-head"><div><div className="vr-card-title">Gir Region · Risk Intelligence Map</div><div className="vr-card-sub">Hotspots and incident concentration across 8 monitored villages</div></div><span className="vr-badge" style={{ color: 'var(--accent-orange)', background: 'var(--accent-orange-dim)' }}>ILLUSTRATIVE</span></div>
          <div className="vr-map">
            <svg viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
              <defs><radialGradient id="forest"><stop offset="0" stopColor="#16482c"/><stop offset="1" stopColor="#07100c"/></radialGradient></defs>
              <rect width="100" height="100" fill="url(#forest)"/><ellipse cx="50" cy="50" rx="38" ry="31" fill="#17472d" opacity=".45"/><ellipse cx="47" cy="48" rx="28" ry="23" fill="#1c5a38" opacity=".25"/>
              <path d="M5 52 C25 43 55 60 95 45" fill="none" stroke="#38536a" strokeWidth=".35" strokeDasharray="2 1.5"/><path d="M50 5 C44 28 58 60 49 96" fill="none" stroke="#38536a" strokeWidth=".35" strokeDasharray="2 1.5"/><path d="M15 20 L85 82" stroke="#2a455b" strokeWidth=".25" strokeDasharray="1 2"/>
              {villages.filter(v => v.risk === 'HIGH').map(v => <circle key={`h-${v.id}`} cx={v.x} cy={v.y} r="10" fill="#ff3b3b" opacity=".07" stroke="#ff3b3b" strokeWidth=".5" />)}
              {villages.map(v => <g key={v.id}><circle cx={v.x} cy={v.y} r="4.2" fill={colors[v.risk]} opacity=".16"/><circle cx={v.x} cy={v.y} r="2.7" fill={colors[v.risk]}/><circle cx={v.x} cy={v.y} r=".9" fill="#fff"/><text x={v.x} y={v.y-5} textAnchor="middle" fill="#eef3f5" fontSize="2.7" fontWeight="700">{v.name}</text>{v.incidents > 0 && <text x={v.x} y={v.y+7} textAnchor="middle" fill={colors[v.risk]} fontSize="2">{v.incidents} INCIDENT{v.incidents > 1 ? 'S' : ''}</text>}</g>)}
              <text x="50" y="46" textAnchor="middle" fill="#bff5d5" fontSize="7" fontWeight="900" opacity=".16" letterSpacing="1.5">GIR</text>
            </svg>
          </div>
          <div className="vr-legend"><span><i className="vr-dot" style={{ background: colors.HIGH }} />High risk</span><span><i className="vr-dot" style={{ background: colors.MEDIUM }} />Medium risk</span><span><i className="vr-dot" style={{ background: colors.LOW }} />Low risk</span><span style={{ marginLeft: 'auto' }}>● Landscape monitoring</span></div>
        </div>

        <div className="vr-card">
          <div className="vr-card-head"><div><div className="vr-card-title">🚨 Priority Incidents</div><div className="vr-card-sub">Latest incidents requiring attention</div></div><span className="vr-badge" style={{ color: colors.HIGH, background: `${colors.HIGH}20` }}>{s.active_incidents} ACTIVE</span></div>
          <div className="vr-list">
            {data.incidents.slice(0, 7).map((i: any) => { const c = colors[i.severity] || colors.MEDIUM; return <div className="vr-incident" key={i.id} style={{ borderLeftColor: c }}><div className="vr-row"><span className="vr-id">{i.display_id}</span><span className="vr-badge" style={{ color: c, background: `${c}18` }}>{i.severity}</span></div><div style={{ fontSize: 12, fontWeight: 700, marginTop: 7 }}>🦁 {i.species}</div><div className="vr-meta">📍 {i.village} · Risk score {(i.risk_score || 0).toFixed(2)} · {ago(i.timestamp)}</div></div> })}
            {data.incidents.length === 0 && <div style={{ padding: 30, textAlign: 'center', color: 'var(--text-muted)' }}>No active incidents</div>}
          </div>
        </div>
      </section>

      <section className="vr-lower">
        <div className="vr-card">
          <div className="vr-card-head"><div><div className="vr-card-title">🦁 Recent Wildlife Sightings</div><div className="vr-card-sub">Latest observations received by the platform</div></div><span className="vr-badge" style={{ color: 'var(--accent-blue)', background: 'var(--accent-blue-dim)' }}>SIMULATED FEED</span></div>
          <div style={{ padding: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>{data.sightings.slice(0, 6).map((x: any) => <div className="vr-sighting" key={x.id}><div className="vr-icon">🦁</div><div><div style={{ fontWeight: 700, fontSize: 12 }}>{x.species}</div><div style={{ color: 'var(--text-muted)', fontSize: 10 }}>📍 {x.village} · {x.distance_km} km</div></div><div style={{ textAlign: 'right', fontSize: 10, color: 'var(--accent-blue)' }}>{Math.round((x.confidence || 0) * 100)}%<div style={{ color: 'var(--text-muted)', marginTop: 3 }}>{ago(x.timestamp)}</div></div></div>)}</div>
        </div>

        <div className="vr-card">
          <div className="vr-card-head"><div><div className="vr-card-title">🤖 AI Agent Network</div><div className="vr-card-sub">Autonomous monitoring and decision support</div></div><span className="vr-badge" style={{ color: 'var(--accent-green)', background: 'var(--accent-green-dim)' }}>AGENT SIMULATION ACTIVE</span></div>
          <div className="vr-agent-grid">{data.agents.slice(0, 6).map((a: any) => { const c = a.status === 'ACTIVE' ? 'var(--accent-green)' : a.status === 'ERROR' ? 'var(--accent-red)' : a.status === 'WAITING' ? 'var(--accent-orange)' : 'var(--accent-blue)'; return <div className="vr-agent" key={a.agent_id}><div className="vr-row"><div style={{ fontSize: 11, fontWeight: 700 }}>{a.name}</div><span style={{ color: c, fontSize: 9, fontWeight: 800 }}>● {a.status}</span></div><div style={{ color: 'var(--text-muted)', fontSize: 9, marginTop: 5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{a.latest_action}</div><div className="vr-progress"><div style={{ width: `${Math.round((a.confidence || 0) * 100)}%`, background: c }} /></div></div> })}</div>
        </div>
      </section>

      <section className="vr-card" style={{ marginTop: 16 }}>
        <div className="vr-card-head"><div><div className="vr-card-title">📍 Village Risk Overview</div><div className="vr-card-sub">Current monitoring priority across the Gir landscape</div></div><span className="vr-badge" style={{ color: 'var(--accent-orange)', background: 'var(--accent-orange-dim)' }}>DEMO DATA</span></div>
        <div className="vr-table">{villages.map(v => <div className="vr-village" key={v.id}><div><strong>{v.name}</strong><div style={{ color: 'var(--text-muted)', fontSize: 9 }}>{v.incidents} incident{v.incidents === 1 ? '' : 's'} recorded</div></div><div><div style={{ height: 5, background: 'var(--border)', borderRadius: 99 }}><div style={{ width: v.risk === 'HIGH' ? '90%' : v.risk === 'MEDIUM' ? '60%' : '30%', height: '100%', background: colors[v.risk], borderRadius: 99 }} /></div></div><div style={{ color: colors[v.risk], fontSize: 9, fontWeight: 800, textAlign: 'right' }}>{v.risk}</div></div>)}</div>
      </section>

      <div className="notice-box warning mt-16"><span>⚠️</span><span><strong>DEMONSTRATION SYSTEM</strong> — This dashboard uses sample/simulated data for the hackathon demonstration. AI recommendations require human officer approval.</span></div>
    </div>
  );
}
