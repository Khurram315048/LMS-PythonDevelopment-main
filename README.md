
```
LMS-PythonDevelopment-main
├─ admin
│  ├─ admin_models.py
│  ├─ admin_routes.py
│  └─ admin_views
│     ├─ admin_dashboard.html
│     ├─ admin_edit.html
│     ├─ admin_login.html
│     ├─ admin_notifications.html
│     ├─ admin_profile.html
│     ├─ assign_classes.html
│     ├─ class_timetable.html
│     ├─ complaints.html
│     ├─ course_attendance.html
│     ├─ course_registration.html
│     ├─ exam_dates.html
│     ├─ fee_management.html
│     ├─ fyp_proposals.html
│     ├─ get_proposals.html
│     ├─ help_desk.html
│     ├─ manage_attendance.html
│     ├─ manage_grades.html
│     ├─ promote_students.html
│     ├─ register_student.html
│     ├─ salary_record.html
│     ├─ stSemester_freeze.html
│     ├─ stSummer_semester.html
│     ├─ student_log.html
│     ├─ system_controls.html
│     ├─ system_settings.html
│     ├─ teacher_log.html
│     └─ view_teachers.html
├─ auto_export_db.py
├─ config.py
├─ main.py
├─ models.py
├─ README.md
├─ requirements.txt
├─ static
│  ├─ css
│  │  ├─ admin_css
│  │  │  ├─ dashboard.css
│  │  │  └─ sidebar.css
│  │  ├─ admit_card.css
│  │  ├─ base_style.css
│  │  ├─ global_style.css
│  │  ├─ help_desk.css
│  │  ├─ semester_freeze.css
│  │  ├─ students_module.css
│  │  ├─ student_profile.css
│  │  ├─ suggesstion_style.css
│  │  ├─ teachers_module.css
│  │  └─ teacher_view.css
│  ├─ images
│  │  ├─ login_view.jpg
│  │  ├─ logo.jpg
│  │  └─ main_view.jpg
│  ├─ js
│  │  ├─ fyp_management.js
│  │  └─ notifications.js
│  └─ uploads
│     └─ students_uploads
│        ├─ students_assignments
│        │  ├─ SID2_20260204_120529_new_cover.docx
│        │  ├─ SID2_20260204_135331_signup_view.PNG
│        │  ├─ SID3_20260204_120727_new_cover.docx
│        │  └─ SID4_20260204_135820_add_view_st.PNG
│        ├─ students_fyp_proposal
│        │  ├─ SID_100_AI_Interns_Learning_Series_Workshop_02_1.pdf
│        │  ├─ SID_100_DOC-20260812-WA0002.pdf
│        │  ├─ SID_2_ccp_seo_project.pdf
│        │  ├─ SID_2_GEOAI_Guradian_Report.pdf
│        │  ├─ SID_2_Muhammad_Khurram_CV_Original.pdf
│        │  ├─ SID_2_Profile.pdf
│        │  ├─ SID_2_PROJECT_REPORT-osama-new.pdf
│        │  ├─ SID_2_res.pdf
│        │  ├─ SID_3_portfolio-cv.pdf
│        │  ├─ SID_4_Leadership_Manager_as_a_Leader.pdf
│        │  ├─ SID_4_Manager_as_a_Decision_Maker.pdf
│        │  ├─ SID_4_Motivation_and_Its_Concept.pdf
│        │  ├─ SID_4_Organizational_Structure_and_Design.pdf
│        │  ├─ SID_4_Strategic_Management.pdf
│        │  ├─ SID_5_COA_CCP_sol.pdf
│        │  └─ SID_8_lecture_1.pdf
│        ├─ students_quizes
│        │  ├─ SID2_20260204_151638_login_view.PNG
│        │  ├─ SID3_20260204_121554_Student_Management_System_Report_Project.docx
│        │  └─ SID4_20260204_135954_home_view.PNG
│        └─ voucher_pics
│           ├─ student_100_back_Screenshot_from_2026-08-27_17-15-29.png
│           ├─ student_100_front_Screenshot_from_2026-08-27_17-01-24.png
│           ├─ student_2_back_2026-02-26-152910.jpg
│           ├─ student_2_back_2026-02-26-152934.jpg
│           ├─ student_2_back_analyze_api_response.png
│           ├─ student_2_back_IMG_0874.jpeg
│           ├─ student_2_back_IMG_0895.jpeg
│           ├─ student_2_back_IMG_1297.jpeg
│           ├─ student_2_back_project_tree.png
│           ├─ student_2_back_Screenshot_2026-09-14_184408.png
│           ├─ student_2_back_Screenshot_2026-09-16_175806.png
│           ├─ student_2_back_Screenshot_from_2026-08-26_14-01-26.png
│           ├─ student_2_back_tuition_receipt.jpg
│           ├─ student_2_front_2026-02-26-152934.jpg
│           ├─ student_2_front_fayvo.jpeg
│           ├─ student_2_front_geojson_api_response.png
│           ├─ student_2_front_IMG_0833_1.jpeg
│           ├─ student_2_front_IMG_1297.jpeg
│           ├─ student_2_front_IMG_1517.jpeg
│           ├─ student_2_front_map_visualization.png
│           ├─ student_2_front_Screenshot_2026-09-14_184408.png
│           ├─ student_2_front_Screenshot_2026-09-16_175618.png
│           ├─ student_2_front_Screenshot_from_2026-04-01_16-03-18.png
│           ├─ student_2_front_Screenshot_from_2026-08-26_14-25-11.png
│           └─ student_2_front_Screenshot_from_2026-08-26_21-25-50.png
├─ students_module
│  ├─ logs
│  │  └─ students_errors.json
│  ├─ log_helper.py
│  ├─ schema.py
│  ├─ students_models.py
│  ├─ students_routes.py
│  ├─ students_views
│  │  ├─ complaint_suggestion.html
│  │  ├─ course_registeration.html
│  │  ├─ fail_subjects.html
│  │  ├─ help_desk.html
│  │  ├─ hostel_view.html
│  │  ├─ improvement_subject.html
│  │  ├─ my_submissions.html
│  │  ├─ notifications.html
│  │  ├─ semester_freeze.html
│  │  ├─ student_dashboard.html
│  │  ├─ student_fee.html
│  │  ├─ student_fyp.html
│  │  ├─ student_login.html
│  │  ├─ student_profile.html
│  │  ├─ summer_semester.html
│  │  ├─ summer_subjects.html
│  │  ├─ upload_fee.html
│  │  ├─ view_attendence.html
│  │  └─ view_grades.html
│  └─ __init__.py
├─ teachers_module
│  ├─ schema.py
│  ├─ teachers_models.py
│  ├─ teachers_routes.py
│  ├─ teachers_views
│  │  ├─ class_attendance.html
│  │  ├─ class_structure.html
│  │  ├─ complaint_suggestion.html
│  │  ├─ fyp_management.html
│  │  ├─ generate_result.html
│  │  ├─ marked_attendance.html
│  │  ├─ teacher_dashboard.html
│  │  ├─ teacher_login.html
│  │  ├─ teacher_profile.html
│  │  └─ view_submissions.html
│  └─ __init__.py
├─ templates
│  ├─ layouts
│  │  ├─ admin_base.html
│  │  ├─ student_base.html
│  │  └─ teacher_base.html
│  ├─ main_view.html
│  ├─ reset_password.html
│  └─ user_signup.html
├─ updated_lms.sql
└─ utils
   ├─ auth.py
   ├─ db.py
   └─ __init__.py

```