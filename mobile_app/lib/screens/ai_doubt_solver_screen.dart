import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AIDoubtSolverScreen extends StatefulWidget {
  const AIDoubtSolverScreen({super.key});

  @override
  State<AIDoubtSolverScreen> createState() => _AIDoubtSolverScreenState();
}

class _AIDoubtSolverScreenState extends State<AIDoubtSolverScreen> {
  final _questionController = TextEditingController();
  bool _isLoading = false;
  Map<String, dynamic>? _doubtResult;
  String? _errorMessage;

  Future<void> _submitDoubt() async {
    final query = _questionController.text.trim();
    if (query.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a question or doubt')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
      _doubtResult = null;
      _errorMessage = null;
    });

    try {
      final res = await ApiService.askAIDoubt(query);
      setState(() {
        _doubtResult = res;
      });
    } catch (e) {
      final friendlyError = e.toString().replaceAll('Exception: ', '').trim();
      setState(() {
        _errorMessage = friendlyError;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(friendlyError),
            backgroundColor: const Color(0xFFB3262B),
          ),
        );
      }
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
              'AI Doubt Solver',
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
            const Text(
              'CONCEPT / QUESTION QUERY',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363)),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _questionController,
              maxLines: 3,
              style: const TextStyle(fontSize: 13, color: Color(0xFF1A1A1A)),
              decoration: InputDecoration(
                hintText: 'Enter any topic, problem, or doubt from your textbook...',
                hintStyle: const TextStyle(color: Color(0xFFC2C2C2), fontSize: 13),
                filled: true,
                fillColor: const Color(0xFFF7F7F7),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFF024AD8), width: 1.5)),
              ),
            ),
            const SizedBox(height: 14),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _submitDoubt,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF024AD8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              icon: _isLoading ? const SizedBox.shrink() : const Icon(Icons.bolt, size: 16),
              label: _isLoading
                  ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('SOLVE DOUBT WITH AI', style: TextStyle(letterSpacing: 0.8, fontSize: 12)),
            ),
            const SizedBox(height: 20),

            if (_errorMessage != null)
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF1F2),
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: const Color(0xFFB3262B)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, size: 18, color: Color(0xFFB3262B)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: const TextStyle(color: Color(0xFFB3262B), fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),

            if (_doubtResult != null) ...[
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
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: const Color(0xFFC9E0FC),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        _doubtResult!['grade_tier'] ?? 'PEDAGOGICAL TIER',
                        style: const TextStyle(color: Color(0xFF0E3191), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 0.8),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      _doubtResult!['answer'] ?? '',
                      style: const TextStyle(fontSize: 13, height: 1.5, color: Color(0xFF1A1A1A)),
                    ),
                    const SizedBox(height: 18),
                    const Text(
                      'STEP-BY-STEP EXPLANATION:',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, letterSpacing: 0.8, color: Color(0xFF024AD8)),
                    ),
                    const SizedBox(height: 8),
                    ...((_doubtResult!['step_by_step'] as List?) ?? []).map(
                      (step) => Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Transform(
                              transform: Matrix4.skewX(-0.4),
                              child: Container(width: 4, height: 14, color: const Color(0xFF024AD8), margin: const EdgeInsets.only(top: 2, right: 8)),
                            ),
                            Expanded(
                              child: Text(step, style: const TextStyle(fontSize: 12, color: Color(0xFF3D3D3D), height: 1.35)),
                            ),
                          ],
                        ),
                      ),
                    ),
                    if ((_doubtResult!['key_takeaways'] as List?)?.isNotEmpty == true) ...[
                      const SizedBox(height: 14),
                      const Text(
                        'KEY TAKEAWAYS:',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11, letterSpacing: 0.8, color: Color(0xFF15803D)),
                      ),
                      const SizedBox(height: 6),
                      ...((_doubtResult!['key_takeaways'] as List)).map(
                        (item) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('• ', style: TextStyle(color: Color(0xFF15803D), fontWeight: FontWeight.bold)),
                              Expanded(child: Text(item, style: const TextStyle(fontSize: 12, color: Color(0xFF166534)))),
                            ],
                          ),
                        ),
                      ),
                    ],
                    if (_doubtResult!['practice_question'] != null && _doubtResult!['practice_question'].toString().isNotEmpty) ...[
                      const SizedBox(height: 16),
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
                            const Text('TRY THIS PRACTICE QUESTION:', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF1E40AF))),
                            const SizedBox(height: 4),
                            Text(
                              _doubtResult!['practice_question'],
                              style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic, color: Color(0xFF1E3A8A)),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ]
          ],
        ),
      ),
    );
  }
}
