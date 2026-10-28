import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Configured for local development / Android emulator (10.0.2.2 points to host machine)
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
  static String? token;
  static Map<String, dynamic>? currentUser;

  static Map<String, String> get headers => {
    'Content-Type': 'application/json',
    if (token != null) 'Authorization': 'Bearer $token',
  };

  // Helper to parse backend error responses into friendly human-readable messages
  static String _parseError(String body) {
    try {
      final data = jsonDecode(body);
      if (data is Map) {
        if (data.containsKey('error') && data['error'] is Map) {
          final errMap = data['error'] as Map;
          if (errMap.containsKey('details') && errMap['details'] is List && (errMap['details'] as List).isNotEmpty) {
            final firstDetail = errMap['details'][0];
            if (firstDetail is Map && firstDetail.containsKey('issue')) {
              return '${firstDetail['issue']} (${firstDetail['field'] ?? 'input'})';
            }
          }
          if (errMap.containsKey('message')) {
            return errMap['message'].toString();
          }
        }
        if (data.containsKey('detail')) {
          final detail = data['detail'];
          if (detail is Map && detail.containsKey('message')) {
            return detail['message'].toString();
          }
          return detail.toString();
        }
      }
    } catch (_) {}
    return 'Action could not be completed. Please try again.';
  }

  // 1. Authentication
  static Future<Map<String, dynamic>> login(String phone, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'phone_number': phone, 'password': password}),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      token = data['access_token'];
      currentUser = data['user'];
      return data;
    } else {
      throw Exception(_parseError(res.body));
    }
  }

  // 2. Student Dashboard
  static Future<Map<String, dynamic>> getStudentDashboard() async {
    final res = await http.get(
      Uri.parse('$baseUrl/student/dashboard'),
      headers: headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception(_parseError(res.body));
    }
  }

  // 3. Subject Chapters & Materials
  static Future<Map<String, dynamic>> getSubjectMaterials(String subjectId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/content/subjects/$subjectId/materials'),
      headers: headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception(_parseError(res.body));
    }
  }

  // 4. Assignment Detail
  static Future<Map<String, dynamic>> getAssignmentDetail(String assignmentId) async {
    final res = await http.get(
      Uri.parse('$baseUrl/assignments/$assignmentId'),
      headers: headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception(_parseError(res.body));
    }
  }

  // 5. Submit Assignment (Multipart)
  static Future<Map<String, dynamic>> submitAssignment(
    String assignmentId, {
    String? notes,
    String? sampleFileName,
  }) async {
    final uri = Uri.parse('$baseUrl/assignments/$assignmentId/submit');
    final request = http.MultipartRequest('POST', uri);
    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    if (notes != null && notes.trim().isNotEmpty) {
      request.fields['notes'] = notes.trim();
    }

    // Attach submission document
    final docContent = '%PDF-1.4 EduBridge Student Homework Submission.\nNotes: ${notes ?? 'Completed assignment work'}';
    request.files.add(
      http.MultipartFile.fromString(
        'files',
        docContent,
        filename: sampleFileName ?? 'my_homework_submission.pdf',
      ),
    );

    final streamedRes = await request.send();
    final res = await http.Response.fromStream(streamedRes);
    if (res.statusCode == 201 || res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception(_parseError(res.body));
    }
  }

  // 6. AI Model 1: Syllabus Doubt Solver
  static Future<Map<String, dynamic>> askAIDoubt(String question, {String? subjectId, String? chapterId}) async {
    final res = await http.post(
      Uri.parse('$baseUrl/ai/doubt/ask'),
      headers: headers,
      body: jsonEncode({
        'question': question,
        'subject_id': subjectId,
        'chapter_id': chapterId,
      }),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception(_parseError(res.body));
    }
  }

  // 7. AI Model 2: Socratic Homework Tutor (Hints)
  static Future<Map<String, dynamic>> getHomeworkHint({
    required String assignmentId,
    required String questionText,
    String? studentAttempt,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/ai/homework/hint'),
      headers: headers,
      body: jsonEncode({
        'assignment_id': assignmentId,
        'question_text': questionText,
        'student_attempt': studentAttempt,
      }),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception(_parseError(res.body));
    }
  }

  // 8. AI Model 4: Chapter Quiz Generator
  static Future<Map<String, dynamic>> generateQuiz({
    required String chapterId,
    int numQuestions = 5,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl/ai/quiz/generate'),
      headers: headers,
      body: jsonEncode({
        'chapter_id': chapterId,
        'num_questions': numQuestions,
      }),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception(_parseError(res.body));
    }
  }

  // 9. Live Classes: Join Meeting Room
  static Future<Map<String, dynamic>> joinLiveClass(String classId) async {
    final res = await http.post(
      Uri.parse('$baseUrl/live/$classId/join'),
      headers: headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    } else {
      throw Exception(_parseError(res.body));
    }
  }
}
