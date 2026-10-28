import 'package:flutter/material.dart';
import '../services/api_service.dart';

class HomeworkHintScreen extends StatefulWidget {
  final String? assignmentId;
  final String? assignmentTitle;
  final String? defaultQuestion;

  const HomeworkHintScreen({
    super.key,
    this.assignmentId,
    this.assignmentTitle,
    this.defaultQuestion,
  });

  @override
  State<HomeworkHintScreen> createState() => _HomeworkHintScreenState();
}

class _HomeworkHintScreenState extends State<HomeworkHintScreen> {
  late final TextEditingController _questionController;
  final _attemptController = TextEditingController();
  bool _isLoading = false;
  Map<String, dynamic>? _hintResult;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _questionController = TextEditingController(text: widget.defaultQuestion ?? '');
  }

  Future<void> _fetchHint() async {
    final q = _questionController.text.trim();
    if (q.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your homework question or problem')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _hintResult = null;
      _errorMessage = null;
    });

    try {
      final res = await ApiService.getHomeworkHint(
        assignmentId: widget.assignmentId ?? 'general-homework',
        questionText: q,
        studentAttempt: _attemptController.text.trim().isNotEmpty ? _attemptController.text.trim() : null,
      );
      setState(() {
        _hintResult = res;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
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
            const Text(
              'Socratic Homework Tutor',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF1A1A1A)),
            ),
          ],
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Info banner
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFF7F7F7),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE8E8E8)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.psychology, color: Color(0xFF024AD8), size: 26),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'AI tutor does not give away the direct answer. It provides Socratic guiding questions to help you solve it yourself!',
                      style: TextStyle(fontSize: 11, color: Color(0xFF3D3D3D), height: 1.4),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            const Text(
              'HOMEWORK PROBLEM / QUESTION',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363)),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: _questionController,
              maxLines: 3,
              style: const TextStyle(fontSize: 13),
              decoration: InputDecoration(
                hintText: 'Paste or type the homework problem you are stuck on...',
                hintStyle: const TextStyle(color: Color(0xFFC2C2C2), fontSize: 12),
                filled: true,
                fillColor: const Color(0xFFF7F7F7),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFF024AD8), width: 1.5)),
              ),
            ),
            const SizedBox(height: 16),

            const Text(
              'WHAT HAVE YOU TRIED SO FAR? (OPTIONAL)',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363)),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: _attemptController,
              maxLines: 2,
              style: const TextStyle(fontSize: 13),
              decoration: InputDecoration(
                hintText: 'e.g. I used formula X, but got confused at step 2...',
                hintStyle: const TextStyle(color: Color(0xFFC2C2C2), fontSize: 12),
                filled: true,
                fillColor: const Color(0xFFF7F7F7),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFF024AD8), width: 1.5)),
              ),
            ),
            const SizedBox(height: 18),

            ElevatedButton.icon(
              onPressed: _isLoading ? null : _fetchHint,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF024AD8),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              icon: _isLoading ? const SizedBox.shrink() : const Icon(Icons.bolt, size: 16),
              label: _isLoading
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('GET SOCRATIC GUIDANCE', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8)),
            ),
            const SizedBox(height: 24),

            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF1F2),
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: const Color(0xFFB3262B)),
                ),
                child: Text(_errorMessage!, style: const TextStyle(color: Color(0xFFB3262B), fontSize: 12)),
              ),

            if (_hintResult != null) ...[
              // Result Card
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFFF7F7F7),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFE8E8E8)),
                  boxShadow: const [
                    BoxShadow(color: Color.fromRGBO(26, 26, 26, 0.05), blurRadius: 8, offset: Offset(0, 2)),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Section 1: Guiding Hint
                    Row(
                      children: [
                        Transform(
                          transform: Matrix4.skewX(-0.4),
                          child: Container(width: 6, height: 16, color: const Color(0xFF024AD8)),
                        ),
                        const SizedBox(width: 8),
                        const Text('GUIDING CLUE', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF024AD8))),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _hintResult!['guiding_hint'] ?? '',
                      style: const TextStyle(fontSize: 13, height: 1.45, color: Color(0xFF1A1A1A)),
                    ),
                    const SizedBox(height: 16),

                    // Section 2: Clarifying Concept
                    Row(
                      children: [
                        Transform(
                          transform: Matrix4.skewX(-0.4),
                          child: Container(width: 6, height: 16, color: const Color(0xFF296EF9)),
                        ),
                        const SizedBox(width: 8),
                        const Text('CONCEPT TO REVIEW', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF296EF9))),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      _hintResult!['clarifying_concept'] ?? '',
                      style: const TextStyle(fontSize: 13, height: 1.45, color: Color(0xFF3D3D3D)),
                    ),
                    const SizedBox(height: 16),

                    // Section 3: Socratic Question
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFEFF6FF),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFBFDBFE)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('THINK ABOUT THIS NEXT STEP:', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF1E40AF))),
                          const SizedBox(height: 4),
                          Text(
                            _hintResult!['socratic_question'] ?? '',
                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF1E3A8A)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
