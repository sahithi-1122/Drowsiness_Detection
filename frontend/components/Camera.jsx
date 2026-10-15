'use client';

import { useRef, useState, useEffect, useCallback } from 'react';

/**
 * Camera component with live monitoring and manual capture modes
 */
export default function Camera({ onCapture, disabled, isLive, onToggleLive }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const intervalRef = useRef(null);
  const previousFrameRef = useRef(null); // Store previous frame for optical flow
  const [error, setError] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [fps, setFps] = useState(0);
  const fpsCounterRef = useRef(0);

  // Initialize webcam
  useEffect(() => {
    const videoElement = videoRef.current;

    async function initCamera() {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'user'
          }
        });

        if (videoElement) {
          videoElement.srcObject = mediaStream;
          mediaStreamRef.current = mediaStream;
          setError(null);
        }
      } catch (err) {
        if (err.name === 'NotAllowedError') {
          setError('Camera permission denied. Please allow camera access and refresh.');
        } else if (err.name === 'NotFoundError') {
          setError('No camera found. Please connect a camera and refresh.');
        } else {
          setError(`Camera error: ${err.message}`);
        }
      }
    }

    initCamera();

    return () => {
      mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
      if (videoElement) videoElement.srcObject = null;
    };
  }, []);

  // Track FPS display (update every second)
  useEffect(() => {
    const fpsInterval = setInterval(() => {
      setFps(fpsCounterRef.current);
      fpsCounterRef.current = 0;
    }, 1000);
    return () => clearInterval(fpsInterval);
  }, []);

  // Capture a single frame and call onCapture
  const captureFrame = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !isReady) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA || !video.videoWidth || !video.videoHeight) {
      return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob && onCapture) {
        fpsCounterRef.current += 1;
        
        // Pass current frame and previous frame to parent
        onCapture(blob, previousFrameRef.current);
        
        // Store current frame as previous for next capture
        previousFrameRef.current = blob;
      }
    }, 'image/jpeg', 0.8);
  }, [isReady, onCapture]);

  // Start / stop the live loop based on isLive prop
  useEffect(() => {
    if (isLive && isReady) {
      // Send a frame every 1000 ms (1 fps — safe for CPU inference)
      intervalRef.current = setInterval(captureFrame, 1000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      previousFrameRef.current = null;
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isLive, isReady, captureFrame]);

  const handleVideoLoaded = () => setIsReady(true);

  if (error) {
    return (
      <div className="card bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-500">
        <div className="flex items-start space-x-3">
          <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <h3 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200">Camera Access Required</h3>
            <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-2">{error}</p>
            <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-sm font-medium transition">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Video preview */}
      <div className="relative bg-black rounded-xl overflow-hidden shadow-2xl">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          onLoadedData={handleVideoLoaded}
          className="w-full h-auto"
        />

        {!isReady && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75">
            <div className="text-center text-white">
              <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p>Initializing camera...</p>
            </div>
          </div>
        )}

        {/* Live badge */}
        {isReady && (
          <div className={`absolute top-4 left-4 flex items-center space-x-2 px-3 py-1.5 rounded-full shadow-lg text-white text-sm font-semibold ${isLive ? 'bg-red-600' : 'bg-gray-600'}`}>
            <div className={`w-2 h-2 rounded-full bg-white ${isLive ? 'animate-pulse' : ''}`}></div>
            <span>{isLive ? 'MONITORING' : 'PAUSED'}</span>
          </div>
        )}

        {/* FPS counter (only in live mode) */}
        {isLive && isReady && (
          <div className="absolute top-4 right-4 bg-black/60 text-white text-xs px-2 py-1 rounded">
            {fps} fps
          </div>
        )}

        {/* Drowsy overlay pulse (only in live mode — parent controls) */}
      </div>

      {/* Hidden canvas */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Controls */}
      <div className="flex gap-3">
        {/* Live monitor toggle */}
        <button
          onClick={onToggleLive}
          disabled={!isReady}
          className={`flex-1 text-base font-semibold flex items-center justify-center gap-2 py-3 rounded-xl transition-all shadow-md
            ${isLive
              ? 'bg-red-600 hover:bg-red-700 text-white'
              : 'bg-green-600 hover:bg-green-700 text-white'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isLive ? (
            <>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M6 6h4v12H6zm8 0h4v12h-4z"/>
              </svg>
              Stop Monitoring
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="9" strokeWidth="2"/>
                <circle cx="12" cy="12" r="3" fill="currentColor"/>
              </svg>
              Start Live Monitoring
            </>
          )}
        </button>

        {/* Manual capture (available only when not in live mode) */}
        {!isLive && (
          <button
            onClick={captureFrame}
            disabled={!isReady || disabled}
            className="flex-1 btn-primary text-base flex items-center justify-center gap-2 py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {disabled ? 'Processing...' : 'Capture Frame'}
          </button>
        )}
      </div>
    </div>
  );
}
