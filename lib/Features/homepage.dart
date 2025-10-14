import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:mindxscope/Features/camera.dart';
import 'dart:io';
import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

enum ServerMode { auto, emulator, lan }

class HomePage extends StatefulWidget {
  final String? capturedImagePath;
  const HomePage({super.key, this.capturedImagePath});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String? _currentImagePath;
  bool _serverReachable = false;
  String _serverMessage = 'Checking server...';
  bool _isAnalyzing = false;
  String? _analysisError;
  Map<String, dynamic>? _analysisResult;
  // Enhancement UI state
  String _selectedFilter = 'clahe';
  double _filterStrength = 1.2; // used for gamma
  // debug info
  String? _lastRawResponse;
  DateTime? _lastAnalyzedAt;
  int? _lastFacesCount;
  final ImagePicker _picker = ImagePicker();
  // When running the Android emulator (Google AVD) use 10.0.2.2 to reach
  // the host machine. If you're running on a physical device use the
  // host's LAN IP (example: http://10.15.1.190:5000).
  static const String SERVER_URL = 'http://10.15.41.155:5000';
  //Home
  static const String Home_server = "http://192.168.68.100:5000";
  // server selection mode
  ServerMode _serverMode = ServerMode.auto;

  @override
  void initState() {
    super.initState();
    _currentImagePath = widget.capturedImagePath;
    _checkServer();
  }

