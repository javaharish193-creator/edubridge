import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import 'subject_detail_screen.dart';
import 'assignment_detail_screen.dart';
import 'ai_doubt_solver_screen.dart';
import 'homework_hint_screen.dart';
import 'login_screen.dart';

class StudentDashboardScreen extends StatefulWidget {
  const StudentDashboardScreen({super.key});

  @override
  State<StudentDashboardScreen> createState() => _StudentDashboardScreenState();
}

class _StudentDashboardScreenState extends State<StudentDashboardScreen> {
  int _currentTabIndex = 0;
  int _homeworkFilter = 0; // 0: Pending, 1: Completed/Graded
  Map<String, dynamic>? _dashboardData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchDashboard();
  }

  Future<void> _fetchDashboard() async {
    setState(() => _isLoading = true);
    try {
      final data = await ApiService.getStudentDashboard();
      setState(() {
        _dashboardData = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceAll('Exception: ', '')),
            backgroundColor: const Color(0xFFB3262B),
          ),
        );
      }
    }
  }

  Future<void> _joinLiveMeeting(Map<String, dynamic> liveClass) async {
    final liveId = liveClass['id'];
    try {
      final res = await ApiService.joinLiveClass(liveId);
      final room = res['room'] ?? 'edubridge-meeting';
      final jitsiUrl = 'https://meet.jit.si/$room';
      final uri = Uri.parse(jitsiUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        await launchUrl(uri);
      }
    } catch (e) {
      // Fallback direct room link
      final directUri = Uri.parse('https://meet.jit.si/edubridge-$liveId');
      try {
        await launchUrl(directUri, mode: LaunchMode.externalApplication);
      } catch (_) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Launching classroom: meet.jit.si/edubridge-$liveId')),
          );
        }
      }
    }
  }

  int get _gradeLevel => _dashboardData?['student']?['grade_level'] ?? 8;

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Colors.white,
        body: Center(child: CircularProgressIndicator(color: Color(0xFF024AD8))),
      );
    }

    final student = _dashboardData?['student'];
    final subjects = (_dashboardData?['subjects'] as List?) ?? [];
    final pendingAssignments = (_dashboardData?['pending_assignments'] as List?) ?? [];
    final submittedAssignments = (_dashboardData?['submitted_assignments'] as List?) ?? [];
    final liveClasses = (_dashboardData?['upcoming_live_classes'] as List?) ?? [];

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
            Text(
              'EduBridge • Class $_gradeLevel-${student?['section']}',
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF1A1A1A)),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_circle_outlined, color: Color(0xFF024AD8)),
            tooltip: 'Student Profile',
            onPressed: () => _showProfileDialog(student),
          ),
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF636363)),
            tooltip: 'Refresh',
            onPressed: _fetchDashboard,
          ),
        ],
      ),
      body: IndexedStack(
        index: _currentTabIndex,
        children: [
          _buildHomeTab(student, subjects, pendingAssignments, liveClasses),
          _buildSubjectsTab(subjects),
          _buildHomeworkTab(pendingAssignments, submittedAssignments),
          _buildAIToolsTab(subjects),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentTabIndex,
        onTap: (idx) => setState(() => _currentTabIndex = idx),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF024AD8),
        unselectedItemColor: const Color(0xFF636363),
        selectedFontSize: 11,
        unselectedFontSize: 10,
        backgroundColor: Colors.white,
        elevation: 8,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.menu_book_outlined),
            activeIcon: Icon(Icons.menu_book),
            label: 'Subjects',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.assignment_outlined),
            activeIcon: Icon(Icons.assignment),
            label: 'Homework',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.psychology_outlined),
            activeIcon: Icon(Icons.psychology),
            label: 'AI Hub',
          ),
        ],
      ),
    );
  }

  // TAB 1: HOME OVERVIEW
  Widget _buildHomeTab(
    Map<String, dynamic>? student,
    List<dynamic> subjects,
    List<dynamic> pendingAssignments,
    List<dynamic> liveClasses,
  ) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // HP Welcome Hero Card
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE8E8E8)),
              boxShadow: const [
                BoxShadow(
                  color: Color.fromRGBO(26, 26, 26, 0.08),
                  blurRadius: 8,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: const Color(0xFFC9E0FC),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        _gradeLevel <= 5
                            ? 'PRIMARY TIER (CLASSES 3-5)'
                            : _gradeLevel <= 8
                                ? 'MIDDLE SCHOOL TIER (CLASSES 6-8)'
                                : 'SENIOR SECONDARY (CLASSES 9-12)',
                        style: const TextStyle(color: Color(0xFF0E3191), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 0.8),
                      ),
                    ),
                    const Text('AY 2026-2027', style: TextStyle(fontSize: 11, color: Color(0xFF636363), fontWeight: FontWeight.w500)),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  'Welcome, ${student?['full_name']}!',
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1A1A1A),
                    letterSpacing: -0.5,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Roll Number: ${student?['roll_number']} • Attendance & Homework Synchronized',
                  style: const TextStyle(fontSize: 12, color: Color(0xFF636363)),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AIDoubtSolverScreen())),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF024AD8),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  ),
                  icon: const Icon(Icons.bolt, size: 16),
                  label: const Text('ASK AI DOUBT SOLVER', style: TextStyle(letterSpacing: 0.7, fontSize: 11, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Live Class Notification (If any)
          if (liveClasses.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1A1A1A), // HP Ink dark slab
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(
                children: [
                  Transform(
                    transform: Matrix4.skewX(-0.4),
                    child: Container(
                      width: 8,
                      height: 32,
                      color: liveClasses[0]['status'] == 'IN_PROGRESS' ? const Color(0xFFFF5050) : const Color(0xFF296EF9),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          liveClasses[0]['status'] == 'IN_PROGRESS' ? '🔴 LIVE SESSION ACTIVE NOW' : 'SCHEDULED LIVE CLASS',
                          style: TextStyle(
                            color: liveClasses[0]['status'] == 'IN_PROGRESS' ? const Color(0xFFFF5050) : const Color(0xFF93C5FD),
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.8,
                          ),
                        ),
                        Text(
                          liveClasses[0]['title'],
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 13),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  ElevatedButton(
                    onPressed: () => _joinLiveMeeting(liveClasses[0]),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF024AD8),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                    ),
                    child: const Text('JOIN', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8)),
                  )
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],

          // Quick Subjects
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('MY SUBJECTS', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363))),
              TextButton(
                onPressed: () => setState(() => _currentTabIndex = 1),
                child: const Text('View All', style: TextStyle(fontSize: 12, color: Color(0xFF024AD8), fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 6),
          ...subjects.take(3).map((s) => _buildSubjectCard(s)),

          const SizedBox(height: 20),

          // Pending Homework
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('PENDING HOMEWORK', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363))),
              TextButton(
                onPressed: () => setState(() => _currentTabIndex = 2),
                child: const Text('View All', style: TextStyle(fontSize: 12, color: Color(0xFF024AD8), fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 6),
          if (pendingAssignments.isEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: const Color(0xFFF7F7F7), borderRadius: BorderRadius.circular(12)),
              child: const Center(
                child: Text('All homework completed! Great job.', style: TextStyle(fontSize: 12, color: Color(0xFF636363))),
              ),
            )
          else
            ...pendingAssignments.take(2).map((a) => _buildAssignmentCard(a)),
        ],
      ),
    );
  }

  // TAB 2: ALL SUBJECTS
  Widget _buildSubjectsTab(List<dynamic> subjects) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('ENROLLED SUBJECTS', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363))),
          const SizedBox(height: 4),
          const Text(
            'Tap on any subject to explore textbook chapters, read revision notes, and take chapter quizzes.',
            style: TextStyle(fontSize: 12, color: Color(0xFF3D3D3D)),
          ),
          const SizedBox(height: 16),
          ...subjects.map((s) => _buildSubjectCard(s)),
        ],
      ),
    );
  }

  Widget _buildSubjectCard(dynamic s) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => SubjectDetailScreen(
              subjectId: s['id'],
              subjectName: s['name'],
              subjectCode: s['code'],
            ),
          ),
        );
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
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
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFE8E8E8)),
              ),
              child: const Icon(Icons.menu_book, color: Color(0xFF024AD8), size: 22),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(s['name'], style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15, color: Color(0xFF1A1A1A))),
                  const SizedBox(height: 2),
                  Text('${s['code']} • ${s['materials_count']} Study Documents', style: const TextStyle(fontSize: 12, color: Color(0xFF636363))),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios, size: 14, color: Color(0xFFC2C2C2)),
          ],
        ),
      ),
    );
  }

  void _showProfileDialog(Map<String, dynamic>? student) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                color: const Color(0xFFC9E0FC),
                borderRadius: BorderRadius.circular(19),
              ),
              child: Center(
                child: Text(
                  student?['full_name'] != null && student!['full_name'].toString().isNotEmpty
                      ? student['full_name'].toString().substring(0, 1)
                      : 'S',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF024AD8)),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    student?['full_name'] ?? 'Student Profile',
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF1A1A1A)),
                  ),
                  Text(
                    'Class ${student?['grade_level']}-${student?['section']} • Roll ${student?['roll_number']}',
                    style: const TextStyle(fontSize: 11, color: Color(0xFF636363)),
                  ),
                ],
              ),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Divider(color: Color(0xFFE8E8E8)),
            const SizedBox(height: 8),
            const Text('ACADEMIC YEAR', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF636363))),
            Text(student?['academic_year'] ?? '2026-2027', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF1A1A1A))),
            const SizedBox(height: 12),
            const Text('SECURITY & ROLE', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF636363))),
            const Text('Enrolled Student (Grade-Locked RBAC)', style: TextStyle(fontSize: 13, color: Color(0xFF1A1A1A))),
            const SizedBox(height: 12),
            const Text('PLATFORM VERSION', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF636363))),
            const Text('EduBridge Enterprise v2.0 (HP Design System)', style: TextStyle(fontSize: 12, color: Color(0xFF1A1A1A))),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('CLOSE', style: TextStyle(color: Color(0xFF024AD8), fontWeight: FontWeight.bold)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen()));
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFB3262B),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
            ),
            child: const Text('LOGOUT', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 11)),
          ),
        ],
      ),
    );
  }

  // TAB 3: HOMEWORK
  Widget _buildHomeworkTab(List<dynamic> pending, List<dynamic> submitted) {
    final activeList = _homeworkFilter == 0 ? pending : submitted;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('HOMEWORK ASSIGNMENTS', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363))),
          const SizedBox(height: 12),
          Row(
            children: [
              ChoiceChip(
                label: Text('PENDING (${pending.length})', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: _homeworkFilter == 0 ? Colors.white : const Color(0xFF1A1A1A))),
                selected: _homeworkFilter == 0,
                selectedColor: const Color(0xFF024AD8),
                backgroundColor: const Color(0xFFF7F7F7),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                onSelected: (_) => setState(() => _homeworkFilter = 0),
              ),
              const SizedBox(width: 8),
              ChoiceChip(
                label: Text('COMPLETED (${submitted.length})', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: _homeworkFilter == 1 ? Colors.white : const Color(0xFF1A1A1A))),
                selected: _homeworkFilter == 1,
                selectedColor: const Color(0xFF15803D),
                backgroundColor: const Color(0xFFF7F7F7),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                onSelected: (_) => setState(() => _homeworkFilter = 1),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (activeList.isEmpty)
            Container(
              padding: const EdgeInsets.all(32),
              decoration: BoxDecoration(color: const Color(0xFFF7F7F7), borderRadius: BorderRadius.circular(16)),
              child: Center(
                child: Text(
                  _homeworkFilter == 0 ? 'No pending homework assignments! You are all caught up.' : 'No submitted homework yet.',
                  style: const TextStyle(color: Color(0xFF636363), fontSize: 13),
                ),
              ),
            )
          else
            ...activeList.map((a) => _buildAssignmentCard(a)),
        ],
      ),
    );
  }

  Widget _buildAssignmentCard(dynamic a) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => AssignmentDetailScreen(
              assignmentId: a['id'],
              title: a['title'],
              subjectName: a['subject_name'] ?? 'Homework',
            ),
          ),
        ).then((_) => _fetchDashboard());
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE8E8E8)),
          boxShadow: const [
            BoxShadow(color: Color.fromRGBO(26, 26, 26, 0.05), blurRadius: 6, offset: Offset(0, 2)),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  a['subject_name'].toString().toUpperCase(),
                  style: const TextStyle(color: Color(0xFF024AD8), fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 0.8),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(color: const Color(0xFFFFFBEB), borderRadius: BorderRadius.circular(4)),
                  child: Text(
                    a['status'],
                    style: const TextStyle(color: Color(0xFFB45309), fontSize: 9, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              a['title'],
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14, color: Color(0xFF1A1A1A)),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Max Marks: ${a['max_marks']}', style: const TextStyle(fontSize: 12, color: Color(0xFF636363))),
                const Row(
                  children: [
                    Text('Open Details', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF024AD8))),
                    SizedBox(width: 4),
                    Icon(Icons.arrow_forward_ios, size: 10, color: Color(0xFF024AD8)),
                  ],
                ),
              ],
            )
          ],
        ),
      ),
    );
  }

  // TAB 4: AI TOOLS HUB
  Widget _buildAIToolsTab(List<dynamic> subjects) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('EDUBRIDGE AI LEARNING MODELS', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363))),
          const SizedBox(height: 4),
          const Text('Age-tailored pedagogical AI assistants to accelerate comprehension.', style: TextStyle(fontSize: 12, color: Color(0xFF3D3D3D))),
          const SizedBox(height: 20),

          // Tool 1: AI Doubt Solver
          _buildAIToolCard(
            title: 'AI Syllabus Doubt Solver',
            badge: 'MODEL 1 • MULTI-TIER',
            description: 'Ask any concept, diagram, or formula. Delivers step-by-step explanations, key takeaways, and self-test practice questions.',
            icon: Icons.bolt,
            accentColor: const Color(0xFF024AD8),
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AIDoubtSolverScreen())),
          ),

          const SizedBox(height: 16),

          // Tool 2: Socratic Homework Tutor
          _buildAIToolCard(
            title: 'Socratic Homework Tutor',
            badge: 'MODEL 2 • NON-SPOILER',
            description: 'Stuck on a homework question? AI guides you step-by-step with Socratic questions without spoiling direct answers.',
            icon: Icons.psychology,
            accentColor: const Color(0xFF296EF9),
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const HomeworkHintScreen())),
          ),

          const SizedBox(height: 16),

          // Tool 3: Chapter Quiz Generator
          _buildAIToolCard(
            title: 'Chapter Quiz Generator',
            badge: 'MODEL 4 • ADAPTIVE MCQs',
            description: 'Practice questions generated on the fly from any textbook chapter with instant explanations and scoring.',
            icon: Icons.quiz_outlined,
            accentColor: const Color(0xFF0E3191),
            onTap: () {
              if (subjects.isNotEmpty) {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => SubjectDetailScreen(
                      subjectId: subjects.first['id'],
                      subjectName: subjects.first['name'],
                      subjectCode: subjects.first['code'],
                    ),
                  ),
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildAIToolCard({
    required String title,
    required String badge,
    required String description,
    required IconData icon,
    required Color accentColor,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8E8E8)),
        boxShadow: const [
          BoxShadow(color: Color.fromRGBO(26, 26, 26, 0.05), blurRadius: 8, offset: Offset(0, 2)),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: const Color(0xFFC9E0FC),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        badge,
                        style: const TextStyle(color: Color(0xFF0E3191), fontSize: 9, fontWeight: FontWeight.bold, letterSpacing: 0.7),
                      ),
                    ),
                    Icon(icon, color: accentColor, size: 24),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  title,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Color(0xFF1A1A1A)),
                ),
                const SizedBox(height: 6),
                Text(
                  description,
                  style: const TextStyle(fontSize: 12, height: 1.4, color: Color(0xFF636363)),
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Text('OPEN TOOL', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: accentColor, letterSpacing: 0.8)),
                    const SizedBox(width: 4),
                    Icon(Icons.arrow_forward, size: 14, color: accentColor),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
