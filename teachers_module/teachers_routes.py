from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from utils.auth import login_required ,teacher_required
from .teachers_models import TeacherModel,Notifications,ActivityModel
import datetime
import MySQLdb.cursors
from utils.db import mysql

teacher =Blueprint('teacher', __name__, template_folder='teachers_views')

# @teacher.before_request
# def track_student_activity():
#     teacher_id=session.get('teacher_id')
#     if not teacher_id:
#         return
    
#     if request.path.startswith('/static'):
#         return
    
#     log_id=session.pop('current_log_id',None)

#     if log_id:
#         ActivityModel.log_exit(log_id)

#     new_log_id=ActivityModel.log_enter(
#         teacher_id=teacher_id,
#         page_name=request.endpoint or request.path,
#         page_url=request.path,
#         ip_address=request.remote_addr
#     )
#     session['current_log_id']=new_log_id


# @teacher.route('/track_exit',methods=['POST'])
# def track_exit():
#     log_id=session.pop('current_log_id',None)

#     if log_id:
#         ActivityModel.log_exit(log_id)
#     return '',204


@teacher.route('/teacher_login',methods=['GET','POST'])
def teacher_login():
    try:
        if request.method=='POST':
            email=request.form.get('email')
            password=request.form.get('password')
            print("Email: ",email)
            print("Password: ",password)
            user_data,logged_user=TeacherModel.get_by_email(email)
            
            if user_data and check_password_hash(logged_user['password'],password):
                session.update({
                    'user_id':logged_user['user_id'], 
                    'role':'teacher', 
                    'teacher_id':user_data['teacher_id']
                })
                return redirect(url_for('teacher.teacher_dashboard'))
            else:
                flash("Invalid email or password","danger")
                return redirect(url_for('teacher.teacher_login'))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return redirect(url_for('teacher.teacher_login'))
            
    return render_template('teacher_login.html')



@teacher.route('/teacher_profile')
@teacher_required
def teacher_profile():
    if session.get('role') != 'teacher': 
        return redirect(url_for('main_view'))
    
    details=TeacherModel.get_profile(session['teacher_id'])
    return render_template('teacher_profile.html',teacher_details=details)



@teacher.route('/teacher_dashboard')
@teacher_required
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('main_view'))
        
    tid=session.get('teacher_id')
    today=datetime.datetime.now().strftime('%A')
    
    full_schedule=TeacherModel.get_full_schedule(tid)
    today_list=[row for row in full_schedule if row['day_of_week']==today]
    
    active_notifications=Notifications.get_active_notifications(session['user_id'],'teacher')
    return render_template('teacher_dashboard.html', 
                           full_schedule=full_schedule, 
                           today_schedule=today_list, 
                           today_name=today,active_notifications=active_notifications)



@teacher.route("/class_attendance")
@teacher_required
def class_attendance():
    tid=session.get('teacher_id')
    today=datetime.datetime.now().strftime('%A')
    
    full_schedule=TeacherModel.get_full_schedule(tid)
    today_list=[row for row in full_schedule if row['day_of_week']==today]
    
    return render_template('class_attendance.html', 
                           full_schedule=full_schedule, 
                           today_schedule=today_list, 
                           today_name=today)



@teacher.route("/marked_attendance/<int:section_id>", methods=['GET', 'POST'])
@teacher_required
def marked_attendance(section_id):
    meta=TeacherModel.get_attendance_meta(section_id)
    if not meta: 
        return "Error: Schedule not found."

    cur_date=request.form.get('attendance_date') or request.args.get('date') or str(datetime.date.today())
    already_marked=TeacherModel.check_attendance_marked(meta['course_schedule_id'], cur_date)

    if request.method=='POST':
        if already_marked: 
            return "Error: Attendance already marked for this date."
            
        students=TeacherModel.get_student_list_for_attendance(section_id, meta['course_id'])
        
        batch_data=[
            (
                s['student_course_id'], 
                meta['course_schedule_id'], 
                cur_date, 
                request.form.get(f"status_{s['student_course_id']}", "Absent"), 
                s['student_id']
            ) for s in students
        ]
        
        TeacherModel.save_bulk_attendance(batch_data)
        TeacherModel.save_course_attendance_log(
            teacher_id=session.get('teacher_id'),
            course_id=meta['course_id'],
            course_schedule_id=meta['course_schedule_id'],
            attendance_date=cur_date,
            semester=meta['semester'],
            attendance_data=batch_data
        )
        return redirect(url_for('teacher.class_attendance'))

    student_list=TeacherModel.get_student_list_for_attendance(section_id,meta['course_id'])
    return render_template('marked_attendance.html', 
                           course_name=meta['course_name'], 
                           students=student_list, 
                           attendance_date=cur_date, 
                           already_marked=already_marked, 
                           section_id=section_id)





@teacher.route("/class_structure/<int:section_id>")
@teacher_required
def class_structure(section_id):
    info=TeacherModel.get_class_structure(section_id)
    return render_template('class_structure.html',class_info=info)



