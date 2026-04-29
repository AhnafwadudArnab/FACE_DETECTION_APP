import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';

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
        if (mounted) {
          setState(() {
            _isCameraInitialized = true;
          });
        }
      }
    } catch (e) {
      if (kDebugMode) print('Error initializing camera: $e');
    }
  }

  /// Takes a picture and immediately returns to the previous screen with the
  /// image path. Analysis is handled by HomePage so there is no race condition
  /// between Navigator.pop and a pending upload.
  Future<void> _takePicture() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    try {
      final XFile image = await _controller!.takePicture();
      setState(() => _capturedImagePath = image.path);
      if (!mounted) return;
      // Return the path — HomePage will trigger analysis automatically.
      Navigator.pop(context, image.path);
    } catch (e) {
      if (kDebugMode) print('Error taking picture: $e');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Error taking picture'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _pickImageFromGallery() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        setState(() => _capturedImagePath = image.path);
        if (!mounted) return;
        // Return selected image to HomePage for analysis.
        Navigator.pop(context, image.path);
      }
    } catch (e) {
      if (kDebugMode) print('Error picking image: $e');
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Error selecting image'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _switchCamera() async {
    if (cameras == null || cameras!.length < 2) return;
    final currentCamera = _controller?.description;
    final newCamera = cameras!.firstWhere(
      (c) => c != currentCamera,
      orElse: () => cameras![0],
    );
    await _controller?.dispose();
    _controller = CameraController(newCamera, ResolutionPreset.high);
    try {
      await _controller!.initialize();
      if (mounted) setState(() {});
    } catch (e) {
      if (kDebugMode) print('Error switching camera: $e');
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
            // ── Camera preview ──────────────────────────────────────────────
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

            // ── Rule-of-thirds grid ─────────────────────────────────────────
            if (_isCameraInitialized)
              Positioned.fill(child: CustomPaint(painter: _GridPainter())),

            // ── Top bar ─────────────────────────────────────────────────────
            Positioned(
              top: 16,
              left: 0,
              right: 0,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: const Icon(Icons.flash_off, color: Colors.white),
                    onPressed: () {},
                  ),
                  const Icon(Icons.expand_less, color: Colors.white),
                  IconButton(
                    icon: const Icon(Icons.switch_camera, color: Colors.white),
                    onPressed: _switchCamera,
                  ),
                ],
              ),
            ),

            // ── Bottom controls ─────────────────────────────────────────────
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
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _ModeText('PHOTO', isSelected: true),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        // Gallery
                        Flexible(
                          flex: 1,
                          child: GestureDetector(
                            onTap: _pickImageFromGallery,
                            child: ConstrainedBox(
                              constraints: const BoxConstraints(
                                  maxWidth: 56, maxHeight: 56,
                                  minWidth: 36, minHeight: 36),
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.white.withOpacity(0.3),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.photo_library,
                                    color: Colors.white, size: 24),
                              ),
                            ),
                          ),
                        ),

                        // Shutter
                        Flexible(
                          flex: 2,
                          child: GestureDetector(
                            onTap: _takePicture,
                            child: ConstrainedBox(
                              constraints: const BoxConstraints(
                                  minWidth: 56, minHeight: 56,
                                  maxWidth: 96, maxHeight: 96),
                              child: Container(
                                width: double.infinity,
                                height: double.infinity,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  border:
                                      Border.all(color: Colors.white, width: 6),
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

                        // Last captured thumbnail
                        Flexible(
                          flex: 1,
                          child: GestureDetector(
                            onTap: () {
                              if (_capturedImagePath != null) {
                                _showImagePreview(_capturedImagePath!);
                              }
                            },
                            child: ConstrainedBox(
                              constraints: const BoxConstraints(
                                  maxWidth: 56, maxHeight: 56,
                                  minWidth: 36, minHeight: 36),
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
                                          errorBuilder: (_, __, ___) =>
                                              const Icon(Icons.image,
                                                  color: Colors.white,
                                                  size: 24),
                                        ),
                                      )
                                    : const Icon(Icons.image,
                                        color: Colors.white, size: 24),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text('0.5', style: TextStyle(color: Colors.white)),
                        SizedBox(width: 24),
                        Text('1x',
                            style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 16)),
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
      builder: (ctx) => Dialog(
        backgroundColor: Colors.transparent,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              constraints: BoxConstraints(
                maxHeight: MediaQuery.of(ctx).size.height * 0.8,
                maxWidth: MediaQuery.of(ctx).size.width * 0.9,
              ),
              child: Image.file(File(imagePath), fit: BoxFit.contain),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () => Navigator.of(ctx).pop(),
                  child: const Text('Close'),
                ),
                ElevatedButton(
                  onPressed: () => Navigator.of(ctx).pop(),
                  child: const Text('Share'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────

class _GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.2)
      ..strokeWidth = 1;
    for (int i = 1; i < 3; i++) {
      final dx = size.width * i / 3;
      canvas.drawLine(Offset(dx, 0), Offset(dx, size.height), paint);
    }
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
