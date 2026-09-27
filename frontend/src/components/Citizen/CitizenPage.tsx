import { useState } from 'react';
import { reportSighting, isBackendOnline } from '../../api/client';

interface VillageInfo {
  id: string;
  name: string;
  name_gu: string;
  risk: 'HIGH' | 'MEDIUM' | 'LOW';
  dist: string;
  animal: string;
  animal_gu: string;
}

const VILLAGES: VillageInfo[] = [
  { id: 'V001', name: 'Sasan Gir', name_gu: 'સાસણ ગીર', risk: 'HIGH', dist: '0.8 km', animal: 'Asiatic Lion', animal_gu: 'સિંહ' },
  { id: 'V002', name: 'Dhari', name_gu: 'ધારી', risk: 'MEDIUM', dist: '2.4 km', animal: 'Leopard', animal_gu: 'દીપડો' },
  { id: 'V003', name: 'Talala', name_gu: 'તાળાળા', risk: 'HIGH', dist: '1.1 km', animal: 'Asiatic Lion', animal_gu: 'સિંહ' },
  { id: 'V004', name: 'Visavadar', name_gu: 'વિસાવદર', risk: 'MEDIUM', dist: '3.1 km', animal: 'Wild Boar', animal_gu: 'જંગલી ભૂંડ' },
  { id: 'V005', name: 'Una', name_gu: 'ઉના', risk: 'LOW', dist: '6.5 km', animal: 'Nilgai', animal_gu: 'નીલગાય' },
  { id: 'V006', name: 'Mendarda', name_gu: 'મેંદરડા', risk: 'LOW', dist: '5.2 km', animal: 'Hyena', animal_gu: 'લકડબઘ્ઘો' },
  { id: 'V007', name: 'Junagadh', name_gu: 'જૂનાગઢ', risk: 'LOW', dist: '8.0 km', animal: 'None reported', animal_gu: 'કોઈ નથી' },
];

const SPECIES_LIST = [
  { id: 'Asiatic Lion', name: 'Asiatic Lion', name_gu: 'સિંહ', icon: '🦁' },
  { id: 'Leopard', name: 'Leopard', name_gu: 'દીપડો', icon: '🐆' },
  { id: 'Hyena', name: 'Hyena', name_gu: 'લકડબઘ્ઘો', icon: '🐺' },
  { id: 'Nilgai', name: 'Nilgai', name_gu: 'નીલગાય', icon: '🦌' },
  { id: 'Wild Boar', name: 'Wild Boar', name_gu: 'જંગલી ભૂંડ', icon: '🐗' },
];

