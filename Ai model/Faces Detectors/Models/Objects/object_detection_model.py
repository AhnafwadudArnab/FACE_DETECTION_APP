"""
Real-Time Object Detection Model
Detects devices, persons, and animals from live camera feed using YOLO
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeObjectDetector:
    """Real-time object detection system focusing on devices, persons, and animals"""
    
    def __init__(self, model_path: str = 'yolov8n.pt', confidence_threshold: float = 0.5):
        """
        Initialize the object detector
        
        Args:
            model_path: Path to YOLO model file (will download if not exists)
            confidence_threshold: Minimum confidence score for detections
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.cap = None
        
        # Define categories of interest
        self.target_categories = {
            'persons': [0],  # person
            'animals': [14, 15, 16, 17, 18, 19, 20, 21, 22, 23],  # various animals
            'devices': [63, 64, 65, 66, 67, 73, 76, 77, 78]  # electronics, phones, laptops, etc.
        }
        
        # COCO class names for reference
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
        
        # Colors for different categories (BGR format)
        self.colors = {
            'persons': (0, 255, 0),    # Green
            'animals': (0, 165, 255),  # Orange
            'devices': (255, 0, 0)     # Blue
        }
        
    def load_model(self) -> bool:
        """Load the YOLO model"""
        try:
            logger.info(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """
        Initialize camera capture
        
        Args:
            camera_index: Index of the camera to use (0 for default)
        """
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                logger.error("Could not open camera")
                return False
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("Camera initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing camera: {e}")
            return False
    
    def categorize_detection(self, class_id: int) -> Optional[str]:
        """
        Categorize a detection into persons, animals, or devices
        
        Args:
            class_id: YOLO class ID
            
        Returns:
            Category name or None if not in target categories
        """
        for category, class_ids in self.target_categories.items():
            if class_id in class_ids:
                return category
        return None
    
    def process_detections(self, results) -> List[Dict]:
        """
        Process YOLO detections and filter for target categories
        
        Args:
            results: YOLO detection results
            
        Returns:
            List of filtered detection dictionaries
        """
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for i in range(len(boxes.cls)):
                    class_id = int(boxes.cls[i].item())
                    confidence = boxes.conf[i].item()
                    
                    # Filter by confidence threshold
                    if confidence < self.confidence_threshold:
                        continue
                    
                    # Filter by target categories
                    category = self.categorize_detection(class_id)
                    if category is None:
                        continue
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = boxes.xyxy[i].tolist()
                    
                    detection = {
                        'category': category,
                        'class_name': self.class_names[class_id],
                        'confidence': confidence,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    }
                    detections.append(detection)
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on the frame
        
        Args:
            frame: Input frame
            detections: List of detection dictionaries
            
        Returns:
            Frame with drawn detections
        """
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            category = detection['category']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            # Get color for category
            color = self.colors.get(category, (128, 128, 128))
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label with confidence
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Draw label background
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def add_stats_overlay(self, frame: np.ndarray, detections: List[Dict], fps: float) -> np.ndarray:
        """
        Add statistics overlay to the frame
        
        Args:
            frame: Input frame
            detections: List of detections
            fps: Current FPS
            
        Returns:
            Frame with stats overlay
        """
        h, w = frame.shape[:2]
        
        # Count detections by category
        counts = {'persons': 0, 'animals': 0, 'devices': 0}
        for detection in detections:
            counts[detection['category']] += 1
        
        # Create stats text
        stats_text = [
            f"FPS: {fps:.1f}",
            f"Persons: {counts['persons']}",
            f"Animals: {counts['animals']}",
            f"Devices: {counts['devices']}",
            f"Total: {len(detections)}"
        ]
        
        # Draw stats background
        stats_height = len(stats_text) * 25 + 10
        cv2.rectangle(frame, (10, 10), (200, stats_height), (0, 0, 0), -1)
        
        # Draw stats text
        for i, text in enumerate(stats_text):
            y_pos = 30 + i * 25
            cv2.putText(frame, text, (15, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def run_detection(self, save_video: bool = False, output_path: str = "output.mp4"):
        """
        Run real-time object detection
        
        Args:
            save_video: Whether to save the output video
            output_path: Path to save the output video
        """
        if not self.load_model():
            return
        
        if not self.initialize_camera():
            return
        
        # Video writer setup
        video_writer = None
        if save_video:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))
        
        # FPS calculation
        fps_counter = 0
        start_time = time.time()
        fps = 0
        
        logger.info("Starting real-time detection. Press 'q' to quit, 's' to save screenshot.")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("Failed to read from camera")
                    break
                
                # Run YOLO detection
                results = self.model(frame, verbose=False)
                
                # Process detections
                detections = self.process_detections(results)
                
                # Draw detections
                frame = self.draw_detections(frame, detections)
                
                # Calculate FPS
                fps_counter += 1
                if fps_counter >= 10:
                    end_time = time.time()
                    fps = fps_counter / (end_time - start_time)
                    fps_counter = 0
                    start_time = time.time()
                
                # Add stats overlay
                frame = self.add_stats_overlay(frame, detections, fps)
                
                # Display frame
                cv2.imshow('Real-Time Object Detection', frame)
                
                # Save video frame if enabled
                if save_video and video_writer is not None:
                    video_writer.write(frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    # Save screenshot
                    timestamp = int(time.time())
                    screenshot_path = f"screenshot_{timestamp}.jpg"
                    cv2.imwrite(screenshot_path, frame)
                    logger.info(f"Screenshot saved: {screenshot_path}")
        
        except KeyboardInterrupt:
            logger.info("Detection stopped by user")
        
        finally:
            # Cleanup
            if self.cap is not None:
                self.cap.release()
            if video_writer is not None:
                video_writer.release()
            cv2.destroyAllWindows()
            logger.info("Cleanup completed")
    
    def detect_from_image(self, image_path: str) -> List[Dict]:
        """
        Detect objects in a single image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of detections
        """
        if not self.load_model():
            return []
        
        try:
            # Load image
            frame = cv2.imread(image_path)
            if frame is None:
                logger.error(f"Could not load image: {image_path}")
                return []
            
            # Run detection
            results = self.model(frame, verbose=False)
            detections = self.process_detections(results)
            
            # Draw detections and save result
            frame_with_detections = self.draw_detections(frame.copy(), detections)
            output_path = f"detected_{image_path.split('/')[-1]}"
            cv2.imwrite(output_path, frame_with_detections)
            
            logger.info(f"Detection completed. Results saved to: {output_path}")
            return detections
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return []

# Example usage and utility functions
def main():
    """Main function to run the object detector"""
    detector = RealTimeObjectDetector(confidence_threshold=0.3)
    
    print("Real-Time Object Detection System")
    print("=================================")
    print("This system detects:")
    print("- Persons (Green boxes)")
    print("- Animals (Orange boxes)")  
    print("- Devices (Blue boxes)")
    print("\nControls:")
    print("- Press 'q' to quit")
    print("- Press 's' to save screenshot")
    print("\nStarting detection...")
    
    detector.run_detection(save_video=False)

if __name__ == "__main__":
    main()
