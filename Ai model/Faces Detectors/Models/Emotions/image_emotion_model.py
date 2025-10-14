import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

try:
    from fer import FER  # type: ignore
except Exception:
    FER = None


class ImageEmotionModel:
  
    def __init__(self, mtcnn: bool = False):
        self.detector = None
        if FER is None:
            logger.warning("FER package not available; image emotions will be 'Unknown'.")
            return

        try:
            # Create detector instance; mtcnn optional
            self.detector = FER(mtcnn=mtcnn)
            logger.info("FER image emotion detector initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize FER detector: {e}")
            self.detector = None

    def predict_emotion(self, face_roi) -> Dict[str, Optional[float]]:
        """Return top emotion and confidence for a face ROI (BGR numpy array).

        Returns: { 'emotion': str, 'confidence': float }
        """
        if self.detector is None:
            return {'emotion': 'Unknown', 'confidence': 0.0} # type: ignore

        try:
            # FER expects RGB images
            import cv2
            roi_rgb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
            results = self.detector.detect_emotions(roi_rgb)
            if not results:
                return {'emotion': 'Unknown', 'confidence': 0.0} # type: ignore

            emotions = results[0].get('emotions', {})
            if not emotions:
                return {'emotion': 'Unknown', 'confidence': 0.0} # type: ignore

            top = max(emotions, key=emotions.get)
            return {'emotion': top, 'confidence': float(emotions[top])}
        except Exception as e:
            logger.warning(f"FER predict_emotion failed: {e}")
            return {'emotion': 'Unknown', 'confidence': 0.0} # type: ignore
    def predict_emotion_whole(self, image) -> Dict[str, Optional[float]]:
        """Run emotion detection on the whole image as a fallback."""
        if self.detector is None:
            return {'emotion': 'Unknown', 'confidence': 0.0} # type: ignore
        try:
            import cv2
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.detector.detect_emotions(img_rgb)
            if not results:
                return {'emotion': 'Unknown', 'confidence': 0.0} # type: ignore
            # FER may return multiple faces; aggregate by picking highest max emotion
            best_emotion = 'Unknown'
            best_conf = 0.0
            for r in results:
                emotions = r.get('emotions', {})
                if not emotions:
                    continue
                top = max(emotions, key=emotions.get)
                conf = float(emotions[top])
                if conf > best_conf:
                    best_conf = conf
                    best_emotion = top
            return {'emotion': best_emotion, 'confidence': best_conf} # type: ignore
        except Exception as e:
            logger.warning(f"FER predict_emotion_whole failed: {e}")
            return {'emotion': 'Unknown', 'confidence': 0.0} # type: ignore
