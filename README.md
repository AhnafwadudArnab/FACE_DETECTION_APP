# Face Detector

> **Project Name:** MindXScope Face Detector

---

## Overview

MindXScope Face Detector is a cross-platform application designed to detect faces using advanced AI models. Built with Flutter and integrated with custom AI models, it supports Android, iOS, and web platforms. The project leverages modern machine learning techniques for real-time face detection and recognition.

---

## Features

- Real-time face detection using AI models
- Multi-platform support: Android, iOS, Web, Windows
- Camera integration for live detection
- Image picker for static image analysis
- Modular architecture for easy extension
- User-friendly interface
- High accuracy and performance

---

## Installation

- Dart SDK (comes with Flutter)
- Android Studio / Xcode (for mobile development)
- Python 3.10+ (for AI model training, if needed)

### Platform-specific Setup
- **Android:**
  - Open `android/` in Android Studio and run on an emulator or device.
- **iOS:**
  - Open `ios/Runner.xcworkspace` in Xcode and run on a simulator or device.
- **Web:**
  - Run `flutter run -d chrome`.
- **Windows:**
  - Run `flutter run -d windows`.

---

## Usage

### Example
- Open the app and grant camera permissions.
- Point the camera at a face to see real-time detection.
- Use the gallery to select an image for analysis.

---


## Screenshots

### Mobile Version

1. 
<img width="922" height="2049" alt="d185733b-a058-4045-a48a-b15bedf0dfc0" src="https://github.com/user-attachments/assets/24ee5052-ef0e-4d2c-8a95-584076a3edc3" />
2.
<img width="922" height="2049" alt="79f00c48-dad0-4a67-be3b-7205970dbd88" src="https://github.com/user-attachments/assets/b23c33c5-86ca-4f66-903c-1ee396138340" />



## Project Structure

```
face-detector/
├── Ai model/
│   ├── Faces Detectors/
│   ├── ai_detector_env/
│   ├── assets/
│   ├── DataSets/
│   ├── Models/
│   └── webapp/
├── android/
├── ios/
├── lib/
│   ├── main.dart
│   └── Features/
├── test/
├── web/
├── windows/
├── pubspec.yaml
└── README.md
```

---

## Development Notes

- **AI Model:**
  - Custom models are stored in `Ai model/Models/`.
  - Training scripts and datasets are in `Ai model/DataSets/`.
  - Python environment for model development: `Ai model/ai_detector_env/`.
- **Flutter App:**
  - Main entry: `lib/main.dart`
  - Features: `lib/Features/`
- **Assets:**
  - Place images, models, and other resources in `Ai model/assets/`.

---

## Contributing

Contributions are welcome! Please open issues and submit pull requests for improvements or bug fixes.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact

- **Author:** Your Name
- **Email:** your.email@example.com
- **GitHub:** [yourusername](https://github.com/yourusername)

---