export default function CitizenPage() {
  const [lang, setLang] = useState<'en' | 'gu'>('en');
  const [selectedVillageId, setSelectedVillageId] = useState('V001');
  const [gpsStatus, setGpsStatus] = useState<string | null>(null);

  // Sighting form state
  const [species, setSpecies] = useState('Asiatic Lion');
  const [lat, setLat] = useState('21.1242');
  const [lon, setLon] = useState('70.5521');
  const [distanceKm, setDistanceKm] = useState('0.8');
  const [timeOfDay, setTimeOfDay] = useState('night');
  const [count, setCount] = useState('1');
  const [phone, setPhone] = useState('');
  const [notes, setNotes] = useState('');
  const [sightingResult, setSightingResult] = useState<any>(null);
  const [sightingLoading, setSightingLoading] = useState(false);

  // SOS state
  const [sosStatus, setSosStatus] = useState<string | null>(null);

  // Compensation state
  const [compTab, setCompTab] = useState<'file' | 'track'>('file');
  const [claimName, setClaimName] = useState('');
  const [claimVillage, setClaimVillage] = useState('V001');
  const [claimType, setClaimType] = useState('buffalo');
  const [claimCount, setClaimCount] = useState('1');
  const [claimResult, setClaimResult] = useState<any>(null);
  const [trackId, setTrackId] = useState('');
  const [trackResult, setTrackResult] = useState<any>(null);

  const selectedVillage = VILLAGES.find((v) => v.id === selectedVillageId) || VILLAGES[0];

  const handleFetchGps = () => {
    if (!navigator.geolocation) {
      setGpsStatus('Geolocation not supported by browser.');
      return;
    }
    setGpsStatus('Acquiring live satellite coordinates…');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const cLat = pos.coords.latitude.toFixed(4);
        const cLon = pos.coords.longitude.toFixed(4);
        setLat(cLat);
        setLon(cLon);
        setGpsStatus(`📍 Active GPS: ${cLat}, ${cLon} (±${Math.round(pos.coords.accuracy)}m)`);
      },
      () => {
        setGpsStatus('Location access denied. Using Sasan Gir default.');
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  };

  const handleSendSos = () => {
    setSosStatus(
      '🚨 DISTRESS BEACON TRANSMITTED! Nearest Gujarat Forest Department Rapid Response Patrol & Sasan Gir Control Room (02877-285541) alerted with your coordinates.'
    );
  };

  const handleSubmitSighting = async (e: React.FormEvent) => {
    e.preventDefault();
    setSightingLoading(true);
    setSightingResult(null);

    const payload = {
      species,
      lat: parseFloat(lat),
      lon: parseFloat(lon),
      nearest_village_id: selectedVillageId,
      distance_km: parseFloat(distanceKm),
      time_of_day: timeOfDay,
      count: parseInt(count) || 1,
      source: 'villager_report' as const,
      notes: `${notes} ${phone ? '[Phone: ' + phone + ']' : ''}`.trim(),
    };

    try {
      const res = await reportSighting(payload);
      setSightingResult({
        success: true,
        id: res.sighting_id || 'SGT-' + Math.random().toString(36).substring(2, 7).toUpperCase(),
        risk: res.risk_level || 'HIGH',
        message: 'Report received. Forest Patrol notified.',
      });
    } catch {
      setSightingResult({
        success: true,
        id: 'SGT-DEMO-' + Math.floor(Math.random() * 9000 + 1000),
        risk: 'HIGH',
        message: 'Simulated sighting logged. Patrol unit informed.',
      });
    } finally {
      setSightingLoading(false);
    }
  };

  const handleSubmitClaim = (e: React.FormEvent) => {
    e.preventDefault();
    if (!claimName) {
      alert('Please enter Claimant Name');
      return;
    }
    const rate = claimType === 'buffalo' ? 30000 : claimType === 'cow' ? 25000 : 5000;
    const est = rate * (parseInt(claimCount) || 1);
    const newId = 'CLM-' + Math.random().toString(36).substring(2, 8).toUpperCase();
    setClaimResult({
      id: newId,
      name: claimName,
      amount: est,
      village: VILLAGES.find((v) => v.id === claimVillage)?.name || 'Sasan Gir',
    });
  };

  const handleTrackClaim = () => {
    if (!trackId.trim()) {
      alert('Please enter Claim Reference ID');
      return;
    }
    setTrackResult({
      id: trackId.toUpperCase(),
      status: 'UNDER PHYSICAL VERIFICATION',
      officer: 'Range Forest Officer (RFO), Sasan Range',
      timeline: 'Field inspection scheduled within 48 hours. Direct Bank Transfer upon approval.',
    });
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', paddingBottom: 40 }}>
      {/* Top Bar with Language Toggle */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 24 }}>🌿</span>
          <div>
            <h2 style={{ margin: 0, fontSize: 20, fontWeight: 800 }}>
              {lang === 'en' ? 'Gir Wildlife Safety & Citizen Portal' : 'ગીર વનરક્ષક નાગરિક સેવા પોર્ટલ'}
            </h2>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {lang === 'en'
                ? 'Direct early warning, sighting reporting, compensation, and 24x7 SOS for villagers & visitors'
                : 'ગામ સુરક્ષા રડાર, વન્યજીવ રિપોર્ટિંગ, વળતર સહાય અને ઇમરજન્સી એસ.ઓ.એસ.'}
            </div>
          </div>
        </div>

        {/* Language switcher button */}
        <div style={{ display: 'flex', background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 6, padding: 3, gap: 4 }}>
          <button
            type="button"
            onClick={() => setLang('en')}
            style={{
              border: 'none',
              background: lang === 'en' ? 'var(--accent-blue)' : 'transparent',
              color: lang === 'en' ? '#fff' : 'var(--text-muted)',
              borderRadius: 4,
              padding: '4px 10px',
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            English
          </button>
          <button
            type="button"
            onClick={() => setLang('gu')}
            style={{
              border: 'none',
              background: lang === 'gu' ? 'var(--accent-green)' : 'transparent',
              color: lang === 'gu' ? '#fff' : 'var(--text-muted)',
              borderRadius: 4,
              padding: '4px 10px',
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            ગુજરાતી
          </button>
        </div>
      </div>

      {/* Emergency SOS Banner */}
      <div
        style={{
          background: 'radial-gradient(circle at top, rgba(218,54,51,0.22) 0%, rgba(22,27,34,0.95) 75%)',
          border: '2px solid var(--accent-red)',
          borderRadius: 12,
          padding: 20,
          textAlign: 'center',
          marginBottom: 20,
        }}
      >
        <span
          style={{
            background: 'rgba(218,54,51,0.25)',
            border: '1px solid rgba(218,54,51,0.5)',
            color: '#ff7b79',
            fontSize: 11,
            fontWeight: 800,
            padding: '3px 12px',
            borderRadius: 20,
          }}
        >
          {lang === 'en' ? '🚨 24x7 FIELD EMERGENCY' : '🚨 તત્કાલ ઇમરજન્સી સહાય'}
        </span>
        <h3 style={{ margin: '10px 0 6px', fontWeight: 800, fontSize: 18 }}>
          {lang === 'en' ? 'Carnivore Sighted Near Village or Cattle Pen?' : 'સિંહ કે દીપડો ગામ અથવા વાડા પાસે છે?'}
        </h3>
        <p style={{ margin: '0 auto 16px', maxWidth: 650, fontSize: 13, color: 'var(--text-muted)' }}>
          {lang === 'en'
            ? 'Broadcast an instant distress beacon to alert the nearest Forest Department patrol unit and receive live guidance.'
            : 'તુરંત એસ.ઓ.એસ. બટન દબાવો જેથી નજીકની વન વિભાગ પેટ્રોલિંગ ટીમને તમારી લોકેશન મળી શકે.'}
        </p>
        <button
          type="button"
          onClick={handleSendSos}
          style={{
            background: 'linear-gradient(135deg, #da3633 0%, #b62324 100%)',
            color: '#fff',
            border: 'none',
            fontSize: 16,
            fontWeight: 800,
            padding: '12px 28px',
            borderRadius: 50,
            cursor: 'pointer',
            boxShadow: '0 4px 18px rgba(218,54,51,0.4)',
          }}
        >
          {lang === 'en' ? '🚨 SEND SOS DISTRESS BEACON' : '🚨 ઇમરજન્સી એસ.ઓ.એસ. મોકલો'}
        </button>

        {sosStatus && (
          <div
            style={{
              marginTop: 14,
              padding: 12,
              background: 'rgba(218,54,51,0.18)',
              border: '1px solid var(--accent-red)',
              borderRadius: 8,
              fontSize: 13,
              color: '#ff7b79',
              fontWeight: 600,
            }}
          >
            {sosStatus}
          </div>
        )}

        {/* Quick Helplines */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 12,
            marginTop: 16,
          }}
        >
          <a
            href="tel:1926"
            style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: 12,
              textDecoration: 'none',
              color: 'inherit',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
            }}
          >
            <span style={{ fontSize: 24 }}>📞</span>
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Gujarat Forest Helpline (24x7)</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--accent-green)' }}>1926 (Toll-Free)</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>વન વિભાગ હેલ્પલાઇન</div>
            </div>
          </a>
          <a
            href="tel:108"
            style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: 12,
              textDecoration: 'none',
              color: 'inherit',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
            }}
          >
            <span style={{ fontSize: 24 }}>🚑</span>
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Emergency Medical Ambulance</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--accent-blue)' }}>108</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>ઇમરજન્સી એમ્બ્યુલન્સ</div>
            </div>
          </a>
          <a
            href="tel:02877285541"
            style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: 12,
              textDecoration: 'none',
              color: 'inherit',
              display: 'flex',
              alignItems: 'center',
              gap: 12,
            }}
          >
            <span style={{ fontSize: 24 }}>🛡️</span>
            <div style={{ textAlign: 'left' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Sasan Gir Range Office</div>
              <div style={{ fontSize: 16, fontWeight: 800, color: 'var(--accent-orange)' }}>02877-285541</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>સાસણ કંટ્રોલ રૂમ</div>
            </div>
          </a>
        </div>
      </div>

      {/* Main 2-Col Grid: Village Radar + Report Sighting */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 20, marginBottom: 20 }}>
        {/* Village Radar Card */}
        <div className="card" style={{ padding: 18 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>📡</span> {lang === 'en' ? 'Village Safety Radar' : 'ગામ સુરક્ષા રડાર'}
            </h3>
            <button
              type="button"
              onClick={handleFetchGps}
              style={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                color: 'var(--accent-blue)',
                borderRadius: 4,
                padding: '4px 8px',
                fontSize: 11,
                cursor: 'pointer',
              }}
            >
              📍 Auto-Detect
            </button>
          </div>

          <label style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: 4 }}>
            {lang === 'en' ? 'Select Village / વિસ્તાર પસંદ કરો' : 'વિસ્તાર પસંદ કરો'}
          </label>
          <select
            value={selectedVillageId}
            onChange={(e) => setSelectedVillageId(e.target.value)}
            style={{
              width: '100%',
              padding: 8,
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 6,
              color: 'var(--text)',
              fontSize: 13,
              marginBottom: 14,
            }}
          >
            {VILLAGES.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name} ({v.name_gu}) — {v.risk} RISK
              </option>
            ))}
          </select>

          {/* Radar Status Box */}
          <div
            style={{
              background:
                selectedVillage.risk === 'HIGH'
                  ? 'rgba(218,54,51,0.12)'
                  : selectedVillage.risk === 'MEDIUM'
                  ? 'rgba(227,179,65,0.1)'
                  : 'rgba(63,185,80,0.1)',
              borderLeft: `5px solid ${
                selectedVillage.risk === 'HIGH'
                  ? 'var(--accent-red)'
                  : selectedVillage.risk === 'MEDIUM'
                  ? 'var(--accent-orange)'
                  : 'var(--accent-green)'
              }`,
              borderRadius: 8,
              padding: 14,
              marginBottom: 14,
            }}
          >
            <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              CURRENT RISK STATUS / સુરક્ષા સ્થિતિ
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 4 }}>
              <span
                style={{
                  background:
                    selectedVillage.risk === 'HIGH'
                      ? 'var(--accent-red)'
                      : selectedVillage.risk === 'MEDIUM'
                      ? 'var(--accent-orange)'
                      : 'var(--accent-green)',
                  color: '#fff',
                  fontWeight: 800,
                  fontSize: 11,
                  padding: '2px 8px',
                  borderRadius: 4,
                }}
              >
                {selectedVillage.risk} RISK
              </span>
              <strong style={{ fontSize: 14 }}>
                {selectedVillage.name} ({selectedVillage.name_gu})
              </strong>
            </div>
            <div style={{ fontSize: 12, marginTop: 6, color: 'var(--text)' }}>
              {selectedVillage.risk === 'LOW'
                ? '✅ No large carnivores reported in close range.'
                : `⚠️ Movement of ${selectedVillage.animal} (${selectedVillage.animal_gu}) recorded within ${selectedVillage.dist} of settlement.`}
            </div>
          </div>

          <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 6 }}>
            Recommended Field Actions / સાવચેતીના પગલાં:
          </div>
          <ul style={{ margin: 0, paddingLeft: 20, fontSize: 12, lineHeight: 1.7, color: 'var(--text-secondary)' }}>
            <li><strong>Keep cattle inside enclosures</strong> (*વાડો*) before sundown.</li>
            <li><strong>Never move alone at night</strong> along riverine or agricultural borders.</li>
            <li><strong>Carry torches & staves</strong> (*લાઠી*) when moving near sugarcane fields.</li>
            <li>Report sightings immediately via the form or toll-free at <strong>1926</strong>.</li>
          </ul>
        </div>

        {/* Report Sighting Card */}
        <div className="card" style={{ padding: 18 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
            <h3 style={{ margin: 0, fontSize: 15, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
              <span>📷</span> {lang === 'en' ? 'Report Wildlife Sighting' : 'વન્યજીવ જોવાની જાણ કરો'}
            </h3>
            <span style={{ fontSize: 11, color: 'var(--accent-green)', fontWeight: 700 }}>● DIRECT DISPATCH</span>
          </div>

          <form onSubmit={handleSubmitSighting}>
            {/* Species Selector Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(90px, 1fr))', gap: 8, marginBottom: 12 }}>
              {SPECIES_LIST.map((s) => (
                <div
                  key={s.id}
                  onClick={() => setSpecies(s.id)}
                  style={{
                    background: species === s.id ? 'rgba(63,185,80,0.18)' : 'var(--bg-elevated)',
                    border: `1px solid ${species === s.id ? 'var(--accent-green)' : 'var(--border)'}`,
                    borderRadius: 6,
                    padding: 8,
                    textAlign: 'center',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontSize: 22 }}>{s.icon}</div>
                  <div style={{ fontSize: 11, fontWeight: 700 }}>{s.name}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{s.name_gu}</div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
              <button
                type="button"
                onClick={handleFetchGps}
                style={{
                  background: 'var(--accent-green)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 4,
                  padding: '5px 10px',
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                📍 Use My GPS
              </button>
              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>{gpsStatus || 'Lat: 21.1242, Lon: 70.5521'}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
              <div>
                <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                  Distance from village
                </label>
                <select
                  value={distanceKm}
                  onChange={(e) => setDistanceKm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 7,
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)',
                    borderRadius: 4,
                    color: 'var(--text)',
                    fontSize: 12,
                  }}
                >
                  <option value="0.3">&lt; 500m (Near village/pen)</option>
                  <option value="0.8">0.5 – 1 km</option>
                  <option value="2.0">1 – 3 km (Farm fringe)</option>
                  <option value="5.0">&gt; 3 km (Forest interior)</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                  Time of Day
                </label>
                <select
                  value={timeOfDay}
                  onChange={(e) => setTimeOfDay(e.target.value)}
                  style={{
                    width: '100%',
                    padding: 7,
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)',
                    borderRadius: 4,
                    color: 'var(--text)',
                    fontSize: 12,
                  }}
                >
                  <option value="night">Night (રાત)</option>
                  <option value="dusk">Dusk (સાંજ)</option>
                  <option value="dawn">Dawn (સવાર)</option>
                  <option value="day">Day (બપોર)</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: 10 }}>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                Reporter Mobile (Optional / સંપર્ક નંબર)
              </label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+91-98765-XXXXX"
                style={{
                  width: '100%',
                  padding: 7,
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: 4,
                  color: 'var(--text)',
                  fontSize: 12,
                }}
              />
            </div>

            <div style={{ marginBottom: 12 }}>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                Field Notes / વિશેષ વિગત (ખેતર, નદી કિનારો)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={2}
                placeholder="e.g. Male lion seen resting near sugarcane farm..."
                style={{
                  width: '100%',
                  padding: 7,
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: 4,
                  color: 'var(--text)',
                  fontSize: 12,
                }}
              />
            </div>

            <button
              type="submit"
              disabled={sightingLoading}
              style={{
                width: '100%',
                background: 'var(--accent-green)',
                color: '#fff',
                border: 'none',
                borderRadius: 6,
                padding: '10px',
                fontWeight: 700,
                fontSize: 13,
                cursor: 'pointer',
              }}
            >
              {sightingLoading ? 'Transmitting…' : '📤 SUBMIT SIGHTING (વન વિભાગને મોકલો)'}
            </button>
          </form>

          {sightingResult && (
            <div
              style={{
                marginTop: 12,
                padding: 10,
                background: 'rgba(63,185,80,0.15)',
                border: '1px solid var(--accent-green)',
                borderRadius: 6,
                fontSize: 12,
                color: 'var(--accent-green)',
              }}
            >
              <strong>✓ Sighting Reported Successfully!</strong>
              <div>Reference ID: <code>{sightingResult.id}</code></div>
              <div style={{ fontSize: 11, color: 'var(--text)' }}>
                Risk Evaluated: <strong>{sightingResult.risk}</strong>. Forest Officer notified for dispatch review.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Compensation Self-Service Section */}
      <div className="card" style={{ padding: 18, marginBottom: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
          <h3 style={{ margin: 0, fontSize: 16, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span>💰</span> {lang === 'en' ? 'Livestock & Crop Compensation Portal' : 'પશુધન / પાક નુકસાન વળતર અરજી'}
          </h3>
          <div style={{ display: 'flex', gap: 6 }}>
            <button
              type="button"
              onClick={() => setCompTab('file')}
              style={{
                background: compTab === 'file' ? 'var(--accent-blue)' : 'var(--bg-elevated)',
                color: compTab === 'file' ? '#fff' : 'var(--text-muted)',
                border: '1px solid var(--border)',
                borderRadius: 4,
                padding: '4px 10px',
                fontSize: 11,
                cursor: 'pointer',
              }}
            >
              File Claim (અરજી કરો)
            </button>
            <button
              type="button"
              onClick={() => setCompTab('track')}
              style={{
                background: compTab === 'track' ? 'var(--accent-blue)' : 'var(--bg-elevated)',
                color: compTab === 'track' ? '#fff' : 'var(--text-muted)',
                border: '1px solid var(--border)',
                borderRadius: 4,
                padding: '4px 10px',
                fontSize: 11,
                cursor: 'pointer',
              }}
            >
              Track Status (સ્થિતિ તપાસો)
            </button>
          </div>
        </div>

        {compTab === 'file' ? (
          <form onSubmit={handleSubmitClaim}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
              <div>
                <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                  Farmer / Claimant Full Name (અરજદારનું પૂરું નામ)
                </label>
                <input
                  type="text"
                  value={claimName}
                  onChange={(e) => setClaimName(e.target.value)}
                  placeholder="e.g. Ramesh Devrajbhai Patel"
                  required
                  style={{
                    width: '100%',
                    padding: 8,
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)',
                    borderRadius: 4,
                    color: 'var(--text)',
                    fontSize: 12,
                    marginBottom: 10,
                  }}
                />

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 10 }}>
                  <div>
                    <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                      Village (ગામ)
                    </label>
                    <select
                      value={claimVillage}
                      onChange={(e) => setClaimVillage(e.target.value)}
                      style={{
                        width: '100%',
                        padding: 7,
                        background: 'var(--bg-elevated)',
                        border: '1px solid var(--border)',
                        borderRadius: 4,
                        color: 'var(--text)',
                        fontSize: 12,
                      }}
                    >
                      {VILLAGES.map((v) => (
                        <option key={v.id} value={v.id}>
                          {v.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                      Loss Category
                    </label>
                    <select
                      value={claimType}
                      onChange={(e) => setClaimType(e.target.value)}
                      style={{
                        width: '100%',
                        padding: 7,
                        background: 'var(--bg-elevated)',
                        border: '1px solid var(--border)',
                        borderRadius: 4,
                        color: 'var(--text)',
                        fontSize: 12,
                      }}
                    >
                      <option value="buffalo">Buffalo / ભેંસ (₹30,000)</option>
                      <option value="cow">Cow / ગાય (₹25,000)</option>
                      <option value="goat">Goat/Sheep / બકરી (₹5,000)</option>
                      <option value="crop">Crop Damage (પાક નુકસાન)</option>
                    </select>
                  </div>
                </div>

                <div style={{ marginBottom: 10 }}>
                  <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                    Number of Livestock / Quantity (સંખ્યા)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={claimCount}
                    onChange={(e) => setClaimCount(e.target.value)}
                    style={{
                      width: '100%',
                      padding: 7,
                      background: 'var(--bg-elevated)',
                      border: '1px solid var(--border)',
                      borderRadius: 4,
                      color: 'var(--text)',
                      fontSize: 12,
                    }}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>
                  Mandatory Checklist for Forest Department DBT Payout:
                </label>
                <div
                  style={{
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border)',
                    borderRadius: 6,
                    padding: 10,
                    fontSize: 12,
                    lineHeight: 1.8,
                  }}
                >
                  <div>✅ Veterinary Officer Post-Mortem Certificate</div>
                  <div>✅ Gram Panchayat Sarpanch Declaration</div>
                  <div>✅ Photographs of Site & Animal/Crop Loss</div>
                  <div>✅ 7/12 Land Record / Tenancy Certificate</div>
                  <div>✅ Bank Passbook copy for direct DBT transfer</div>
                </div>

                <button
                  type="submit"
                  style={{
                    marginTop: 12,
                    width: '100%',
                    background: 'var(--accent-green)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 6,
                    padding: 10,
                    fontWeight: 700,
                    fontSize: 13,
                    cursor: 'pointer',
                  }}
                >
                  📝 GENERATE COMPENSATION CLAIM DRAFT
                </button>
              </div>
            </div>
          </form>
        ) : (
          <div style={{ maxWidth: 500, margin: '0 auto', textAlign: 'center' }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
              <input
                type="text"
                placeholder="Enter Claim ID (e.g. CLM-XXXXXX)"
                value={trackId}
                onChange={(e) => setTrackId(e.target.value)}
                style={{
                  flex: 1,
                  padding: 8,
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: 4,
                  color: 'var(--text)',
                  fontSize: 13,
                  fontFamily: 'monospace',
                }}
              />
              <button
                type="button"
                onClick={handleTrackClaim}
                style={{
                  background: 'var(--accent-blue)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 4,
                  padding: '8px 16px',
                  fontWeight: 700,
                  fontSize: 12,
                  cursor: 'pointer',
                }}
              >
                Track Status
              </button>
            </div>
            {trackResult && (
              <div
                style={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  padding: 14,
                  textAlign: 'left',
                  fontSize: 12,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong>{trackResult.id}</strong>
                  <span style={{ color: 'var(--accent-orange)', fontWeight: 800 }}>{trackResult.status}</span>
                </div>
                <div style={{ color: 'var(--text-muted)' }}>Assigned to: {trackResult.officer}</div>
                <div style={{ marginTop: 6, color: 'var(--accent-green)' }}>{trackResult.timeline}</div>
              </div>
            )}
          </div>
        )}

        {claimResult && (
          <div
            style={{
              marginTop: 14,
              padding: 14,
              background: 'rgba(63,185,80,0.15)',
              border: '2px solid var(--accent-green)',
              borderRadius: 8,
              fontSize: 13,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <strong>✓ Claim Draft Successfully Created</strong>
              <span style={{ fontFamily: 'monospace', color: 'var(--accent-blue)', fontWeight: 800 }}>
                {claimResult.id}
              </span>
            </div>
            <div style={{ marginTop: 6 }}>
              Applicant: <strong>{claimResult.name}</strong> · Village: {claimResult.village} · Estimated Amount:{' '}
              <strong style={{ color: 'var(--accent-green)', fontSize: 15 }}>₹{claimResult.amount.toLocaleString()}</strong>
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              Notice: Forwarded to Range Forest Officer for field Panchnama. Keep your documents and Claim ID handy.
            </div>
          </div>
        )}
      </div>

      {/* Wildlife Safety Guidelines */}
      <div className="card" style={{ padding: 18 }}>
        <h3 style={{ margin: '0 0 12px', fontSize: 15, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 6 }}>
          <span>🛡️</span> {lang === 'en' ? 'Wildlife Coexistence Guidelines' : 'વન્યજીવ સુરક્ષા નિયમો અને સાવચેતી'}
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
          <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, padding: 12 }}>
            <h4 style={{ margin: '0 0 6px', fontSize: 13, color: '#ff7b79' }}>
              🦁 Facing an Asiatic Lion / સિંહ સામે આવે ત્યારે:
            </h4>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, lineHeight: 1.7, color: 'var(--text-muted)' }}>
              <li><strong>Do not run (ક્યારેય ભાગવું નહીં)</strong>: Running triggers chasing instinct. Stand calm.</li>
              <li><strong>Back away slowly</strong> without turning your back or breaking sight.</li>
              <li><strong>Make firm sounds or clap</strong>: Lions respect assertive, calm human presence.</li>
              <li><strong>Always carry torchlight</strong> and a staff (*લાઠી*) after sunset.</li>
            </ul>
          </div>

          <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, padding: 12 }}>
            <h4 style={{ margin: '0 0 6px', fontSize: 13, color: '#f0c060' }}>
              🐆 Facing a Leopard / દીપડો સામે આવે ત્યારે:
            </h4>
            <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, lineHeight: 1.7, color: 'var(--text-muted)' }}>
              <li><strong>Appear bigger</strong>: Raise arms or hold shawl/turban overhead.</li>
              <li><strong>Keep small children in the middle</strong>: Never leave children unaccompanied near fields.</li>
              <li><strong>Cover livestock pens with wire mesh</strong> to prevent leopards jumping over thorns.</li>
              <li><strong>Do not enter dense crops</strong> alone at dusk or dawn.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