@teacher.route("/generate_result/<int:section_id>",methods=['GET', 'POST'])
@teacher_required
def generate_result(section_id):
    if session.get('role') != 'teacher':
        return redirect(url_for('main_view'))
    
    teacher_id=session.get('teacher_id')
    if not TeacherModel.is_section_owned_by_teacher(section_id, teacher_id):
        flash('Unauthorized. This section does not belong to you.', 'danger')
        return redirect(url_for('teacher.teacher_dashboard'))
    details=TeacherModel.get_attendance_meta(section_id) 
    
    if request.method=='POST':
        students=TeacherModel.get_student_list_for_attendance(section_id, details['course_id'])
        
        for stud in students:
            sid=stud['student_id']
            if request.form.get(f'sessional_{sid}'):
                s=int(request.form.get(f'sessional_{sid}', 0))
                m=int(request.form.get(f'mids_{sid}', 0))
                f=int(request.form.get(f'final_{sid}', 0))
                total = s + m + f
                
                if total >= 80: 
                    g='A'
                    gpa=4.0
                elif total >= 70: 
                    g='B'
                    gpa=3.0 
                elif total >= 60: 
                    g='C'
                    gpa=2.0
                elif total >= 50: 
                    g='D'
                    gpa=1.0
                else:
                    g='F'
                    gpa=0.0           
                
                result_data={
                    'sessional':s, 
                    'mids':m, 
                    'final':f, 
                    'total':total, 
                    'grade':g, 
                    'gpa':gpa, 
                    'status':'Pass' if total >= 50 else 'Fail'
                }
                
                TeacherModel.process_student_result(sid,section_id,details['course_id'],details['semester'],result_data)
        
        flash("Results updated successfully!", "success")
        return redirect(url_for('teacher.teacher_dashboard'))

    grading_list=TeacherModel.get_grading_data(details['course_id'],section_id)
    return render_template('generate_result.html',students=grading_list,info=details)




@teacher.route('/fyp_management')
@teacher_required
def fyp_management():
    tid=session.get('teacher_id')
    groups=TeacherModel.get_fyp_groups(tid)
    
    
    for g in groups:
        if g['messages'] and g['messages'][-1]['sender_role']=='student':
            g['has_unread']=True
        else:
            g['has_unread']=False
    
    stats={
        'total': len(groups), 
        'completed': len([g for g in groups if g['status']=='Approved']), 
        'pending': len([g for g in groups if g['status']=='Pending Approval'])
    }
    
    return render_template('fyp_management.html',fyp_data=groups, **stats)


@teacher.route('/approve_fyp/<int:fyp_id>/<string:status>')
@teacher_required
def approve_fyp(fyp_id, status):
    TeacherModel.update_fyp_status(fyp_id, status)
    flash(f'FYP {status} successfully.', 'success')
    return redirect(url_for('teacher.fyp_management'))
    

@teacher.route('/send_message/<int:fyp_id>', methods=['POST'])
@teacher_required
def send_message(fyp_id):
    if session.get('role') != 'teacher': 
        return redirect(url_for('main_view'))
        
    msg_text = request.form.get('message')
    TeacherModel.add_fyp_message(fyp_id, session.get('teacher_id'), msg_text)
    return redirect(url_for('teacher.fyp_management'))



@teacher.route("/view_submissions/<int:section_id>/<string:sub_type>")
@login_required
def view_submissions(section_id,sub_type):
    if session.get('role') != 'teacher':
        return redirect(url_for('main_view'))

    teacher_id=session.get('teacher_id')
    if not TeacherModel.is_section_owned_by_teacher(section_id, teacher_id):
        flash('Unauthorized. This section does not belong to you.', 'danger')
        return redirect(url_for('teacher.teacher_dashboard'))

    subs, meta=TeacherModel.get_submissions_by_type(section_id,sub_type)
    title=f"{meta['course_name']} ({meta['section_name']})" if meta else "Submissions"
    return render_template('view_submissions.html',
                           submissions=subs,
                           sub_type=sub_type,
                           course_name=title,
                           section_id=section_id)



@teacher.route("/mark_submission/<int:submission_id>", methods=['POST'])
@teacher_required
def mark_submission(submission_id):
    marks=request.form.get('marks')
    total=request.form.get('total_marks')
    
    TeacherModel.update_submission_marks(submission_id, marks, total)
    
    return redirect(url_for('teacher.view_submissions', 
                            section_id=request.form.get('section_id'), 
                            sub_type=request.form.get('sub_type')))



@teacher.route("/toggle_upload/<int:section_id>/<string:upload_type>",methods=['POST'])
@login_required
def toggle_upload(section_id, upload_type):
    if session.get('role') != 'teacher':
        return redirect(url_for('main_view'))

    teacher_id=session.get('teacher_id')
    if not TeacherModel.is_section_owned_by_teacher(section_id, teacher_id):
        flash('Unauthorized. This section does not belong to you.', 'danger')
        return redirect(url_for('teacher.teacher_dashboard'))

    TeacherModel.toggle_upload_status(section_id, upload_type)
    flash(f"{upload_type.capitalize()} status updated.", 'success')
    return redirect(url_for('teacher.teacher_dashboard'))


@teacher.route('/complaint_suggestion', methods=['GET', 'POST'])
@teacher_required
def complaint_suggestion():
    if request.method=='POST':
        title=request.form['title']
        description=request.form['description']
        user_id=session['user_id']
        TeacherModel.insert_complaint_suggestion(title, description, user_id)
        return redirect(url_for('teacher.teacher_dashboard'))
    return render_template('complaint_suggestion.html')    



@teacher.route('/set_submission_status/<int:submission_id>/<string:status>',methods=['POST'])
@login_required
def set_submission_status(submission_id,status):
    cursor=mysql.connection.cursor()
    section_id=request.form.get('section_id')
    sub_type =request.form.get('sub_type')
    cursor.execute('UPDATE student_submissions SET submission_status=%s WHERE submission_id=%s',
                   (status, submission_id))
    mysql.connection.commit()
    
    flash(f'Status set to {status}.', 'success')
    return redirect(url_for('teacher.view_submissions',section_id=section_id,sub_type=sub_type))