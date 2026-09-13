
```
LMS-PythonDevelopment
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
│        │  ├─ SID_2_ccp_seo_project.pdf
│        │  ├─ SID_2_Muhammad_Khurram_CV_Original.pdf
│        │  ├─ SID_2_Profile.pdf
│        │  ├─ SID_2_PROJECT_REPORT-osama-new.pdf
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
│           ├─ student_2_back_students_view.PNG
│           ├─ student_2_front_dep_view.PNG
│           ├─ student_3_back_2nd_design_1st_part.PNG
│           ├─ student_3_back_ChatGPT_Image_Jul_31_2025_03_17_32_PM.png
│           ├─ student_3_front_1st_design_1st_part.PNG
│           ├─ student_3_front_WhatsApp_Image_2025-08-06_at_12.31.57_PM_1.jpeg
│           ├─ student_4_back_prj.PNG
│           └─ student_4_front_contact.PNG
├─ students_module
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