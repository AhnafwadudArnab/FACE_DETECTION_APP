# Real-Time Object Detection System

This system provides real-time object detection capabilities focusing on three main categories:
- **Persons** (displayed with green bounding boxes)
- **Animals** (displayed with orange bounding boxes) 
- **Devices** (displayed with blue bounding boxes)

## Features

- **Real-time detection** from camera feed
- **Single image detection** for static images
- **Batch processing** for multiple images
- **Configurable confidence thresholds**
- **Live statistics display** (FPS, detection counts)
- **Screenshot and video recording** capabilities
- **High-performance YOLO-based detection**

## Requirements

- Python 3.8+
- Webcam or camera device
- GPU recommended for better performance

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. The YOLO model will be automatically downloaded on first run.

## Usage

### Important: Use the Virtual Environment

This project uses a virtual environment. Always use the full Python path or the provided runner scripts.

**Full Python Path:**
```bash
"C:/flutter/projects/Ai models/.venv/Scripts/python.exe" object_detection_demo.py
```

**Or use the convenient runner scripts:**

#### Windows Batch Script
```batch
# Run tests
run.bat test

# Start real-time detection
run.bat demo

# Test camera
run.bat camera-test

# Process single image
run.bat image "path/to/image.jpg"

# Process multiple images
run.bat batch
```

#### PowerShell Script
```powershell
# Run tests
.\run.ps1 test

# Start real-time detection
.\run.ps1 demo

# Test camera
.\run.ps1 camera-test

# Process single image
.\run.ps1 image "path/to/image.jpg"

# Process multiple images
.\run.ps1 batch
```

### Manual Command Line Options

```bash
# Real-time detection (default)
"C:/flutter/projects/Ai models/.venv/Scripts/python.exe" object_detection_demo.py --mode realtime

# Process a single image
"C:/flutter/projects/Ai models/.venv/Scripts/python.exe" object_detection_demo.py --mode image --image path/to/image.jpg

# Batch process multiple images
"C:/flutter/projects/Ai models/.venv/Scripts/python.exe" object_detection_demo.py --mode batch --folder path/to/images/

# Test camera access
"C:/flutter/projects/Ai models/.venv/Scripts/python.exe" object_detection_demo.py --mode test

# Adjust confidence threshold
"C:/flutter/projects/Ai models/.venv/Scripts/python.exe" object_detection_demo.py --confidence 0.5
```

### Python API Usage

```python
from object_detection_model import RealTimeObjectDetector

detector = RealTimeObjectDetector(confidence_threshold=0.3)
detector.run_detection()
```

### Controls During Real-Time Detection

- **'q'** - Quit the application
- **'s'** - Save screenshot with detections
- **ESC** - Also quits the application

## API Reference

### RealTimeObjectDetector Class

#### Constructor
```python
RealTimeObjectDetector(model_path='yolov8n.pt', confidence_threshold=0.5)
```

- `model_path`: Path to YOLO model (auto-downloads if not found)
- `confidence_threshold`: Minimum confidence score (0.0-1.0)

#### Methods

##### run_detection()
```python
run_detection(save_video=False, output_path="output.mp4")
```
Starts real-time detection from camera.

##### detect_from_image()
```python
detect_from_image(image_path) -> List[Dict]
```
Detects objects in a single image file.

##### initialize_camera()
```python
initialize_camera(camera_index=0) -> bool
```
Initializes camera capture device.

## Detection Categories

### Persons (Class ID: 0)
- People in various poses and positions
- Displayed with **green** bounding boxes

### Animals (Class IDs: 14-23)
- **Birds** (14)
- **Cats** (15)  
- **Dogs** (16)
- **Horses** (17)
- **Sheep** (18)
- **Cows** (19)
- **Elephants** (20)
- **Bears** (21)
- **Zebras** (22)
- **Giraffes** (23)
- Displayed with **orange** bounding boxes

### Devices (Class IDs: 63-67, 73, 76-78)
- **TVs/Monitors** (63)
- **Laptops** (64)
- **Computer Mouse** (65)
- **Remote Controls** (66)
- **Keyboards** (67)
- **Books** (73)
- **Cell Phones** (76)
- **Microwaves** (77)
- **Ovens** (78)
- Displayed with **blue** bounding boxes

## Performance Optimization

### For Better Performance:
- Use GPU-enabled PyTorch installation
- Lower confidence threshold for more detections
- Reduce camera resolution for faster processing
- Use YOLOv8n (nano) model for speed over accuracy

### For Better Accuracy:
- Use YOLOv8m or YOLOv8l models
- Increase confidence threshold
- Use higher camera resolution
- Ensure good lighting conditions

## Model Information

This system uses YOLOv8 (You Only Look Once) models:
- **YOLOv8n**: Fastest, lowest accuracy (default)
- **YOLOv8s**: Balanced speed and accuracy
- **YOLOv8m**: Better accuracy, slower
- **YOLOv8l**: High accuracy, slower
- **YOLOv8x**: Best accuracy, slowest

To use a different model:
```python
detector = RealTimeObjectDetector(model_path='yolov8s.pt')
```

## Troubleshooting

### Camera Issues
1. Check if camera is connected and working
2. Ensure no other applications are using the camera
3. Try different camera indices (0, 1, 2...)
4. Grant camera permissions to Python/terminal

### Performance Issues
1. Install GPU-enabled PyTorch for CUDA support
2. Reduce camera resolution or FPS
3. Use a lighter YOLO model (yolov8n.pt)
4. Close other resource-intensive applications

### Model Download Issues
1. Check internet connection
2. Ensure sufficient disk space
3. Try manually downloading model files
4. Check firewall/antivirus settings

## Output Files

- **Screenshots**: `screenshot_[timestamp].jpg`
- **Processed images**: `detected_[original_name]`
- **Video recordings**: `output.mp4` (if enabled)

## Examples

### Basic Usage
```python
# Simple real-time detection
detector = RealTimeObjectDetector()
detector.run_detection()
```

### Custom Configuration
```python
# High-accuracy detection with video recording
detector = RealTimeObjectDetector(
    model_path='yolov8l.pt',
    confidence_threshold=0.7
)
detector.run_detection(save_video=True, output_path="my_video.mp4")
```

### Image Processing
```python
# Process single image
detector = RealTimeObjectDetector(confidence_threshold=0.4)
detections = detector.detect_from_image('my_image.jpg')

for detection in detections:
    print(f"Found {detection['class_name']} with {detection['confidence']:.2f} confidence")
```

## License

This project uses the Ultralytics YOLOv8 model, which is licensed under AGPL-3.0.

## Contributing

Feel free to submit issues and enhancement requests!