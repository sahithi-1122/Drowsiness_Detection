/**
 * Browser notifications and voice alerts for driver drowsiness warnings.
 * Source: frontend/lib/notifications.js
 *
 * Safety note: This is a prototype warning aid only.
 * It is NOT a substitute for safe driving practices.
 */

/**
 * Request browser notification permission.
 * Should be called once on app mount.
 */
export async function requestNotificationPermission() {
  if (typeof window === 'undefined') return;
  if (!('Notification' in window)) return;
  if (Notification.permission === 'default') {
    await Notification.requestPermission();
  }
}

/**
 * Show a browser notification if permission is granted.
 *
 * @param {string} title   Notification title
 * @param {string} body    Notification body
 */
function showNotification(title, body) {
  if (typeof window === 'undefined') return;
  if (!('Notification' in window)) return;
  if (Notification.permission !== 'granted') return;

  try {
    new Notification(title, {
      body,
      icon: '/favicon.ico',
      tag: 'drowsiness-alert',   // replaces any existing notification with the same tag
      renotify: true,
    });
  } catch {
    // Notifications may be blocked in certain contexts
  }
}

/**
 * Speak a message using the Web Speech API if available.
 *
 * @param {string} message   Text to speak
 */
function speak(message) {
  if (typeof window === 'undefined') return;
  if (!window.speechSynthesis) return;

  try {
    // Cancel any ongoing speech first
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(message);
    utterance.rate   = 1.1;
    utterance.pitch  = 1.0;
    utterance.volume = 1.0;

    window.speechSynthesis.speak(utterance);
  } catch {
    // Speech synthesis may not be available
  }
}

/**
 * Trigger a composite alert (notification + optional voice) based on alert level.
 *
 * Level 1 — Caution   : browser notification only
 * Level 2 — Warning   : notification + voice warning
 * Level 3 — Danger    : notification + louder voice + "pull over" message
 *
 * @param {number}  level              Temporal alert level (1–3)
 * @param {object}  [options]
 * @param {boolean} [options.muteVoice]  Skip voice if audio alarm is already sounding
 */
export function triggerAlert(level, options = {}) {
  const { muteVoice = false } = options;

  if (level <= 0) return;

  const messages = {
    1: {
      title: '⚡ Drowsiness Caution',
      body:  'Slight fatigue detected. Stay vigilant.',
      voice: null,
    },
    2: {
      title: '⚠️ Drowsiness Warning',
      body:  'Moderate drowsiness detected. Consider taking a break.',
      voice: 'Warning. Drowsiness detected. Please stay alert.',
    },
    3: {
      title: '🚨 DANGER — Pull Over Now',
      body:  'Sustained drowsiness detected. Stop driving immediately.',
      voice: 'Danger! Sustained drowsiness detected. Pull over and rest immediately.',
    },
  };

  const alert = messages[Math.min(level, 3)];
  if (!alert) return;

  showNotification(alert.title, alert.body);

  if (!muteVoice && alert.voice) {
    speak(alert.voice);
  }
}
