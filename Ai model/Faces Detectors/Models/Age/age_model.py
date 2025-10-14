import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from typing import Dict, List, Tuple, Optional, Union
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use the centralized image emotion wrapper if available
try:
    from Models.Emotions.image_emotion_model import ImageEmotionModel  # type: ignore
except Exception:
    ImageEmotionModel = None

class AgeGenderDetector:
    """Age and Gender Detection using OpenCV DNN and Haar Cascades"""
    
    def __init__(self, model_path: str = None): # type: ignore
        """
        Initialize the Age Gender Detector
        
        Args:
            model_path (str, optional): Path to directory containing model files
        """
        self.model_path = model_path or os.path.dirname(os.path.abspath(__file__))
        
        # Model file names
        self.face_proto = "opencv_face_detector.pbtxt"
        self.face_model = "opencv_face_detector_uint8.pb"
        self.age_proto = "age_deploy.prototxt"
        self.age_model = "age_net.caffemodel"
        self.gender_proto = "gender_deploy.prototxt"
        self.gender_model = "gender_net.caffemodel"
        
        # Model mean values for preprocessing
        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        
        # Age and gender categories
        self.age_categories = ['(0-2)', '(4-6)', '(8-12)', '(15-20)',
                              '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        self.gender_categories = ['Male', 'Female']
        
        # Initialize models
        self.face_net = None
        self.age_net = None
        self.gender_net = None
        self.face_cascade = None
        
        self._load_models()
    
    def _load_models(self):
        """Load DNN models and fallback cascades"""
        try:
            # Try to load DNN models
            self._load_dnn_models()
        except Exception as e:
            logger.warning(f"Could not load DNN models: {e}")
            logger.info("Falling back to Haar cascades for face detection")
        
        # Load Haar cascade as fallback
        self._load_haar_cascade()
    
    def _load_dnn_models(self):
        """Load OpenCV DNN models"""
        face_proto_path = os.path.join(self.model_path, self.face_proto)
        face_model_path = os.path.join(self.model_path, self.face_model)
        
        if os.path.exists(face_proto_path) and os.path.exists(face_model_path):
            self.face_net = cv2.dnn.readNet(face_model_path, face_proto_path)
            logger.info("Face detection DNN model loaded successfully")
        else:
            logger.warning("DNN face detection models not found")
        
        # Load age model
        age_proto_path = os.path.join(self.model_path, self.age_proto)
        age_model_path = os.path.join(self.model_path, self.age_model)
        
        if os.path.exists(age_proto_path) and os.path.exists(age_model_path):
            self.age_net = cv2.dnn.readNet(age_model_path, age_proto_path)
            logger.info("Age detection DNN model loaded successfully")
        else:
            logger.warning("DNN age detection models not found")
        
        # Load gender model
        gender_proto_path = os.path.join(self.model_path, self.gender_proto)
        gender_model_path = os.path.join(self.model_path, self.gender_model)
        
        if os.path.exists(gender_proto_path) and os.path.exists(gender_model_path):
            self.gender_net = cv2.dnn.readNet(gender_model_path, gender_proto_path)
            logger.info("Gender detection DNN model loaded successfully")
        else:
            logger.warning("DNN gender detection models not found")

        # Initialize centralized image emotion detector wrapper if available
        if ImageEmotionModel is not None:
            try:
                self.emotion_detector = ImageEmotionModel(mtcnn=False)
            except Exception as e:
                self.emotion_detector = None
                logger.warning(f"Failed to initialize ImageEmotionModel: {e}")
        else:
            self.emotion_detector = None
    
    def _load_haar_cascade(self):
        """Load Haar cascade for face detection as fallback"""
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml' # type: ignore
            )
            logger.info("Haar cascade face detector loaded as fallback")
        except Exception as e:
            logger.error(f"Could not load Haar cascade: {e}")
    
    def detect_faces_dnn(self, image: np.ndarray, confidence_threshold: float = 0.7) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using DNN model
        
        Args:
            image (np.ndarray): Input image
            confidence_threshold (float): Minimum confidence for detection
            
        Returns:
            List[Tuple]: List of face bounding boxes (x1, y1, x2, y2)
        """
        if self.face_net is None:
            return []
        
        h, w = image.shape[:2]
        
        # Create blob from image
        blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), [104, 117, 123], True, False)
        
        # Set input to the network
        self.face_net.setInput(blob)
        detections = self.face_net.forward()
        
        face_boxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > confidence_threshold:
                x1 = int(detections[0, 0, i, 3] * w)
                y1 = int(detections[0, 0, i, 4] * h)
                x2 = int(detections[0, 0, i, 5] * w)
                y2 = int(detections[0, 0, i, 6] * h)
                
                face_boxes.append((x1, y1, x2, y2))
        
        return face_boxes
    
    def detect_faces_haar(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using Haar cascade
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            List[Tuple]: List of face bounding boxes (x, y, x+w, y+h)
        """
        if self.face_cascade is None:
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Make Haar cascade slightly more permissive for varied images
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.05, minNeighbors=3, minSize=(24, 24)
        )
        
        # Convert to (x1, y1, x2, y2) format
        face_boxes = []
        for (x, y, w, h) in faces:
            face_boxes.append((x, y, x + w, y + h))
        
        return face_boxes
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using available methods (DNN preferred, Haar as fallback)
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            List[Tuple]: List of face bounding boxes
        """
        # Try DNN first
        faces = self.detect_faces_dnn(image)
        
        # If no faces found with DNN, try Haar cascade
        if not faces:
            faces = self.detect_faces_haar(image)
        
        return faces

    
    def predict_age_gender(self, face_roi: np.ndarray) -> Dict[str, Union[str, float]]:
        """
        Predict age and gender for a face region
        
        Args:
            face_roi (np.ndarray): Cropped face region
            
        Returns:
            Dict: Prediction results with age, gender, and confidence scores
        """
        result = {
            'age': 'Unknown',
            'gender': 'Unknown',
            'age_confidence': 0.0,
            'gender_confidence': 0.0
        }
        
        if face_roi is None or face_roi.size == 0:
            return result
        
        # Prepare blob for prediction
        blob = cv2.dnn.blobFromImage(
            face_roi, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False
        )
        
        # Predict gender
        if self.gender_net is not None:
            try:
                self.gender_net.setInput(blob)
                gender_preds = self.gender_net.forward()
                gender_idx = gender_preds[0].argmax()
                result['gender'] = self.gender_categories[gender_idx]
                result['gender_confidence'] = float(gender_preds[0][gender_idx])
            except Exception as e:
                logger.warning(f"Gender prediction failed: {e}")
        
        # Predict age
        if self.age_net is not None:
            try:
                self.age_net.setInput(blob)
                age_preds = self.age_net.forward()
                age_idx = age_preds[0].argmax()
                result['age'] = self.age_categories[age_idx]
                result['age_confidence'] = float(age_preds[0][age_idx])
            except Exception as e:
                logger.warning(f"Age prediction failed: {e}")
        
        return result
    
    def process_image(self, image_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Process an image for age and gender detection
        
        Args:
            image_path (str): Path to input image
            output_path (str, optional): Path to save annotated image
            
        Returns:
            Dict: Detection results
        """
        try:
            # Load image
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            return self.process_image_array(image, output_path)
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {'error': str(e), 'detections': []}
    
    def process_image_array(self, image: np.ndarray, output_path: Optional[str] = None) -> Dict:
        """
        Process a numpy image array for age and gender detection
        
        Args:
            image (np.ndarray): Input image array
            output_path (str, optional): Path to save annotated image
            
        Returns:
            Dict: Detection results
        """
        try:
            # Resize image for consistent processing while preserving aspect ratio
            original_image = image.copy()
            h, w = image.shape[:2]
            max_dim = 800
            if max(h, w) > max_dim:
                scale = max_dim / float(max(h, w))
                new_w = int(w * scale)
                new_h = int(h * scale)
                image = cv2.resize(image, (new_w, new_h))
            
            # Detect faces
            face_boxes = self.detect_faces(image)

            # If no faces found, try multiple fallbacks: original image, equalized gray, and scaled versions
            if not face_boxes:
                logger.info("No faces found on first pass, trying fallbacks...")
                # 1) try original image (no resize)
                face_boxes = self.detect_faces(original_image)

            if not face_boxes:
                # 2) try histogram equalization on grayscale
                try:
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    eq = cv2.equalizeHist(gray)
                    eq_bgr = cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)
                    face_boxes = self.detect_faces(eq_bgr)
                except Exception:
                    face_boxes = []

            if not face_boxes:
                # 3) try multiple scales (smaller and larger)
                for scale in (0.8, 1.2, 1.5):
                    try:
                        new_w = max(100, int(image.shape[1] * scale))
                        new_h = max(100, int(image.shape[0] * scale))
                        scaled = cv2.resize(image, (new_w, new_h))
                        fb = self.detect_faces(scaled)
                        if fb:
                            # scale boxes back to resized image coordinates
                            ratio_x = image.shape[1] / float(scaled.shape[1])
                            ratio_y = image.shape[0] / float(scaled.shape[0])
                            face_boxes = []
                            for (x1, y1, x2, y2) in fb:
                                sx1 = int(x1 * ratio_x)
                                sy1 = int(y1 * ratio_y)
                                sx2 = int(x2 * ratio_x)
                                sy2 = int(y2 * ratio_y)
                                face_boxes.append((sx1, sy1, sx2, sy2))
                            break
                    except Exception:
                        continue

            if not face_boxes:
                logger.info("Fallback attempts produced no face detections")
            
            detections = []
            annotated_image = image.copy()
            
            if not face_boxes:
                logger.info("No faces detected in the image")
                return {
                    'detections': [],
                    'total_faces': 0,
                    'image_shape': image.shape,
                    'message': 'No faces detected'
                }
            
            # Process each detected face
            for i, (x1, y1, x2, y2) in enumerate(face_boxes):
                # Extract face region with padding
                padding = 15
                face_y1 = max(0, y1 - padding)
                face_y2 = min(image.shape[0], y2 + padding)
                face_x1 = max(0, x1 - padding)
                face_x2 = min(image.shape[1], x2 + padding)
                
                face_roi = image[face_y1:face_y2, face_x1:face_x2]
                
                if face_roi.size == 0:
                    continue
                
                # Predict age and gender
                predictions = self.predict_age_gender(face_roi)

                # Emotion detection (image-based) is not implemented in this repo.
                # Provide default values so UI and API can display a consistent schema.
                # If you add an image-based emotion model later, set predictions['emotion'] and predictions['emotion_confidence'] accordingly.
                # If a FER detector is available, run it on the face ROI
                if getattr(self, 'emotion_detector', None) is not None:
                    try:
                        # Use centralized wrapper API: predict_emotion(face_roi) -> {'emotion', 'confidence'}
                        em = self.emotion_detector.predict_emotion(face_roi) # type: ignore
                        e_label = em.get('emotion', 'Unknown') # type: ignore
                        e_conf = float(em.get('confidence', 0.0) or 0.0) # type: ignore

                        # If ROI result is low-confidence or Unknown, try whole-image fallback
                        fallback_threshold = 0.35
                        if e_label == 'Unknown' or e_conf < fallback_threshold:
                            fb = self.emotion_detector.predict_emotion_whole(original_image) # type: ignore
                            fb_conf = float(fb.get('confidence', 0.0) or 0.0)
                            if fb_conf > e_conf:
                                e_label = fb.get('emotion', e_label)
                                e_conf = fb_conf

                        predictions['emotion'] = e_label # type: ignore
                        predictions['emotion_confidence'] = e_conf
                    except Exception as e:
                        logger.warning(f"Emotion detection failed: {e}")
                        predictions.setdefault('emotion', 'Unknown')
                        predictions.setdefault('emotion_confidence', 0.0)
                else:
                    predictions.setdefault('emotion', 'Unknown')
                    predictions.setdefault('emotion_confidence', 0.0)
                
                # Store detection result
                detection = {
                    'face_id': i + 1,
                    'bbox': (x1, y1, x2, y2),
                    'age': predictions['age'],
                    'gender': predictions['gender'],
                    'age_confidence': predictions.get('age_confidence', 0.0),
                    'gender_confidence': predictions.get('gender_confidence', 0.0),
                    'emotion': predictions.get('emotion', 'Unknown'),
                    'emotion_confidence': predictions.get('emotion_confidence', 0.0)
                }
                detections.append(detection)
                
                # Draw bounding box
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), 
                             (0, 255, 0), int(round(image.shape[0]/150)), 8)
                
                # Add text label: include gender, age and emotion
                label = f"{predictions['gender']}, {predictions['age']} | {predictions.get('emotion', 'Unknown')}"
                label_y = max(y1 - 10, 30)  # Ensure label is visible
                cv2.putText(annotated_image, label, (x1, label_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.3, (217, 0, 0), 4, cv2.LINE_AA)
                
                logger.info(f"Detected face {i+1}: {predictions['gender']}, {predictions['age']}")
            
            # Save annotated image if output path is provided
            if output_path:
                try:
                    cv2.imwrite(output_path, annotated_image)
                    logger.info(f"Annotated image saved to: {output_path}")
                except Exception as e:
                    logger.warning(f"Could not save annotated image: {e}")
            
            result = {
                'detections': detections,
                'total_faces': len(detections),
                'image_shape': image.shape,
                'annotated_image': annotated_image
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing image array: {e}")
            return {'error': str(e), 'detections': []}
    
    def visualize_results(self, result: Dict, save_path: Optional[str] = None, show: bool = True):
        """
        Visualize detection results using matplotlib
        
        Args:
            result (Dict): Detection results from process_image
            save_path (str, optional): Path to save the visualization
            show (bool): Whether to display the plot
        """
        if 'annotated_image' not in result:
            logger.error("No annotated image found in results")
            return
        
        try:
            # Convert BGR to RGB for matplotlib
            image_rgb = cv2.cvtColor(result['annotated_image'], cv2.COLOR_BGR2RGB)
            
            plt.figure(figsize=(12, 8))
            plt.imshow(image_rgb)
            plt.axis('off')
            plt.title(f"Age & Gender Detection - {result['total_faces']} faces detected", 
                     fontsize=16, fontweight='bold')
            
            # Add detection summary
            if result['detections']:
                summary_text = []
                for i, detection in enumerate(result['detections'], 1):
                    summary_text.append(f"Face {i}: {detection['gender']}, {detection['age']}")
                
                plt.figtext(0.02, 0.02, '\n'.join(summary_text), 
                           fontsize=10, verticalalignment='bottom',
                           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Visualization saved to: {save_path}")
            
            if show:
                plt.show()
            else:
                plt.close()
                
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
    
    def create_demo_image(self, save_path: str = "demo_result.jpg"):
        """
        Create a demo image with sample face detection (for testing when no real images available)
        
        Args:
            save_path (str): Path to save the demo image
        """
        try:
            # Create a simple demo image
            demo_image = np.ones((480, 640, 3), dtype=np.uint8) * 255
            
            # Add title
            cv2.putText(demo_image, "Age & Gender Detection Demo", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            # Add instructions
            instructions = [
                "To use this model:",
                "1. Place your image files in the same directory",
                "2. Call detector.process_image('your_image.jpg')",
                "3. Or use the demo interface below"
            ]
            
            for i, instruction in enumerate(instructions):
                cv2.putText(demo_image, instruction, (50, 120 + i * 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Add sample detection boxes (simulated)
            cv2.rectangle(demo_image, (200, 300), (350, 450), (0, 255, 0), 3)
            cv2.putText(demo_image, "Sample: Male, (25-32)", (200, 290),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (217, 0, 0), 2)
            
            cv2.rectangle(demo_image, (400, 300), (550, 450), (0, 255, 0), 3)
            cv2.putText(demo_image, "Sample: Female, (21-30)", (400, 290),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (217, 0, 0), 2)
            
            cv2.imwrite(save_path, demo_image)
            logger.info(f"Demo image created: {save_path}")
            
            return demo_image
            
        except Exception as e:
            logger.error(f"Error creating demo image: {e}")
            return None

    def test_detect(self, image_path: str, out_path: str = 'debug_out.jpg') -> Dict:
        """Helper to run detection from command line for debugging."""
        try:
            if not os.path.exists(image_path):
                return {'error': 'file not found'}
            img = cv2.imread(image_path)
            res = self.process_image_array(img, out_path) # type: ignore
            return res
        except Exception as e:
            return {'error': str(e)}


def download_models():
    """
    Download required OpenCV DNN models
    Note: This is a placeholder - in practice, you would download from official sources
    """
    print("Model Download Instructions:")
    print("="*50)
    print("To use DNN models, download the following files:")
    print("\nFace Detection:")
    print("- opencv_face_detector.pbtxt")
    print("- opencv_face_detector_uint8.pb")
    print("\nAge Detection:")
    print("- age_deploy.prototxt") 
    print("- age_net.caffemodel")
    print("\nGender Detection:")
    print("- gender_deploy.prototxt")
    print("- gender_net.caffemodel")
    print(f"\nPlace these files in: {os.path.dirname(os.path.abspath(__file__))}")
    print("\nDownload links:")
    print("https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector")
    print("https://github.com/GilLevi/AgeGenderDeepLearning")


def demo_interface():
    """Interactive demo interface"""
    print("="*60)
    print("        Age & Gender Detection Model Demo")
    print("="*60)
    
    # Initialize detector
    detector = AgeGenderDetector()
    
    while True:
        print("\nChoose an option:")
        print("1. Process single image")
        print("2. Create demo visualization")
        print("3. Download model instructions")
        print("4. Test with sample data")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            image_path = input("Enter image path: ").strip()
            if os.path.exists(image_path):
                output_path = input("Enter output path (or press Enter to skip): ").strip()
                output_path = output_path if output_path else None
                
                print("Processing image...")
                result = detector.process_image(image_path, output_path)
                
                if 'error' not in result:
                    print(f"✓ Found {result['total_faces']} faces")
                    for detection in result['detections']:
                        print(f"  Face {detection['face_id']}: {detection['gender']}, {detection['age']}")
                    
                    # Show visualization
                    show_viz = input("Show visualization? (y/n): ").strip().lower()
                    if show_viz == 'y':
                        detector.visualize_results(result)
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("❌ File not found!")
        
        elif choice == '2':
            print("Creating demo visualization...")
            demo_image = detector.create_demo_image()
            if demo_image is not None:
                result = {
                    'annotated_image': demo_image,
                    'total_faces': 2,
                    'detections': [
                        {'face_id': 1, 'gender': 'Male', 'age': '(25-32)'},
                        {'face_id': 2, 'gender': 'Female', 'age': '(21-30)'}
                    ]
                }
                detector.visualize_results(result)
        
        elif choice == '3':
            download_models()
        
        elif choice == '4':
            print("Testing with sample data...")
            # Create a test image
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            result = detector.process_image_array(test_image)
            print(f"Test completed. Found {result['total_faces']} faces (expected: 0)")
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")


def main():
    """Main function to demonstrate the age gender detection model"""
    try:
        print("Age & Gender Detection Model")
        print("="*40)
        
        # Initialize detector
        detector = AgeGenderDetector()
        
        # Check if we have any sample images in the workspace
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sample_images = []
        
        # Look for common image extensions
        for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            for file in os.listdir(current_dir):
                if file.lower().endswith(ext):
                    sample_images.append(file)
        
        if sample_images:
            print(f"\nFound {len(sample_images)} image(s) in current directory:")
            for img in sample_images[:5]:  # Show first 5
                print(f"  - {img}")
            
            # Process first sample image
            sample_path = os.path.join(current_dir, sample_images[0])
            print(f"\nProcessing sample image: {sample_images[0]}")
            
            result = detector.process_image(sample_path, "sample_output.jpg")
            
            if 'error' not in result:
                print(f"✓ Detected {result['total_faces']} faces")
                for detection in result['detections']:
                    print(f"  {detection['gender']}, {detection['age']}")
            else:
                print(f"Processing failed: {result['error']}")
        else:
            print("\nNo sample images found. Creating demo...")
            detector.create_demo_image()
        
        # Start interactive demo
        print("\nStarting interactive demo...")
        demo_interface()
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    """
    Age & Gender Detection Model
    ===========================
    
    Installation:
    pip install opencv-python numpy matplotlib pillow
    
    Usage:
    1. Basic usage:
       detector = AgeGenderDetector()
       result = detector.process_image("image.jpg", "output.jpg")
    
    2. Process numpy array:
       result = detector.process_image_array(image_array)
    
    3. Interactive demo:
       python age_model.py
    
    Model Files (optional, for better accuracy):
    - Download OpenCV DNN models for improved face detection
    - Place model files in the same directory as this script
    - The model will work with Haar cascades if DNN models are not available
    """
    main()