import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'dart:convert';

class CameraPage extends StatefulWidget {
  const CameraPage({super.key});

  @override
  State<CameraPage> createState() => _CameraPageState();
}

class _CameraPageState extends State<CameraPage> {
  CameraController? _controller;
  List<CameraDescription>? cameras;
  bool _isCameraInitialized = false;
  final ImagePicker _picker = ImagePicker();
  String? _capturedImagePath;
  // Update this to your server address. For Android emulator use 10.0.2.2
  static const String SERVER_URL = 'http://10.15.41.155:5000';
  //mobile
  static const String MOBILE_SERVER_URL = 'http://10.0.2.2:5000';
  //home
  static const String Home_server="http://192.168.68.100:5000";

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      cameras = await availableCameras();
      if (cameras != null && cameras!.isNotEmpty) {
        _controller = CameraController(cameras![0], ResolutionPreset.high);

        await _controller!.initialize();
        setState(() {
          _isCameraInitialized = true;
        });
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error initializing camera: $e');
      }
    }
  }

  Future<void> _takePicture() async {
    if (_controller != null && _controller!.value.isInitialized) {
      try {
        final XFile image = await _controller!.takePicture();
        setState(() {
          _capturedImagePath = image.path;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Picture saved to: ${image.path}'),
            backgroundColor: Colors.green,
          ),
        );

        // Upload to server and show results
        _uploadImageAndShowResults(image.path);
        // Optionally return to previous screen with image path
        Navigator.pop(context, image.path);
      } catch (e) {
        if (kDebugMode) {
          print('Error taking picture: $e');
        }
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error taking picture'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _uploadImageAndShowResults(String imagePath) async {
  final uri = Uri.parse('$SERVER_URL/api/detect');
    try {
      final request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath('image', imagePath));
      final streamed = await request.send();
      final res = await http.Response.fromStream(streamed);
      if (res.statusCode == 200) {
        final Map<String, dynamic> body = json.decode(res.body);
        _showDetectionResults(body);
      } else {
        _showError('Server returned ${res.statusCode}');
      }
    } catch (e) {
      if (kDebugMode) print('Upload error: $e');
      _showError('Failed to upload image: $e');
    }
  }

  void _showError(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('OK'))],
      ),
    );
  }

  void _showDetectionResults(Map<String, dynamic> body) {
    final faces = (body['faces'] as List<dynamic>?) ?? [];
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text('Detections (${faces.length})'),
          content: SizedBox(
            width: double.maxFinite,
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: faces.length,
              itemBuilder: (context, index) {
                final f = faces[index] as Map<String, dynamic>;
                final age = f['age']?.toString() ?? 'N/A';
                final gender = f['gender']?.toString() ?? 'N/A';
                final emotion = f['emotion']?.toString() ?? 'N/A';
                return ListTile(
                  title: Text('Face ${f['face_id'] ?? index}'),
                  subtitle: Text('Age: $age, Gender: $gender, Emotion: $emotion'),
                );
              },
            ),
          ),
          actions: [TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Close'))],
        );
      },
    );
  }

  Future<void> _pickImageFromGallery() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        setState(() {
          _capturedImagePath = image.path;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Image selected: ${image.path}'),
            backgroundColor: Colors.blue,
          ),
        );
      }
    } catch (e) {
      if (kDebugMode) {
        print('Error picking image: $e');
      }
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Error selecting image'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _switchCamera() async {
    if (cameras != null && cameras!.length > 1) {
      final currentCamera = _controller?.description;
      final newCamera = cameras!.firstWhere(
        (camera) => camera != currentCamera,
        orElse: () => cameras![0],
      );

      await _controller?.dispose();
      _controller = CameraController(newCamera, ResolutionPreset.high);

      try {
        await _controller!.initialize();
        setState(() {});
      } catch (e) {
        if (kDebugMode) {
          print('Error switching camera: $e');
        }
      }
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF893939),
      body: SafeArea(
        child: Stack(
          children: [
            // Camera preview or placeholder
            Positioned.fill(
              child: _isCameraInitialized && _controller != null
                  ? CameraPreview(_controller!)
                  : Container(
                      color: const Color(0xFF893939),
                      child: const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            CircularProgressIndicator(color: Colors.white),
                            SizedBox(height: 16),
                            Text(
                              'Initializing Camera...',
                              style: TextStyle(color: Colors.white),
                            ),
                          ],
                        ),
                      ),
                    ),
            ),

            // Grid overlay for better photo composition
            if (_isCameraInitialized)
              Positioned.fill(child: CustomPaint(painter: _GridPainter())),

            // Top bar with controls
            Positioned(
              top: 16,
              left: 0,
              right: 0,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: const Icon(Icons.flash_off, color: Colors.white),
                    onPressed: () {
                      // Flash toggle functionality can be added here
                    },
                  ),
                  const Icon(Icons.expand_less, color: Colors.white),
                  IconButton(
                    icon: const Icon(Icons.switch_camera, color: Colors.white),
                    onPressed: _switchCamera,
                  ),
                ],
              ),
            ),

            // Bottom controls
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 24),
                color: Colors.black.withOpacity(0.3),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Mode selector
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        // _ModeText('CINEMA'),
                        // _ModeText('VIDEO'),
                        _ModeText('PHOTO', isSelected: true),
                        // _ModeText('PORTRAIT'),
                        // _ModeText('PANO'),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Camera controls
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        // Gallery button - allow to shrink
                        Flexible(
                          flex: 1,
                          child: GestureDetector(
                            onTap: _pickImageFromGallery,
                            child: ConstrainedBox(
                              constraints: const BoxConstraints(maxWidth: 56, maxHeight: 56, minWidth: 36, minHeight: 36),
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.3),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(
                                  Icons.photo_library,
                                  color: Colors.white,
                                  size: 24,
                                ),
                              ),
                            ),
                          ),
                        ),

                        // Shutter button - keep prominent but allow slight shrinking
                        Flexible(
                          flex: 2,
                          child: GestureDetector(
                            onTap: _takePicture,
                            child: ConstrainedBox(
                              constraints: const BoxConstraints(minWidth: 56, minHeight: 56, maxWidth: 96, maxHeight: 96),
                              child: Container(
                                width: double.infinity,
                                height: double.infinity,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  border: Border.all(color: Colors.white, width: 6),
                                ),
                                child: Center(
                                  child: Container(
                                    width: 56,
                                    height: 56,
                                    decoration: const BoxDecoration(
                                      color: Colors.white,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),

                        // Preview of last captured image - allow to shrink
                        Flexible(
                          flex: 1,
                          child: GestureDetector(
                            onTap: () {
                              if (_capturedImagePath != null) {
                                _showImagePreview(_capturedImagePath!);
                              }
                            },
                            child: ConstrainedBox(
                              constraints: const BoxConstraints(maxWidth: 56, maxHeight: 56, minWidth: 36, minHeight: 36),
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.3),
                                  shape: BoxShape.circle,
                                ),
                                child: _capturedImagePath != null
                                    ? ClipOval(
                                        child: Image.file(
                                          File(_capturedImagePath!),
                                          fit: BoxFit.cover,
                                          errorBuilder: (context, error, stackTrace) {
                                            return const Icon(
                                              Icons.image,
                                              color: Colors.white,
                                              size: 24,
                                            );
                                          },
                                        ),
                                      )
                                    : const Icon(
                                        Icons.image,
                                        color: Colors.white,
                                        size: 24,
                                      ),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // Zoom controls
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('0.5', style: TextStyle(color: Colors.white)),
                        SizedBox(width: 24),
                        Text(
                          '1x',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        SizedBox(width: 24),
                        Text('2x', style: TextStyle(color: Colors.white)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showImagePreview(String imagePath) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Dialog(
          backgroundColor: Colors.transparent,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                constraints: BoxConstraints(
                  maxHeight: MediaQuery.of(context).size.height * 0.8,
                  maxWidth: MediaQuery.of(context).size.width * 0.9,
                ),
                child: Image.file(File(imagePath), fit: BoxFit.contain),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  ElevatedButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('Close'),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      // Add share functionality here
                      Navigator.of(context).pop();
                    },
                    child: const Text('Share'),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}

class _GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.2)
      ..strokeWidth = 1;

    // Draw vertical lines (rule of thirds)
    for (int i = 1; i < 3; i++) {
      final dx = size.width * i / 3;
      canvas.drawLine(Offset(dx, 0), Offset(dx, size.height), paint);
    }

    // Draw horizontal lines (rule of thirds)
    for (int i = 1; i < 3; i++) {
      final dy = size.height * i / 3;
      canvas.drawLine(Offset(0, dy), Offset(size.width, dy), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class _ModeText extends StatelessWidget {
  final String text;
  final bool isSelected;

  const _ModeText(this.text, {this.isSelected = false});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: TextStyle(
        color: isSelected ? Colors.yellow : Colors.white,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        fontSize: 12,
      ),
    );
  }
}
