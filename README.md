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

### Prerequisites
- [Flutter SDK](https://flutter.dev/docs/get-started/install)
- Dart SDK (comes with Flutter)
- Android Studio / Xcode (for mobile development)
- Python 3.10+ (for AI model training, if needed)

### Clone the Repository
```bash
git clone https://github.com/yourusername/face-detector.git
cd face-detector
```

### Install Dependencies
```bash
flutter pub get
```

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

### Running the App
```bash
flutter run
```

### Example
- Open the app and grant camera permissions.
- Point the camera at a face to see real-time detection.
- Use the gallery to select an image for analysis.

---


## Screenshots

### Web Version

1. **Main Upload Page**
   <img width="894" height="337" alt="1" src="https://github.com/user-attachments/assets/41910e1e-eeb2-4c92-9a48-c2d9e098bdb2" />

2. **Detection Results (Summary and Face Analysis)**
   
<img width="778" height="896" alt="2" src="https://github.com/user-attachments/assets/19a90db7-b851-4fb7-8cc6-58cb28e52395" />

3. **Detection Results (Detailed View)**
   
<img width="714" height="746" alt="3" src="https://github.com/user-attachments/assets/34e2a119-de76-4e1a-aa3f-509f4a5da3bd" />

### Mobile Version

1. **Face Analysis Loading Screen**
   
 ![af](https://github.com/user-attachments/assets/17c5a37f-05ae-493e-98bd-8060c83e4fb4)

2. **Camera Interface (No Face)**
 
<img width="478" height="915" alt="camera" src="https://github.com/user-attachments/assets/7bddcb86-edf9-4fb8-91ee-3105b409fb14" />

3. **Camera Interface (With Object)**
 
<img width="350" height="608" alt="m3" src="https://github.com/user-attachments/assets/6a0af3cb-1862-491f-8ecd-0d6c58ae157b" />

![45](https://github.com/user-attachments/assets/934b1859-c2d4-408b-bf09-26128c7fb49c)

---


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
