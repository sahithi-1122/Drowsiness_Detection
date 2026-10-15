'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Camera from '@/components/Camera';
import DetectionResult from '@/components/DetectionResult';
import { predictDrowsiness, testConnection, resetTemporalAnalyzer } from '@/lib/api';
import { triggerAlert, requestNotificationPermission } from '@/lib/notifications';

// Continuous drowsiness duration required before sounding the alarm.
const DROWSY_ALARM_SECONDS = 5;

export default function Home() {
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [isLive, setIsLive] = useState(false);
  const [drowsyStreak, setDrowsyStreak] = useState(0);
  const [isAlarming, setIsAlarming] = useState(false);
  const [sessionStats, setSessionStats] = useState({ total: 0, drowsy: 0, alert: 0 });
  const audioCtxRef = useRef(null);
  const alarmAudioRef = useRef(null);
  const alarmIntervalRef = useRef(null);
  const drowsySinceRef = useRef(null);
  const sessionIdRef = useRef(null);
  const isAlarmingRef = useRef(false);
  const lastNotifiedAlertLevelRef = useRef(0);
  const isProcessingRef = useRef(false); // prevent overlapping requests in live mode

  useEffect(() => {
    sessionIdRef.current = window.crypto?.randomUUID?.()
      || `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  }, []);

  // Check backend on mount and request notification permissions
  useEffect(() => {
    async function checkBackend() {
      const ok = await testConnection();
      setBackendStatus(ok ? 'connected' : 'disconnected');
    }
    checkBackend();
    
    // Request notification permissions
    requestNotificationPermission();
  }, []);

  // --------------- Audio alarm ---------------
  const playBeep = useCallback(() => {
    try {
      const audio = alarmAudioRef.current;
      if (audio && audio.readyState > 0) {
        audio.currentTime = 0;
        audio.play().catch(() => {});
        return;
      }

      if (!audioCtxRef.current) {
        audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
      }
      const ctx = audioCtxRef.current;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.type = 'square';
      osc.frequency.setValueAtTime(880, ctx.currentTime);
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
      osc.start(ctx.currentTime);
      osc.stop(ctx.currentTime + 0.4);
    } catch (_) {}
  }, []);

  const startAlarm = useCallback(() => {
    if (alarmIntervalRef.current) return;
    playBeep();
    alarmIntervalRef.current = setInterval(playBeep, 800);
    isAlarmingRef.current = true;
    setIsAlarming(true);
  }, [playBeep]);

  const stopAlarm = useCallback(() => {
    if (alarmIntervalRef.current) {
      clearInterval(alarmIntervalRef.current);
      alarmIntervalRef.current = null;
    }
    isAlarmingRef.current = false;
    setIsAlarming(false);
  }, []);

  // Stop alarm when live mode is turned off
  useEffect(() => {
    if (!isLive) stopAlarm();
  }, [isLive, stopAlarm]);

  // Cleanup alarm on unmount
  useEffect(() => () => stopAlarm(), [stopAlarm]);

  // --------------- Frame handler ---------------
  const handleCapture = useCallback(async (imageBlob, previousFrameBlob) => {
    // Skip if already waiting for a response (live mode)
    if (isProcessingRef.current) return;
    isProcessingRef.current = true;
    setIsLoading(true);
    setError(null);

    try {
      // Send both current and previous frame for optical flow analysis
      const result = await predictDrowsiness(imageBlob, {
        previousFrame: previousFrameBlob,
        extractCv: true,
        detectEyes: false,
        sessionId: sessionIdRef.current || 'default',
      });

      if (result.success && result.prediction) {
        const pred = result.prediction;
        setPrediction(pred);
        setBackendStatus('connected');

        const drowsy = pred.status === 'drowsy';

        setSessionStats(prev => ({
          total: prev.total + 1,
          drowsy: prev.drowsy + (drowsy ? 1 : 0),
          alert: prev.alert + (drowsy ? 0 : 1),
        }));

        // Enhanced alarm logic using temporal analysis
        if (drowsy) {
          const now = Date.now();
          if (drowsySinceRef.current === null) drowsySinceRef.current = now;
          const elapsedSeconds = (now - drowsySinceRef.current) / 1000;
          setDrowsyStreak(Math.floor(elapsedSeconds));
          
          // Use temporal analysis alert level for more intelligent alarming
          const temporalLevel = pred.temporal_analysis?.temporal_alert_level || 0;
          const consecutiveDrowsy = pred.temporal_analysis?.consecutive_drowsy || 0;
          
          // Trigger comprehensive alerts based on temporal level
          if (temporalLevel >= 2 && temporalLevel > lastNotifiedAlertLevelRef.current) {
            triggerAlert(temporalLevel, { muteVoice: isAlarmingRef.current });
            lastNotifiedAlertLevelRef.current = temporalLevel;
          } else if (temporalLevel < 2) {
            lastNotifiedAlertLevelRef.current = 0;
          }
          
          // Trigger audio alarm based on temporal alert level:
          // Level 2 (Warning): 3+ consecutive frames
          // Level 3 (Danger): 5+ consecutive frames or immediate
          if (elapsedSeconds >= DROWSY_ALARM_SECONDS) startAlarm();
        } else {
          drowsySinceRef.current = null;
          setDrowsyStreak(0);
          lastNotifiedAlertLevelRef.current = 0;
          stopAlarm();
        }
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      setError(err.message || 'Failed to analyze image.');
      setBackendStatus('disconnected');
      drowsySinceRef.current = null;
      setDrowsyStreak(0);
      lastNotifiedAlertLevelRef.current = 0;
      stopAlarm();
    } finally {
      setIsLoading(false);
      isProcessingRef.current = false;
    }
  }, [startAlarm, stopAlarm]);

  const handleToggleLive = async () => {
    if (isLive) {
      drowsySinceRef.current = null;
      setDrowsyStreak(0);
      lastNotifiedAlertLevelRef.current = 0;
      stopAlarm();
      setIsLive(false);
      return;
    }

    await resetTemporalAnalyzer(sessionIdRef.current || 'default');
    setSessionStats({ total: 0, drowsy: 0, alert: 0 });
    setPrediction(null);
    setError(null);
    drowsySinceRef.current = null;
    lastNotifiedAlertLevelRef.current = 0;
    setIsLive(true);
  };

  const drowsyPercent = sessionStats.total > 0
    ? ((sessionStats.drowsy / sessionStats.total) * 100).toFixed(1)
    : '0.0';

  // Get temporal alert level from current prediction
  const temporalAlertLevel = prediction?.temporal_analysis?.temporal_alert_level || 0;
  const temporalRecommendation = prediction?.temporal_analysis?.recommendation || '';

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Multi-level alert overlays */}
      {isAlarming && (
        <div className="fixed inset-0 pointer-events-none z-50 border-8 border-red-600 animate-pulse rounded-none" />
      )}
      
      {/* Temporal alert banner (shows even before full alarm) */}
      {isLive && temporalAlertLevel >= 2 && !isAlarming && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-40 animate-bounce">
          <div className={`px-6 py-3 rounded-lg shadow-lg font-bold text-white ${
            temporalAlertLevel >= 3 ? 'bg-red-600' : 'bg-orange-500'
          }`}>
            ⚠️ {temporalAlertLevel >= 3 ? 'DANGER' : 'WARNING'}: Drowsiness Detected
          </div>
        </div>
      )}

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-3">
            🚗 Driver Drowsiness Detection
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Real-time AI-powered drowsiness detection using computer vision and deep learning
          </p>

          <div className="mt-4 flex items-center justify-center gap-4 flex-wrap">
            {/* Backend status */}
            <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium bg-white dark:bg-slate-800 shadow">
              <div className={`w-2 h-2 rounded-full ${
                backendStatus === 'connected' ? 'bg-green-500 animate-pulse' :
                backendStatus === 'disconnected' ? 'bg-red-500' :
                'bg-yellow-500 animate-pulse'
              }`} />
              <span className="text-gray-700 dark:text-gray-300">
                Backend: {backendStatus === 'connected' ? 'Connected' : backendStatus === 'disconnected' ? 'Disconnected' : 'Checking...'}
              </span>
            </div>

            {/* Alarm badge */}
            {isAlarming && (
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-bold bg-red-600 text-white shadow animate-bounce">
                🚨 DROWSINESS ALERT
              </div>
            )}
          </div>
        </header>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left: Camera */}
          <div className="space-y-6">
            <div className="card">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Live Camera Feed
              </h2>
              <Camera
                onCapture={handleCapture}
                disabled={isLoading}
                isLive={isLive}
                onToggleLive={handleToggleLive}
              />
              <audio ref={alarmAudioRef} src="/alarm.mp3" preload="auto" aria-hidden="true" />
            </div>

            {/* Session stats (visible once monitoring started) */}
            {sessionStats.total > 0 && (
              <div className="card">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Session Summary</h3>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="bg-slate-100 dark:bg-slate-700 rounded-lg p-3">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{sessionStats.total}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Frames</div>
                  </div>
                  <div className="bg-green-100 dark:bg-green-900/30 rounded-lg p-3">
                    <div className="text-2xl font-bold text-green-700 dark:text-green-300">{sessionStats.alert}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Alert</div>
                  </div>
                  <div className="bg-red-100 dark:bg-red-900/30 rounded-lg p-3">
                    <div className="text-2xl font-bold text-red-700 dark:text-red-300">{sessionStats.drowsy}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Drowsy</div>
                  </div>
                </div>
                <div className="mt-3">
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                    <span>Drowsy frames</span>
                    <span>{drowsyPercent}%</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500 bg-red-500"
                      style={{ width: `${drowsyPercent}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Instructions */}
            <div className="card bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-800">
              <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-200 mb-3 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                How to Use
              </h3>
              <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800 dark:text-blue-300">
                <li>Allow camera access when prompted</li>
                <li>Click <strong>Start Live Monitoring</strong> for continuous analysis</li>
                <li>Or click <strong>Capture Frame</strong> for a single snapshot</li>
                <li>Alarm sounds after {DROWSY_ALARM_SECONDS} seconds of continuous drowsiness</li>
              </ol>
            </div>
          </div>

          {/* Right: Results */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Detection Results
                {isLoading && (
                  <span className="ml-auto text-xs font-normal text-gray-400 flex items-center gap-1">
                    <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    Analyzing...
                  </span>
                )}
              </h2>

              <DetectionResult
                prediction={prediction}
                error={error}
                drowsyStreak={drowsyStreak}
                isAlarming={isAlarming}
              />
            </div>

            {/* Info cards (only when idle) */}
            {!prediction && !error && (
              <div className="space-y-4">
                <div className="card bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-2 border-purple-200 dark:border-purple-800">
                  <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-200 mb-2">🤖 AI-Powered Detection</h3>
                  <p className="text-sm text-purple-800 dark:text-purple-300">
                    YOLOv8 fine-tuned on UTA-RLDD to classify driver images as Alert or Drowsy. This is a research prototype, not a safety system.
                  </p>
                </div>
                <div className="card bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-2 border-green-200 dark:border-green-800">
                  <h3 className="text-lg font-semibold text-green-900 dark:text-green-200 mb-2">🎯 Live Monitoring</h3>
                  <p className="text-sm text-green-800 dark:text-green-300">
                    Analyzes 1 frame/second continuously. Alarm triggers after {DROWSY_ALARM_SECONDS} seconds of continuous drowsiness.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-sm text-gray-500 dark:text-gray-400 space-y-2">
          <p>Built with Next.js, FastAPI, and YOLOv8 · Team 25</p>
          <p className="text-xs">
            Dataset:{' '}
            <a href="https://www.kaggle.com/datasets/minhngt02/uta-rldd" target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
              UTA Real-Life Drowsiness Dataset (UTA-RLDD)
            </a>
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-600">
            ⚠️ This is an assistive prototype. It is not a replacement for safe driving.
          </p>
        </footer>
      </div>
    </main>
  );
}
