import type { EmergencyAlertData } from '../components/Citizen/EmergencyAlertModal';

const BROADCAST_CHANNEL_NAME = 'vanrakshak_emergency_broadcast';
const STORAGE_KEY = 'vanrakshak_latest_emergency_alert';

/**
 * Broadcast an emergency alert across all open tabs, windows, and devices.
 * Uses BroadcastChannel for instant messaging and localStorage for cross-tab storage events.
 */
export function broadcastEmergencyAlert(data: EmergencyAlertData): void {
  const payload: EmergencyAlertData = {
    ...data,
    timestamp: data.timestamp || new Date().toISOString(),
  };

  // 1. BroadcastChannel (modern zero-latency inter-tab communication)
  try {
    if (typeof BroadcastChannel !== 'undefined') {
      const channel = new BroadcastChannel(BROADCAST_CHANNEL_NAME);
      channel.postMessage({ type: 'EMERGENCY_ALERT', payload });
      setTimeout(() => channel.close(), 100);
    }
  } catch (err) {
    console.warn('BroadcastChannel error:', err);
  }

  // 2. LocalStorage event (supported across all browsers and windows)
  try {
    const serialized = JSON.stringify({
      id: Math.random().toString(36).substring(2, 9),
      time: Date.now(),
      payload,
    });
    localStorage.setItem(STORAGE_KEY, serialized);
  } catch (err) {
    console.warn('localStorage broadcast error:', err);
  }

  // 3. Dispatch custom window event for in-tab listeners
  try {
    window.dispatchEvent(
      new CustomEvent('vanrakshak_local_emergency_alert', { detail: payload })
    );
  } catch (err) {
    console.warn('CustomEvent dispatch error:', err);
  }
}

// Attach to window object for developer debugging / interactive testing
if (typeof window !== 'undefined') {
  (window as any).broadcastEmergencyAlert = broadcastEmergencyAlert;
  (window as any).generateEmergencyAlert = (village = 'Sasan Gir', species = 'Asiatic Lion') => {
    broadcastEmergencyAlert({
      alert_id: 'ALT-' + Math.random().toString(36).substring(2, 7).toUpperCase(),
      village_name: village,
      species,
      severity: 'HIGH',
      distance_km: 0.6,
      timestamp: new Date().toISOString(),
      en_text: `EMERGENCY: ${species} detected near ${village} settlement. Village nodes alerted.`,
      gu_text: `તાત્કાલિક એલર્ટ: ${village} નજીક ${species} ની હિલચાલ નોંધાઈ છે. સાવચેત રહો.`,
      safety_actions: [
        'Secure all cattle inside enclosures immediately',
        'Avoid moving outside alone after dusk',
        'Keep emergency torches lit and call 1926 if spotted',
      ],
    });
  };
}
