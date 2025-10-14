# Real-time Face Detection Model

A comprehensive face detection system built with OpenCV for real-time video processing and static image analysis.

## Features

- **Real-time face detection** from camera feed
- **Static image processing** for batch analysis
- **Multiple detection methods** (Haar Cascade and DNN-based)
- **Performance monitoring** with FPS tracking
- **Configurable parameters** for detection sensitivity
- **Bounding box visualization** with confidence scores
- **Frame saving** capabilities for analysis
- **Cross-platform compatibility** (Windows, Linux, macOS)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have a working camera connected to your system.

## Usage

### Real-time Detection

Run the demo script for real-time face detection:

```bash
python face_detection_demo.py
```

### Advanced Options

```bash
# Use specific camera
python face_detection_demo.py --camera_id 1

# Use DNN detection method (requires model files)
python face_detection_demo.py --method dnn

# Save detected frames
python face_detection_demo.py --save --output_dir my_output

# Run without display window (headless)
python face_detection_demo.py --no-display
```

### Single Image Processing

Process a single image file:

```bash
python face_detection_demo.py --image path/to/image.jpg --output result.jpg
```

### Programmatic Usage

```python
from face_detection_model import RealTimeFaceDetector, FaceDetectionModel

# Create detector
detector = RealTimeFaceDetector(
    camera_id=0,
    detection_method="haar",
    display_window=True
)

# Start real-time detection
detector.start_detection()

# Or process single image
faces = detector.detect_single_image("image.jpg", "output.jpg")
```

## Controls (Real-time Mode)

- **Q or ESC**: Quit the application
- **S**: Save current frame as screenshot

## Configuration Options

### FaceDetectionModel Parameters

- `detection_method`: "haar" (fast) or "dnn" (accurate)
- `scale_factor`: Image pyramid scaling (default: 1.1)
- `min_neighbors`: Detection stability threshold (default: 5)
- `min_size`: Minimum face size in pixels (default: 30x30)
- `confidence_threshold`: Minimum confidence for DNN (default: 0.5)

### RealTimeFaceDetector Parameters

- `camera_id`: Camera device ID (default: 0)
- `display_window`: Show video window (default: True)
- `save_frames`: Save detection frames (default: False)
- `output_dir`: Output directory for saved frames

## Performance

- **Haar Cascade**: ~30+ FPS on modern hardware
- **DNN Method**: ~10-15 FPS (more accurate but slower)
- Memory usage: ~50-100MB depending on resolution

## Troubleshooting

### Common Issues

1. **Camera not found**: Check camera connections and permissions
2. **Low FPS**: Reduce video resolution or use Haar cascade method
3. **No faces detected**: Adjust lighting or detection parameters
4. **OpenCV errors**: Ensure proper OpenCV installation

### Camera Issues

```python
# Test camera availability
import cv2
cap = cv2.VideoCapture(0)
print("Camera available:", cap.isOpened())
cap.release()
```

### Dependencies

If you encounter OpenCV issues, try:

```bash
# Uninstall existing OpenCV
pip uninstall opencv-python opencv-contrib-python

# Install fresh OpenCV
pip install opencv-python
```

## Model Information

### Haar Cascade
- **Method**: Classical computer vision approach
- **Speed**: Very fast (30+ FPS)
- **Accuracy**: Good for frontal faces
- **File**: Uses OpenCV's built-in haarcascade_frontalface_default.xml

### DNN Method (Future Enhancement)
- **Method**: Deep neural network
- **Speed**: Moderate (10-15 FPS)  
- **Accuracy**: Better for various angles and conditions
- **Requirements**: Additional model files (deploy.prototxt, .caffemodel)

## File Structure

```
Face/
├── face_detection_model.py    # Main model implementation
├── face_detection_demo.py     # Demo and testing script
├── requirements.txt           # Python dependencies
├── README.md                 # This documentation
└── output/                   # Default output directory
```

## API Reference

### FaceDetectionModel Class

#### Methods
- `detect_faces(frame)`: Detect faces in a frame
- `draw_faces(frame, faces)`: Draw bounding boxes on frame
- `get_performance_stats()`: Get FPS and timing statistics
- `reset_performance_stats()`: Reset performance counters

### RealTimeFaceDetector Class

#### Methods
- `start_detection()`: Start real-time camera detection
- `stop_detection()`: Stop detection and cleanup
- `detect_single_image(path, output)`: Process single image file

## License

This project is part of the AI Models collection. See the main project license for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Changelog

- **v1.0.0**: Initial release with Haar cascade support
- Real-time camera detection
- Single image processing
- Performance monitoring
- Configurable parameters