import cv2
import numpy as np
import os
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceDetectionModel:
  
    def __init__(self, 
                 detection_method: str = "haar",
                 scale_factor: float = 1.1,
                 min_neighbors: int = 5,
                 min_size: Tuple[int, int] = (30, 30),
                 confidence_threshold: float = 0.5):
      
        self.detection_method = detection_method
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size
        self.confidence_threshold = confidence_threshold
        
        # Initialize detection models
        self._initialize_models()
        
        # Performance metrics
        self.frame_count = 0
        self.total_time = 0
        
    def _initialize_models(self):
        """Initialize the face detection models based on the selected method."""
        try:
            if self.detection_method == "haar":
                self._initialize_haar_cascade()
            elif self.detection_method == "dnn":
                self._initialize_dnn_model()
            else:
                raise ValueError(f"Unknown detection method: {self.detection_method}")
                
            logger.info(f"Initialized {self.detection_method} face detection model")
            
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    def _initialize_haar_cascade(self):
        """Initialize Haar cascade classifier."""
        # Try to load the Haar cascade file
        haar_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml' # type: ignore
        
        if not os.path.exists(haar_path):
            raise FileNotFoundError(f"Haar cascade file not found: {haar_path}")
            
        self.face_cascade = cv2.CascadeClassifier(haar_path)
        
        if self.face_cascade.empty():
            raise RuntimeError("Failed to load Haar cascade classifier")
    
    def _initialize_dnn_model(self):
        """Initialize DNN-based face detection model."""
        # Try to load DNN Caffe model from the local Models/Face directory
        try:
            model_dir = Path(__file__).resolve().parent
            prototxt = model_dir / 'deploy.prototxt'
            caffemodel = model_dir / 'res10_300x300_ssd_iter_140000.caffemodel'

            if prototxt.exists() and caffemodel.exists():
                self.net = cv2.dnn.readNetFromCaffe(str(prototxt), str(caffemodel))
                logger.info('Face detection DNN model loaded successfully')
                self.detection_method = 'dnn'
                return
            else:
                logger.warning('DNN model files not found in Models/Face, falling back to Haar cascade')
                self.detection_method = 'haar'
                self._initialize_haar_cascade()

        except Exception as e:
            logger.warning(f'Failed to load DNN model, falling back to Haar cascade: {e}')
            self.detection_method = 'haar'
            self._initialize_haar_cascade()
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect faces in a single frame.
        
        Args:
            frame: Input image/frame as numpy array
            
        Returns:
            List of detected faces with bounding boxes and confidence scores
        """
        start_time = time.time()
        
        if self.detection_method == "haar":
            faces = self._detect_faces_haar(frame)
        elif self.detection_method == "dnn":
            faces = self._detect_faces_dnn(frame)
        else:
            faces = []
        
        # Update performance metrics
        self.frame_count += 1
        frame_time = time.time() - start_time
        self.total_time += frame_time
        
        return faces
    
    def _detect_faces_haar(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces using Haar cascade classifier."""
        # Convert to grayscale for Haar cascade
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces_rect = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size
        )
        
        faces = []
        for (x, y, w, h) in faces_rect:
            faces.append({
                'bbox': (x, y, w, h),
                'confidence': 1.0,  # Haar cascade doesn't provide confidence scores
                'center': (x + w // 2, y + h // 2)
            })
        
        return faces
    
    def _detect_faces_dnn(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Detect faces using DNN model."""
        if not hasattr(self, 'net') or self.net is None:
            return self._detect_faces_haar(frame)

        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()

        faces = []
        for i in range(0, detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            if confidence > self.confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype('int')
                # Clamp coordinates
                x1 = max(0, x1); y1 = max(0, y1); x2 = min(w - 1, x2); y2 = min(h - 1, y2)
                faces.append({'bbox': (x1, y1, x2 - x1, y2 - y1), 'confidence': confidence, 'center': ((x1 + x2)//2, (y1 + y2)//2)})

        return faces
    
    def draw_faces(self, frame: np.ndarray, faces: List[Dict[str, Any]], 
                   draw_confidence: bool = True) -> np.ndarray:
        """
        Draw bounding boxes around detected faces.
        
        Args:
            frame: Input frame
            faces: List of detected faces
            draw_confidence: Whether to draw confidence scores
            
        Returns:
            Frame with drawn bounding boxes
        """
        result_frame = frame.copy()
        
        for face in faces:
            x, y, w, h = face['bbox']
            confidence = face['confidence']
            
            # Choose color based on confidence
            if confidence >= 0.8:
                color = (0, 255, 0)  # Green for high confidence
            elif confidence >= 0.6:
                color = (0, 255, 255)  # Yellow for medium confidence
            else:
                color = (0, 0, 255)  # Red for low confidence
            
            # Draw bounding box
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw confidence score if requested
            if draw_confidence and confidence < 1.0:  # Don't show 1.0 for Haar cascade
                label = f"Face: {confidence:.2f}"
                cv2.putText(result_frame, label, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return result_frame
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics."""
        if self.frame_count == 0:
            return {"fps": 0, "avg_time_per_frame": 0}
        
        avg_time = self.total_time / self.frame_count
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        return {
            "fps": fps,
            "avg_time_per_frame": avg_time,
            "total_frames": self.frame_count,
            "total_time": self.total_time
        }
    
    def reset_performance_stats(self):
        """Reset performance counters."""
        self.frame_count = 0
        self.total_time = 0


class RealTimeFaceDetector:
    """
    Real-time face detection system using camera feed.
    """
    
    def __init__(self, 
                 camera_id: int = 0,
                 detection_method: str = "haar",
                 display_window: bool = True,
                 save_frames: bool = False,
                 output_dir: str = "output"):
        """
        Initialize the real-time face detector.
        
        Args:
            camera_id: Camera device ID (0 for default camera)
            detection_method: Face detection method ('haar' or 'dnn')
            display_window: Whether to display the video window
            save_frames: Whether to save frames with detections
            output_dir: Directory to save output frames
        """
        self.camera_id = camera_id
        self.display_window = display_window
        self.save_frames = save_frames
        self.output_dir = output_dir
        
        # Initialize face detection model
        self.face_detector = FaceDetectionModel(detection_method=detection_method)
        
        # Initialize camera
        self.camera = None
        self._initialize_camera()
        
        # Create output directory if needed
        if self.save_frames:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Control flags
        self.is_running = False
        self.frame_counter = 0
    
    def _initialize_camera(self):
        """Initialize camera capture."""
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            
            if not self.camera.isOpened():
                raise RuntimeError(f"Failed to open camera {self.camera_id}")
            
            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info(f"Camera {self.camera_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            raise
    
    def start_detection(self):
        """Start real-time face detection."""
        if not self.camera or not self.camera.isOpened():
            logger.error("Camera not initialized")
            return
        
        self.is_running = True
        logger.info("Starting real-time face detection...")
        
        try:
            while self.is_running:
                ret, frame = self.camera.read()
                
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    break
                
                # Detect faces
                faces = self.face_detector.detect_faces(frame)
                
                # Draw faces on frame
                result_frame = self.face_detector.draw_faces(frame, faces)
                
                # Add performance info
                stats = self.face_detector.get_performance_stats()
                fps_text = f"FPS: {stats['fps']:.1f} | Faces: {len(faces)}"
                cv2.putText(result_frame, fps_text, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Display frame if requested
                if self.display_window:
                    cv2.imshow('Real-time Face Detection', result_frame)
                    
                    # Check for exit key
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' or ESC
                        break
                    elif key == ord('s'):  # Save screenshot
                        self._save_frame(result_frame, f"screenshot_{int(time.time())}.jpg")
                
                # Save frame if requested
                if self.save_frames and len(faces) > 0:
                    self._save_frame(result_frame, f"detection_{self.frame_counter:06d}.jpg")
                
                self.frame_counter += 1
                
        except KeyboardInterrupt:
            logger.info("Detection stopped by user")
        except Exception as e:
            logger.error(f"Error during detection: {e}")
        finally:
            self.stop_detection()
    
    def stop_detection(self):
        """Stop face detection and cleanup."""
        self.is_running = False
        
        if self.camera:
            self.camera.release()
        
        if self.display_window:
            cv2.destroyAllWindows()
        
        # Print final statistics
        stats = self.face_detector.get_performance_stats()
        logger.info(f"Detection stopped. Final stats: {stats}")
    
    def _save_frame(self, frame: np.ndarray, filename: str):
        """Save a frame to disk."""
        try:
            filepath = os.path.join(self.output_dir, filename)
            cv2.imwrite(filepath, frame)
            logger.debug(f"Saved frame: {filepath}")
        except Exception as e:
            logger.error(f"Error saving frame: {e}")
    
    def detect_single_image(self, image_path: str, output_path: Optional[str] = None) -> List[Dict[str, Any]]:
       
        try:
            # Load image
            frame = cv2.imread(image_path)
            if frame is None:
                raise ValueError(f"Failed to load image: {image_path}")
            
            # Detect faces
            faces = self.face_detector.detect_faces(frame)
            
            # Draw faces and save if requested
            if output_path:
                result_frame = self.face_detector.draw_faces(frame, faces)
                cv2.imwrite(output_path, result_frame)
                logger.info(f"Result saved to: {output_path}")
            
            logger.info(f"Detected {len(faces)} faces in {image_path}")
            return faces
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return []


def main():
    """Main function for testing the face detection model."""
    print("Real-time Face Detection Model")
    print("==============================")
    print("Controls:")
    print("  - Press 'q' or ESC to quit")
    print("  - Press 's' to save screenshot")
    print()
    
    try:
        # Create real-time detector
        detector = RealTimeFaceDetector(
            camera_id=0,
            detection_method="haar",
            display_window=True,
            save_frames=False
        )
        
        # Start detection
        detector.start_detection()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
