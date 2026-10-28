import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'student_dashboard_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController(text: '9876543221'); // Student Class 8
  final _passwordController = TextEditingController(text: 'Student@123');
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _handleLogin() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await ApiService.login(
        _phoneController.text.trim(),
        _passwordController.text.trim(),
      );
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const StudentDashboardScreen()),
        );
      }
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
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 28),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // HP Parallel Chevron Slash Motif
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Transform(
                      transform: Matrix4.skewX(-0.4),
                      child: Container(
                        width: 14,
                        height: 48,
                        color: const Color(0xFF024AD8),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Transform(
                      transform: Matrix4.skewX(-0.4),
                      child: Container(
                        width: 14,
                        height: 48,
                        color: const Color(0xFF296EF9),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                const Text(
                  'EduBridge',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF1A1A1A),
                    letterSpacing: -0.5,
                  ),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Enterprise Hybrid Learning Platform',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.8,
                    color: Color(0xFF636363),
                  ),
                ),
                const SizedBox(height: 36),
                if (_errorMessage != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    margin: const EdgeInsets.only(bottom: 16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFF1F2),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: const Color(0xFFF43F5E)),
                    ),
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: Color(0xFFBE123C), fontSize: 12),
                    ),
                  ),
                TextField(
                  controller: _phoneController,
                  keyboardType: TextInputType.phone,
                  style: const TextStyle(fontSize: 14, color: Color(0xFF1A1A1A)),
                  decoration: InputDecoration(
                    labelText: 'PHONE NUMBER',
                    labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363)),
                    prefixIcon: const Icon(Icons.phone_outlined, color: Color(0xFF636363), size: 20),
                    filled: true,
                    fillColor: const Color(0xFFF7F7F7),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFF024AD8), width: 1.5)),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  style: const TextStyle(fontSize: 14, color: Color(0xFF1A1A1A)),
                  decoration: InputDecoration(
                    labelText: 'PASSWORD',
                    labelStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 0.8, color: Color(0xFF636363)),
                    prefixIcon: const Icon(Icons.lock_outline, color: Color(0xFF636363), size: 20),
                    filled: true,
                    fillColor: const Color(0xFFF7F7F7),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFFE8E8E8))),
                    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(4), borderSide: const BorderSide(color: Color(0xFF024AD8), width: 1.5)),
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: _isLoading ? null : _handleLogin,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF024AD8),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          height: 18,
                          width: 18,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Text(
                          'LOG IN TO PORTAL',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, letterSpacing: 0.8),
                        ),
                ),
                const SizedBox(height: 28),
                const Text(
                  'QUICK TEST ACCOUNTS',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.0, color: Color(0xFF636363)),
                ),
                const SizedBox(height: 10),
                Wrap(
                  alignment: WrapAlignment.center,
                  spacing: 8,
                  children: [
                    ActionChip(
                      label: const Text('CLASS 4', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                      backgroundColor: const Color(0xFFF7F7F7),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                      onPressed: () {
                        _phoneController.text = '9876543220';
                        _passwordController.text = 'Student@123';
                      },
                    ),
                    ActionChip(
                      label: const Text('CLASS 8', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF024AD8))),
                      backgroundColor: const Color(0xFFC9E0FC),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                      onPressed: () {
                        _phoneController.text = '9876543221';
                        _passwordController.text = 'Student@123';
                      },
                    ),
                    ActionChip(
                      label: const Text('CLASS 10', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                      backgroundColor: const Color(0xFFF7F7F7),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                      onPressed: () {
                        _phoneController.text = '9876543222';
                        _passwordController.text = 'Student@123';
                      },
                    ),
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