  Future<void> _checkServer() async {
    // choose server list based on selection
    final servers = _serverMode == ServerMode.auto
        ? ['http://10.15.41.155:5000', 'http://192.168.68.100:5000']
        : _serverMode == ServerMode.emulator
            ? ['http://10.15.41.155:5000']
            : ['http://192.168.68.100:5000'];

    try {
      final r = await http.get(Uri.parse('${servers[0]}/'), headers: {'Accept': 'text/html'}).timeout(const Duration(seconds: 3));
      final wasReachable = _serverReachable;
      final nowReachable = r.statusCode == 200;
      setState(() {
        _serverReachable = nowReachable;
        _serverMessage = _serverReachable ? 'Model server reachable' : 'Server responded ${r.statusCode}';
      });
      // Show a SnackBar notification on change
      if (nowReachable != wasReachable) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(nowReachable ? 'Model server reachable' : 'Server unreachable'),
            backgroundColor: nowReachable ? Colors.green : Colors.red,
            duration: const Duration(seconds: 2),
          ),
        );
      }
    } catch (e) {
      final wasReachable = _serverReachable;
      final errText = e.toString();
      setState(() {
        _serverReachable = false;
        _serverMessage = 'Server unreachable: ${errText.length > 60 ? '${errText.substring(0, 60)}...' : errText}';
      });
      if (wasReachable) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Server unreachable: ${errText.length > 120 ? '${errText.substring(0, 120)}...' : errText}'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    }
  }

  void _navigateToCamera() async {
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
  final servers = _serverMode == ServerMode.auto
    ? ['http://10.15.41.155:5000', 'http://192.168.68.100:5000']
    : _serverMode == ServerMode.emulator
      ? ['http://10.15.41.155:5000']
      : ['http://192.168.68.100:5000'];
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
            _serverMessage = 'Model server reachable (${base.replaceFirst('http://', '')})';
            _lastRawResponse = res.body;
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
      _serverMessage = 'Server unreachable';
    });
  }

  // POST image file to /api/enhance and return the response body
  Future<Map<String, dynamic>?> _enhanceImage(String imagePath) async {
    final servers = _serverMode == ServerMode.auto
        ? ['http://10.0.2.2:5000', 'http://192.168.68.104:5000']
        : _serverMode == ServerMode.emulator
            ? ['http://10.0.2.2:5000']
            : ['http://192.168.68.104:5000'];

    for (final base in servers) {
      try {
        final uri = Uri.parse('$base/api/enhance');
        final request = http.MultipartRequest('POST', uri);
        request.fields['filter'] = _selectedFilter;
        if (_selectedFilter == 'gamma') request.fields['strength'] = _filterStrength.toString();
        request.files.add(await http.MultipartFile.fromPath('image', imagePath));
        final streamed = await request.send().timeout(const Duration(seconds: 20));
        final res = await http.Response.fromStream(streamed);
        if (res.statusCode == 200) {
          return json.decode(res.body) as Map<String, dynamic>;
        }
      } catch (e) {
        // try next server
      }
    }
    return null;
  }

  // Call /api/detect_file with filename in results and update analysis UI
  Future<bool> _detectFile(String filename) async {
    final servers = _serverMode == ServerMode.auto
        ? ['http://10.0.2.2:5000', 'http://192.168.68.104:5000']
        : _serverMode == ServerMode.emulator
            ? ['http://10.0.2.2:5000']
            : ['http://192.168.68.104:5000'];

    for (final base in servers) {
      try {
        final uri = Uri.parse('$base/api/detect_file');
        final r = await http.post(uri, headers: {'Content-Type': 'application/json'}, body: json.encode({'filename': filename})).timeout(const Duration(seconds: 10));
        if (r.statusCode == 200) {
          final Map<String, dynamic> body = json.decode(r.body);
          setState(() {
            _analysisResult = body;
            _isAnalyzing = false;
            _lastRawResponse = r.body;
            _lastAnalyzedAt = DateTime.now();
            _lastFacesCount = (body['faces'] is List) ? (body['faces'] as List).length : null;
          });
          return true;
        }
      } catch (e) {
        // try next
      }
    }
    return false;
  }

  Widget _buildAnalysisRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, size: 20, color: const Color(0xFF39393B)),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF39393B),
                ),
              ),
              Text(
                value,
                style: const TextStyle(fontSize: 12, color: Color(0xFF666666)),
              ),
            ],
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final mq = MediaQuery.of(context);
    final screenWidth = mq.size.width;
    final screenHeight = mq.size.height;

    // responsive sizes
    final imageWidth = screenWidth * 0.9; // use most of width
    final imageHeight = screenHeight * 0.28; // avoid taking too much vertical space
  final cardHeight = screenHeight * 0.43;

  // per-face details will be shown in the list below
    final String objectText = _analysisResult?['object']?.toString() ?? 'Human Face';

    // Per-face list will present the details; objectText already set above

    return Scaffold(
      backgroundColor: const Color(0xFF1e1e2e),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.fromLTRB(16.0, 16.0, 16.0, mq.viewPadding.bottom + 24.0),
          child: Column(
            children: [
              const SizedBox(height: 20),
              // Server status banner
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _serverReachable ? Colors.green[700] : Colors.red[700],
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      // Make the left side flexible so long server messages don't overflow
                      Expanded(
                        child: Row(
                          children: [
                            Icon(_serverReachable ? Icons.check_circle : Icons.error, color: Colors.white),
                            const SizedBox(width: 8),
                            // Allow the message to ellipsize if it's too long for the available space
                            Expanded(
                              child: Text(
                                _serverMessage,
                                style: const TextStyle(color: Colors.white),
                                overflow: TextOverflow.ellipsis,
                                maxLines: 1,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Row(
                        children: [
                          // Server mode selector
                          ToggleButtons(
                            isSelected: [
                              _serverMode == ServerMode.auto,
                              _serverMode == ServerMode.emulator,
                              _serverMode == ServerMode.lan
                            ],
                            onPressed: (i) {
                              setState(() {
                                _serverMode = i == 0 ? ServerMode.auto : i == 1 ? ServerMode.emulator : ServerMode.lan;
                              });
                              _checkServer();
                            },
                            color: Colors.white,
                            selectedColor: Colors.black,
                            fillColor: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                            children: const [
                              Padding(padding: EdgeInsets.symmetric(horizontal: 8), child: Text('Auto')),
                              Padding(padding: EdgeInsets.symmetric(horizontal: 8), child: Text('Emulator')),
                              Padding(padding: EdgeInsets.symmetric(horizontal: 8), child: Text('LAN')),
                            ],
                          ),
                          const SizedBox(width: 8),
                          TextButton(
                            onPressed: _checkServer,
                            child: const Text('Retry', style: TextStyle(color: Colors.white)),
                          ),
                        ],
                      )
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              // Debug: last analysis info
              if (_lastAnalyzedAt != null)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Last analyzed: ${_lastAnalyzedAt!.toLocal().toIso8601String()} • Faces: ${_lastFacesCount ?? 0}',
                      style: const TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ),
                ),
              // Profile Avatar or Captured Image
              Center(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(40),
                  child: Container(
                    width: imageWidth.clamp(260.0, 400.0).toDouble(),
                    height: imageHeight.clamp(180.0, 320.0).toDouble(),
                    color: const Color(0xFFBDBDBD),
                    child: _currentImagePath != null
                        ? Image.file(
                            File(_currentImagePath!),
                            fit: BoxFit.cover,
                            width: double.infinity,
                            height: double.infinity,
                            filterQuality: FilterQuality.high,
                            gaplessPlayback: true,
                            errorBuilder: (context, error, stackTrace) {
                              return const Center(
                                child: Icon(
                                  Icons.broken_image,
                                  size: 100,
                                  color: Color(0xFF39393B),
                                ),
                              );
                            },
                          )
                        : const Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.camera_alt,
                                  size: 60,
                                  color: Color(0xFF39393B),
                                ),
                                SizedBox(height: 8),
                                Text(
                                  'No Image',
                                  style: TextStyle(
                                    color: Color(0xFF39393B),
                                    fontSize: 16,
                                  ),
                                ),
                              ],
                            ),
                          ),
                  ),
                ),
              ),
              // Face Analysis Details Card (scrollable to avoid overflow)
              Center(
                child: Container(
                  width: screenWidth * 0.9,
                  constraints: BoxConstraints(maxHeight: cardHeight.clamp(280.0, 440.0).toDouble()),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE0E0E0),
                    borderRadius: BorderRadius.circular(40),
                  ),
                  child: _currentImagePath != null
                      ? Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
                          child: SingleChildScrollView(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Center(
                                  child: Text(
                                    'Face Analysis',
                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF39393B),
                                    ),
                                  ),
                                ),
                                const SizedBox(height: 12),
                                if (_isAnalyzing)
                                  const Center(
                                    child: Column(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        CircularProgressIndicator(),
                                        SizedBox(height: 12),
                                        Text('Analyzing...', style: TextStyle(color: Color(0xFF39393B))),
                                      ],
                                    ),
                                  )
                                else if (_analysisError != null)
                                  Center(
                                    child: Text(
                                      _analysisError!,
                                      style: const TextStyle(color: Colors.red),
                                    ),
                                  )
                                else ...[
                                  Text('Object: $objectText', style: const TextStyle(fontSize: 12, color: Color(0xFF666666))),
                                  const SizedBox(height: 8),
                                  if (_analysisResult != null && _analysisResult!['annotated_url'] is String)
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.stretch,
                                      children: [
                                        Center(
                                          child: Padding(
                                            padding: const EdgeInsets.symmetric(vertical: 8.0),
                                            child: Image.network(
                                              _analysisResult!['annotated_url'],
                                              width: imageWidth.clamp(260.0, 400.0).toDouble(),
                                              height: imageHeight.clamp(120.0, 220.0).toDouble(),
                                              fit: BoxFit.cover,
                                              errorBuilder: (context, error, stackTrace) => const Icon(Icons.broken_image),
                                            ),
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                        // Enhancement controls
                                        Padding(
                                          padding: const EdgeInsets.symmetric(horizontal: 6.0),
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.stretch,
                                            children: [
                                              Text('Enhance image', style: Theme.of(context).textTheme.titleMedium),
                                              const SizedBox(height: 6),
                                              Row(
                                                children: [
                                                  Expanded(
                                                    child: DropdownButton<String>(
                                                      value: _selectedFilter,
                                                      items: <String>['clahe', 'sharpen', 'denoise', 'contrast', 'unsharp', 'gamma']
                                                          .map((f) => DropdownMenuItem(value: f, child: Text(f)))
                                                          .toList(),
                                                      onChanged: (v) {
                                                        if (v != null) setState(() => _selectedFilter = v);
                                                      },
                                                    ),
                                                  ),
                                                  const SizedBox(width: 8),
                                                  ElevatedButton(
                                                    onPressed: () async {
                                                      final annotatedUrl = _analysisResult!['annotated_url'] as String;
                                                      final uri = Uri.parse(annotatedUrl);
                                                      final fname = uri.pathSegments.isNotEmpty ? uri.pathSegments.last : null;
                                                      if (fname == null) return;
                                                      setState(() => _isAnalyzing = true);
                                                      try {
                                                        final resp = await http.get(Uri.parse(annotatedUrl)).timeout(const Duration(seconds: 10));
                                                        if (resp.statusCode == 200) {
                                                          final bytes = resp.bodyBytes;
                                                            final tmpDir = Directory.systemTemp;
                                                            final tmpFile = File('${tmpDir.path}/$fname');
                                                          await tmpFile.writeAsBytes(bytes);
                                                          final enhanced = await _enhanceImage(tmpFile.path);
                                                          if (enhanced != null && enhanced['enhanced_url'] != null) {
                                                            var url = enhanced['enhanced_url'] as String;
                                                            if (url.contains('127.0.0.1') || url.contains('localhost')) {
                                                              url = url.replaceAll('127.0.0.1', '10.0.2.2').replaceAll('localhost', '10.0.2.2');
                                                            }
                                                            setState(() {
                                                              _analysisResult!['annotated_url'] = url;
                                                            });
                                                            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enhanced image ready')));
                                                          } else {
                                                            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enhance failed')));
                                                          }
                                                        }
                                                      } catch (e) {
                                                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Enhance error: $e')));
                                                      } finally {
                                                        setState(() => _isAnalyzing = false);
                                                      }
                                                    },
                                                    child: const Text('Enhance'),
                                                  ),
                                                ],
                                              ),
                                              if (_selectedFilter == 'gamma')
                                                Column(
                                                  children: [
                                                    const SizedBox(height: 8),
                                                    Text('Strength: ${_filterStrength.toStringAsFixed(2)}'),
                                                    Slider(
                                                      min: 0.1,
                                                      max: 3.0,
                                                      value: _filterStrength,
                                                      onChanged: (v) => setState(() => _filterStrength = v),
                                                    ),
                                                  ],
                                                ),
                                              const SizedBox(height: 8),
                                              Row(
                                                children: [
                                                  ElevatedButton(
                                                    onPressed: _isAnalyzing
                                                        ? null
                                                        : () async {
                                                            final url = _analysisResult!['annotated_url'] as String;
                                                            final uri = Uri.parse(url);
                                                            final fname = uri.pathSegments.isNotEmpty ? uri.pathSegments.last : null;
                                                            if (fname == null) return;
                                                            setState(() => _isAnalyzing = true);
                                                            final ok = await _detectFile(fname);
                                                            if (!ok) {
                                                              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Analyze enhanced failed')));
                                                            }
                                                          },
                                                    child: const Text('Analyze Enhanced'),
                                                  ),
                                                  const SizedBox(width: 8),
                                                  if (_isAnalyzing) const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
                                                ],
                                              ),
                                            ],
                                          ),
                                        ),
                                        const SizedBox(height: 8),
                                      ],
                                    ),
                                  if (_analysisResult != null && _analysisResult!['faces'] is List)
                                    SizedBox(
                                      height: 120,
                                      child: ListView.builder(
                                        itemCount: (_analysisResult!['faces'] as List).length,
                                        itemBuilder: (context, idx) {
                                          final f = (_analysisResult!['faces'] as List)[idx] as Map<String, dynamic>;
                                          final fid = f['face_id'] ?? idx + 1;
                                          final fag = f['age']?.toString() ?? 'N/A';
                                          final fgen = f['gender']?.toString() ?? 'N/A';
                                          final femo = f['emotion']?.toString() ?? 'N/A';
                                          return ListTile(
                                            onTap: () {
                                              showDialog(
                                                  context: context,
                                                  builder: (_) => Dialog(
                                                        child: Column(
                                                          mainAxisSize: MainAxisSize.min,
                                                          children: [
                                                            if (_currentImagePath != null) Image.file(File(_currentImagePath!)),
                                                            Padding(
                                                              padding: const EdgeInsets.all(8.0),
                                                              child: Text('Face $fid — Age: $fag, Gender: $fgen, Emotion: $femo'),
                                                            )
                                                          ],
                                                        ),
                                                      ));
                                            },
                                            leading: const Icon(Icons.face),
                                            title: Text('Face $fid'),
                                            subtitle: Text('Age: $fag • Gender: $fgen • Emotion: $femo'),
                                            trailing: TextButton(
                                              child: const Text('Edit'),
                                              onPressed: () async {
                                                // show emotion picker
                                                final emotions = ['neutral', 'happy', 'sad', 'angry', 'surprised', 'fear', 'disgust'];
                                                String? picked = await showDialog<String?>(
                                                  context: context,
                                                  builder: (_) {
                                                    String sel = femo;
                                                    return AlertDialog(
                                                      title: const Text('Override emotion'),
                                                      content: StatefulBuilder(builder: (c, setS) {
                                                        return Column(
                                                          mainAxisSize: MainAxisSize.min,
                                                          children: emotions.map((e) {
                                                            return RadioListTile<String>(
                                                              title: Text(e),
                                                              value: e,
                                                              groupValue: sel,
                                                              onChanged: (v) => setS(() => sel = v ?? sel),
                                                            );
                                                          }).toList(),
                                                        );
                                                      }),
                                                      actions: [
                                                        TextButton(onPressed: () => Navigator.of(context).pop(null), child: const Text('Cancel')),
                                                        TextButton(onPressed: () => Navigator.of(context).pop(sel), child: const Text('Save')),
                                                      ],
                                                    );
                                                  },
                                                );

                                                if (picked != null && picked != femo) {
                                                  // send override to server
                                                  final servers = _serverMode == ServerMode.auto
                                                      ? ['http://10.0.2.2:5000', 'http://192.168.68.104:5000']
                                                      : _serverMode == ServerMode.emulator
                                                          ? ['http://10.0.2.2:5000']
                                                          : ['http://192.168.68.104:5000'];

                                                  bool done = false;
                                                  for (final base in servers) {
                                                    try {
                                                      final resp = await http
                                                          .post(Uri.parse('$base/api/override'),
                                                              headers: {'Content-Type': 'application/json'},
                                                              body: json.encode({'uid': _analysisResult?['uid'], 'face_id': fid, 'emotion': picked}))
                                                          .timeout(const Duration(seconds: 5));
                                                      if (resp.statusCode == 200) {
                                                        // update local model
                                                        setState(() {
                                                          if (_analysisResult != null && _analysisResult!['faces'] is List) {
                                                            final list = _analysisResult!['faces'] as List;
                                                            for (var item in list) {
                                                              if ((item['face_id'] ?? -1) == fid) {
                                                                item['emotion'] = picked;
                                                              }
                                                            }
                                                          }
                                                        });
                                                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Override saved')));
                                                        done = true;
                                                        break;
                                                      }
                                                    } catch (e) {
                                                      // try next
                                                    }
                                                  }

                                                  if (!done) {
                                                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Failed to save override')));
                                                  }
                                                }
                                              },
                                            ),
                                          );
                                        },
                                      ),
                                    ),
                                  const SizedBox(height: 8),
                                  const Center(
                                    child: Text(
                                      'Analysis Complete ✓',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Colors.green,
                                        fontWeight: FontWeight.w500,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                    children: [
                                      ElevatedButton(
                                        onPressed: () {
                                          if (_currentImagePath != null) _analyzeImage(_currentImagePath!);
                                        },
                                        child: const Text('Retry Analysis'),
                                      ),
                                      ElevatedButton(
                                        onPressed: () {
                                          final text = json.encode(_analysisResult ?? {});
                                          Clipboard.setData(ClipboardData(text: text));
                                          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Results copied to clipboard')));
                                        },
                                        child: const Text('Copy Results'),
                                      ),
                                    ],
                                  ),
                                ],
                              ],
                            ),
                          ),
                        )
                      : const Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.analytics_outlined,
                                size: 60,
                                color: Color(0xFF39393B),
                              ),
                              SizedBox(height: 8),
                              Text(
                                'Take a photo to analyze',
                                style: TextStyle(
                                  color: Color(0xFF39393B),
                                  fontSize: 16,
                                ),
                              ),
                              SizedBox(height: 4),
                              Text(
                                'Object • Face • Age • Emotions',
                                style: TextStyle(
                                  color: Color(0xFF666666),
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 20),

              // Camera Button
              Padding(
                padding: const EdgeInsets.only(bottom: 30.0, top: 8.0),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        IconButton(
                          icon: const Icon(
                            Icons.photo_library,
                            size: 36,
                            color: Colors.white,
                          ),
                          onPressed: _pickImageFromGallery,
                        ),
                        const SizedBox(width: 12),
                        IconButton(
                          icon: const Icon(
                            Icons.camera_alt_rounded,
                            size: 50,
                            color: Colors.white,
                          ),
                          onPressed: _navigateToCamera,
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    // Hint-style button at bottom
                    TextButton(
                      onPressed: _navigateToCamera,
                      style: TextButton.styleFrom(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                        backgroundColor: Colors.transparent,
                      ),
                      child: const Text(
                        'Tap to open camera',
                        style: TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              // Add bottom spacer to account for system navigation bars
              SizedBox(height: mq.viewPadding.bottom + 24.0),
            ],
          ),
        ),
      ),
    );
  }
}