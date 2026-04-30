<div align="center">

<img src="https://img.shields.io/badge/Flutter-3.x-02569B?style=for-the-badge&logo=flutter&logoColor=white" />
<img src="https://img.shields.io/badge/Dart-3.x-0175C2?style=for-the-badge&logo=dart&logoColor=white" />
<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Platform-Android%20%7C%20iOS%20%7C%20Web-lightgrey?style=for-the-badge" />
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />

# 🧠 MindXScope — AI Face Analysis

**Real-time face detection with age, gender, emotion & race analysis — powered by a custom AI model and built with Flutter.**

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Face Detection** | Detects multiple faces in a single image |
| 🎂 **Age Estimation** | Predicts approximate age with confidence score |
| ⚧ **Gender Classification** | Male / Female detection with confidence bar |
| 😊 **Emotion Recognition** | 7 emotions — Happy, Sad, Angry, Surprised, Fear, Disgust, Neutral |
| 🌍 **Race / Ethnicity** | Ethnicity classification per face |
| 📊 **Emotion Breakdown** | Animated bar chart showing all emotion scores |
| ✏️ **Emotion Override** | Manually correct emotion labels and sync to server |
| 📷 **Camera Integration** | Full-screen live camera with flash & front/back switch |
| 🖼️ **Gallery Picker** | Analyze any image from device gallery |
| 🌐 **Server Status** | Live server health indicator with auto wake-up (Render cold start) |
| 📋 **Copy JSON** | Export raw analysis result to clipboard |
| 🎨 **Dark UI** | Polished dark theme with animated face cards |

---

## 📸 Screenshots

### Mobile App

| Home Screen | Camera | Analysis Results |
|---|---|---|
| <img width="250" src="https://github.com/user-attachments/assets/17c5a37f-05ae-493e-98bd-8060c83e4fb4" /> | <img width="250" src="https://github.com/user-attachments/assets/7bddcb86-edf9-4fb8-91ee-3105b409fb14" /> | <img width="250" src="https://github.com/user-attachments/assets/934b1859-c2d4-408b-bf09-26128c7fb49c" /> |

### Web Version

| Upload Page | Detection Summary | Detailed Results |
|---|---|---|
| <img src="https://github.com/user-attachments/assets/41910e1e-eeb2-4c92-9a48-c2d9e098bdb2" /> | <img src="https://github.com/user-attachments/assets/19a90db7-b851-4fb7-8cc6-58cb28e52395" /> | <img src="https://github.com/user-attachments/assets/34e2a119-de76-4e1a-aa3f-509f4a5da3bd" /> |

---

## 🏗️ Architecture

```
MindXScope/
├── lib/
│   ├── main.dart               # App entry point, camera init
│   └── Features/
│       ├── homepage.dart       # Main analysis UI + API calls
│       └── camera.dart         # Full-screen camera with controls
│
├── Ai model/
│   ├── Faces Detectors/        # Core detection model
│   ├── Models/                 # Trained model files
│   ├── DataSets/               # Training datasets
│   └── webapp/                 # Python Flask/FastAPI backend
│
├── android/                    # Android platform config
├── ios/                        # iOS platform config
├── web/                        # Web platform config
└── windows/                    # Windows platform config
```

---

## 🔧 Tech Stack

**Frontend (Mobile & Web)**
- [Flutter](https://flutter.dev/) — cross-platform UI framework
- `camera` — live camera preview & capture
- `image_picker` — gallery image selection
- `http` — REST API communication

**Backend (AI Server)**
- Python 3.10+
- Custom face detection & attribute analysis model
- Hosted on [Render](https://render.com) — `https://face-detection-app-9ea5.onrender.com`

---

## 🚀 Getting Started

### Prerequisites

- Flutter SDK `^3.x` — [Install Flutter](https://docs.flutter.dev/get-started/install)
- Dart SDK `^3.8.1` (bundled with Flutter)
- Android Studio / Xcode for mobile builds

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/mindxscope.git
cd mindxscope

# 2. Install dependencies
flutter pub get

# 3. Run the app
flutter run                  # auto-detect connected device
flutter run -d chrome        # web
flutter run -d android       # Android
flutter run -d ios           # iOS
```

### Android Permissions

Camera and storage permissions are handled automatically via `permission_handler`. Make sure your device allows camera access when prompted.

---

## 🌐 API Reference

The app communicates with a hosted Python backend.

**Base URL:** `https://face-detection-app-9ea5.onrender.com`

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check / wake-up ping |
| `/api/detect` | POST | Analyze image — returns faces array |
| `/api/override` | POST | Override emotion label for a face |

**`/api/detect` Response Example:**
```json
{
  "uid": "abc123",
  "object": "Human Face",
  "annotated_url": "https://...",
  "faces": [
    {
      "face_id": "1",
      "age": "25",
      "gender": "Male",
      "emotion": "Happy",
      "race": "Asian",
      "bbox": [120, 80, 200, 220],
      "age_confidence": 0.87,
      "gender_confidence": 0.94,
      "emotion_confidence": 0.76,
      "emotion_scores": {
        "happy": 0.76,
        "neutral": 0.14,
        "sad": 0.05,
        "angry": 0.03,
        "surprised": 0.01,
        "fear": 0.01,
        "disgust": 0.00
      }
    }
  ]
}
```

---

## 📱 Platform Support

| Platform | Status |
|---|---|
| Android | ✅ Supported |
| iOS | ✅ Supported |
| Web (Chrome) | ✅ Supported |
| Windows | ✅ Supported |

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch — `git checkout -b feature/your-feature`
3. Commit your changes — `git commit -m 'Add your feature'`
4. Push to the branch — `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

<div align="center">
  <sub>Built with ❤️ using Flutter & AI</sub>
</div>
