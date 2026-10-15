"""
Temporal Robustness Module
Analyzes drowsiness patterns over time to reduce false positives
"""
from typing import List, Dict, Optional
from collections import OrderedDict, deque
import numpy as np


class TemporalBuffer:
    """
    Maintains a sliding window of recent predictions for temporal analysis
    """
    
    def __init__(self, max_size: int = 10):
        """
        Initialize temporal buffer
        
        Args:
            max_size: Maximum number of frames to keep in history
        """
        self.max_size = max_size
        self.predictions = deque(maxlen=max_size)
        self.confidences = deque(maxlen=max_size)
        self.eye_closures = deque(maxlen=max_size)
        self.timestamps = deque(maxlen=max_size)
        
    def add(self, is_drowsy: bool, confidence: float, 
            eyes_closed: bool = False, timestamp: Optional[float] = None):
        """
        Add a new prediction to the buffer
        
        Args:
            is_drowsy: Whether drowsiness was detected
            confidence: Confidence score of prediction
            eyes_closed: Whether eyes were detected as closed
            timestamp: Optional timestamp for the frame
        """
        self.predictions.append(is_drowsy)
        self.confidences.append(confidence)
        self.eye_closures.append(eyes_closed)
        self.timestamps.append(timestamp)
    
    def get_history(self) -> Dict:
        """
        Get the current history
        
        Returns:
            Dictionary with history arrays
        """
        return {
            "predictions": list(self.predictions),
            "confidences": list(self.confidences),
            "eye_closures": list(self.eye_closures),
            "timestamps": list(self.timestamps),
            "size": len(self.predictions)
        }
    
    def clear(self):
        """Clear all history"""
        self.predictions.clear()
        self.confidences.clear()
        self.eye_closures.clear()
        self.timestamps.clear()


