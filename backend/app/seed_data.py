from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app.models import (
    User, RoleEnum, Class, Student, Subject, Chapter, Material, MaterialTypeEnum,
    Assignment, Submission, SubmissionStatusEnum, LiveClass, LiveClassStatusEnum, LiveAttendance
)
from app.services.auth_service import get_password_hash
from app.services.storage_service import save_uploaded_file

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Check if admin already exists
    admin = db.query(User).filter(User.phone_number == "9876543210").first()
    if admin:
        print("[Seed] Database already seeded. Skipping.")
        db.close()
        return

    print("[Seed] Seeding EduBridge database...")

    # 1. Super Admin & Teacher
    admin = User(
        phone_number="9876543210",
        email="admin@edubridge.org",
        full_name="Harish Kumar D (Super Admin)",
        password_hash=get_password_hash("Admin@123"),
        role=RoleEnum.SUPER_ADMIN,
        is_active=True
    )
    db.add(admin)

    teacher = User(
        phone_number="9876543211",
        email="teacher@edubridge.org",
        full_name="Priya Sundaram (Teacher)",
        password_hash=get_password_hash("Teacher@123"),
        role=RoleEnum.TEACHER,
        is_active=True
    )
    db.add(teacher)
    db.flush()

    # 2. Classes (Tiers: 3-5, 6-8, 9-12)
    c4 = Class(grade_level=4, section="A", academic_year="2026-2027")
    c8 = Class(grade_level=8, section="A", academic_year="2026-2027")
    c10 = Class(grade_level=10, section="A", academic_year="2026-2027")
    db.add_all([c4, c8, c10])
    db.flush()

    # 3. Students
    # Student 1: Primary (Class 4)
    u_st1 = User(
        phone_number="9876543220",
        full_name="Kavya Ramesh",
        password_hash=get_password_hash("Student@123"),
        role=RoleEnum.STUDENT,
        is_active=True
    )
    db.add(u_st1)
    db.flush()
    st1 = Student(
        user_id=u_st1.id,
        class_id=c4.id,
        roll_number="04A01",
        guardian_name="Ramesh Kumar",
        guardian_phone="9876543290"
    )
    db.add(st1)

    # Student 2: Middle School (Class 8)
    u_st2 = User(
        phone_number="9876543221",
        full_name="Aarav Kumar",
        password_hash=get_password_hash("Student@123"),
        role=RoleEnum.STUDENT,
        is_active=True
    )
    db.add(u_st2)
    db.flush()
    st2 = Student(
        user_id=u_st2.id,
        class_id=c8.id,
        roll_number="08A07",
        guardian_name="Sundar Kumar",
        guardian_phone="9876543291"
    )
    db.add(st2)

    # Student 3: High School (Class 10)
    u_st3 = User(
        phone_number="9876543222",
        full_name="Diya Sharma",
        password_hash=get_password_hash("Student@123"),
        role=RoleEnum.STUDENT,
        is_active=True
    )
    db.add(u_st3)
    db.flush()
    st3 = Student(
        user_id=u_st3.id,
        class_id=c10.id,
        roll_number="10A15",
        guardian_name="Vikram Sharma",
        guardian_phone="9876543292"
    )
    db.add(st3)
    db.flush()

    # =====================================================
    # 4. SUBJECTS — ALL 7 Subjects across 3 Classes
    # =====================================================

    # --- Class 8 Subjects ---
    sci8 = Subject(
        class_id=c8.id,
        name="Science",
        code="SCI8",
        thumbnail_url="https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=60"
    )
    math8 = Subject(
        class_id=c8.id,
        name="Mathematics",
        code="MAT8",
        thumbnail_url="https://images.unsplash.com/photo-1509228468518-180dd4864904?w=500&auto=format&fit=crop&q=60"
    )
    eng8 = Subject(
        class_id=c8.id,
        name="English",
        code="ENG8",
        thumbnail_url="https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=500&auto=format&fit=crop&q=60"
    )
    db.add_all([sci8, math8, eng8])
    db.flush()

    # --- Class 4 Subjects ---
    evs4 = Subject(
        class_id=c4.id,
        name="Environmental Studies & Science",
        code="EVS4",
        thumbnail_url="https://images.unsplash.com/photo-1500534623283-312aade485b7?w=500&auto=format&fit=crop&q=60"
    )
    math4 = Subject(
        class_id=c4.id,
        name="Fun Mathematics",
        code="MAT4",
        thumbnail_url="https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=500&auto=format&fit=crop&q=60"
    )
    db.add_all([evs4, math4])
    db.flush()

    # --- Class 10 Subjects ---
    sci10 = Subject(
        class_id=c10.id,
        name="Physics & Chemistry",
        code="SCI10",
        thumbnail_url="https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?w=500&auto=format&fit=crop&q=60"
    )
    math10 = Subject(
        class_id=c10.id,
        name="Advanced Mathematics",
        code="MAT10",
        thumbnail_url="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=500&auto=format&fit=crop&q=60"
    )
    db.add_all([sci10, math10])
    db.flush()

    # =====================================================
    # 5. CHAPTERS & MATERIALS — ALL Subjects
    # =====================================================

    def make_material(chapter, title, filename, content_desc):
        """Helper to create a mock PDF material for a chapter."""
        content = f"%PDF-1.4 Mock EduBridge Notes: {title}. Key concepts: {content_desc}.".encode()
        key, size = save_uploaded_file(content, filename)
        mat = Material(
            chapter_id=chapter.id,
            title=title,
            material_type=MaterialTypeEnum.PDF_NOTES,
            file_key=key,
            file_size_bytes=size,
            is_downloadable=True
        )
        db.add(mat)
        return mat

    # ----- Science Class 8 (SCI8) -----
    sci8_ch1 = Chapter(subject_id=sci8.id, title="1. Crop Production and Management", order_index=1)
    sci8_ch2 = Chapter(subject_id=sci8.id, title="2. Microorganisms: Friend and Foe", order_index=2)
    sci8_ch3 = Chapter(subject_id=sci8.id, title="3. Coal and Petroleum", order_index=3)
    db.add_all([sci8_ch1, sci8_ch2, sci8_ch3])
    db.flush()

    make_material(sci8_ch1, "Comprehensive Revision Notes - Crop Production",
                  "Crop_Production_Notes.pdf",
                  "Soil preparation, sowing seeds, irrigation methods, harvesting, storage")
    make_material(sci8_ch1, "Drip vs Sprinkler Irrigation Comparison",
                  "Irrigation_Methods.pdf",
                  "Drip irrigation, sprinkler system, canal irrigation, advantages and disadvantages")
    make_material(sci8_ch2, "Microorganisms Study Guide",
                  "Microorganisms_Notes.pdf",
                  "Bacteria, virus, fungi, protozoa, algae, nitrogen fixation, fermentation")
    make_material(sci8_ch3, "Coal and Petroleum Revision",
                  "Coal_Petroleum_Notes.pdf",
                  "Fossil fuels, coal formation, petroleum refining, natural gas, conservation")

    # ----- Mathematics Class 8 (MAT8) -----
    mat8_ch1 = Chapter(subject_id=math8.id, title="1. Rational Numbers", order_index=1)
    mat8_ch2 = Chapter(subject_id=math8.id, title="2. Linear Equations in One Variable", order_index=2)
    mat8_ch3 = Chapter(subject_id=math8.id, title="3. Data Handling & Graphs", order_index=3)
    db.add_all([mat8_ch1, mat8_ch2, mat8_ch3])
    db.flush()

    make_material(mat8_ch1, "Rational Numbers - Complete Theory & Practice",
                  "Rational_Numbers_Notes.pdf",
                  "Number line, properties of rational numbers, operations, between two rationals")
    make_material(mat8_ch2, "Linear Equations Solved Examples",
                  "Linear_Equations_Notes.pdf",
                  "Solving equations, transposing, word problems, cross multiplication")
    make_material(mat8_ch3, "Data Handling & Graph Types",
                  "Data_Handling_Notes.pdf",
                  "Bar graph, pie chart, histogram, frequency distribution, probability basics")

    # ----- English Class 8 (ENG8) -----
    eng8_ch1 = Chapter(subject_id=eng8.id, title="1. Parts of Speech & Tenses", order_index=1)
    eng8_ch2 = Chapter(subject_id=eng8.id, title="2. Reading Comprehension", order_index=2)
    eng8_ch3 = Chapter(subject_id=eng8.id, title="3. Essay Writing & Letter Format", order_index=3)
    db.add_all([eng8_ch1, eng8_ch2, eng8_ch3])
    db.flush()

    make_material(eng8_ch1, "Grammar Essentials - Parts of Speech & Tenses",
                  "Grammar_Tenses_Notes.pdf",
                  "Nouns, verbs, adjectives, adverbs, prepositions, present, past, future tenses")
    make_material(eng8_ch2, "Reading Comprehension Strategies",
                  "Reading_Comprehension_Notes.pdf",
                  "Skimming, scanning, inference, main idea, supporting details, vocabulary in context")
    make_material(eng8_ch3, "Essay & Letter Writing Guide",
                  "Essay_Letter_Writing_Notes.pdf",
                  "Formal letter, informal letter, essay structure, introduction, body, conclusion")

    # ----- EVS Class 4 (EVS4) -----
    evs4_ch1 = Chapter(subject_id=evs4.id, title="1. Plants & Their Parts", order_index=1)
    evs4_ch2 = Chapter(subject_id=evs4.id, title="2. Animals & Habitats", order_index=2)
    evs4_ch3 = Chapter(subject_id=evs4.id, title="3. Water & Weather", order_index=3)
    db.add_all([evs4_ch1, evs4_ch2, evs4_ch3])
    db.flush()

    make_material(evs4_ch1, "Fun with Plants - Roots Stems Leaves Flowers",
                  "Plants_Parts_Notes.pdf",
                  "Root, stem, leaf, flower, fruit, seed, photosynthesis for kids, plant growth")
    make_material(evs4_ch2, "Animals Around Us - Where Do They Live?",
                  "Animals_Habitats_Notes.pdf",
                  "Land animals, water animals, birds, insects, forest, desert, ocean habitats")
    make_material(evs4_ch3, "Water Cycle & Seasons",
                  "Water_Weather_Notes.pdf",
                  "Evaporation, condensation, rain, clouds, summer, winter, monsoon, saving water")

    # ----- Fun Mathematics Class 4 (MAT4) -----
    mat4_ch1 = Chapter(subject_id=math4.id, title="1. Numbers Up to 10000", order_index=1)
    mat4_ch2 = Chapter(subject_id=math4.id, title="2. Addition & Subtraction", order_index=2)
    mat4_ch3 = Chapter(subject_id=math4.id, title="3. Shapes & Patterns", order_index=3)
    db.add_all([mat4_ch1, mat4_ch2, mat4_ch3])
    db.flush()

    make_material(mat4_ch1, "Fun with Numbers - Place Value & Comparison",
                  "Numbers_10000_Notes.pdf",
                  "Place value, ones tens hundreds thousands, number names, ascending descending")
    make_material(mat4_ch2, "Add and Subtract Like a Pro!",
                  "Addition_Subtraction_Notes.pdf",
                  "Carrying, borrowing, word problems, mental math tricks, estimation")
    make_material(mat4_ch3, "Shapes Patterns and Symmetry",
                  "Shapes_Patterns_Notes.pdf",
                  "Triangle, square, rectangle, circle, pentagon, mirror symmetry, repeating patterns")

    # ----- Physics & Chemistry Class 10 (SCI10) -----
    sci10_ch1 = Chapter(subject_id=sci10.id, title="1. Chemical Reactions & Equations", order_index=1)
    sci10_ch2 = Chapter(subject_id=sci10.id, title="2. Light - Reflection & Refraction", order_index=2)
    sci10_ch3 = Chapter(subject_id=sci10.id, title="3. Electricity & Circuits", order_index=3)
    db.add_all([sci10_ch1, sci10_ch2, sci10_ch3])
    db.flush()

    make_material(sci10_ch1, "Chemical Reactions - Balancing & Types",
                  "Chemical_Reactions_Notes.pdf",
                  "Combination, decomposition, displacement, double displacement, redox, balancing equations")
    make_material(sci10_ch2, "Optics - Mirrors & Lenses",
                  "Light_Reflection_Refraction_Notes.pdf",
                  "Reflection laws, plane mirror, concave convex, refraction, Snell law, lens formula")
    make_material(sci10_ch3, "Electricity - Ohm's Law & Circuits",
                  "Electricity_Circuits_Notes.pdf",
                  "Current, voltage, resistance, Ohm law, series parallel circuit, power, kWh")

    # ----- Advanced Mathematics Class 10 (MAT10) -----
    mat10_ch1 = Chapter(subject_id=math10.id, title="1. Polynomials & Factorization", order_index=1)
    mat10_ch2 = Chapter(subject_id=math10.id, title="2. Trigonometry", order_index=2)
    mat10_ch3 = Chapter(subject_id=math10.id, title="3. Statistics & Probability", order_index=3)
    db.add_all([mat10_ch1, mat10_ch2, mat10_ch3])
    db.flush()

    make_material(mat10_ch1, "Polynomials - Zeroes & Factor Theorem",
                  "Polynomials_Notes.pdf",
                  "Degree, zeroes, remainder theorem, factor theorem, algebraic identities, factorization")
    make_material(mat10_ch2, "Trigonometric Ratios & Identities",
                  "Trigonometry_Notes.pdf",
                  "Sin cos tan, ratios of specific angles, complementary angles, trigonometric identities")
    make_material(mat10_ch3, "Statistics - Mean Median Mode & Probability",
                  "Statistics_Probability_Notes.pdf",
                  "Grouped data, mean, median, mode, cumulative frequency, ogive, classical probability")

    # =====================================================
    # 6. ASSIGNMENTS — Across All 3 Classes
    # =====================================================
    now = datetime.utcnow()

    # Class 8 Assignments
    asgn1 = Assignment(
        class_id=c8.id,
        subject_id=sci8.id,
        title="Science Worksheet 4: Irrigation & Soil Health",
        instructions="Answer all questions in your notebook. Upload clear photos of pages 1 to 3.",
        due_date=now + timedelta(days=5),
        max_marks=25,
        allow_late_submission=True,
        created_by=teacher.id
    )
    asgn2 = Assignment(
        class_id=c8.id,
        subject_id=math8.id,
        title="Maths Problem Set 2: Rational Numbers",
        instructions="Complete exercise 2.1 to 2.4 showing every intermediate step.",
        due_date=now + timedelta(days=2),
        max_marks=50,
        allow_late_submission=False,
        created_by=teacher.id
    )
    asgn_eng8 = Assignment(
        class_id=c8.id,
        subject_id=eng8.id,
        title="English Grammar Practice: Tenses Worksheet",
        instructions="Fill in the blanks with correct tense forms. Write at least 5 sentences in each tense.",
        due_date=now + timedelta(days=4),
        max_marks=20,
        allow_late_submission=True,
        created_by=teacher.id
    )

    # Class 4 Assignments
    asgn_evs4 = Assignment(
        class_id=c4.id,
        subject_id=evs4.id,
        title="EVS Activity: Draw & Label Parts of a Plant",
        instructions="Draw a plant with roots, stem, leaves, and flower. Color and label each part neatly.",
        due_date=now + timedelta(days=7),
        max_marks=15,
        allow_late_submission=True,
        created_by=teacher.id
    )
    asgn_mat4 = Assignment(
        class_id=c4.id,
        subject_id=math4.id,
        title="Fun Maths: Addition & Subtraction Practice Sheet",
        instructions="Solve all 20 problems. Show your working for word problems.",
        due_date=now + timedelta(days=6),
        max_marks=20,
        allow_late_submission=True,
        created_by=teacher.id
    )

    # Class 10 Assignments
    asgn_sci10 = Assignment(
        class_id=c10.id,
        subject_id=sci10.id,
        title="Physics Lab Report: Ohm's Law Verification",
        instructions="Perform the experiment, record observations in a table, plot V-I graph, and derive the resistance value.",
        due_date=now + timedelta(days=3),
        max_marks=30,
        allow_late_submission=False,
        created_by=teacher.id
    )
    asgn_mat10 = Assignment(
        class_id=c10.id,
        subject_id=math10.id,
        title="Trigonometry Problem Set: Heights & Distances",
        instructions="Solve exercises 9.1 to 9.3 from NCERT. Draw diagrams for all height-distance problems.",
        due_date=now + timedelta(days=5),
        max_marks=40,
        allow_late_submission=True,
        created_by=teacher.id
    )

    db.add_all([asgn1, asgn2, asgn_eng8, asgn_evs4, asgn_mat4, asgn_sci10, asgn_mat10])
    db.flush()

    # =====================================================
    # 7. SUBMISSIONS — Sample Graded Work
    # =====================================================
    sample_content = b"%PDF-1.4 Mock student submission page scan."
    sub_key, sub_size = save_uploaded_file(sample_content, "student_submission.pdf")

    sub1 = Submission(
        assignment_id=asgn1.id,
        student_id=st2.id,
        file_keys=[{"name": "aarav_worksheet4_p1.pdf", "key": sub_key}],
        student_notes="Question 5 diagram is attached on page 1.",
        marks_awarded=22.5,
        feedback_remarks="Excellent neat diagrams! Review the difference between drip and sprinkler irrigation.",
        status=SubmissionStatusEnum.GRADED,
        submitted_at=now - timedelta(hours=12),
        graded_at=now - timedelta(hours=2),
        graded_by=teacher.id
    )
    db.add(sub1)

    # =====================================================
    # 8. LIVE CLASSES — Multiple Classes
    # =====================================================
    live1 = LiveClass(
        class_id=c8.id,
        subject_id=sci8.id,
        title="Light, Reflection and Human Eye - Interactive Session",
        meeting_room_id="eb-sci8-light-2026",
        scheduled_start=now + timedelta(minutes=10),
        duration_minutes=45,
        status=LiveClassStatusEnum.IN_PROGRESS,
        created_by=teacher.id
    )
    live2 = LiveClass(
        class_id=c10.id,
        subject_id=sci10.id,
        title="Chemical Bonding & Molecular Structure - Doubt Clearing",
        meeting_room_id="eb-sci10-chem-2026",
        scheduled_start=now + timedelta(hours=2),
        duration_minutes=60,
        status=LiveClassStatusEnum.SCHEDULED,
        created_by=teacher.id
    )
    live3 = LiveClass(
        class_id=c4.id,
        subject_id=evs4.id,
        title="Fun with Plants - Virtual Garden Tour",
        meeting_room_id="eb-evs4-plants-2026",
        scheduled_start=now + timedelta(hours=1),
        duration_minutes=30,
        status=LiveClassStatusEnum.SCHEDULED,
        created_by=teacher.id
    )
    db.add_all([live1, live2, live3])

    db.commit()
    print("[Seed] Successfully seeded:")
    print("  -> Admin + Teacher")
    print("  -> 3 Classes (4-A, 8-A, 10-A)")
    print("  -> 3 Students (Primary, Middle, High School)")
    print("  -> 7 Subjects with 21 Chapters and 21 Study Materials")
    print("  -> 7 Assignments across all classes")
    print("  -> 1 Graded Submission")
    print("  -> 3 Live Classes")
    db.close()

if __name__ == "__main__":
    seed()
