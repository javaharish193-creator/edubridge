import 'package:flutter/material.dart';
import '../services/api_service.dart';

class QuizScreen extends StatefulWidget {
  final String chapterId;
  final String chapterTitle;

  const QuizScreen({
    super.key,
    required this.chapterId,
    required this.chapterTitle,
  });

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  bool _isLoading = true;
  String? _errorMessage;
  List<dynamic> _questions = [];
  int _currentIndex = 0;
  int? _selectedOption;
  bool _answered = false;
  int _score = 0;
  bool _quizCompleted = false;

  @override
  void initState() {
    super.initState();
    _loadQuiz();
  }

  Future<void> _loadQuiz() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _currentIndex = 0;
      _score = 0;
      _answered = false;
      _selectedOption = null;
      _quizCompleted = false;
    });

    try {
      final res = await ApiService.generateQuiz(chapterId: widget.chapterId, numQuestions: 5);
      setState(() {
        _questions = (res['questions'] as List?) ?? [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  void _checkAnswer() {
    if (_selectedOption == null) return;
    final currentQ = _questions[_currentIndex];
    final correctIdx = currentQ['correct_option_index'] ?? 0;

    setState(() {
      _answered = true;
      if (_selectedOption == correctIdx) {
        _score++;
      }
    });
  }

  void _nextQuestion() {
    if (_currentIndex + 1 < _questions.length) {
      setState(() {
        _currentIndex++;
        _selectedOption = null;
        _answered = false;
      });
    } else {
      setState(() {
        _quizCompleted = true;
      });
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
              'AI Chapter Quiz',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF1A1A1A)),
            ),
          ],
        ),
      ),
      body: _isLoading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Color(0xFF024AD8)),
                  SizedBox(height: 16),
                  Text('Generating syllabus quiz with AI...', style: TextStyle(color: Color(0xFF636363), fontSize: 13)),
                ],
              ),
            )
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
                          onPressed: _loadQuiz,
                          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF024AD8)),
                          child: const Text('RETRY', style: TextStyle(color: Colors.white)),
                        )
                      ],
                    ),
                  ),
                )
              : _quizCompleted
                  ? _buildCompletionCard()
                  : _buildQuestionCard(),
    );
  }

  Widget _buildQuestionCard() {
    if (_questions.isEmpty) {
      return const Center(child: Text('No quiz questions available.'));
    }

    final q = _questions[_currentIndex];
    final options = (q['options'] as List?) ?? [];
    final correctIdx = q['correct_option_index'] ?? 0;
    final explanation = q['explanation'] ?? '';

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header info
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'QUESTION ${_currentIndex + 1} OF ${_questions.length}',
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF024AD8)),
              ),
              Text(
                'SCORE: $_score',
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF15803D)),
              ),
            ],
          ),
          const SizedBox(height: 8),

          // Progress indicator
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: (_currentIndex + 1) / _questions.length,
              backgroundColor: const Color(0xFFE8E8E8),
              valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF024AD8)),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 20),

          // Question Text Card
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFFF7F7F7),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE8E8E8)),
            ),
            child: Text(
              q['question'] ?? '',
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Color(0xFF1A1A1A), height: 1.4),
            ),
          ),
          const SizedBox(height: 18),

          // Options
          ...List.generate(options.length, (idx) {
            final optText = options[idx];
            Color borderColor = const Color(0xFFE8E8E8);
            Color bgColor = Colors.white;

            if (_answered) {
              if (idx == correctIdx) {
                borderColor = const Color(0xFF15803D);
                bgColor = const Color(0xFFDCFCE7);
              } else if (idx == _selectedOption) {
                borderColor = const Color(0xFFB3262B);
                bgColor = const Color(0xFFFFF1F2);
              }
            } else if (_selectedOption == idx) {
              borderColor = const Color(0xFF024AD8);
              bgColor = const Color(0xFFEFF6FF);
            }

            return GestureDetector(
              onTap: _answered ? null : () => setState(() => _selectedOption = idx),
              child: Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: bgColor,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: borderColor, width: 1.5),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 24,
                      height: 24,
                      decoration: BoxDecoration(
                        color: _selectedOption == idx ? const Color(0xFF024AD8) : const Color(0xFFF7F7F7),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Center(
                        child: Text(
                          String.fromCharCode(65 + idx),
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: _selectedOption == idx ? Colors.white : const Color(0xFF636363),
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        optText,
                        style: const TextStyle(fontSize: 13, color: Color(0xFF1A1A1A)),
                      ),
                    ),
                  ],
                ),
              ),
            );
          }),
          const SizedBox(height: 16),

          // Check or Next Button
          if (!_answered)
            ElevatedButton(
              onPressed: _selectedOption == null ? null : _checkAnswer,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF024AD8),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: const Text('CHECK ANSWER', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8)),
            )
          else ...[
            if (explanation.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: const Color(0xFFF7F7F7),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFE8E8E8)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.info_outline, size: 16, color: Color(0xFF024AD8)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        explanation,
                        style: const TextStyle(fontSize: 12, color: Color(0xFF3D3D3D)),
                      ),
                    ),
                  ],
                ),
              ),
            ElevatedButton(
              onPressed: _nextQuestion,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF024AD8),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              child: Text(
                _currentIndex + 1 < _questions.length ? 'NEXT QUESTION' : 'VIEW FINAL SCORE',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildCompletionCard() {
    final pct = (_score / _questions.length * 100).round();
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE8E8E8)),
            boxShadow: const [
              BoxShadow(color: Color.fromRGBO(26, 26, 26, 0.08), blurRadius: 16, offset: Offset(0, 4)),
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: const Color(0xFFC9E0FC),
                  borderRadius: BorderRadius.circular(32),
                ),
                child: const Icon(Icons.emoji_events, color: Color(0xFF024AD8), size: 36),
              ),
              const SizedBox(height: 16),
              const Text(
                'Quiz Completed!',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1A1A1A)),
              ),
              const SizedBox(height: 6),
              Text(
                widget.chapterTitle,
                textAlign: TextAlign.center,
                style: const TextStyle(fontSize: 12, color: Color(0xFF636363)),
              ),
              const SizedBox(height: 20),
              Text(
                '$_score / ${_questions.length}',
                style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF024AD8)),
              ),
              Text(
                '$pct% Accuracy',
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF15803D)),
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _loadQuiz,
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFF024AD8)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text('RETAKE QUIZ', style: TextStyle(color: Color(0xFF024AD8), fontWeight: FontWeight.bold, fontSize: 11)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => Navigator.pop(context),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF024AD8),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text('DONE', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
