# Quick Reference - Object Detection System

## 🚀 Quick Start

### Easy Way (Recommended)
```powershell
# Run tests
.\run.ps1 test

# Start real-time detection
.\run.ps1 demo

# Test camera
.\run.ps1 camera-test
```

### Manual Way
```bash
"C:/flutter/projects/Ai models/.venv/Scripts/python.exe" object_detection_demo.py
```

## 🎯 What It Detects

| Category | Color | Objects |
|----------|-------|---------|
| **Persons** | 🟢 Green | People in any pose |
| **Animals** | 🟠 Orange | Cats, dogs, birds, horses, etc. |
| **Devices** | 🔵 Blue | Phones, laptops, TVs, keyboards |

## 🎮 Controls (Real-time mode)

- **'q'** - Quit
- **'s'** - Save screenshot
- **ESC** - Also quits

## 📁 Key Files

- `object_detection_model.py` - Main system
- `object_detection_demo.py` - Demo script
- `run.ps1` / `run.bat` - Easy runners
- `test_object_detection.py` - Test suite

## ✅ Status Check

Run `.\run.ps1 test` to verify:
- ✅ Dependencies installed
- ✅ Camera working
- ✅ All tests passing

## 🐛 Common Issues

**"ModuleNotFoundError: No module named 'cv2'"**
- Solution: Use `.\run.ps1` scripts or full Python path
- Don't use just `python`, use the virtual environment

**Camera not working**
- Check if other apps are using camera
- Try different camera index (0, 1, 2...)
- Ensure camera permissions granted

## 📊 Performance Tips

- **Faster**: Use `yolov8n.pt` (default)
- **More accurate**: Use `yolov8l.pt`
- **Lower confidence**: More detections
- **Higher confidence**: Fewer, more certain detections