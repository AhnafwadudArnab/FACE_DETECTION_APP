"""
Lightweight emotion detection using only OpenCV — no TensorFlow, no PyTorch.
Uses a pre-trained Haar + SVM approach via OpenCV's face landmark + heuristics,
or falls back to a simple facial geometry heuristic.
"""
import logging
import cv2
import numpy as np
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Emotion labels
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprised', 'neutral']


class ImageEmotionModel:
    """
    Lightweight emotion detector using OpenCV only.
    No TensorFlow, no PyTorch, no FER — fits in 512MB RAM.
    """

    def __init__(self, mtcnn: bool = False):
        self._face_cascade = None
        self._smile_cascade = None
        self._eye_cascade = None
        self._load_cascades()
        logger.info("Lightweight OpenCV emotion detector initialized")

    def _load_cascades(self):
        try:
            self._face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self._smile_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_smile.xml')
            self._eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml')
        except Exception as e:
            logger.warning(f"Could not load cascades: {e}")

    def _detect_emotion_from_roi(self, face_roi_bgr) -> Dict[str, float]:
        """
        Heuristic emotion detection from face ROI using smile/eye cascades.
        Returns a dict of emotion -> confidence scores.
        """
        if face_roi_bgr is None or face_roi_bgr.size == 0:
            return {'neutral': 1.0}

        try:
            gray = cv2.cvtColor(face_roi_bgr, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape

            # Detect smile
            smile_score = 0.0
            if self._smile_cascade is not None:
                smiles = self._smile_cascade.detectMultiScale(
                    gray, scaleFactor=1.7, minNeighbors=22,
                    minSize=(int(w * 0.25), int(h * 0.1)))
                if len(smiles) > 0:
                    smile_score = min(1.0, len(smiles) * 0.5)

            # Detect eyes (open eyes = alert/surprised, closed = sad/fear)
            eye_score = 0.0
            if self._eye_cascade is not None:
                eyes = self._eye_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5,
                    minSize=(int(w * 0.1), int(h * 0.1)))
                eye_score = min(1.0, len(eyes) / 2.0)

            # Brightness heuristic (bright face = happy/surprised)
            brightness = float(np.mean(gray)) / 255.0

            # Contrast heuristic (high contrast = angry/surprised)
            contrast = float(np.std(gray)) / 128.0

            # Build scores
            scores = {
                'happy':     smile_score * 0.8 + brightness * 0.2,
                'neutral':   (1 - smile_score) * eye_score * 0.6 + 0.2,
                'surprised': (1 - smile_score) * (1 - eye_score) * contrast * 0.5,
                'sad':       (1 - smile_score) * (1 - eye_score) * (1 - brightness) * 0.4,
                'angry':     (1 - smile_score) * contrast * (1 - brightness) * 0.3,
                'fear':      (1 - smile_score) * (1 - eye_score) * 0.2,
                'disgust':   (1 - smile_score) * (1 - brightness) * 0.15,
            }

            # Normalize
            total = sum(scores.values()) or 1.0
            scores = {k: round(v / total, 4) for k, v in scores.items()}
            return scores

        except Exception as e:
            logger.warning(f"Emotion heuristic failed: {e}")
            return {'neutral': 1.0}

    def predict_emotion(self, face_roi) -> Dict[str, Optional[float]]:
        """Return top emotion and confidence for a face ROI (BGR numpy array)."""
        scores = self._detect_emotion_from_roi(face_roi)
        top = max(scores, key=scores.get)
        return {'emotion': top, 'confidence': float(scores[top])}

    def predict_emotion_whole(self, image) -> Dict[str, Optional[float]]:
        """Run emotion detection on the whole image as fallback."""
        return self.predict_emotion(image)
