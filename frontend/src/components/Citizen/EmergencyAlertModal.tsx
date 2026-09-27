import { useState, useEffect, useRef } from 'react';

export interface EmergencyAlertData {
  alert_id?: string;
  village_id?: string;
  village_name?: string;
  species?: string;
  severity?: 'HIGH' | 'MEDIUM' | 'LOW';
  distance_km?: number;
  timestamp?: string;
  en_text?: string;
  gu_text?: string;
  safety_actions?: string[];
}

export default function EmergencyAlertModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [alertData, setAlertData] = useState<EmergencyAlertData | null>(null);
  const [isSirenActive, setIsSirenActive] = useState(false);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const oscRef = useRef<OscillatorNode | null>(null);
  const intervalRef = useRef<any>(null);

  const stopSiren = () => {
    setIsSirenActive(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (oscRef.current) {
      try {
        oscRef.current.stop();
        oscRef.current.disconnect();
      } catch (e) {}
      oscRef.current = null;
    }
    if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
      try {
        audioCtxRef.current.close();
      } catch (e) {}
      audioCtxRef.current = null;
    }
  };

  const playSiren = () => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;

      stopSiren();

      const ctx = new AudioCtx();
      audioCtxRef.current = ctx;

      if (ctx.state === 'suspended') {
        ctx.resume().catch(() => {});
      }

      const masterGain = ctx.createGain();
      masterGain.gain.setValueAtTime(0.2, ctx.currentTime);
      masterGain.connect(ctx.destination);

      const osc = ctx.createOscillator();
      osc.type = 'sawtooth';

      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(1400, ctx.currentTime);

      osc.connect(filter);
      filter.connect(masterGain);

      let isHigh = true;
      osc.frequency.setValueAtTime(920, ctx.currentTime);
      osc.start();
      oscRef.current = osc;
      setIsSirenActive(true);

      intervalRef.current = setInterval(() => {
        if (!ctx || ctx.state === 'closed') {
          clearInterval(intervalRef.current);
          return;
        }
        isHigh = !isHigh;
        const targetFreq = isHigh ? 920 : 680;
        const now = ctx.currentTime;
        try {
          osc.frequency.cancelScheduledValues(now);
          osc.frequency.linearRampToValueAtTime(targetFreq, now + 0.08);
        } catch (e) {}
      }, 360);

      // Auto shut off after 25s
      setTimeout(() => {
        stopSiren();
      }, 25000);
    } catch (err) {
      console.warn('Audio siren failed:', err);
      setIsSirenActive(false);
    }
  };

  const triggerAlert = (data: EmergencyAlertData, playSound = true) => {
    setAlertData(data);
    setIsOpen(true);
    if (playSound) {
      playSiren();
    }
  };

  const handleClose = () => {
    stopSiren();
    setIsOpen(false);
  };

  useEffect(() => {
    (window as any).triggerEmergencyAlert = (data: EmergencyAlertData) => triggerAlert(data, true);

    const channel = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('vanrakshak_emergency_broadcast') : null;
    if (channel) {
      channel.onmessage = (e) => {
        if (e?.data?.type === 'EMERGENCY_ALERT') {
          triggerAlert(e.data.payload, true);
        }
      };
    }

    const onStorage = (e: StorageEvent) => {
      if (e.key === 'vanrakshak_latest_emergency_alert' && e.newValue) {
        try {
          const parsed = JSON.parse(e.newValue);
          if (parsed?.payload) {
            triggerAlert(parsed.payload, true);
          }
        } catch (err) {}
      }
    };
    window.addEventListener('storage', onStorage);

    return () => {
      stopSiren();
      if (channel) channel.close();
      window.removeEventListener('storage', onStorage);
    };
  }, []);

  if (!isOpen || !alertData) return null;

  const species = alertData.species || 'Asiatic Lion';
  const village = alertData.village_name || alertData.village_id || 'Sasan Gir';
  const dist = alertData.distance_km != null ? alertData.distance_km : 0.8;
  const sev = (alertData.severity || 'HIGH').toUpperCase();

  return (
    <div className="citizen-emergency-popup" role="dialog" aria-modal="true">
      <div className="citizen-emergency-backdrop" onClick={handleClose} />
      <div className="citizen-emergency-box">
        {/* Head */}
        <div className="citizen-emergency-head">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span className="emergency-beacon-icon">🚨</span>
            <div>
              <div className="citizen-emergency-tag">
                <span className="pulse-dot" /> EMERGENCY BROADCAST / આપાતકાલીન એલર્ટ
              </div>
              <h4 className="citizen-emergency-title">
                WILDLIFE ALERT: {species.toUpperCase()} SIGHTED
              </h4>
            </div>
          </div>
          <button className="citizen-emergency-close" onClick={handleClose} title="Close">
            ✕
          </button>
        </div>

        {/* Sound Bar */}
        <div className="citizen-sound-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className={`sound-wave-bars ${!isSirenActive ? 'muted' : ''}`}>
              <span className="bar bar-1" />
              <span className="bar bar-2" />
              <span className="bar bar-3" />
              <span className="bar bar-4" />
              <span className="bar bar-5" />
            </div>
            <span className="sound-label">
              {isSirenActive ? '🔊 Audio Siren Active / સાયરન ચાલુ છે' : '🔇 Siren Silenced / સાયરન બંધ છે'}
            </span>
          </div>
          <button
            className="siren-mute-btn"
            onClick={isSirenActive ? stopSiren : playSiren}
          >
            {isSirenActive ? 'Silence Siren' : 'Play Siren'}
          </button>
        </div>

        {/* Badges */}
        <div className="emergency-badge-row">
          <span className={sev === 'HIGH' ? 'emergency-badge-danger' : 'emergency-badge-warning'}>
            ⚠️ {sev} RISK / {sev === 'HIGH' ? 'અતિ જોખમ' : 'મધ્યમ જોખમ'}
          </span>
          <span className="emergency-badge-village">
            📍 {village} ({dist} km)
          </span>
          <span className="emergency-badge-time">
            🕒 Just Now / હમણાં જ
          </span>
        </div>

        {/* Warning messages */}
        <div className="emergency-message-wrap">
          <div className="emergency-msg-en">
            {alertData.en_text ||
              `Dangerous wildlife (${species}) detected within ${dist} km of ${village}. Move indoors and guard cattle immediately.`}
          </div>
          <div className="emergency-msg-gu">
            {alertData.gu_text ||
              `ચેતવણી: ${village} ગામ પાસે ${species} ની હિલચાલ નોંધાઈ છે (${dist} કિમી). પશુધનને બંધ વાડામાં રાખો અને સાવચેત રહો.`}
          </div>
        </div>

        {/* Safety actions */}
        <div className="emergency-actions-card">
          <div className="emergency-actions-title">IMMEDIATE SAFETY ACTIONS / તાત્કાલિક સાવચેતી:</div>
          <ul className="emergency-checklist">
            <li><strong>Secure Livestock</strong> — Move cattle, goats, and buffaloes inside covered pens immediately.</li>
            <li><strong>Stay Indoors</strong> — Avoid solitary movement; keep perimeter lamps and high-beam torches lit.</li>
            <li><strong>Report Activity</strong> — If animal is spotted near your house, dial toll-free 1926 immediately.</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="citizen-emergency-footer">
          <a href="tel:1926" className="emergency-call-btn">
            📞 Call Forest Helpline 1926
          </a>
          <button className="emergency-ack-btn" onClick={handleClose}>
            ✓ I Acknowledge / સ્વીકાર્યું
          </button>
        </div>
      </div>
    </div>
  );
}
