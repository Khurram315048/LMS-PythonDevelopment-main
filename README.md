
```
LMS-PythonDevelopment-main
├─ LMS
│  ├─ .env
│  ├─ .pytest_cache
│  │  ├─ CACHEDIR.TAG
│  │  ├─ README.md
│  │  └─ v
│  │     └─ cache
│  │        ├─ lastfailed
│  │        └─ nodeids
│  ├─ app
│  │  ├─ main.py
│  │  ├─ __init__.py
│  │  └─ __pycache__
│  │     ├─ main.cpython-313.pyc
│  │     └─ __init__.cpython-313.pyc
│  ├─ core
│  │  ├─ auth.py
│  │  ├─ config.py
│  │  ├─ cookies.py
│  │  ├─ csrf.py
│  │  ├─ exceptions.py
│  │  ├─ logger.py
│  │  ├─ rate_limiter.py
│  │  ├─ security.py
│  │  ├─ templating.py
│  │  ├─ ws_auth.py
│  │  └─ __pycache__
│  │     ├─ auth.cpython-312.pyc
│  │     ├─ auth.cpython-313.pyc
│  │     ├─ config.cpython-312.pyc
│  │     ├─ config.cpython-313.pyc
│  │     ├─ cookies.cpython-312.pyc
│  │     ├─ cookies.cpython-313.pyc
│  │     ├─ csrf.cpython-312.pyc
│  │     ├─ csrf.cpython-313.pyc
│  │     ├─ exceptions.cpython-312.pyc
│  │     ├─ exceptions.cpython-313.pyc
│  │     ├─ logger.cpython-312.pyc
│  │     ├─ logger.cpython-313.pyc
│  │     ├─ logging.cpython-313.pyc
│  │     ├─ rate_limiter.cpython-312.pyc
│  │     ├─ rate_limiter.cpython-313.pyc
│  │     ├─ security.cpython-312.pyc
│  │     ├─ security.cpython-313.pyc
│  │     ├─ templating.cpython-312.pyc
│  │     ├─ templating.cpython-313.pyc
│  │     └─ ws_auth.cpython-313.pyc
│  ├─ db
│  │  ├─ models
│  │  │  ├─ orm.py
│  │  │  └─ __pycache__
│  │  │     ├─ orm.cpython-312.pyc
│  │  │     └─ orm.cpython-313.pyc
│  │  ├─ session.py
│  │  └─ __pycache__
│  │     ├─ session.cpython-312.pyc
│  │     └─ session.cpython-313.pyc
│  ├─ knowledge_base
│  │  └─ docs
│  │     ├─ admin
│  │     │  ├─ account_management.md
│  │     │  ├─ admissions_process.md
│  │     │  ├─ fee_collection.md
│  │     │  └─ fee_rules.md
│  │     ├─ all
│  │     │  ├─ attendance_policy.md
│  │     │  ├─ exams_results.md
│  │     │  └─ helpdesk.md
│  │     ├─ student
│  │     │  ├─ course_registration.md
│  │     │  ├─ fee_rules.md
│  │     │  ├─ improvement_retake.md
│  │     │  ├─ semester_freeze.md
│  │     │  └─ summer_semester.md
│  │     └─ teacher
│  │        ├─ attendance_marking.md
│  │        ├─ fyp_supervision.md
│  │        ├─ leave_rules.md
│  │        ├─ marks_and_assignments.md
│  │        └─ salary_rules.md
│  ├─ logs
│  │  └─ app.log
│  ├─ modules
│  │  ├─ admin
│  │  │  ├─ repository.py
│  │  │  ├─ routes.py
│  │  │  ├─ service.py
│  │  │  └─ __pycache__
│  │  │     ├─ repository.cpython-312.pyc
│  │  │     ├─ repository.cpython-313.pyc
│  │  │     ├─ routes.cpython-312.pyc
│  │  │     ├─ routes.cpython-313.pyc
│  │  │     ├─ service.cpython-312.pyc
│  │  │     └─ service.cpython-313.pyc
│  │  ├─ auth
│  │  │  ├─ refresh.py
│  │  │  ├─ repository.py
│  │  │  ├─ routes.py
│  │  │  ├─ schema.py
│  │  │  └─ __pycache__
│  │  │     ├─ refresh.cpython-313.pyc
│  │  │     ├─ repository.cpython-313.pyc
│  │  │     ├─ routes.cpython-313.pyc
│  │  │     └─ schema.cpython-313.pyc
│  │  ├─ chatbot
│  │  │  ├─ agent.py
│  │  │  ├─ cache.py
│  │  │  ├─ citations.py
│  │  │  ├─ llm.py
│  │  │  ├─ rag
│  │  │  │  ├─ chunker.py
│  │  │  │  ├─ embedder.py
│  │  │  │  ├─ evaluate.py
│  │  │  │  ├─ eval_cases.json
│  │  │  │  ├─ indexer.py
│  │  │  │  ├─ loader.py
│  │  │  │  ├─ reranker.py
│  │  │  │  ├─ retriever.py
│  │  │  │  ├─ settings.py
│  │  │  │  ├─ store.py
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ __main__.py
│  │  │  │  └─ __pycache__
│  │  │  │     ├─ chunker.cpython-312.pyc
│  │  │  │     ├─ chunker.cpython-313.pyc
│  │  │  │     ├─ embedder.cpython-312.pyc
│  │  │  │     ├─ embedder.cpython-313.pyc
│  │  │  │     ├─ evaluate.cpython-312.pyc
│  │  │  │     ├─ evaluate.cpython-313.pyc
│  │  │  │     ├─ indexer.cpython-312.pyc
│  │  │  │     ├─ indexer.cpython-313.pyc
│  │  │  │     ├─ loader.cpython-312.pyc
│  │  │  │     ├─ loader.cpython-313.pyc
│  │  │  │     ├─ reranker.cpython-313.pyc
│  │  │  │     ├─ retriever.cpython-312.pyc
│  │  │  │     ├─ retriever.cpython-313.pyc
│  │  │  │     ├─ settings.cpython-312.pyc
│  │  │  │     ├─ settings.cpython-313.pyc
│  │  │  │     ├─ store.cpython-312.pyc
│  │  │  │     ├─ store.cpython-313.pyc
│  │  │  │     ├─ __init__.cpython-312.pyc
│  │  │  │     ├─ __init__.cpython-313.pyc
│  │  │  │     ├─ __main__.cpython-312.pyc
│  │  │  │     └─ __main__.cpython-313.pyc
│  │  │  ├─ registry.py
│  │  │  ├─ routes.py
│  │  │  ├─ tools
│  │  │  │  ├─ tools_sql.py
│  │  │  │  ├─ tools_student.py
│  │  │  │  └─ tools_teacher.py
│  │  │  ├─ __init__.py
│  │  │  └─ __pycache__
│  │  │     ├─ agent.cpython-313.pyc
│  │  │     ├─ cache.cpython-313.pyc
│  │  │     ├─ citations.cpython-313.pyc
│  │  │     ├─ llm.cpython-313.pyc
│  │  │     ├─ registry.cpython-313.pyc
│  │  │     ├─ routes.cpython-313.pyc
│  │  │     └─ __init__.cpython-313.pyc
│  │  ├─ files
│  │  │  ├─ routes.py
│  │  │  └─ __pycache__
│  │  │     └─ routes.cpython-313.pyc
│  │  ├─ notifications
│  │  │  ├─ updates_routes.py
│  │  │  ├─ websocket_routes.py
│  │  │  └─ __pycache__
│  │  │     └─ websocket_routes.cpython-313.pyc
│  │  ├─ students
│  │  │  ├─ repository.py
│  │  │  ├─ routes.py
│  │  │  ├─ schemas.py
│  │  │  ├─ service.py
│  │  │  └─ __pycache__
│  │  │     ├─ repository.cpython-312.pyc
│  │  │     ├─ repository.cpython-313.pyc
│  │  │     ├─ routes.cpython-312.pyc
│  │  │     ├─ routes.cpython-313.pyc
│  │  │     ├─ schemas.cpython-312.pyc
│  │  │     ├─ schemas.cpython-313.pyc
│  │  │     ├─ service.cpython-312.pyc
│  │  │     └─ service.cpython-313.pyc
│  │  └─ teachers
│  │     ├─ repository.py
│  │     ├─ routes.py
│  │     ├─ schemas.py
│  │     ├─ service.py
│  │     └─ __pycache__
│  │        ├─ repository.cpython-312.pyc
│  │        ├─ repository.cpython-313.pyc
│  │        ├─ routes.cpython-312.pyc
│  │        ├─ routes.cpython-313.pyc
│  │        ├─ schemas.cpython-312.pyc
│  │        ├─ schemas.cpython-313.pyc
│  │        ├─ service.cpython-312.pyc
│  │        └─ service.cpython-313.pyc
│  ├─ pytest.ini
│  ├─ requirements.txt
│  ├─ scripts
│  │  ├─ auto_export_db.py
│  │  └─ updated_lms.sql
│  ├─ shared
│  │  ├─ mail.py
│  │  ├─ websocket_manager.py
│  │  └─ __pycache__
│  │     ├─ mail.cpython-312.pyc
│  │     ├─ mail.cpython-313.pyc
│  │     └─ websocket_manager.cpython-313.pyc
│  ├─ storage
│  │  └─ students_uploads
│  │     ├─ students_assignments
│  │     │  ├─ SID2_20260204_120529_new_cover.docx
│  │     │  ├─ SID2_20260204_135331_signup_view.PNG
│  │     │  ├─ SID3_20260204_120727_new_cover.docx
│  │     │  ├─ SID4_20260204_135820_add_view_st.PNG
│  │     │  └─ SID_2_20261008_161308_Python_AI_ML_Developer.pdf
│  │     ├─ students_fyp_proposal
│  │     │  ├─ SID_100_AI_Interns_Learning_Series_Workshop_02_1.pdf
│  │     │  ├─ SID_100_DOC-20260812-WA0002.pdf
│  │     │  ├─ SID_2_20261008_160923_Attendance_Report.pdf
│  │     │  ├─ SID_2_20261107_131656_Week_3_Asymptotic_Notations_Student_Notes.pdf
│  │     │  ├─ SID_2_ccp_seo_project.pdf
│  │     │  ├─ SID_2_GEOAI_Guradian_Report.pdf
│  │     │  ├─ SID_2_Muhammad_Khurram_CV_Original.pdf
│  │     │  ├─ SID_2_Profile.pdf
│  │     │  ├─ SID_2_PROJECT_REPORT-osama-new.pdf
│  │     │  ├─ SID_2_res.pdf
│  │     │  ├─ SID_2_test2.jpg
│  │     │  ├─ SID_3_portfolio-cv.pdf
│  │     │  ├─ SID_4_Leadership_Manager_as_a_Leader.pdf
│  │     │  ├─ SID_4_Manager_as_a_Decision_Maker.pdf
│  │     │  ├─ SID_4_Motivation_and_Its_Concept.pdf
│  │     │  ├─ SID_4_Organizational_Structure_and_Design.pdf
│  │     │  ├─ SID_4_Strategic_Management.pdf
│  │     │  ├─ SID_5_COA_CCP_sol.pdf
│  │     │  ├─ SID_7_20261002_134647_GEOAI_Guradian_Report.pdf
│  │     │  ├─ SID_7_20261002_135108_GEOAI_Guradian_Report.pdf
│  │     │  ├─ SID_7_20261002_135334_GEOAI_Guradian_Report.pdf
│  │     │  ├─ SID_7_20261002_140309_fine_report.pdf
│  │     │  └─ SID_8_lecture_1.pdf
│  │     ├─ students_quizes
│  │     │  ├─ SID2_20260204_151638_login_view.PNG
│  │     │  ├─ SID3_20260204_121554_Student_Management_System_Report_Project.docx
│  │     │  ├─ SID4_20260204_135954_home_view.PNG
│  │     │  └─ SID_2_20261008_161413_InfinityWave_internship_certificate.pdf
│  │     └─ voucher_pics
│  │        ├─ student_100_back_Screenshot_from_2026-08-27_17-15-29.png
│  │        ├─ student_100_front_Screenshot_from_2026-08-27_17-01-24.png
│  │        ├─ student_13_back_analyze_api_response.png
│  │        ├─ student_13_front_project_tree.png
│  │        ├─ student_2_back_2026-02-26-152910.jpg
│  │        ├─ student_2_back_2026-02-26-152934.jpg
│  │        ├─ student_2_back_analyze_api_response.png
│  │        ├─ student_2_back_Capture001.png
│  │        ├─ student_2_back_geojson_api_response.png
│  │        ├─ student_2_back_IMG_0874.jpeg
│  │        ├─ student_2_back_IMG_0895.jpeg
│  │        ├─ student_2_back_IMG_1297.jpeg
│  │        ├─ student_2_back_map_visualization.png
│  │        ├─ student_2_back_project_tree.png
│  │        ├─ student_2_back_Screenshot_2026-09-14_184408.png
│  │        ├─ student_2_back_Screenshot_2026-09-16_175806.png
│  │        ├─ student_2_back_Screenshot_2026-09-16_181159.png
│  │        ├─ student_2_back_Screenshot_2026-09-16_181442.png
│  │        ├─ student_2_back_Screenshot_2026-09-19_203515.png
│  │        ├─ student_2_back_Screenshot_from_2026-08-26_14-01-26.png
│  │        ├─ student_2_back_test5.jpg
│  │        ├─ student_2_back_test6.jpg
│  │        ├─ student_2_back_tuition_receipt.jpg
│  │        ├─ student_2_front_2026-02-26-152934.jpg
│  │        ├─ student_2_front_analyze_api_response.png
│  │        ├─ student_2_front_Capture001.png
│  │        ├─ student_2_front_fayvo.jpeg
│  │        ├─ student_2_front_geojson_api_response.png
│  │        ├─ student_2_front_IMG_0833_1.jpeg
│  │        ├─ student_2_front_IMG_1297.jpeg
│  │        ├─ student_2_front_IMG_1517.jpeg
│  │        ├─ student_2_front_map_visualization.png
│  │        ├─ student_2_front_Screenshot_2026-09-14_184408.png
│  │        ├─ student_2_front_Screenshot_2026-09-14_190312.png
│  │        ├─ student_2_front_Screenshot_2026-09-16_175618.png
│  │        ├─ student_2_front_Screenshot_2026-09-17_203316.png
│  │        ├─ student_2_front_Screenshot_2026-09-18_190813.png
│  │        ├─ student_2_front_Screenshot_2026-09-20_130413.png
│  │        ├─ student_2_front_Screenshot_from_2026-04-01_16-03-18.png
│  │        ├─ student_2_front_Screenshot_from_2026-08-26_14-25-11.png
│  │        ├─ student_2_front_Screenshot_from_2026-08-26_21-25-50.png
│  │        ├─ student_2_front_test4.jpg
│  │        └─ student_2_front_test8.jpg
│  ├─ tests
│  │  ├─ confest.py
│  │  ├─ integration
│  │  │  ├─ test_access_control.py
│  │  │  └─ __pycache__
│  │  │     └─ test_access_control.cpython-312-pytest-9.2.0.pyc
│  │  ├─ smoke
│  │  │  ├─ test_imports.py
│  │  │  └─ __pycache__
│  │  │     └─ test_imports.cpython-312-pytest-9.2.0.pyc
│  │  └─ unit
│  │     ├─ test_auth.py
│  │     ├─ test_student_service.py
│  │     └─ __pycache__
│  │        ├─ test_auth.cpython-312-pytest-9.2.0.pyc
│  │        └─ test_student_service.cpython-312-pytest-9.2.0.pyc
│  ├─ updated_lms.sql
│  └─ web
│     ├─ static
│     │  ├─ css
│     │  │  ├─ admin_css
│     │  │  │  ├─ dashboard.css
│     │  │  │  └─ sidebar.css
│     │  │  ├─ admit_card.css
│     │  │  ├─ base_style.css
│     │  │  ├─ global_style.css
│     │  │  ├─ help_desk.css
│     │  │  ├─ semester_freeze.css
│     │  │  ├─ students_module.css
│     │  │  ├─ student_profile.css
│     │  │  ├─ suggesstion_style.css
│     │  │  ├─ teachers_module.css
│     │  │  └─ teacher_view.css
│     │  ├─ images
│     │  │  ├─ login_view.jpg
│     │  │  ├─ logo.jpg
│     │  │  └─ main_view.jpg
│     │  └─ js
│     │     ├─ fyp_chat.js
│     │     ├─ fyp_management.js
│     │     ├─ notifications.js
│     │     └─ teacher_fyp_chat.js
│     └─ templates
│        ├─ admin
│        │  ├─ admin_dashboard.html
│        │  ├─ admin_edit.html
│        │  ├─ admin_login.html
│        │  ├─ admin_notifications.html
│        │  ├─ admin_profile.html
│        │  ├─ assign_classes.html
│        │  ├─ class_timetable.html
│        │  ├─ complaints.html
│        │  ├─ course_attendance.html
│        │  ├─ course_registration.html
│        │  ├─ exam_dates.html
│        │  ├─ fee_management.html
│        │  ├─ fyp_proposals.html
│        │  ├─ get_proposals.html
│        │  ├─ help_desk.html
│        │  ├─ manage_attendance.html
│        │  ├─ manage_grades.html
│        │  ├─ promote_students.html
│        │  ├─ register_student.html
│        │  ├─ salary_record.html
│        │  ├─ stSemester_freeze.html
│        │  ├─ stSummer_semester.html
│        │  ├─ system_controls.html
│        │  ├─ system_settings.html
│        │  └─ view_teachers.html
│        ├─ auth
│        │  ├─ main_view.html
│        │  ├─ otp_verify.html
│        │  ├─ send_reset_email.html
│        │  ├─ update_password.html
│        │  └─ user_signup.html
│        ├─ chatbot
│        │  └─ chat_widget.html
│        ├─ layouts
│        │  ├─ admin_base.html
│        │  ├─ student_base.html
│        │  └─ teacher_base.html
│        ├─ student
│        │  ├─ complaint_suggestion.html
│        │  ├─ course_registeration.html
│        │  ├─ fail_subjects.html
│        │  ├─ help_desk.html
│        │  ├─ hostel_view.html
│        │  ├─ improvement_subject.html
│        │  ├─ my_submissions.html
│        │  ├─ notifications.html
│        │  ├─ semester_freeze.html
│        │  ├─ student_dashboard.html
│        │  ├─ student_fee.html
│        │  ├─ student_fyp.html
│        │  ├─ student_login.html
│        │  ├─ student_profile.html
│        │  ├─ summer_semester.html
│        │  ├─ summer_subjects.html
│        │  ├─ upload_fee.html
│        │  ├─ view_attendence.html
│        │  └─ view_grades.html
│        └─ teacher
│           ├─ class_attendance.html
│           ├─ class_structure.html
│           ├─ fyp_management.html
│           ├─ generate_result.html
│           ├─ marked_attendance.html
│           ├─ teacher_complaint.html
│           ├─ teacher_dashboard.html
│           ├─ teacher_login.html
│           ├─ teacher_profile.html
│           └─ view_submissions.html
└─ README.md

```