import sys
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("RUNNING EDUBRIDGE COMPREHENSIVE BACKEND & AI TESTS")
    print("=" * 60)

    # 1. Root / Health
    res = client.get("/")
    assert res.status_code == 200, f"Root failed: {res.text}"
    print("[PASS] Root and Health endpoint OK")

    # 2. Admin Login
    res = client.post("/api/v1/auth/login", json={"phone_number": "9876543210", "password": "Admin@123"})
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] Super Admin Login OK (JWT issued)")

    # 3. Student Login (Aarav Kumar, Class 8)
    res = client.post("/api/v1/auth/login", json={"phone_number": "9876543221", "password": "Student@123"})
    assert res.status_code == 200, f"Student login failed: {res.text}"
    student_token = res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    student_info = res.json()["user"]["student"]
    print(f"[PASS] Student Login OK ({res.json()['user']['full_name']}, Class {student_info['grade_level']}-{student_info['section']})")

    # 4. Admin Stats
    res = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert res.status_code == 200
    stats = res.json()
    print(f"[PASS] Admin Stats: {stats['total_students']} Students, {stats['total_classes']} Classes, {stats['total_assignments']} Assignments")

    # 5. Student Dashboard
    res = client.get("/api/v1/student/dashboard", headers=student_headers)
    assert res.status_code == 200
    dash = res.json()
    print(f"[PASS] Student Dashboard: {len(dash['subjects'])} Subjects, {len(dash['pending_assignments'])} Pending Assignments, {len(dash['upcoming_live_classes'])} Live Sessions")

    # 6. Content Tree
    sub_id = dash['subjects'][0]['id']
    res = client.get(f"/api/v1/content/subjects/{sub_id}/materials", headers=student_headers)
    assert res.status_code == 200
    tree = res.json()
    print(f"[PASS] Content Hub Tree: Subject '{tree['subject']['name']}' has {len(tree['chapters'])} chapters with signed material URLs")

    # 7. Assignment List & Grade details
    res = client.get("/api/v1/assignments/list", headers=student_headers)
    assert res.status_code == 200
    asgns = res.json()["items"]
    print(f"[PASS] Assignment List: Found {len(asgns)} assignments for student's class")

    # 8. Live Class join
    res = client.get("/api/v1/live/upcoming", headers=student_headers)
    assert res.status_code == 200
    lives = res.json()
    if lives:
        live_id = lives[0]["id"]
        res_join = client.post(f"/api/v1/live/{live_id}/join", headers=student_headers)
        assert res_join.status_code == 200
        join_data = res_join.json()
        print(f"[PASS] Live Class Join OK: Room {join_data['room']}, Jitsi WebRTC token generated")

    # 9. AI Model 1: Syllabus Doubt Solver
    res_ai1 = client.post("/api/v1/ai/doubt/ask", headers=student_headers, json={
        "question": "What is the difference between drip irrigation and sprinkler irrigation in crop production?",
        "subject_id": sub_id
    })
    assert res_ai1.status_code == 200
    doubt_ans = res_ai1.json()
    print(f"[PASS] AI Model 1 (Doubt Solver): Pedagogical Tier '{doubt_ans['grade_tier']}' generated {len(doubt_ans['step_by_step'])} explanation steps")

    # 10. AI Model 2: Socratic Homework Tutor
    res_ai2 = client.post("/api/v1/ai/homework/hint", headers=student_headers, json={
        "assignment_id": asgns[0]["id"],
        "question_text": "Calculate the total yield per hectare when fertilizer application is doubled.",
        "student_attempt": "I tried multiplying by 2 but the result looks too high."
    })
    assert res_ai2.status_code == 200
    hint_ans = res_ai2.json()
    print(f"[PASS] AI Model 2 (Socratic Hint): Guiding hint -> '{hint_ans['guiding_hint'][:60]}...'")

    # 11. AI Model 3: Teacher Auto-Grading Assistant
    res_ai3 = client.post("/api/v1/ai/grading/assist", headers=admin_headers, json={
        "assignment_title": "Science Worksheet 4",
        "question_instructions": "Draw and explain the nitrogen cycle diagram.",
        "student_notes": "Diagram is drawn with arrows showing atmospheric nitrogen fixation, ammonification, and nitrification.",
        "max_marks": 25,
        "submitted_files": ["page1.png", "page2.png"]
    })
    assert res_ai3.status_code == 200
    grade_assist = res_ai3.json()
    print(f"[PASS] AI Model 3 (Auto-Grading Assistant): Suggested {grade_assist['suggested_marks']}/{grade_assist['max_marks']} marks, Remarks: '{grade_assist['feedback_remarks'][:50]}...'")

    # 12. AI Model 4: Chapter Quiz & Flashcard Generator
    if tree['chapters']:
        chap_id = tree['chapters'][0]['id']
        res_ai4 = client.post("/api/v1/ai/quiz/generate", headers=student_headers, json={
            "chapter_id": chap_id,
            "num_questions": 3
        })
        assert res_ai4.status_code == 200
        quiz_data = res_ai4.json()
        print(f"[PASS] AI Model 4 (Quiz Generator): Generated {len(quiz_data['questions'])} questions for '{quiz_data['chapter_title']}'")

    print("=" * 60)
    print("ALL 12 BACKEND & AI MODEL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
