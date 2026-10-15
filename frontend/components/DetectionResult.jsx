/**
 * Detection result display component
 */
export default function DetectionResult({ prediction, error, drowsyStreak = 0, isAlarming = false }) {
  if (error) {
    return (
      <div className="card bg-red-50 dark:bg-red-900/20 border-2 border-red-500">
        <div className="flex items-start space-x-3">
          <svg className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 className="text-lg font-semibold text-red-700 dark:text-red-300">Error</h3>
            <p className="text-sm text-red-600 dark:text-red-400 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="card border-2 border-dashed border-gray-300 dark:border-gray-600">
        <div className="text-center text-gray-500 dark:text-gray-400 py-8">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <p className="text-lg font-medium">No detection yet</p>
          <p className="text-sm mt-1">Start live monitoring or capture a frame</p>
        </div>
      </div>
    );
  }

  const { label, confidence, confidence_basis, raw_confidence, status, all_probs, cv_features, cv_validation, eye_analysis, eye_closure_detected, eye_closure_warning, temporal_analysis, temporal_smoothed, raw_prediction } = prediction;
  const isDrowsy = status === 'drowsy';

  return (
    <div className="space-y-4">
      {/* Alarm banner */}
      {isAlarming && (
        <div className="flex items-center gap-3 px-4 py-3 bg-red-600 text-white rounded-xl font-bold text-lg animate-pulse shadow-lg">
          <span className="text-2xl">🚨</span>
          <span>DROWSINESS ALERT! Please rest.</span>
        </div>
      )}

      {/* Main result card */}
      <div className={`card ${isDrowsy
        ? 'bg-red-50 dark:bg-red-900/20 border-2 border-red-500'
        : 'bg-green-50 dark:bg-green-900/20 border-2 border-green-500'}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Status icon */}
            <div className={`w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0 ${isDrowsy ? 'bg-red-500' : 'bg-green-500'}`}>
              {isDrowsy ? (
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              ) : (
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>

            {/* Status text */}
            <div>
              <h2 className={`text-2xl font-bold ${isDrowsy ? 'text-red-700 dark:text-red-300' : 'text-green-700 dark:text-green-300'}`}>
                {isDrowsy ? '😴 Drowsy Detected' : '✅ Driver Alert'}
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Class: <span className="font-semibold">{label}</span>
              </p>
              {isDrowsy && drowsyStreak > 0 && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1 font-medium">
                  🔁 {drowsyStreak} consecutive drowsy frame{drowsyStreak > 1 ? 's' : ''}
                </p>
              )}
            </div>
          </div>

          {/* Confidence */}
          <div className="text-right flex-shrink-0">
            <div className={`text-3xl font-bold ${isDrowsy ? 'text-red-700 dark:text-red-300' : 'text-green-700 dark:text-green-300'}`}>
              {(confidence * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {confidence_basis === 'temporal_vote' ? 'Recent-frame vote support' : 'Model confidence'}
            </div>
          </div>
        </div>

        {/* Confidence bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs mb-1 text-gray-500 dark:text-gray-400">
            <span>{confidence_basis === 'temporal_vote' ? 'Recent-frame vote support' : 'Model confidence'}</span>
            <span>{(confidence * 100).toFixed(2)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${isDrowsy ? 'bg-red-500' : 'bg-green-500'}`}
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
        </div>

        {temporal_smoothed && raw_prediction && raw_confidence != null && (
          <p className="mt-3 text-xs text-gray-600 dark:text-gray-400">
            Current frame: {raw_prediction} ({(raw_confidence * 100).toFixed(1)}% model confidence)
          </p>
        )}
      </div>

      {/* Eye Closure Detection */}
      {eye_analysis && (
        <div className={`card ${eye_analysis.eyes_likely_closed 
          ? 'bg-orange-50 dark:bg-orange-900/20 border-2 border-orange-500' 
          : 'bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-800'}`}
        >
          <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <span className={eye_analysis.eyes_likely_closed ? 'text-orange-900 dark:text-orange-200' : 'text-blue-900 dark:text-blue-200'}>
              Eye Closure Detection
            </span>
            {eye_closure_detected && (
              <span className="ml-auto text-xs font-bold text-red-600 dark:text-red-400 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-red-600 animate-pulse"></span>
                CRITICAL
              </span>
            )}
            {eye_closure_warning && (
              <span className="ml-auto text-xs font-bold text-yellow-600 dark:text-yellow-400 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-yellow-600 animate-pulse"></span>
                WARNING
              </span>
            )}
          </h3>
          
          <div className="space-y-3">
            {/* Detection status */}
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">Face Detected:</span>
              <span className={`text-sm font-semibold ${eye_analysis.face_detected ? 'text-green-600' : 'text-red-600'}`}>
                {eye_analysis.face_detected ? '✓ Yes' : '✗ No'}
              </span>
            </div>
            
            {eye_analysis.face_detected && (
              <>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Eyes Detected:</span>
                  <span className={`text-sm font-semibold ${eye_analysis.eyes_detected ? 'text-green-600' : 'text-yellow-600'}`}>
                    {eye_analysis.both_eyes_detected ? '✓ Both' : eye_analysis.eyes_detected ? '⚠ One' : '✗ None'}
                  </span>
                </div>
                
                {eye_analysis.eyes_detected && (
                  <>
                    {/* Closure score */}
                    <div>
                      <div className="flex justify-between text-xs mb-1 text-gray-600 dark:text-gray-400">
                        <span>Eye Closure Score</span>
                        <span>{(eye_analysis.overall_closure_score * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-300 ${
                            eye_analysis.overall_closure_score > 0.7 ? 'bg-red-500' :
                            eye_analysis.overall_closure_score > 0.4 ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${eye_analysis.overall_closure_score * 100}%` }}
                        />
                      </div>
                    </div>
                    
                    {/* Eye status */}
                    <div className={`text-center py-2 px-3 rounded-lg ${
                      eye_analysis.eyes_likely_closed 
                        ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300' 
                        : 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                    }`}>
                      <span className="text-sm font-bold">
                        {eye_analysis.eyes_likely_closed ? '👁️ Eyes Closed' : '👀 Eyes Open'}
                      </span>
                    </div>
                    
                    {/* Individual eye analysis */}
                    {(eye_analysis.left_eye || eye_analysis.right_eye) && (
                      <div className="grid grid-cols-2 gap-2 mt-2">
                        {eye_analysis.left_eye && (
                          <div className="bg-white dark:bg-slate-800 rounded-lg p-2 text-xs">
                            <div className="font-semibold text-gray-700 dark:text-gray-300 mb-1">Left Eye</div>
                            <div className="text-gray-600 dark:text-gray-400">
                              Ratio: {eye_analysis.left_eye.aspect_ratio?.toFixed(3) || 'N/A'}
                            </div>
                            <div className={`font-semibold ${eye_analysis.left_eye.is_closed ? 'text-red-600' : 'text-green-600'}`}>
                              {eye_analysis.left_eye.is_closed ? 'Closed' : 'Open'}
                            </div>
                          </div>
                        )}
                        {eye_analysis.right_eye && (
                          <div className="bg-white dark:bg-slate-800 rounded-lg p-2 text-xs">
                            <div className="font-semibold text-gray-700 dark:text-gray-300 mb-1">Right Eye</div>
                            <div className="text-gray-600 dark:text-gray-400">
                              Ratio: {eye_analysis.right_eye.aspect_ratio?.toFixed(3) || 'N/A'}
                            </div>
                            <div className={`font-semibold ${eye_analysis.right_eye.is_closed ? 'text-red-600' : 'text-green-600'}`}>
                              {eye_analysis.right_eye.is_closed ? 'Closed' : 'Open'}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </>
                )}
              </>
            )}
            
            {/* Confidence indicator */}
            <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
              Detection confidence: {(eye_analysis.confidence * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      )}

      {/* Temporal Analysis */}
      {temporal_analysis && (
        <div className="card bg-indigo-50 dark:bg-indigo-900/20 border-2 border-indigo-200 dark:border-indigo-800">
          <h3 className="text-sm font-semibold text-indigo-900 dark:text-indigo-200 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Temporal Analysis (Smoothing Over Time)
            {temporal_smoothed && raw_prediction && (
              <span className="ml-auto text-xs text-indigo-600 dark:text-indigo-400">
                Raw: {raw_prediction}
              </span>
            )}
          </h3>
          
          <div className="space-y-3">
            {/* Alert Level */}
            <div className="grid grid-cols-4 gap-2">
              {[0, 1, 2, 3].map(level => {
                const isActive = temporal_analysis.temporal_alert_level >= level;
                const labels = ['Safe', 'Caution', 'Warning', 'Danger'];
                const colors = [
                  'bg-green-500',
                  'bg-yellow-500',
                  'bg-orange-500',
                  'bg-red-500'
                ];
                return (
                  <div
                    key={level}
                    className={`text-center py-2 rounded-lg text-xs font-semibold transition-all ${
                      isActive 
                        ? `${colors[level]} text-white shadow-md` 
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                    }`}
                  >
                    {labels[level]}
                  </div>
                );
              })}
            </div>
            
            {/* Metrics */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-white dark:bg-slate-800 rounded-lg p-3">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Consecutive Drowsy</div>
                <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                  {temporal_analysis.consecutive_drowsy}
                </div>
                <div className="text-xs text-gray-500">frames</div>
              </div>
              
              <div className="bg-white dark:bg-slate-800 rounded-lg p-3">
                <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Drowsy Rate</div>
                <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                  {(temporal_analysis.drowsy_rate * 100).toFixed(0)}%
                </div>
                <div className="text-xs text-gray-500">
                  in {temporal_analysis.buffer_size} frames
                </div>
              </div>
            </div>
            
            {/* Recommendation */}
            <div className={`p-3 rounded-lg text-sm font-medium ${
              temporal_analysis.temporal_alert_level >= 3 ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' :
              temporal_analysis.temporal_alert_level >= 2 ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300' :
              temporal_analysis.temporal_alert_level >= 1 ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' :
              'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
            }`}>
              <div className="font-bold mb-1">
                {temporal_analysis.temporal_alert_level >= 3 ? '🚨' : 
                 temporal_analysis.temporal_alert_level >= 2 ? '⚠️' :
                 temporal_analysis.temporal_alert_level >= 1 ? '⚡' : '✓'} Recommendation
              </div>
              {temporal_analysis.recommendation}
            </div>
            
            {/* Additional metrics */}
            <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400">
              <span>Recent Trend: {(temporal_analysis.recent_drowsy_rate * 100).toFixed(0)}%</span>
              <span>Eye Closure: {(temporal_analysis.eye_closure_rate * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>
      )}

      {/* CV Features (Task 6) */}
      {cv_features && (
        <div className="card bg-purple-50 dark:bg-purple-900/20 border-2 border-purple-200 dark:border-purple-800">
          <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-200 mb-3 flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
            Computer Vision Features
          </h3>
          
          <div className="grid grid-cols-2 gap-3">
            {/* HOG Features */}
            {cv_features.hog && (
              <div className="bg-white dark:bg-slate-800 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-bold text-purple-600 dark:text-purple-400">HOG</span>
                  {cv_validation?.hog_valid && (
                    <span className="text-green-500 text-xs">✓</span>
                  )}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                  <div>Features: {cv_features.hog.feature_length}</div>
                  <div>Method: {cv_features.hog.method}</div>
                </div>
              </div>
            )}

            {/* Sobel Features */}
            {cv_features.sobel && (
              <div className="bg-white dark:bg-slate-800 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-bold text-purple-600 dark:text-purple-400">Sobel</span>
                  {cv_validation?.sobel_valid && (
                    <span className="text-green-500 text-xs">✓</span>
                  )}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                  <div>Edge Density: {(cv_features.sobel.edge_density * 100).toFixed(2)}%</div>
                  <div>Method: {cv_features.sobel.threshold_method}</div>
                </div>
              </div>
            )}

            {/* Optical Flow */}
            {cv_features.optical_flow ? (
              <div className="bg-white dark:bg-slate-800 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-bold text-purple-600 dark:text-purple-400">Optical Flow</span>
                  {cv_validation?.optical_flow_valid && (
                    <span className="text-green-500 text-xs">✓</span>
                  )}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                  <div>Mean: {cv_features.optical_flow.mean_magnitude?.toFixed(3) || 'N/A'}</div>
                  <div>Max: {cv_features.optical_flow.max_magnitude?.toFixed(3) || 'N/A'}</div>
                </div>
              </div>
            ) : (
              <div className="bg-gray-100 dark:bg-slate-700 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-bold text-gray-500">Optical Flow</span>
                  <span className="text-yellow-500 text-xs">⧗</span>
                </div>
                <div className="text-xs text-gray-500">
                  Waiting for 2nd frame...
                </div>
              </div>
            )}

            {/* Morphology */}
            {cv_features.morphology && (
              <div className="bg-white dark:bg-slate-800 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-bold text-purple-600 dark:text-purple-400">Morphology</span>
                  {cv_validation?.morphology_valid && (
                    <span className="text-green-500 text-xs">✓</span>
                  )}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                  <div>Density: {(cv_features.morphology.cleaned_density * 100).toFixed(2)}%</div>
                  <div>Ops: {cv_features.morphology.operations?.join(', ')}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Class probabilities */}
      {all_probs && Object.keys(all_probs).length > 0 && (
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Class Probabilities
          </h3>
          <div className="space-y-2">
            {Object.entries(all_probs)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 5)
              .map(([className, prob]) => (
                <div key={className}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-medium text-gray-600 dark:text-gray-400 capitalize">
                      {className.replace(/_/g, ' ')}
                    </span>
                    <span className="text-gray-500 dark:text-gray-500">
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-full rounded-full transition-all duration-300"
                      style={{ width: `${prob * 100}%` }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
