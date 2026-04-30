import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:mindxscope/Features/camera.dart';
import 'dart:io';
import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

class HomePage extends StatefulWidget {
  final String? capturedImagePath;
  const HomePage({super.key, this.capturedImagePath});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String? _currentImagePath;
  bool _serverReachable = false;
  bool _isAnalyzing = false;
  String? _analysisError;
  Map<String, dynamic>? _analysisResult;

  DateTime? _lastAnalyzedAt;
  int? _lastFacesCount;
  final ImagePicker _picker = ImagePicker();
  static const String _serverUrl = 'https://face-detection-app-9ea5.onrender.com';

  @override
  void initState() {
    super.initState();
    _currentImagePath = widget.capturedImagePath;
    _checkServer();
  }

  List<String> _getServers() => [_serverUrl];

  Future<void> _checkServer() async {
    try {
      final r = await http
          .get(Uri.parse('$_serverUrl/'), headers: {'Accept': 'text/html'})
          .timeout(const Duration(seconds: 5));
      setState(() => _serverReachable = r.statusCode == 200);
    } catch (_) {
      setState(() => _serverReachable = false);
    }
  }

  Future<void> _navigateToCamera() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CameraPage()),
    );

    if (result != null && result is String) {
      setState(() {
        _currentImagePath = result;
        _analysisResult = null;
        _analysisError = null;
      });

      // Start analysis automatically when we have a new image
      _analyzeImage(result);
    }

  }

  Future<void> _pickImageFromGallery() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
      if (image != null) {
        setState(() {
          _currentImagePath = image.path;
          _analysisResult = null;
          _analysisError = null;
        });
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Image selected: ${image.path}')));
        await _analyzeImage(image.path);
      }
    } catch (e) {
      if (kDebugMode) print('Error picking image: $e');
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Error selecting image'), backgroundColor: Colors.red));
    }
  }

  Future<void> _analyzeImage(String imagePath) async {
    setState(() {
      _isAnalyzing = true;
      _analysisError = null;
      _analysisResult = null;
    });

  // Determine server list from selection
  final servers = _getServers();
    String? lastError;

    for (final base in servers) {
      final uri = Uri.parse('$base/api/detect');
      try {
        final request = http.MultipartRequest('POST', uri);
        request.files.add(await http.MultipartFile.fromPath('image', imagePath));
        final streamed = await request.send().timeout(const Duration(seconds: 10));
        final res = await http.Response.fromStream(streamed);
        if (res.statusCode == 200) {
          final Map<String, dynamic> body = json.decode(res.body);
          // If an annotated_url was provided, convert localhost to emulator host if needed
          if (body.containsKey('annotated_url') && body['annotated_url'] is String) {
            var url = body['annotated_url'] as String;
            // Replace 127.0.0.1 or localhost with emulator host when running on emulator
            if (url.contains('127.0.0.1') || url.contains('localhost')) {
              url = url.replaceAll('127.0.0.1', '10.0.2.2').replaceAll('localhost', '10.0.2.2');
            }
            body['annotated_url'] = url;
          }
          setState(() {
            _analysisResult = body;
            _isAnalyzing = false;
            _serverReachable = true;
            _lastAnalyzedAt = DateTime.now();
            _lastFacesCount = (body['faces'] is List) ? (body['faces'] as List).length : null;
          });
          if (kDebugMode) print('Analysis response: ${res.body}');
          return;
        } else {
          lastError = 'Server $base returned ${res.statusCode}';
        }
      } catch (e) {
        lastError = e.toString();
      }
    }

    setState(() {
      _isAnalyzing = false;
      _analysisError = 'Failed to analyze image: ${lastError ?? 'unknown'}';
      _serverReachable = false;
    });
  }

  /// A single info row: icon + bold label + value underneath.
  Widget _buildAnalysisRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 15, color: const Color(0xFF6C63FF)),
          const SizedBox(width: 8),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(
                    fontSize: 13, color: Color(0xFFCCCCEE)),
                children: [
                  TextSpan(
                    text: '$label: ',
                    style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF9D97FF)),
                  ),
                  TextSpan(text: value),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Confidence bar widget (0.0 – 1.0).
  Widget _buildConfidenceBar(double confidence) {
    final pct = (confidence * 100).toStringAsFixed(1);
    final color = confidence >= 0.8
        ? const Color(0xFF2ECC71)
        : confidence >= 0.5
            ? const Color(0xFFF39C12)
            : const Color(0xFFE74C3C);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.bar_chart, size: 15,
                color: Color(0xFF6C63FF)),
            const SizedBox(width: 8),
            const Text('Confidence: ',
                style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF9D97FF))),
            Text('$pct%',
                style: TextStyle(
                    fontSize: 13,
                    color: color,
                    fontWeight: FontWeight.w700)),
          ],
        ),
        const SizedBox(height: 6),
        Padding(
          padding: const EdgeInsets.only(left: 23.0),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: confidence.clamp(0.0, 1.0),
              minHeight: 6,
              backgroundColor: Colors.white.withOpacity(0.08),
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
        ),
      ],
    );
  }

  /// Per-face animated detail card.
  Widget _buildFaceCard(Map<String, dynamic> f, int idx) {
    return _FaceCard(
      data: f,
      idx: idx,
      emotionIcon: _emotionIcon,
      emotionColor: _emotionColor,
      formatBbox: _formatBbox,
      onEditEmotion: () => _showEmotionOverride(f, f['face_id']?.toString() ?? '${idx + 1}'),
    );
  }

  IconData _emotionIcon(String emotion) {
    switch (emotion.toLowerCase()) {
      case 'happy':    return Icons.sentiment_very_satisfied;
      case 'sad':      return Icons.sentiment_very_dissatisfied;
      case 'angry':    return Icons.mood_bad;
      case 'surprised':return Icons.sentiment_satisfied_alt;
      case 'fear':     return Icons.warning_amber_outlined;
      case 'disgust':  return Icons.sick_outlined;
      default:         return Icons.sentiment_neutral;
    }
  }

  Color _emotionColor(String emotion) {
    switch (emotion.toLowerCase()) {
      case 'happy':    return Colors.amber;
      case 'sad':      return Colors.blue;
      case 'angry':    return Colors.red;
      case 'surprised':return Colors.purple;
      case 'fear':     return Colors.orange;
      case 'disgust':  return Colors.green;
      default:         return Colors.grey;
    }
  }

  String _formatBbox(dynamic bbox) {
    if (bbox is List && bbox.length >= 4) {
      final vals = bbox.map((v) => (v as num).toStringAsFixed(0)).toList();
      return 'x:${vals[0]}  y:${vals[1]}  w:${vals[2]}  h:${vals[3]}';
    }
    if (bbox is Map) {
      final x = bbox['x'] ?? bbox['left'] ?? '?';
      final y = bbox['y'] ?? bbox['top'] ?? '?';
      final w = bbox['w'] ?? bbox['width'] ?? '?';
      final h = bbox['h'] ?? bbox['height'] ?? '?';
      return 'x:$x  y:$y  w:$w  h:$h';
    }
    return bbox.toString();
  }

  Future<void> _showEmotionOverride(Map<String, dynamic> f, String fid) async {
    final femo = f['emotion']?.toString() ?? 'neutral';
    final emotions = ['neutral','happy','sad','angry','surprised','fear','disgust'];
    final picked = await showDialog<String?>(
      context: context,
      builder: (_) {
        String sel = femo;
        return AlertDialog(
          backgroundColor: const Color(0xFF1A1A2E),
          title: const Text('Override Emotion',
              style: TextStyle(color: Color(0xFFEAEAFF))),
          content: StatefulBuilder(builder: (c, setS) {
            return Column(
              mainAxisSize: MainAxisSize.min,
              children: emotions.map((e) {
                return RadioListTile<String>(
                  title: Text(e,
                      style: const TextStyle(color: Color(0xFFCCCCEE))),
                  value: e,
                  groupValue: sel,
                  activeColor: const Color(0xFF6C63FF),
                  onChanged: (v) => setS(() => sel = v ?? sel),
                );
              }).toList(),
            );
          }),
          actions: [
            TextButton(
                onPressed: () => Navigator.of(context).pop(null),
                child: const Text('Cancel',
                    style: TextStyle(color: Color(0xFF8888AA)))),
            TextButton(
                onPressed: () => Navigator.of(context).pop(sel),
                child: const Text('Save',
                    style: TextStyle(color: Color(0xFF6C63FF)))),
          ],
        );
      },
    );

    if (picked == null || picked == femo) return;
    final servers = _getServers();
    bool done = false;
    for (final base in servers) {
      try {
        final resp = await http
            .post(
              Uri.parse('$base/api/override'),
              headers: {'Content-Type': 'application/json'},
              body: json.encode({
                'uid': _analysisResult?['uid'],
                'face_id': fid,
                'emotion': picked,
              }),
            )
            .timeout(const Duration(seconds: 5));
        if (resp.statusCode == 200) {
          setState(() {
            if (_analysisResult != null && _analysisResult!['faces'] is List) {
              for (var item in _analysisResult!['faces'] as List) {
                if ((item['face_id']?.toString() ?? '') == fid) {
                  item['emotion'] = picked;
                }
              }
            }
          });
          if (!mounted) return;
          ScaffoldMessenger.of(context)
              .showSnackBar(const SnackBar(content: Text('Override saved')));
          done = true;
          break;
        }
      } catch (_) {}
    }
    if (!done && mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Failed to save override')));
    }
  }

  // ── Design tokens ──────────────────────────────────────────────────────
  static const _bg        = Color(0xFF0F0F1A);
  static const _surface   = Color(0xFF1A1A2E);
  static const _card      = Color(0xFF16213E);
  static const _accent    = Color(0xFF6C63FF);
  static const _accentSoft= Color(0xFF9D97FF);
  static const _textPri   = Color(0xFFEAEAFF);
  static const _textSec   = Color(0xFF8888AA);

  @override
  Widget build(BuildContext context) {
    final mq = MediaQuery.of(context);
    final imageHeight = mq.size.height * 0.30;
    final String objectText =
        _analysisResult?['object']?.toString() ?? 'Human Face';

    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(16, 12, 16, mq.viewPadding.bottom + 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── App header ────────────────────────────────────────────
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
                child: Row(
                  children: [
                    Container(
                      width: 36, height: 36,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [_accent, Color(0xFFFF6584)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.face_retouching_natural,
                          color: Colors.white, size: 20),
                    ),
                    const SizedBox(width: 10),
                    const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('MindXScope',
                            style: TextStyle(
                                color: _textPri, fontSize: 18,
                                fontWeight: FontWeight.w700, letterSpacing: 0.5)),
                        Text('AI Face Analysis',
                            style: TextStyle(
                                color: _textSec, fontSize: 11, letterSpacing: 0.3)),
                      ],
                    ),
                    const Spacer(),
                    // Server status pill
                    GestureDetector(
                      onTap: _checkServer,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: _serverReachable
                              ? const Color(0xFF1A3A2A)
                              : const Color(0xFF3A1A1A),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(
                            color: _serverReachable
                                ? const Color(0xFF2ECC71)
                                : const Color(0xFFE74C3C),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              width: 7, height: 7,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: _serverReachable
                                    ? const Color(0xFF2ECC71)
                                    : const Color(0xFFE74C3C),
                              ),
                            ),
                            const SizedBox(width: 6),
                            Text(
                              _serverReachable ? 'Online' : 'Offline',
                              style: TextStyle(
                                color: _serverReachable
                                    ? const Color(0xFF2ECC71)
                                    : const Color(0xFFE74C3C),
                                fontSize: 11, fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // ── Last analyzed info ────────────────────────────────────
              if (_lastAnalyzedAt != null)
                Padding(
                  padding: const EdgeInsets.only(left: 4, bottom: 8),
                  child: Text(
                    '${_lastAnalyzedAt!.toLocal().hour.toString().padLeft(2, '0')}:'
                    '${_lastAnalyzedAt!.toLocal().minute.toString().padLeft(2, '0')} • '
                    '${_lastFacesCount ?? 0} face${(_lastFacesCount ?? 0) == 1 ? '' : 's'} detected',
                    style: const TextStyle(color: _textSec, fontSize: 11),
                  ),
                ),

              // ── Image preview card ────────────────────────────────────
              Container(
                width: double.infinity,
                height: imageHeight.clamp(200.0, 320.0),
                decoration: BoxDecoration(
                  color: _surface,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: Colors.white.withOpacity(0.07)),
                ),
                clipBehavior: Clip.antiAlias,
                child: _currentImagePath != null
                    ? Stack(
                        fit: StackFit.expand,
                        children: [
                          Image.file(
                            File(_currentImagePath!),
                            fit: BoxFit.cover,
                            filterQuality: FilterQuality.high,
                            gaplessPlayback: true,
                            errorBuilder: (_, __, ___) => const Center(
                              child: Icon(Icons.broken_image, size: 60, color: _textSec),
                            ),
                          ),
                          Positioned(
                            bottom: 0, left: 0, right: 0,
                            child: Container(
                              height: 60,
                              decoration: BoxDecoration(
                                gradient: LinearGradient(
                                  begin: Alignment.bottomCenter,
                                  end: Alignment.topCenter,
                                  colors: [
                                    Colors.black.withOpacity(0.6),
                                    Colors.transparent,
                                  ],
                                ),
                              ),
                            ),
                          ),
                          if (_isAnalyzing)
                            Container(
                              color: Colors.black.withOpacity(0.5),
                              child: const Center(
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    CircularProgressIndicator(color: _accent),
                                    SizedBox(height: 12),
                                    Text('Analyzing...',
                                        style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 14,
                                            fontWeight: FontWeight.w500)),
                                  ],
                                ),
                              ),
                            ),
                        ],
                      )
                    : Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            width: 72, height: 72,
                            decoration: BoxDecoration(
                              color: _accent.withOpacity(0.1),
                              shape: BoxShape.circle,
                              border: Border.all(
                                  color: _accent.withOpacity(0.3), width: 2),
                            ),
                            child: const Icon(Icons.add_photo_alternate_outlined,
                                color: _accent, size: 32),
                          ),
                          const SizedBox(height: 16),
                          const Text('No image selected',
                              style: TextStyle(
                                  color: _textPri, fontSize: 15,
                                  fontWeight: FontWeight.w600)),
                          const SizedBox(height: 4),
                          const Text('Tap camera or gallery below',
                              style: TextStyle(color: _textSec, fontSize: 12)),
                        ],
                      ),
              ),
              const SizedBox(height: 16),

              // ── Analysis results card ─────────────────────────────────
              Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: _surface,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: Colors.white.withOpacity(0.07)),
                ),
                padding: const EdgeInsets.all(20),
                child: _currentImagePath == null
                    ? Column(
                        children: [
                          const SizedBox(height: 8),
                          Icon(Icons.analytics_outlined,
                              size: 48, color: _accent.withOpacity(0.4)),
                          const SizedBox(height: 12),
                          const Text('Take a photo to analyze',
                              style: TextStyle(
                                  color: _textPri, fontSize: 15,
                                  fontWeight: FontWeight.w600)),
                          const SizedBox(height: 4),
                          const Text('Face • Age • Gender • Emotion',
                              style: TextStyle(color: _textSec, fontSize: 12)),
                          const SizedBox(height: 8),
                        ],
                      )
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Title row
                          Row(
                            children: [
                              Container(
                                width: 4, height: 18,
                                decoration: BoxDecoration(
                                  color: _accent,
                                  borderRadius: BorderRadius.circular(2),
                                ),
                              ),
                              const SizedBox(width: 8),
                              const Text('Analysis Results',
                                  style: TextStyle(
                                      color: _textPri, fontSize: 16,
                                      fontWeight: FontWeight.w700)),
                              const Spacer(),
                              if (_analysisResult != null)
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF1A3A2A),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(objectText,
                                      style: const TextStyle(
                                          color: Color(0xFF2ECC71),
                                          fontSize: 11,
                                          fontWeight: FontWeight.w600)),
                                ),
                            ],
                          ),
                          const SizedBox(height: 16),

                          if (_isAnalyzing)
                            const Center(
                              child: Padding(
                                padding: EdgeInsets.symmetric(vertical: 24),
                                child: CircularProgressIndicator(color: _accent),
                              ),
                            )
                          else if (_analysisError != null)
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: const Color(0xFF3A1A1A),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                    color: const Color(0xFFE74C3C).withOpacity(0.4)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.error_outline,
                                      color: Color(0xFFE74C3C), size: 18),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(_analysisError!,
                                        style: const TextStyle(
                                            color: Color(0xFFE74C3C), fontSize: 12)),
                                  ),
                                ],
                              ),
                            )
                          else ...[
                            // Annotated image — smaller, clear face view
                            if (_analysisResult != null &&
                                _analysisResult!['annotated_url'] is String) ...[
                              ClipRRect(
                                borderRadius: BorderRadius.circular(16),
                                child: Image.network(
                                  _analysisResult!['annotated_url'],
                                  width: double.infinity,
                                  height: 160,
                                  fit: BoxFit.contain,
                                  errorBuilder: (_, __, ___) =>
                                      const Icon(Icons.broken_image, color: _textSec),
                                ),
                              ),
                              const SizedBox(height: 16),
                            ],

                            // Face cards
                            // Face cards
                            if (_analysisResult != null &&
                                _analysisResult!['faces'] is List)
                              ...List.generate(
                                (_analysisResult!['faces'] as List).length,
                                (idx) => _buildFaceCard(
                                  (_analysisResult!['faces'] as List)[idx]
                                      as Map<String, dynamic>,
                                  idx,
                                ),
                              ),

                            const SizedBox(height: 12),
                            if (_analysisResult != null)
                              Center(
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 14, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF1A3A2A),
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: const Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.check_circle_outline,
                                          color: Color(0xFF2ECC71), size: 14),
                                      SizedBox(width: 6),
                                      Text('Analysis Complete',
                                          style: TextStyle(
                                              color: Color(0xFF2ECC71),
                                              fontSize: 12,
                                              fontWeight: FontWeight.w600)),
                                    ],
                                  ),
                                ),
                              ),
                            const SizedBox(height: 16),

                            Row(
                              children: [
                                Expanded(
                                  child: _ActionButton(
                                    label: 'Retry',
                                    icon: Icons.refresh_rounded,
                                    onTap: () {
                                      if (_currentImagePath != null) {
                                        _analyzeImage(_currentImagePath!);
                                      }
                                    },
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: _ActionButton(
                                    label: 'Copy JSON',
                                    icon: Icons.copy_rounded,
                                    onTap: () {
                                      Clipboard.setData(ClipboardData(
                                          text: json.encode(
                                              _analysisResult ?? {})));
                                      ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(
                                              content: Text('Copied!')));
                                    },
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ],
                      ),
              ),
              const SizedBox(height: 20),

              // ── Bottom action buttons ─────────────────────────────────
              Row(
                children: [
                  Expanded(
                    child: _BigActionButton(
                      icon: Icons.photo_library_outlined,
                      label: 'Gallery',
                      onTap: _pickImageFromGallery,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: _BigActionButton(
                      icon: Icons.camera_alt_rounded,
                      label: 'Camera',
                      primary: true,
                      onTap: _navigateToCamera,
                    ),
                  ),
                ],
              ),
              SizedBox(height: mq.viewPadding.bottom + 16),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Animated Face Card ────────────────────────────────────────────────────

class _FaceCard extends StatefulWidget {
  final Map<String, dynamic> data;
  final int idx;
  final IconData Function(String) emotionIcon;
  final Color Function(String) emotionColor;
  final String Function(dynamic) formatBbox;
  final VoidCallback onEditEmotion;

  const _FaceCard({
    required this.data,
    required this.idx,
    required this.emotionIcon,
    required this.emotionColor,
    required this.formatBbox,
    required this.onEditEmotion,
  });

  @override
  State<_FaceCard> createState() => _FaceCardState();
}

class _FaceCardState extends State<_FaceCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: 400 + widget.idx * 120),
    );
    _fadeAnim = CurvedAnimation(parent: _ctrl, curve: Curves.easeOut);
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.18),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOutCubic));
    _ctrl.forward();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final f = widget.data;
    final fid = f['face_id']?.toString() ?? '${widget.idx + 1}';
    final age = f['age']?.toString() ?? 'N/A';
    final gender = f['gender']?.toString() ?? 'N/A';
    final emotion = f['emotion']?.toString() ?? 'N/A';
    final race = f['race']?.toString() ?? f['ethnicity']?.toString();
    final bbox = f['bbox'] ?? f['bounding_box'];

    // Per-attribute confidences from server
    final ageConf = f['age_confidence'] != null
        ? (f['age_confidence'] as num).toDouble()
        : null;
    final genderConf = f['gender_confidence'] != null
        ? (f['gender_confidence'] as num).toDouble()
        : null;
    final emotionConf = f['emotion_confidence'] != null
        ? (f['emotion_confidence'] as num).toDouble()
        : null;
    // Fallback: generic confidence/score field
    final rawConf = f['confidence'] ?? f['score'];
    final double? genericConf =
        rawConf != null ? (rawConf as num).toDouble() : null;

    final emotionScores =
        f['emotion_scores'] as Map<String, dynamic>?;

    return FadeTransition(
      opacity: _fadeAnim,
      child: SlideTransition(
        position: _slideAnim,
        child: Container(
          margin: const EdgeInsets.only(bottom: 14),
          decoration: BoxDecoration(
            color: const Color(0xFF16213E),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withOpacity(0.07)),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF6C63FF).withOpacity(0.08),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Header ──────────────────────────────────────────────
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 12),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      const Color(0xFF6C63FF).withOpacity(0.15),
                      Colors.transparent,
                    ],
                    begin: Alignment.centerLeft,
                    end: Alignment.centerRight,
                  ),
                  borderRadius: const BorderRadius.vertical(
                      top: Radius.circular(20)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [
                            Color(0xFF6C63FF),
                            Color(0xFF9D97FF)
                          ],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Center(
                        child: Text(fid,
                            style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.bold)),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Face $fid',
                            style: const TextStyle(
                                color: Color(0xFFEAEAFF),
                                fontSize: 15,
                                fontWeight: FontWeight.w700)),
                        Text(
                          '$gender • $age',
                          style: const TextStyle(
                              color: Color(0xFF8888AA),
                              fontSize: 11),
                        ),
                      ],
                    ),
                    const Spacer(),
                    GestureDetector(
                      onTap: widget.onEditEmotion,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: const Color(0xFF6C63FF)
                              .withOpacity(0.15),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                              color: const Color(0xFF6C63FF)
                                  .withOpacity(0.3)),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.edit_rounded,
                                size: 12,
                                color: Color(0xFF9D97FF)),
                            SizedBox(width: 4),
                            Text('Edit',
                                style: TextStyle(
                                    color: Color(0xFF9D97FF),
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // ── Body ────────────────────────────────────────────────
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Age row with confidence bar
                    _ConfidenceRow(
                      icon: Icons.cake_outlined,
                      label: 'Age',
                      value: age,
                      confidence: ageConf,
                      color: const Color(0xFF6C63FF),
                    ),
                    const SizedBox(height: 10),

                    // Gender row with confidence bar
                    _ConfidenceRow(
                      icon: gender.toLowerCase() == 'male'
                          ? Icons.male
                          : gender.toLowerCase() == 'female'
                              ? Icons.female
                              : Icons.person,
                      label: 'Gender',
                      value: gender,
                      confidence: genderConf,
                      color: gender.toLowerCase() == 'male'
                          ? const Color(0xFF4FC3F7)
                          : const Color(0xFFF48FB1),
                    ),
                    const SizedBox(height: 10),

                    // Emotion row with confidence bar
                    _ConfidenceRow(
                      icon: widget.emotionIcon(emotion),
                      label: 'Emotion',
                      value: emotion,
                      confidence: emotionConf,
                      color: widget.emotionColor(emotion),
                    ),

                    // Race / Ethnicity
                    if (race != null) ...[
                      const SizedBox(height: 10),
                      _InfoRow(
                        icon: Icons.people_outline,
                        label: 'Race',
                        value: race,
                      ),
                    ],

                    // Generic confidence (if no per-field ones)
                    if (genericConf != null &&
                        ageConf == null &&
                        genderConf == null) ...[
                      const SizedBox(height: 10),
                      _ConfidenceRow(
                        icon: Icons.bar_chart,
                        label: 'Confidence',
                        value:
                            '${(genericConf * 100).toStringAsFixed(1)}%',
                        confidence: genericConf,
                        color: genericConf >= 0.8
                            ? const Color(0xFF2ECC71)
                            : genericConf >= 0.5
                                ? const Color(0xFFF39C12)
                                : const Color(0xFFE74C3C),
                      ),
                    ],

                    // Bounding box
                    if (bbox != null) ...[
                      const SizedBox(height: 10),
                      _InfoRow(
                        icon: Icons.crop_free,
                        label: 'BBox',
                        value: widget.formatBbox(bbox),
                      ),
                    ],

                    // Emotion scores breakdown
                    if (emotionScores != null &&
                        emotionScores.isNotEmpty) ...[
                      const SizedBox(height: 14),
                      const Text('Emotion Breakdown',
                          style: TextStyle(
                              color: Color(0xFF9D97FF),
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              letterSpacing: 0.3)),
                      const SizedBox(height: 8),
                      ...emotionScores.entries.map((e) {
                        final v = (e.value as num).toDouble();
                        final col = widget.emotionColor(e.key);
                        return Padding(
                          padding:
                              const EdgeInsets.symmetric(vertical: 3),
                          child: Row(
                            children: [
                              SizedBox(
                                width: 68,
                                child: Text(e.key,
                                    style: const TextStyle(
                                        fontSize: 11,
                                        color: Color(0xFF8888AA))),
                              ),
                              Expanded(
                                child: ClipRRect(
                                  borderRadius:
                                      BorderRadius.circular(4),
                                  child: TweenAnimationBuilder<double>(
                                    tween: Tween(begin: 0, end: v.clamp(0.0, 1.0)),
                                    duration: Duration(
                                        milliseconds: 600 +
                                            widget.idx * 80),
                                    curve: Curves.easeOutCubic,
                                    builder: (_, val, __) =>
                                        LinearProgressIndicator(
                                      value: val,
                                      minHeight: 6,
                                      backgroundColor: Colors.white
                                          .withOpacity(0.07),
                                      valueColor:
                                          AlwaysStoppedAnimation<
                                              Color>(col),
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                '${(v * 100).toStringAsFixed(0)}%',
                                style: TextStyle(
                                    fontSize: 11,
                                    color: col,
                                    fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                        );
                      }),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Confidence Row ─────────────────────────────────────────────────────────

class _ConfidenceRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final double? confidence;
  final Color color;

  const _ConfidenceRow({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
    this.confidence,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 15, color: color),
            const SizedBox(width: 8),
            Text('$label: ',
                style: TextStyle(
                    fontSize: 12,
                    color: color,
                    fontWeight: FontWeight.w600)),
            Text(value,
                style: const TextStyle(
                    fontSize: 13,
                    color: Color(0xFFEAEAFF),
                    fontWeight: FontWeight.w600)),
            const Spacer(),
            if (confidence != null)
              Text(
                '${(confidence! * 100).toStringAsFixed(0)}%',
                style: TextStyle(
                    fontSize: 11,
                    color: color.withOpacity(0.8),
                    fontWeight: FontWeight.w600),
              ),
          ],
        ),
        if (confidence != null) ...[
          const SizedBox(height: 5),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: TweenAnimationBuilder<double>(
              tween: Tween(begin: 0, end: confidence!.clamp(0.0, 1.0)),
              duration: const Duration(milliseconds: 700),
              curve: Curves.easeOutCubic,
              builder: (_, val, __) => LinearProgressIndicator(
                value: val,
                minHeight: 5,
                backgroundColor: Colors.white.withOpacity(0.07),
                valueColor: AlwaysStoppedAnimation<Color>(color),
              ),
            ),
          ),
        ],
      ],
    );
  }
}

// ── Info Row ───────────────────────────────────────────────────────────────

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 15, color: const Color(0xFF6C63FF)),
        const SizedBox(width: 8),
        Text('$label: ',
            style: const TextStyle(
                fontSize: 12,
                color: Color(0xFF9D97FF),
                fontWeight: FontWeight.w600)),
        Expanded(
          child: Text(value,
              style: const TextStyle(
                  fontSize: 12, color: Color(0xFFCCCCEE))),
        ),
      ],
    );
  }
}