class TemporalAnalyzer:
    """
    Analyzes temporal patterns for robust drowsiness detection
    """
    
    def __init__(self, buffer_size: int = 10):
        """
        Initialize temporal analyzer
        
        Args:
            buffer_size: Number of frames to analyze
        """
        self.buffer = TemporalBuffer(max_size=buffer_size)
        
    def add_prediction(self, is_drowsy: bool, confidence: float,
                      eyes_closed: bool = False, timestamp: Optional[float] = None):
        """
        Add a new prediction and analyze temporal patterns
        
        Args:
            is_drowsy: Current frame drowsiness prediction
            confidence: Confidence score
            eyes_closed: Eye closure state
            timestamp: Optional timestamp
        """
        self.buffer.add(is_drowsy, confidence, eyes_closed, timestamp)
    
    def analyze(self) -> Dict:
        """
        Perform temporal analysis on buffered predictions
        
        Returns:
            Dictionary with temporal analysis results:
            - smoothed_prediction: Temporally smoothed prediction
            - confidence: Confidence in the smoothed prediction
            - consecutive_drowsy: Number of consecutive drowsy frames
            - drowsy_rate: Percentage of drowsy frames in buffer
            - eye_closure_rate: Percentage of frames with closed eyes
            - temporal_alert_level: 0=safe, 1=caution, 2=warning, 3=danger
            - recommendation: Action recommendation
        """
        history = self.buffer.get_history()
        
        if history["size"] == 0:
            return self._empty_analysis()
        
        predictions = history["predictions"]
        confidences = history["confidences"]
        eye_closures = history["eye_closures"]
        
        # Calculate metrics
        drowsy_count = sum(predictions)
        drowsy_rate = drowsy_count / len(predictions)
        avg_confidence = np.mean(confidences)
        
        # Count consecutive drowsy frames from the end
        consecutive_drowsy = 0
        for pred in reversed(predictions):
            if pred:
                consecutive_drowsy += 1
            else:
                break
        
        # Eye closure analysis
        eye_closure_count = sum(eye_closures)
        eye_closure_rate = eye_closure_count / len(eye_closures) if eye_closures else 0.0
        
        # Temporal smoothing using majority voting
        # Require at least 50% of recent frames to be drowsy for positive prediction
        smoothed_prediction = drowsy_rate >= 0.5
        
        # Enhanced smoothing: if recent frames show drowsiness trend, upgrade
        recent_window = min(3, len(predictions))
        recent_drowsy = sum(predictions[-recent_window:])
        recent_drowsy_rate = recent_drowsy / recent_window
        
        # Determine alert level based on multiple factors
        alert_level = self._calculate_alert_level(
            drowsy_rate=drowsy_rate,
            consecutive_drowsy=consecutive_drowsy,
            eye_closure_rate=eye_closure_rate,
            recent_drowsy_rate=recent_drowsy_rate,
            avg_confidence=avg_confidence
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(alert_level, consecutive_drowsy)
        
        return {
            "smoothed_prediction": smoothed_prediction,
            "confidence": float(avg_confidence),
            "consecutive_drowsy": consecutive_drowsy,
            "drowsy_rate": float(drowsy_rate),
            "eye_closure_rate": float(eye_closure_rate),
            "temporal_alert_level": alert_level,
            "recommendation": recommendation,
            "buffer_size": len(predictions),
            "recent_drowsy_rate": float(recent_drowsy_rate)
        }
    
    def _calculate_alert_level(self, drowsy_rate: float, consecutive_drowsy: int,
                              eye_closure_rate: float, recent_drowsy_rate: float,
                              avg_confidence: float) -> int:
        """
        Calculate temporal alert level based on multiple factors
        
        Returns:
            0: Safe (no concern)
            1: Caution (slight concern, monitor)
            2: Warning (moderate concern, alert driver)
            3: Danger (high concern, immediate action)
        """
        # Level 3: Danger - sustained drowsiness with eye closure
        if consecutive_drowsy >= 5 or (drowsy_rate >= 0.7 and eye_closure_rate >= 0.5):
            return 3
        
        # Level 2: Warning - consistent recent drowsiness
        if consecutive_drowsy >= 3 or (recent_drowsy_rate >= 0.67 and drowsy_rate >= 0.5):
            return 2
        
        # Level 1: Caution - intermittent drowsiness
        if drowsy_rate >= 0.3 or consecutive_drowsy >= 2:
            return 1
        
        # Level 0: Safe
        return 0
    
    def _generate_recommendation(self, alert_level: int, consecutive_drowsy: int) -> str:
        """
        Generate action recommendation based on alert level
        
        Args:
            alert_level: Current alert level (0-3)
            consecutive_drowsy: Number of consecutive drowsy frames
            
        Returns:
            Recommendation string
        """
        recommendations = {
            0: "Driver appears alert. Continue monitoring.",
            1: "Slight fatigue detected. Stay vigilant.",
            2: "Moderate drowsiness detected. Consider taking a break soon.",
            3: f"DANGER: Sustained drowsiness detected ({consecutive_drowsy} consecutive frames). Pull over immediately!"
        }
        return recommendations.get(alert_level, "Unknown state")
    
    def _empty_analysis(self) -> Dict:
        """Return default analysis when buffer is empty"""
        return {
            "smoothed_prediction": False,
            "confidence": 0.0,
            "consecutive_drowsy": 0,
            "drowsy_rate": 0.0,
            "eye_closure_rate": 0.0,
            "temporal_alert_level": 0,
            "recommendation": "Insufficient data for temporal analysis",
            "buffer_size": 0,
            "recent_drowsy_rate": 0.0
        }
    
    def get_trend(self) -> str:
        """
        Analyze trend over time
        
        Returns:
            Trend description: "improving", "stable", "worsening", or "insufficient_data"
        """
        history = self.buffer.get_history()
        
        if history["size"] < 4:
            return "insufficient_data"
        
        predictions = history["predictions"]
        
        # Split into first half and second half
        mid = len(predictions) // 2
        first_half_rate = sum(predictions[:mid]) / mid
        second_half_rate = sum(predictions[mid:]) / (len(predictions) - mid)
        
        # Compare rates
        if second_half_rate < first_half_rate - 0.2:
            return "improving"
        elif second_half_rate > first_half_rate + 0.2:
            return "worsening"
        else:
            return "stable"
    
    def reset(self):
        """Reset the analyzer (clear all history)"""
        self.buffer.clear()


# Keep a bounded analyzer per frontend monitoring session. This prevents
# different browser sessions from sharing temporal history.
_analyzers: "OrderedDict[str, TemporalAnalyzer]" = OrderedDict()
_max_sessions = 128


def get_temporal_analyzer(session_id: str = "default", buffer_size: int = 10) -> TemporalAnalyzer:
    """
    Get or create the global temporal analyzer instance
    
    Args:
        session_id: Client-generated monitoring session identifier.
        buffer_size: Size of the temporal buffer
        
    Returns:
        TemporalAnalyzer instance
    """
    session_id = str(session_id).strip()
    if not session_id:
        session_id = "default"

    analyzer = _analyzers.pop(session_id, None)
    if analyzer is None:
        analyzer = TemporalAnalyzer(buffer_size=buffer_size)
    _analyzers[session_id] = analyzer

    while len(_analyzers) > _max_sessions:
        _analyzers.popitem(last=False)

    return analyzer


def reset_temporal_analyzer(session_id: Optional[str] = None):
    """Reset one session's analyzer, or all analyzers when no ID is given."""
    if session_id is None:
        _analyzers.clear()
        return

    analyzer = _analyzers.get(str(session_id).strip())
    if analyzer is not None:
        analyzer.reset()


# Example usage
if __name__ == "__main__":
    # Create analyzer
    analyzer = TemporalAnalyzer(buffer_size=10)
    
    # Simulate predictions over time
    test_predictions = [
        (False, 0.9, False),  # Alert
        (False, 0.85, False),  # Alert
        (True, 0.6, False),   # Drowsy (isolated)
        (False, 0.8, False),  # Alert
        (True, 0.7, True),    # Drowsy + eyes closed
        (True, 0.75, True),   # Drowsy + eyes closed
        (True, 0.8, True),    # Drowsy + eyes closed
        (True, 0.85, True),   # Drowsy + eyes closed
    ]
    
    print("Temporal Analysis Simulation")
    print("=" * 50)
    
    for i, (is_drowsy, conf, eyes_closed) in enumerate(test_predictions, 1):
        analyzer.add_prediction(is_drowsy, conf, eyes_closed)
        analysis = analyzer.analyze()
        
        print(f"\nFrame {i}:")
        print(f"  Input: Drowsy={is_drowsy}, Confidence={conf:.2f}, Eyes Closed={eyes_closed}")
        print(f"  Smoothed Prediction: {analysis['smoothed_prediction']}")
        print(f"  Consecutive Drowsy: {analysis['consecutive_drowsy']}")
        print(f"  Drowsy Rate: {analysis['drowsy_rate']:.1%}")
        print(f"  Alert Level: {analysis['temporal_alert_level']} - {analysis['recommendation']}")
        print(f"  Trend: {analyzer.get_trend()}")
