/**
 * API client for Driver Drowsiness Detection backend
 * Source: frontend/lib/api.js
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Default request timeout in ms
const REQUEST_TIMEOUT_MS = 30000;

/**
 * Wraps fetch with a timeout so the UI shows a readable error
 * instead of hanging indefinitely (important for cold starts on Render).
 */
async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    return response;
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error(
        'Request timed out. The backend may be starting up (cold start). Please try again.'
      );
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Check backend health.
 * @returns {Promise<boolean>} true if healthy
 */
export async function testConnection() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/health`);
    if (!response.ok) return false;
    const data = await response.json();
    return data.status === 'healthy' || data.model_loaded === true;
  } catch {
    return false;
  }
}

/**
 * Full health check — returns the raw JSON for diagnostics.
 * @returns {Promise<object|null>}
 */
export async function checkHealth() {
  try {
    const response = await fetchWithTimeout(`${API_BASE_URL}/health`);
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

/**
 * Send a frame to the /predict endpoint.
 *
 * @param {Blob} imageBlob       Current webcam frame (JPEG blob)
 * @param {object} [options]
 * @param {Blob}   [options.previousFrame]  Previous frame for optical-flow analysis
 * @param {boolean} [options.extractCv]     Extract HOG / Sobel / OF / Morphology (default true)
 * @param {boolean} [options.detectEyes]    Run eye-closure detection (unavailable by default)
 * @param {boolean} [options.useTemporal]   Apply temporal smoothing (default true)
 * @param {string} [options.sessionId]      Monitoring session identifier
 * @returns {Promise<{success: boolean, prediction: object}>}
 */
export async function predictDrowsiness(imageBlob, options = {}) {
  const {
    previousFrame = null,
    extractCv     = true,
    detectEyes    = false,
    useTemporal   = true,
    sessionId     = 'default',
  } = options;

  const formData = new FormData();
  formData.append('file', imageBlob, 'capture.jpg');

  if (previousFrame) {
    formData.append('previous_frame', previousFrame, 'prev_capture.jpg');
  }

  // Build query string for boolean flags
  const params = new URLSearchParams({
    extract_cv:   String(extractCv),
    detect_eyes:  String(detectEyes),
    use_temporal: String(useTemporal),
    session_id:   sessionId,
  });

  const response = await fetchWithTimeout(
    `${API_BASE_URL}/predict?${params.toString()}`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    let detail = `Server error: ${response.status}`;
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch {
      // ignore JSON parse error
    }
    throw new Error(detail);
  }

  return response.json();
}

/**
 * Reset the backend temporal analyzer.
 * Call this at the start of each new monitoring session.
 * @returns {Promise<void>}
 */
export async function resetTemporalAnalyzer(sessionId = 'default') {
  try {
    const params = new URLSearchParams({ session_id: sessionId });
    const response = await fetchWithTimeout(`${API_BASE_URL}/reset-temporal?${params}`, {
      method: 'POST',
    });
    if (!response.ok) {
      console.warn('Failed to reset temporal analyzer:', response.status);
    }
  } catch (err) {
    console.warn('resetTemporalAnalyzer error:', err.message);
  }
}