// ── Helper Widgets ─────────────────────────────────────────────────────────

class _ModeChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _ModeChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            color: selected ? const Color(0xFF6C63FF) : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                color: selected ? Colors.white : const Color(0xFF8888AA),
                fontSize: 12,
                fontWeight: selected ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback? onTap;
  final bool fullWidth;
  final bool loading;

  const _ActionButton({
    required this.label,
    required this.icon,
    this.onTap,
    this.fullWidth = false,
    this.loading = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: loading ? null : onTap,
      child: Container(
        width: fullWidth ? double.infinity : null,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: const Color(0xFF6C63FF).withOpacity(0.15),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
              color: const Color(0xFF6C63FF).withOpacity(0.3)),
        ),
        child: Row(
          mainAxisSize: fullWidth ? MainAxisSize.max : MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (loading)
              const SizedBox(
                width: 14, height: 14,
                child: CircularProgressIndicator(
                    strokeWidth: 2, color: Color(0xFF6C63FF)),
              )
            else
              Icon(icon, size: 16, color: const Color(0xFF9D97FF)),
            const SizedBox(width: 6),
            Text(label,
                style: const TextStyle(
                    color: Color(0xFF9D97FF),
                    fontSize: 13,
                    fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

class _BigActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool primary;

  const _BigActionButton({
    required this.icon,
    required this.label,
    required this.onTap,
    this.primary = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          gradient: primary
              ? const LinearGradient(
                  colors: [Color(0xFF6C63FF), Color(0xFF9D97FF)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                )
              : null,
          color: primary ? null : const Color(0xFF1A1A2E),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
              color: primary
                  ? Colors.transparent
                  : Colors.white.withOpacity(0.1)),
        ),
        child: Column(
          children: [
            Icon(icon,
                color: primary ? Colors.white : const Color(0xFF9D97FF),
                size: primary ? 32 : 28),
            const SizedBox(height: 6),
            Text(label,
                style: TextStyle(
                    color: primary ? Colors.white : const Color(0xFF9D97FF),
                    fontSize: 13,
                    fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

