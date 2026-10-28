import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import 'quiz_screen.dart';

class SubjectDetailScreen extends StatefulWidget {
  final String subjectId;
  final String subjectName;
  final String subjectCode;

  const SubjectDetailScreen({
    super.key,
    required this.subjectId,
    required this.subjectName,
    required this.subjectCode,
  });

  @override
  State<SubjectDetailScreen> createState() => _SubjectDetailScreenState();
}

class _SubjectDetailScreenState extends State<SubjectDetailScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<dynamic> _chapters = [];

  @override
  void initState() {
    super.initState();
    _fetchSubjectContent();
  }

  Future<void> _fetchSubjectContent() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final res = await ApiService.getSubjectMaterials(widget.subjectId);
      setState(() {
        _chapters = res['chapters'] as List? ?? [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  Future<void> _openMaterial(String? url) async {
    if (url == null || url.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Download URL unavailable')),
      );
      return;
    }

    // Convert host machine localhost URL to Android emulator host 10.0.2.2 if needed
    final cleanUrl = url.replaceAll('127.0.0.1', '10.0.2.2').replaceAll('localhost', '10.0.2.2');
    final uri = Uri.parse(cleanUrl);

    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        await launchUrl(uri);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Opening material: $cleanUrl')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Row(
          children: [
            Transform(
              transform: Matrix4.skewX(-0.4),
              child: Container(width: 8, height: 20, color: const Color(0xFF024AD8)),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                widget.subjectName,
                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF1A1A1A)),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF024AD8)))
          : _errorMessage != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, color: Color(0xFFB3262B), size: 40),
                        const SizedBox(height: 12),
                        Text(_errorMessage!, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF1A1A1A))),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _fetchSubjectContent,
                          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF024AD8)),
                          child: const Text('RETRY', style: TextStyle(color: Colors.white)),
                        )
                      ],
                    ),
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Header Card
                      Container(
                        padding: const EdgeInsets.all(18),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF7F7F7),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: const Color(0xFFE8E8E8)),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 44,
                              height: 44,
                              decoration: BoxDecoration(
                                color: const Color(0xFFC9E0FC),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: const Icon(Icons.menu_book, color: Color(0xFF024AD8), size: 24),
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    widget.subjectName,
                                    style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF1A1A1A)),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    'Code: ${widget.subjectCode} • ${_chapters.length} Chapters In Syllabus',
                                    style: const TextStyle(fontSize: 12, color: Color(0xFF636363)),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 24),

                      const Text(
                        'CHAPTERS & STUDY MATERIALS',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363)),
                      ),
                      const SizedBox(height: 12),

                      if (_chapters.isEmpty)
                        Container(
                          padding: const EdgeInsets.all(32),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF7F7F7),
                            borderRadius: BorderRadius.circular(16),
                          ),
                          child: const Center(
                            child: Text('No chapters uploaded for this subject yet.', style: TextStyle(color: Color(0xFF636363), fontSize: 13)),
                          ),
                        )
                      else
                        ..._chapters.map((ch) {
                          final materials = (ch['materials'] as List?) ?? [];
                          return Container(
                            margin: const EdgeInsets.only(bottom: 16),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(color: const Color(0xFFE8E8E8)),
                              boxShadow: const [
                                BoxShadow(
                                  color: Color.fromRGBO(26, 26, 26, 0.04),
                                  blurRadius: 8,
                                  offset: Offset(0, 2),
                                ),
                              ],
                            ),
                            child: ExpansionTile(
                              initiallyExpanded: true,
                              shape: const Border(),
                              title: Text(
                                ch['title'] ?? 'Chapter',
                                style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: Color(0xFF1A1A1A)),
                              ),
                              subtitle: Text(
                                '${materials.length} learning resources',
                                style: const TextStyle(fontSize: 11, color: Color(0xFF636363)),
                              ),
                              children: [
                                const Divider(height: 1, color: Color(0xFFE8E8E8)),
                                ...materials.map((m) {
                                  final isPdf = m['material_type'] == 'PDF_NOTES';
                                  return ListTile(
                                    leading: Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: isPdf ? const Color(0xFFFFF1F2) : const Color(0xFFEFF6FF),
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: Icon(
                                        isPdf ? Icons.picture_as_pdf : Icons.play_circle_outline,
                                        color: isPdf ? const Color(0xFFB3262B) : const Color(0xFF024AD8),
                                        size: 20,
                                      ),
                                    ),
                                    title: Text(
                                      m['title'] ?? 'Material',
                                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: Color(0xFF1A1A1A)),
                                    ),
                                    subtitle: Text(
                                      isPdf ? 'PDF Revision Notes' : 'Video Lecture',
                                      style: const TextStyle(fontSize: 10, color: Color(0xFF636363)),
                                    ),
                                    trailing: OutlinedButton.icon(
                                      onPressed: () => _openMaterial(m['download_url']),
                                      style: OutlinedButton.styleFrom(
                                        side: const BorderSide(color: Color(0xFF024AD8)),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                      ),
                                      icon: const Icon(Icons.download, size: 14, color: Color(0xFF024AD8)),
                                      label: const Text('OPEN', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF024AD8))),
                                    ),
                                  );
                                }),
                                Padding(
                                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                  child: SizedBox(
                                    width: double.infinity,
                                    child: ElevatedButton.icon(
                                      onPressed: () {
                                        Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder: (_) => QuizScreen(
                                              chapterId: ch['id'],
                                              chapterTitle: ch['title'],
                                            ),
                                          ),
                                        );
                                      },
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: const Color(0xFF024AD8),
                                        foregroundColor: Colors.white,
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                                        padding: const EdgeInsets.symmetric(vertical: 10),
                                      ),
                                      icon: const Icon(Icons.quiz_outlined, size: 16),
                                      label: const Text('TAKE AI CHAPTER QUIZ', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.7)),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          );
                        }),
                    ],
                  ),
                ),
    );
  }
}
