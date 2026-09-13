import MySQLdb
import MySQLdb.cursors
from utils.db import mysql 
import datetime

class UserModel:
    @staticmethod
    def get_user_by_email(email):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT user_id,password,role_id FROM users WHERE email=%s',(email,))
        user=cursor.fetchone()
        cursor.close()
        return user


    @staticmethod
    def create_user(email,password_hash):
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO users(email,password) VALUES (%s,%s)',(email,password_hash))
        mysql.connection.commit()
        user_id=cursor.lastrowid
        cursor.close()
        return user_id


class StudentModel:
    @staticmethod
    def get_student_by_user_id(user_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM students WHERE user_id=%s AND is_deleted=%s',(user_id,0,))
        student=cursor.fetchone()
        cursor.close()
        return student


    @staticmethod
    def get_student_by_id(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM students WHERE student_id=%s AND is_deleted=%s',(student_id,0,))
        student=cursor.fetchone()
        cursor.close()
        return student


    @staticmethod
    def get_student_name_by_user_id(user_id):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT first_name,last_name,student_id FROM students WHERE user_id=%s',(user_id,))
        student_name=cursor.fetchone()
        cursor.close()
        return student_name


    @staticmethod
    def get_student_program_details(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT program_id FROM students WHERE student_id=%s',(student_id,))
        student=cursor.fetchone()
        if student and student['program_id']:
            cursor.execute('SELECT * FROM programs WHERE program_id=%s',(student['program_id'],))
            program=cursor.fetchone()
            cursor.close()
            return program
        cursor.close()
        return None


    @staticmethod
    def get_enrolled_courses_by_student_id(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""SELECT DISTINCT c.course_id,c.course_name,c.credit_hours
            FROM student_course sc
            JOIN courses c ON sc.course_id=c.course_id
            WHERE sc.student_id=%s 
            AND sc.is_deleted=0 
            AND c.is_deleted=0 """,(student_id,))
        courses=cursor.fetchall()
        cursor.close()
        return courses


    @staticmethod
    def get_course_details_by_ids(course_ids):
        if not course_ids:
            return []
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        course_placeholders= ','.join(['%s'] * len(course_ids))
        cursor.execute(f'''
            SELECT course_id,course_name
            FROM courses
            WHERE course_id IN ({course_placeholders})
        ''', tuple(course_ids))
        course_data=cursor.fetchall()
        cursor.close()
        return course_data


    @staticmethod
    def get_teachers_by_course_ids(course_ids):
        if not course_ids:
            return []
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        course_placeholders=','.join(['%s'] * len(course_ids))
        cursor.execute(f'''
            SELECT course_id,teacher_id
            FROM teacher_course
            WHERE course_id IN ({course_placeholders}) AND is_deleted=0''', tuple(course_ids))
        teacher_rows=cursor.fetchall()
        cursor.close()
        return teacher_rows


    @staticmethod
    def get_teacher_info_by_ids(teacher_ids):
        if not teacher_ids:
            return []
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        teacher_placeholders=','.join(['%s'] * len(teacher_ids))
        cursor.execute(f'''
            SELECT teacher_id,first_name,last_name
            FROM teachers
            WHERE teacher_id IN ({teacher_placeholders}) AND is_deleted=0
        ''', tuple(teacher_ids))
        teacher_data=cursor.fetchall()
        cursor.close()
        return teacher_data

    

    @staticmethod
    def get_course_schedule_by_course_ids(course_ids):
        if not course_ids:
            return []

        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        placeholder= ', '.join(['%s'] * len(course_ids))
        query=f"""SELECT cs.*,s.assignments_enabled,s.quizzes_enabled
        FROM course_schedule cs
        JOIN sections s ON cs.section_id=s.section_id
        WHERE cs.course_id IN ({placeholder})"""
        cursor.execute(query,tuple(course_ids))
        schedule=cursor.fetchall()
        cursor.close()
        return schedule



    @staticmethod
    def get_course_schedule_for_enrolled_sections(course_ids,student_id):
        if not course_ids:
            return []
    
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        placeholders=', '.join(['%s'] * len(course_ids))
        query=f"""SELECT DISTINCT cs.course_id,cs.section_id,
         cs.day_of_week,cs.start_time,cs.end_time,
          cs.location,s.assignments_enabled,s.quizzes_enabled,
           s.section_name
            FROM course_schedule cs
             JOIN sections s ON cs.section_id=s.section_id
              JOIN student_section ss ON s.section_id=ss.section_id
               WHERE cs.course_id IN ({placeholders})
                AND ss.student_id=%s AND cs.is_deleted=0 AND s.is_deleted=0 """
        params=list(course_ids)
        params.append(student_id)
    
        cursor.execute(query, tuple(params))
        schedule=cursor.fetchall()
        cursor.close()
        return schedule



    @staticmethod
    def get_student_fee_records(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query="""
        SELECT p.program_name AS program,
            sf.update_date AS paid_date,sf.fee_month AS month,
            sf.fee_amount AS fee_amount,sf.voucher_front_pic AS front_voucher,
            sf.voucher_back_pic AS back_voucher,DATE(sf.update_date) AS fee_paid_at,
            sf.fee_status AS status
        FROM student_fees sf
        JOIN programs p ON sf.program_id=p.program_id
        WHERE sf.student_id=%s AND sf.is_deleted=0"""
        cursor.execute(query,(student_id,))
        fee_records=cursor.fetchall()
        cursor.close()
        return fee_records


    @staticmethod
    def insert_complaint_suggestion(title,description,user_id):
        cursor=mysql.connection.cursor()
        cursor.execute('INSERT INTO complaint_suggestion(title,description,user_id) VALUES (%s,%s,%s)',(title,description,user_id))
        mysql.connection.commit()
        cursor.close()


    @staticmethod
    def get_complaint_status(user_id):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * FROM complaint_suggestion WHERE user_id=%s',(user_id,))
        status=cursor.fetchall()
        cursor.close()
        return status
            


    @staticmethod
    def insert_submission(student_id,course_id,section_id,file_path,submission_type):
        cursor=mysql.connection.cursor()
        query="""
            INSERT INTO student_submissions 
            (student_id,course_id,section_id,file_path,submission_type)
            VALUES (%s,%s,%s,%s,%s)
        """
        cursor.execute(query,(student_id,course_id,section_id,file_path,submission_type))
        mysql.connection.commit()
        cursor.close()  


    @staticmethod
    def get_all_submissions(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query="""
            SELECT sub.*, c.course_name
            FROM student_submissions sub
            JOIN courses c ON sub.course_id=c.course_id
            WHERE sub.student_id=%s
            ORDER BY sub.upload_date DESC
        """
        cursor.execute(query,(student_id,))
        submissions=cursor.fetchall()
        cursor.close()
        return submissions


    @staticmethod
    def get_student_submission_status(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query="""
            SELECT course_id,submission_type,marks,total_marks 
            FROM student_submissions 
            WHERE student_id=%s
        """
        cursor.execute(query,(student_id,))
        submissions=cursor.fetchall()
        cursor.close()
        return submissions     


    @staticmethod
    def upload_fee_voucher(student_id,program_id,month,fee_amount,front_path,back_path):
        cursor=mysql.connection.cursor()
        cursor.execute('''
            INSERT INTO student_fees(fee_amount,fee_status,update_date,voucher_front_pic,
            voucher_back_pic,program_id,fee_month,student_id,is_deleted)
            VALUES(%s,%s,NOW(),%s,%s,%s,%s,%s,%s)''',
            (fee_amount,'due',front_path,back_path,program_id,month,student_id,0))
        mysql.connection.commit()
        cursor.close()



    @staticmethod
    def get_student_courses_for_attendance(student_id):
        cursor=mysql.connection.cursor()
        cursor.execute('''
            SELECT sc.student_course_id,c.course_name,c.credit_hours
            FROM student_course sc
            JOIN courses c ON sc.course_id=c.course_id
            WHERE sc.student_id=%s
        ''', (student_id,))
        courses=cursor.fetchall()
        cursor.close()
        return courses



    @staticmethod
    def get_course_schedule_for_student_course(student_course_id):
        cursor=mysql.connection.cursor()
        cursor.execute('''
            SELECT cs.course_schedule_id
            FROM course_schedule cs
            JOIN student_course sc ON cs.course_id=sc.course_id
            WHERE sc.student_course_id=%s
        ''', (student_course_id,))
        schedule=cursor.fetchone()
        cursor.close()
        return schedule



    @staticmethod
    def get_attendance_summary(student_course_id):
        cursor=mysql.connection.cursor()
        cursor.execute('''
        SELECT COUNT(*) AS total
        FROM attendance
        WHERE student_course_id=%s
        ''', (student_course_id,))
        total_lectures_row=cursor.fetchone()

        cursor.execute('''
        SELECT COUNT(*) AS attended
        FROM attendance
        WHERE student_course_id=%s AND attendance_status=%s
        ''', (student_course_id,'Present'))
        attended_row=cursor.fetchone()
        cursor.close()
        return total_lectures_row['total'] if total_lectures_row else 0, \
           attended_row['attended'] if attended_row else 0



    @staticmethod
    def get_attendance_status_details(student_course_id): 
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
        SELECT attendance_date,attendance_status
        FROM attendance
        WHERE student_course_id=%s
        ORDER BY attendance_date ASC
        ''', (student_course_id,))
        lecture_status=cursor.fetchall()
        cursor.close()
        return lecture_status


    @staticmethod
    def get_student_results_with_marks(student_id):
        cursor=mysql.connection.cursor()
        query="""
            SELECT DISTINCT
                sr.student_semester AS semester,
                c.course_name,
                c.credit_hours,
                srm.total_marks,
                srm.student_grade,
                srm.subject_gpa,
                srm.status
            FROM student_results sr
            JOIN student_result_marks srm ON sr.student_result_id=srm.student_result_id
            JOIN student_course sc ON srm.student_course_id=sc.student_course_id
            JOIN courses c ON sc.course_id=c.course_id
            WHERE sr.student_id=%s
        """
        cursor.execute(query, (student_id,))
        all_marks=cursor.fetchall()
        cursor.close()
        return all_marks


    @staticmethod
    def get_improvement_subjects(student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            SELECT si.improvement_id AS id,si.status,'improvement' AS type,c.course_name,c.course_id
            FROM student_improvement si
            JOIN courses c ON si.course_id=c.course_id
            WHERE si.student_id=%s
        """, (student_id,))
        improvements=cursor.fetchall()
        cursor.close()
        return improvements


    @staticmethod
    def get_retake_subjects(student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            SELECT sf.student_fail_id AS id, sf.status, 'retake' AS type,c.course_name,c.course_id
            FROM student_fail_subjects sf
            JOIN courses c ON sf.course_id=c.course_id
            WHERE sf.student_id = %s
        """, (student_id,))
        retakes=cursor.fetchall()
        cursor.close()
        return retakes


    @staticmethod
    def get_existing_improvement_request(student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM student_improvement WHERE student_id=%s",(student_id,))
        existing=cursor.fetchone()
        cursor.close()
        return existing


    @staticmethod
    def get_max_semester_passed(student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT MAX(student_semester) AS max_sem FROM student_results WHERE student_id=%s",(student_id,))
        res=cursor.fetchone()
        cursor.close()
        return int(res['max_sem']) if res and res['max_sem'] else 0


    @staticmethod
    def get_eligible_improvement_courses(student_id,max_semester):
        cursor=mysql.connection.cursor()
        cursor.execute("""SELECT c.course_id,c.course_name,c.credit_hours,
                GROUP_CONCAT(DISTINCT CONCAT(t.first_name, ' ', t.last_name) SEPARATOR ', ') AS teacher_name,
                MIN(s.semester) AS semester
            FROM courses c
            LEFT JOIN teacher_course tc ON c.course_id=tc.course_id AND tc.is_deleted=0
            LEFT JOIN teachers t ON tc.teacher_id=t.teacher_id AND t.is_deleted=0
            LEFT JOIN sections s ON c.course_id=s.course_id AND s.is_deleted=0
            LEFT JOIN student_section ss ON s.section_id=ss.section_id AND ss.is_deleted=0
            LEFT JOIN student_course sc ON c.course_id=sc.course_id AND sc.is_deleted=0
            LEFT JOIN student_result_marks rm ON rm.student_course_id=sc.student_course_id AND rm.is_deleted = 0
            WHERE ss.student_id=%s 
              AND sc.student_id=%s
              AND s.semester BETWEEN 1 AND %s
              AND (rm.student_grade != 'F' OR rm.student_grade IS NULL)  
              AND c.is_deleted=0
            GROUP BY c.course_id,c.course_name,c.credit_hours
            ORDER BY semester ASC
        """, (student_id,student_id,max_semester))
        courses=cursor.fetchall()
        cursor.close()
        return courses


    @staticmethod
    def delete_improvement_subject(improvement_id,student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("DELETE FROM student_improvement WHERE improvement_id=%s AND student_id=%s", (improvement_id,student_id))
        mysql.connection.commit()
        cursor.close()


    @staticmethod
    def add_improvement_subject(student_id,course_id):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO student_improvement(student_id,course_id,status)
            VALUES(%s,%s,%s)
        """,(student_id,course_id,'Pending'))
        mysql.connection.commit()
        cursor.close()



    @staticmethod
    def add_notification(sender_id,sender_role,receiver_id,receiver_role,title,description,related_course_id,status):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO notifications(sender_id,sender_role,receiver_id,receiver_role,title,description,related_course_id,status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (sender_id,sender_role,receiver_id,receiver_role,title,description,related_course_id,status))
        mysql.connection.commit()
        cursor.close()



    @staticmethod
    def get_existing_retake_request(student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT * FROM student_fail_subjects WHERE student_id=%s",(student_id,))
        existing=cursor.fetchone()
        cursor.close()
        return existing



    @staticmethod
    def get_eligible_fail_subjects(student_id,max_semester):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            SELECT c.course_id,c.course_name,c.credit_hours,
                GROUP_CONCAT(DISTINCT CONCAT(t.first_name, ' ',t.last_name) SEPARATOR ', ') AS teacher_name,
                MIN(s.semester) AS semester
            FROM courses c
            LEFT JOIN teacher_course tc ON c.course_id=tc.course_id AND tc.is_deleted=0
            LEFT JOIN teachers t ON tc.teacher_id = t.teacher_id AND t.is_deleted=0
            LEFT JOIN sections s ON c.course_id = s.course_id AND s.is_deleted=0
            LEFT JOIN student_section ss ON s.section_id=ss.section_id AND ss.is_deleted=0
            LEFT JOIN student_course sc ON c.course_id=sc.course_id AND sc.is_deleted=0
            LEFT JOIN student_result_marks rm ON rm.student_course_id=sc.student_course_id AND rm.is_deleted = 0
            WHERE ss.student_id=%s AND sc.student_id=%s 
              AND s.semester BETWEEN 1 AND %s AND rm.student_grade='F'
              AND c.is_deleted=0
            GROUP BY c.course_id,c.course_name,c.credit_hours
            ORDER BY semester ASC
        """, (student_id,student_id,max_semester))
        courses=cursor.fetchall()
        cursor.close()
        return courses


    @staticmethod
    def add_fail_subject(student_id,course_id):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO student_fail_subjects(student_id,course_id,status)
            VALUES(%s,%s,%s)
        """, (student_id,course_id,'Pending'))
        mysql.connection.commit()
        cursor.close()


    @staticmethod
    def delete_fail_subject(fail_id,student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("DELETE FROM student_fail_subjects WHERE student_fail_id=%s AND student_id=%s",(fail_id,student_id))
        mysql.connection.commit()
        cursor.close()


    @staticmethod
    def get_active_semester_freeze_request(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT * FROM semester_freeze_students
            WHERE student_id=%s
            ORDER BY applied_date DESC
            LIMIT 1
        """, (student_id,))
        request=cursor.fetchone()
        cursor.close()
        return request


    @staticmethod
    def get_last_recorded_semester(student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            SELECT rm.student_semester
            FROM student_result_marks rm
            JOIN student_course sc ON rm.student_course_id=sc.student_course_id
            WHERE sc.student_id=%s
            ORDER BY rm.student_result_id DESC
            LIMIT 1
        """, (student_id,))
        result=cursor.fetchone()
        cursor.close()
        return result['student_semester'] if result else None


    @staticmethod
    def add_semester_freeze_request(student_id,semester,reason):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO semester_freeze_students(student_id,semester,reason,status)
            VALUES(%s,%s,%s,'Pending')
        """, (student_id,semester,reason))
        mysql.connection.commit()
        cursor.close()


    @staticmethod
    def get_eligible_summer_failed_subjects(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query="""SELECT c.course_id, c.course_name, c.credit_hours,
                rm.student_semester as semester,
                CONCAT(t.first_name, ' ', t.last_name) AS teacher_name
            FROM student_result_marks rm
            JOIN student_course sc ON rm.student_course_id=sc.student_course_id
            JOIN courses c ON sc.course_id=c.course_id
            LEFT JOIN teacher_course tc ON c.course_id=tc.course_id
            LEFT JOIN teachers t ON tc.teacher_id=t.teacher_id
            WHERE sc.student_id=%s AND rm.student_grade='F'
              AND rm.student_semester = (
                  SELECT MAX(rm2.student_semester) 
                  FROM student_result_marks rm2 
                  JOIN student_course sc2 ON rm2.student_course_id=sc2.student_course_id 
                  WHERE sc2.student_id=%s AND rm2.student_grade= 'F')"""
        cursor.execute(query,(student_id,student_id))
        failed_subjects=cursor.fetchall()
        cursor.close()
        return failed_subjects
 


    @staticmethod
    def get_latest_summer_semester():
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
            SELECT *
            FROM summer_semesters
            ORDER BY summer_semesters_id ASC
            LIMIT 1
        """)
        semester=cursor.fetchone()
        cursor.close()
        return semester  


    @staticmethod
    def get_failed_subjects_for_last_semester(student_id,last_semester):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            SELECT
                c.course_id,
                c.course_name,
                c.credit_hours,
                CONCAT(t.first_name, ' ', t.last_name) AS teacher_name,
                rm.student_semester AS semester
            FROM student_result_marks rm
            JOIN student_course sc ON rm.student_course_id=sc.student_course_id
            JOIN courses c ON sc.course_id=c.course_id
            LEFT JOIN teacher_course tc ON tc.course_id=c.course_id
            LEFT JOIN teachers t ON tc.teacher_id=t.teacher_id
            WHERE sc.student_id=%s
              AND rm.student_semester=%s
              AND rm.status = 'Fail'
        """, (student_id,last_semester))
        subjects=cursor.fetchall()
        cursor.close()
        return subjects

        
    @staticmethod
    def get_system_setting(key):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT setting_value FROM system_settings WHERE setting_key=%s', (key,))
        result=cursor.fetchone()
        cursor.close()
        return result['setting_value'] if result else None

    @staticmethod
    def add_summer_subject(student_id,course_id,summer_semester_id):
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * FROM summer_registration WHERE student_id=%s AND course_id=%s AND summer_semesters_id=%s',
                   (student_id,course_id,summer_semester_id))
        if cursor.fetchone():
            cursor.close()
            return False
        
        cursor.execute('''
            INSERT INTO summer_registration(student_id,course_id,summer_semesters_id,registration_date)
            VALUES (%s,%s,%s, NOW())
            ''',(student_id,course_id,summer_semester_id))
        mysql.connection.commit()
        cursor.close()
        return True


    @staticmethod
    def delete_summer_subject(student_id,course_id,summer_semester_id):
        cursor=mysql.connection.cursor()
        query="DELETE FROM summer_registration WHERE student_id=%s AND course_id=%s AND summer_semesters_id=%s"
        cursor.execute(query,(student_id,course_id,summer_semester_id))
        mysql.connection.commit()
        cursor.close()
        return True


    @staticmethod
    def get_selected_summer_subjects(student_id,summer_semester_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query="""
            SELECT sr.course_id,c.course_name,c.credit_hours,'Summer' as type,'Registered' as status
            FROM summer_registration sr
            JOIN courses c ON sr.course_id=c.course_id
            WHERE sr.student_id=%s AND sr.summer_semesters_id=%s
        """
        cursor.execute(query,(student_id,summer_semester_id))
        selected=cursor.fetchall()
        cursor.close()
        return selected
    

    @staticmethod
    def create_notification(sender_id,sender_role,receiver_role,title,description,related_course_id,status='Pending', receiver_id=None):
        cursor=mysql.connection.cursor()
        if receiver_id:
            cursor.execute("""
                INSERT INTO notifications(sender_id,sender_role,receiver_id,receiver_role,title,description,related_course_id,status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (sender_id,sender_role,receiver_id,receiver_role,title,description,related_course_id,status))
        else:
            cursor.execute("""
                INSERT INTO notifications(sender_id,sender_role,receiver_role,title,description,related_course_id,status)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (sender_id,sender_role,receiver_role,title,description,related_course_id,status))
        mysql.connection.commit()

        cursor.close()


    @staticmethod
    def get_all_teachers():
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT teacher_id,first_name,last_name FROM teachers WHERE is_deleted=0")
        teachers=cursor.fetchall()
        cursor.close()
        return teachers



    @staticmethod
    def get_fyp_by_id_and_student(fyp_id,student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT fyp_id FROM fyp_groups WHERE fyp_id=%s AND student_id=%s",
            (fyp_id, student_id)
            )
        fyp=cursor.fetchone()
        cursor.close()
        return fyp


    @staticmethod
    def get_fyp_project(student_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query="""
            SELECT f.*, t.first_name as t_fname,t.last_name as t_lname
            FROM fyp_groups f
            LEFT JOIN teachers t ON f.teacher_id=t.teacher_id
            WHERE f.student_id=%s
        """
        
        cursor.execute(query,(student_id,))
        fyp=cursor.fetchone()
        cursor.close()
        return fyp


    @staticmethod
    def insert_fyp_proposal(student_id,title,description,teacher_id,filename):
        cursor=mysql.connection.cursor()
        query="""INSERT INTO fyp_groups 
                   (project_title, description,teacher_id,student_id,status,progress,last_submission) 
                   VALUES (%s,%s,%s,%s, 'In Progress',0, %s)"""
        cursor.execute(query, (title,description,teacher_id,student_id,filename))
        mysql.connection.commit()
        cursor.close()    



    @staticmethod
    def get_fyp_messages(fyp_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query="""
            SELECT * FROM fyp_messages 
            WHERE fyp_id=%s 
            ORDER BY created_at ASC
        """
        cursor.execute(query,(fyp_id,))
        messages=cursor.fetchall()
        cursor.close()
        return messages



    @staticmethod
    def insert_fyp_message(fyp_id,student_id,role,message_text):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT teacher_id FROM fyp_groups WHERE fyp_id=%s", (fyp_id,))
        group=cursor.fetchone()
        
        if group:
            teacher_id=group['teacher_id']
            query="""
                INSERT INTO fyp_messages(fyp_id,teacher_id,student_id,sender_role,message)
                VALUES (%s,%s,%s,%s,%s)
            """
            cursor.execute(query, (fyp_id,teacher_id,student_id,role,message_text))
            mysql.connection.commit()
            
        cursor.close()



    @staticmethod
    def update_fyp_data(student_id,title,filename=None):
        cursor=mysql.connection.cursor()
        if filename:
            cursor.execute('SELECT progress FROM fyp_groups WHERE student_id=%s',(student_id,))
            current_progress=cursor.fetchone()['progress']
            new_progress=min(current_progress + 10, 100)
            query="UPDATE fyp_groups SET project_title=%s,last_submission=%s,progress=%s WHERE student_id=%s"
            cursor.execute(query,(title,filename,new_progress,student_id))
        else:
            query="UPDATE fyp_groups SET project_title=%s WHERE student_id=%s"
            cursor.execute(query, (title,student_id))
        
        mysql.connection.commit()
        cursor.close()    



    @staticmethod
    def get_teacher_full_details(teacher_id):
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query ="SELECT teacher_id,first_name,last_name,email,contact_num FROM teachers WHERE teacher_id=%s"
        cursor.execute(query,(teacher_id,))
        teacher=cursor.fetchone()
        cursor.close()
        return teacher   



class NotificationModel:
    @staticmethod
    def get_notifications_for_user(user_id, student_id):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            SELECT * FROM notifications
            WHERE sender_id=%s OR (receiver_role='student' AND receiver_id=%s)
            ORDER BY created_at DESC
        """, (user_id,student_id))
        notifications=cursor.fetchall()
        cursor.close()
        return notifications


    @staticmethod
    def get_active_notifications(user_id,role):
        cursor=mysql.connection.cursor()
        cursor.execute("""
            SELECT id,title,description,created_at
            FROM notifications
            WHERE (receiver_id=%s OR receiver_id IS NULL)
            AND receiver_role=%s
            AND is_deleted=%s
            AND status='Pending'
            """, (user_id,role,0))
        notifications=cursor.fetchall()
        cursor.close()
        return notifications    



# class ActivityModel:

#     @staticmethod
#     def log_enter(student_id,page_name,page_url,ip_address):
#         cursor=mysql.connection.cursor()
#         cursor.execute('''INSERT INTO student_activity_log(student_id,page_name,page_url,entered_at,ip_address)
#                        VALUES(%s,%s,%s,NOW(),%s)''',(student_id,page_name,page_url,ip_address))
#         mysql.connection.commit()
#         return cursor.lastrowid

#     @staticmethod
#     def log_exit(log_id):
#         cursor=mysql.connection.cursor()
#         cursor.execute('''UPDATE student_activity_log
#                        SET exited_at=NOW(),
#                        time_spent_seconds=TIMESTAMPDIFF(SECOND,entered_at,NOW())
#                        WHERE log_id=%s''',(log_id,))
#         mysql.connection.commit()

#     @staticmethod
#     def get_all_activity():
#         cursor=mysql.connection.cursor()
#         cursor.execute('''SELECT sal.log_id,sal.page_name,sal.page_url,sal.entered_at,
#                        sal.exited_at,sal.time_spent_seconds,sal.ip_address,
#                        s.first_name,s.last_name,s.student_id
#                        FROM student_activity_log sal
#                        JOIN students s ON sal.student_id=s.student_id
#                        ORDER BY sal.entered_at DESC''')
#         return cursor.fetchall()

#     @staticmethod
#     def get_activity_by_student(student_id):
#         cursor=mysql.connection.cursor()
#         cursor.execute('''SELECT log_id,page_name,page_url,entered_at,exited_at,time_spent_seconds
#                        FROM student_activity_log
#                        WHERE student_id=%s ORDER BY entered_at DESC''',(student_id,))
#         return cursor.fetchall()

#     @staticmethod
#     def get_page_summary():
#         cursor=mysql.connection.cursor()
#         cursor.execute('''SELECT page_name,COUNT(*) AS total_visits,
#                        AVG(time_spent_seconds) AS avg_seconds,
#                        MAX(time_spent_seconds) AS max_seconds
#                        FROM student_activity_log
#                        WHERE time_spent_seconds IS NOT NULL
#                        GROUP BY page_name ORDER BY total_visits DESC''')
#         return cursor.fetchall()

#     @staticmethod
#     def get_student_page_summary(student_id):
#         cursor=mysql.connection.cursor()
#         cursor.execute('''SELECT page_name,COUNT(*) AS total_visits,
#                        SUM(time_spent_seconds) AS total_seconds,
#                        AVG(time_spent_seconds) AS avg_seconds
#                        FROM student_activity_log
#                        WHERE student_id=%s AND time_spent_seconds IS NOT NULL
#                        GROUP BY page_name ORDER BY total_seconds DESC''',(student_id,))
#         return cursor.fetchall()

#     @staticmethod
#     def get_active_now():
#         cursor=mysql.connection.cursor()
#         cursor.execute('''SELECT sal.log_id,sal.page_name,sal.entered_at,sal.ip_address,
#                        s.first_name,s.last_name,s.student_id
#                        FROM student_activity_log sal
#                        JOIN students s ON sal.student_id=s.student_id
#                        WHERE sal.exited_at IS NULL
#                        ORDER BY sal.entered_at DESC''')
#         return cursor.fetchall()