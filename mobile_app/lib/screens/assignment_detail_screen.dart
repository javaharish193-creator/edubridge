import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import 'homework_hint_screen.dart';

class AssignmentDetailScreen extends StatefulWidget {
  final String assignmentId;
  final String title;
  final String subjectName;

  const AssignmentDetailScreen({
    super.key,
    required this.assignmentId,
    required this.title,
    required this.subjectName,
  });

  @override
  State<AssignmentDetailScreen> createState() => _AssignmentDetailScreenState();
}

class _AssignmentDetailScreenState extends State<AssignmentDetailScreen> {
  bool _isLoading = true;
  bool _isSubmitting = false;
  String? _errorMessage;
  Map<String, dynamic>? _assignment;
  final _notesController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchDetail();
  }

  Future<void> _fetchDetail() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final res = await ApiService.getAssignmentDetail(widget.assignmentId);
      setState(() {
        _assignment = res;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  Future<void> _handleSubmit() async {
    final notes = _notesController.text.trim();
    setState(() => _isSubmitting = true);

    try {
      await ApiService.submitAssignment(
        widget.assignmentId,
        notes: notes.isNotEmpty ? notes : 'Assignment solutions submitted via EduBridge mobile portal.',
        sampleFileName: 'student_work.pdf',
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Homework submitted successfully! Marked for teacher review.'),
            backgroundColor: Color(0xFF024AD8),
          ),
        );
      }
      await _fetchDetail();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceAll('Exception: ', '')),
            backgroundColor: const Color(0xFFB3262B),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  Future<void> _downloadAttachment(String? url) async {
    if (url == null || url.isEmpty) return;
    final cleanUrl = url.replaceAll('127.0.0.1', '10.0.2.2').replaceAll('localhost', '10.0.2.2');
    final uri = Uri.parse(cleanUrl);
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        await launchUrl(uri);
      }
    } catch (_) {}
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
            const Text(
              'Assignment Details',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF1A1A1A)),
            ),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF024AD8)))
          : _errorMessage != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, color: Color(0xFFB3262B), size: 40),
                        const SizedBox(height: 12),
                        Text(_errorMessage!, textAlign: TextAlign.center),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _fetchDetail,
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
                      // Status and Subject Badge
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFC9E0FC),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              widget.subjectName.toUpperCase(),
                              style: const TextStyle(color: Color(0xFF0E3191), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 0.8),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                            decoration: BoxDecoration(
                              color: _assignment?['status'] == 'GRADED'
                                  ? const Color(0xFFDCFCE7)
                                  : _assignment?['status'] == 'SUBMITTED'
                                      ? const Color(0xFFEFF6FF)
                                      : const Color(0xFFFFFBEB),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              _assignment?['status'] ?? 'PENDING',
                              style: TextStyle(
                                color: _assignment?['status'] == 'GRADED'
                                    ? const Color(0xFF15803D)
                                    : _assignment?['status'] == 'SUBMITTED'
                                        ? const Color(0xFF1D4ED8)
                                        : const Color(0xFFB45309),
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),

                      // Title
                      Text(
                        _assignment?['title'] ?? widget.title,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF1A1A1A),
                          letterSpacing: -0.3,
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Meta details row
                      Container(
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF7F7F7),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFFE8E8E8)),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            Column(
                              children: [
                                const Text('MAX MARKS', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF636363))),
                                const SizedBox(height: 4),
                                Text('${_assignment?['max_marks'] ?? 100}', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF024AD8))),
                              ],
                            ),
                            Container(width: 1, height: 28, color: const Color(0xFFE8E8E8)),
                            Column(
                              children: [
                                const Text('DUE DATE', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF636363))),
                                const SizedBox(height: 4),
                                Text(
                                  (_assignment?['due_date'] ?? '').toString().split('T').first,
                                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Color(0xFF1A1A1A)),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 20),

                      // Instructions
                      const Text(
                        'INSTRUCTIONS',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363)),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFFE8E8E8)),
                        ),
                        child: Text(
                          _assignment?['instructions'] ?? 'Follow the textbook guidelines and write your answers clearly.',
                          style: const TextStyle(fontSize: 13, height: 1.45, color: Color(0xFF3D3D3D)),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Question paper attachment button
                      if (_assignment?['attachment_url'] != null) ...[
                        OutlinedButton.icon(
                          onPressed: () => _downloadAttachment(_assignment!['attachment_url']),
                          style: OutlinedButton.styleFrom(
                            side: const BorderSide(color: Color(0xFF024AD8)),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                          ),
                          icon: const Icon(Icons.download, size: 16, color: Color(0xFF024AD8)),
                          label: const Text('DOWNLOAD QUESTION PAPER / WORKSHEET', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF024AD8))),
                        ),
                        const SizedBox(height: 16),
                      ],

                      // Socratic Homework Tutor AI Button
                      ElevatedButton.icon(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => HomeworkHintScreen(
                                assignmentId: widget.assignmentId,
                                assignmentTitle: widget.title,
                                defaultQuestion: _assignment?['instructions'] ?? widget.title,
                              ),
                            ),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1A1A1A),
                          foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                          padding: const EdgeInsets.symmetric(vertical: 13),
                        ),
                        icon: const Icon(Icons.psychology, size: 18, color: Color(0xFF296EF9)),
                        label: const Text('ASK SOCRATIC HOMEWORK TUTOR', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8)),
                      ),
                      const SizedBox(height: 28),

                      // Submission Area
                      const Text(
                        'YOUR SUBMISSION',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363)),
                      ),
                      const SizedBox(height: 8),

                      if (_assignment?['status'] == 'GRADED') ...[
                        Container(
                          padding: const EdgeInsets.all(18),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF0FDF4),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFF86EFAC)),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  const Text('GRADE AWARDED', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF15803D))),
                                  Text(
                                    '${_assignment?['marks_awarded'] ?? 0} / ${_assignment?['max_marks'] ?? 100}',
                                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF15803D)),
                                  ),
                                ],
                              ),
                              if (_assignment?['feedback_remarks'] != null) ...[
                                const SizedBox(height: 10),
                                const Text('TEACHER REMARKS:', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF166534))),
                                const SizedBox(height: 4),
                                Text(
                                  _assignment!['feedback_remarks'],
                                  style: const TextStyle(fontSize: 12, color: Color(0xFF166534)),
                                ),
                              ],
                              if (_assignment?['answer_key_url'] != null) ...[
                                const SizedBox(height: 14),
                                OutlinedButton.icon(
                                  onPressed: () => _downloadAttachment(_assignment!['answer_key_url']),
                                  style: OutlinedButton.styleFrom(
                                    side: const BorderSide(color: Color(0xFF15803D)),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                                  ),
                                  icon: const Icon(Icons.verified, size: 16, color: Color(0xFF15803D)),
                                  label: const Text('VIEW OFFICIAL ANSWER KEY', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF15803D))),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ] else ...[
                        TextField(
                          controller: _notesController,
                          maxLines: 4,
                          style: const TextStyle(fontSize: 13),
                          decoration: InputDecoration(
                            hintText: 'Enter student notes, explanation, or answers for this homework...',
                            hintStyle: const TextStyle(color: Color(0xFFC2C2C2), fontSize: 12),
                            filled: true,
                            fillColor: const Color(0xFFF7F7F7),
                            border: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                            enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                            focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFF024AD8), width: 1.5)),
                          ),
                        ),
                        const SizedBox(height: 14),
                        ElevatedButton.icon(
                          onPressed: _isSubmitting ? null : _handleSubmit,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF024AD8),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                            padding: const EdgeInsets.symmetric(vertical: 14),
                          ),
                          icon: _isSubmitting
                              ? const SizedBox.shrink()
                              : const Icon(Icons.cloud_upload_outlined, size: 18),
                          label: _isSubmitting
                              ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                              : Text(
                                  _assignment?['status'] == 'SUBMITTED' ? 'RESUBMIT HOMEWORK' : 'SUBMIT HOMEWORK',
                                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8),
                                ),
                        ),
                      ],
                    ],
                  ),
                ),
    );
  }
}
