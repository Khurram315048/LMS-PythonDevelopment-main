import logging
from utils.db import mysql
from datetime import datetime


class UserModel:

    @staticmethod
    def get_by_email(email):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE email=%s AND is_deleted=0 ',(email,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Err during gtbyeml(models): {str(e)}")
            raise
        finally:
            conn.close()


    @staticmethod
    def update_email(user_id,email):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE users SET email=%s WHERE user_id=%s AND is_deleted=0 ',(email,user_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Err during updtemil(model): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


    @staticmethod
    def soft_delete(email):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE users SET is_deleted=%s WHERE email=%s',(1,email))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete user(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()



    @staticmethod
    def create(email,password_hash,role_id):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO users(email,password,role_id) VALUES(%s,%s,%s)',(email,password_hash,role_id))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.exception(f"Error during user create(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()



    @staticmethod
    def email_exists(email):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT user_id FROM users WHERE email=%s AND is_deleted=%s',(email,0))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during email_exists(admin_models): {str(e)}")
            raise
        finally:
            conn.close()



    @staticmethod
    def get_all():
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT us.user_id,us.email,rl.role_type 
                               FROM users us
                               JOIN users_role rl ON us.role_id=rl.role_id WHERE us.is_deleted=%s''',(0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all users(admin_models): {str(e)}")
            raise
        finally:
            conn.close()


class AdminModel:

    @staticmethod
    def get_admin_by_email(email):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM admins WHERE email=%s AND is_deleted=0 ',(email,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during get_by_email admin(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_email_by_user_id(user_id:int):
            try:
                conn=mysql.get_dict_connection()
                with conn.cursor() as cursor:
                    cursor.execute('SELECT email FROM users WHERE user_id=%s AND is_deleted=0',(user_id,))
                    row=cursor.fetchone()
                    return row['email'] if row else None
            except Exception as e:
                logging.exception(f"Error during get email by user id(models): {str(e)}")
                return None
            finally:
                conn.close()        



    @staticmethod
    def get_by_id(admin_id):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM admins WHERE admin_id=%s AND is_deleted=%s',(admin_id,0,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during get_by_id admin(admin_models): {str(e)}")
            raise
        finally:
            conn.close()



    @staticmethod
    def update(admin_id,email,first_name,last_name,contact):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE admins SET email=%s,first_name=%s,last_name=%s,contact=%s WHERE admin_id=%s AND is_deleted=%s',
                               (email,first_name,last_name,contact,admin_id,0))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during update admin(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()



    @staticmethod
    def get_dashboard_counts():
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                keys=['students','teachers','pending_fees','courses','fyp','complaints','freeze','exams','notifications']
                queries=[
                    'SELECT COUNT(*) AS c FROM students WHERE is_deleted=0',
                    'SELECT COUNT(*) AS c FROM teachers WHERE is_deleted=0',
                    "SELECT COUNT(*) AS c FROM student_fees WHERE fee_status='due' ",
                    'SELECT COUNT(*) AS c FROM courses WHERE is_deleted=0',
                    'SELECT COUNT(*) AS c FROM fyp_groups WHERE is_deleted=0',
                    'SELECT COUNT(*) AS c FROM complaint_suggestion',
                    "SELECT COUNT(*) AS c FROM semester_freeze_students WHERE status='Pending'",
                    "SELECT COUNT(*) AS c FROM exams WHERE status='Ongoing' AND is_deleted=0",
                    "SELECT COUNT(*) AS c FROM notifications WHERE status='Pending' AND is_deleted=0",
                ]
                counts={}
                for key,query in zip(keys,queries):
                    cursor.execute(query)
                    counts[key]=cursor.fetchone()['c']
                return counts
        except Exception as e:
            logging.exception(f"Error during get_dashboard_counts(admin_models): {str(e)}")
            raise
        finally:
            conn.close()


class SystemModel:

    @staticmethod
    def get_all_settings():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM system_settings')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all_settings(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def update_setting(setting_key, new_value):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE system_settings SET setting_value=%s WHERE setting_key=%s', (new_value, setting_key))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during update_setting(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class ComplaintModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT cs.*,u.email FROM complaint_suggestion cs
                               JOIN users u ON cs.user_id=u.user_id''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all complaints(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def mark_solved(complt_sugst_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE complaint_suggestion SET is_status=%s WHERE complt_sugst_id=%s', ('Solved', complt_sugst_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during mark_solved(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class StudentModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT ss.*,p.program_name,u.email FROM students ss
                               JOIN programs p ON ss.program_id=p.program_id
                               JOIN users u ON ss.user_id=u.user_id
                               WHERE ss.is_deleted=%s''', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all students(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_by_id(student_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM students WHERE student_id=%s', (student_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during get_by_id student(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_user_id(student_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT user_id FROM students WHERE student_id=%s AND is_deleted=%s', (student_id, 0,))
                return cursor.fetchone()['user_id']
        except Exception as e:
            logging.exception(f"Error during get_user_id student(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_admission_sessions():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT DISTINCT admission_session FROM students WHERE admission_session IS NOT NULL')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_admission_sessions(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def create(user_id, first_name, last_name, email, contact, program_id, admission_session, last_qual, admission_date, current_semester):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO students
                               (user_id,first_name,last_name,contact,email,last_qualification,program_id,admission_session,admission_date,current_semester)
                               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', (user_id, first_name, last_name, contact, email,
                                                                          last_qual, program_id, admission_session,
                                                                          admission_date, current_semester))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during student create(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def update(student_id, first_name, last_name, email, contact, program_id, admission_session, last_qualification, admission_date):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''UPDATE students SET first_name=%s,last_name=%s,email=%s,contact=%s,program_id=%s,
                               admission_session=%s,last_qualification=%s,admission_date=%s WHERE student_id=%s''',
                               (first_name, last_name, email, contact, program_id, admission_session, last_qualification,
                                admission_date, student_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during student update(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def soft_delete(student_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE students SET is_deleted=%s WHERE student_id=%s', (1, student_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete student(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def promote(student_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE students SET current_semester=current_semester+1 WHERE student_id=%s', (student_id,))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during promote student(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_with_results():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT s.student_id,s.first_name,s.last_name,s.current_semester,
                               sr.result_status,sr.overall_gpa,sr.student_semester,p.program_name
                               FROM students s
                               JOIN programs p ON s.program_id=p.program_id
                               LEFT JOIN student_results sr ON s.student_id=sr.student_id
                               AND sr.student_semester=(SELECT MAX(sr2.student_semester) FROM student_results sr2
                               WHERE sr2.student_id=s.student_id)
                               WHERE s.is_deleted=0 ORDER BY s.student_id ASC''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_with_results(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_result_by_id(student_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT result_status,student_semester FROM student_results WHERE student_id=%s ORDER BY student_semester ASC LIMIT 1', (student_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during get_result_by_id(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def count_active():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) AS total FROM students WHERE is_deleted=0')
                return cursor.fetchone()['total']
        except Exception as e:
            logging.exception(f"Error during count_active students(admin_models): {str(e)}")
            raise
        finally:
            conn.close()


class TeacherModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT teacher_id,first_name,last_name,email,contact_num,qualification,joining_date FROM teachers WHERE is_deleted=%s', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all teachers(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_by_id(teacher_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM teachers WHERE teacher_id=%s', (teacher_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during get_by_id teacher(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_user_id(teacher_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT user_id FROM teachers WHERE teacher_id=%s', (teacher_id,))
                return cursor.fetchone()['user_id']
        except Exception as e:
            logging.exception(f"Error during get_user_id teacher(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_courses(teacher_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT c.course_name FROM teacher_course tc
                               JOIN courses c ON tc.course_id=c.course_id
                               WHERE tc.teacher_id=%s AND tc.is_deleted=%s''', (teacher_id, 0))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_courses(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def email_exists(email):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT email FROM teachers WHERE email=%s AND is_deleted=%s', (email, 0))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during email_exists teacher(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def create(user_id, first_name, last_name, email, contact_num, qualification, joining_date):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO teachers(user_id,first_name,last_name,email,contact_num,qualification,joining_date)
                               VALUES(%s,%s,%s,%s,%s,%s,%s)''', (user_id, first_name, last_name, email, contact_num, qualification, joining_date))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.exception(f"Error during teacher create(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def update(user_id, first_name, last_name, email, contact_num, qualification, joining_date):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''UPDATE teachers SET first_name=%s,last_name=%s,email=%s,
                               contact_num=%s,qualification=%s,joining_date=%s WHERE user_id=%s''',
                               (first_name, last_name, email, contact_num, qualification, joining_date, user_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during teacher update(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def soft_delete(teacher_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE teachers SET is_deleted=%s WHERE teacher_id=%s', (1, teacher_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete teacher(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def set_courses(teacher_id, course_ids):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM teacher_course WHERE teacher_id=%s', (teacher_id,))
                for cid in course_ids:
                    cursor.execute('INSERT INTO teacher_course(teacher_id,course_id) VALUES(%s,%s)', (teacher_id, cid))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during set_courses(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_all_assignments():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT tc.teacher_course_id,t.first_name,t.last_name,
                               c.course_name,c.credit_hours,p.program_name
                               FROM teacher_course tc
                               JOIN teachers t ON tc.teacher_id=t.teacher_id
                               JOIN courses c ON tc.course_id=c.course_id
                               JOIN programs p ON c.program_id=p.program_id
                               WHERE tc.is_deleted=0 AND t.is_deleted=0 AND c.is_deleted=0''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all_assignments(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def assign_course(teacher_id, course_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO teacher_course(course_id,teacher_id) VALUES(%s,%s)', (course_id, teacher_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during assign_course(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def remove_assignment(teacher_course_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE teacher_course SET is_deleted=%s WHERE teacher_course_id=%s', (1, teacher_course_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during remove_assignment(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class SalaryModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT s.salary_id,t.first_name,t.last_name,s.month,s.year,
                               s.basic_salary,s.bonus,s.deductions,
                               (s.basic_salary+s.bonus-s.deductions) AS net_salary,s.status
                               FROM teacher_salary s
                               JOIN teachers t ON s.teacher_id=t.teacher_id
                               WHERE s.is_deleted=%s ORDER BY s.salary_id ASC''', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all salary(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def exists(teacher_id, month, year):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT salary_id FROM teacher_salary WHERE teacher_id=%s AND month=%s AND year=%s', (teacher_id, month, year))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during salary exists(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def create(teacher_id, month, year, basic_salary, bonus, deductions, status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO teacher_salary(teacher_id,month,year,basic_salary,bonus,deductions,status)
                               VALUES(%s,%s,%s,%s,%s,%s,%s)''', (teacher_id, month, year, basic_salary, bonus, deductions, status))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during salary create(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def update(salary_id, basic_salary, bonus, deductions, status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE teacher_salary SET basic_salary=%s,bonus=%s,deductions=%s,status=%s WHERE salary_id=%s',
                               (basic_salary, bonus, deductions, status, salary_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during salary update(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def soft_delete(salary_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE teacher_salary SET is_deleted=%s WHERE salary_id=%s', (1, salary_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete salary(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class EnrollmentModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT sc.student_course_id,s.first_name,s.last_name,s.student_id,
                               c.course_name,p.program_name
                               FROM student_course sc
                               JOIN students s ON sc.student_id=s.student_id
                               JOIN courses c ON sc.course_id=c.course_id
                               JOIN programs p ON s.program_id=p.program_id
                               WHERE sc.is_deleted=%s''', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all enrollments(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def exists(student_id, course_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM student_course WHERE student_id=%s AND course_id=%s AND is_deleted=%s', (student_id, course_id, 0))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during enrollment exists(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def enroll(student_id, course_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO student_course(student_id,course_id) VALUES(%s,%s)', (student_id, course_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during enroll(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def remove(student_course_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT student_id,course_id FROM student_course WHERE student_course_id=%s', (student_course_id,))
                record = cursor.fetchone()
                cursor.execute('UPDATE student_course SET is_deleted=%s WHERE student_course_id=%s', (1, student_course_id))
                if record:
                    cursor.execute('''UPDATE student_section SET is_deleted=1 WHERE student_id=%s
                                   AND section_id IN(SELECT section_id FROM sections WHERE course_id=%s)''',
                                   (record['student_id'], record['course_id']))
                conn.commit()
                return record
        except Exception as e:
            logging.exception(f"Error during enrollment remove(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_section(student_id, section_id, is_deleted=0):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM student_section WHERE student_id=%s AND section_id=%s AND is_deleted=%s', (student_id, section_id, is_deleted))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during get_section(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def add_or_restore_section(student_id, section_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM student_section WHERE student_id=%s AND section_id=%s AND is_deleted=1', (student_id, section_id))
                if cursor.fetchone():
                    cursor.execute('UPDATE student_section SET is_deleted=0 WHERE student_id=%s AND section_id=%s', (student_id, section_id))
                else:
                    cursor.execute('INSERT INTO student_section(student_id,section_id) VALUES(%s,%s)', (student_id, section_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during add_or_restore_section(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_all_sections():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT section_id,section_name,semester,course_id FROM sections')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all_sections(admin_models): {str(e)}")
            raise
        finally:
            conn.close()


class AttendanceModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT a.attendance_id,a.attendance_date,a.attendance_status,
                               s.first_name,s.last_name,c.course_name,sec.section_name
                               FROM attendance a
                               JOIN students s ON a.student_id=s.student_id
                               JOIN student_course sc ON a.student_course_id=sc.student_course_id
                               JOIN courses c ON sc.course_id=c.course_id
                               JOIN course_schedule cs ON a.course_schedule_id=cs.course_schedule_id
                               JOIN sections sec ON cs.section_id=sec.section_id
                               WHERE a.is_deleted=%s''', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all attendance(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def update(attendance_id, status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE attendance SET attendance_status=%s WHERE attendance_id=%s', (status, attendance_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during attendance update(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_all_course_logs():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT cal.log_id,cal.attendance_date,cal.total_students,cal.total_present,cal.total_absent,
                               t.first_name,t.last_name,c.course_name,cs.day_of_week
                               FROM course_attendance_log cal
                               JOIN teachers t ON cal.teacher_id=t.teacher_id
                               JOIN courses c ON cal.course_id=c.course_id
                               JOIN course_schedule cs ON cal.course_schedule_id=cs.course_schedule_id
                               WHERE cal.is_deleted=0''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all_course_logs(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_schedule_by_section(section_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT cs.course_schedule_id,s.semester FROM course_schedule cs
                               JOIN sections s ON cs.section_id=s.section_id
                               WHERE cs.section_id=%s LIMIT 1''', (section_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during get_schedule_by_section(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def insert_course_log(teacher_id, course_id, course_schedule_id, attendance_date, semester, total_students, total_present, total_absent):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO course_attendance_log
                               (teacher_id,course_id,course_schedule_id,attendance_date,semester,total_students,total_present,total_absent)
                               VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',
                               (teacher_id, course_id, course_schedule_id, attendance_date, semester, total_students, total_present, total_absent))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during insert_course_log(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class GradeModel:

    @staticmethod
    def get_results(program_id=None, selected_semester=None):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                query = '''SELECT sr.student_result_id,sr.student_id,sr.student_semester,
                               sr.overall_gpa,sr.result_status,s.first_name,s.last_name
                               FROM student_results sr
                               JOIN students s ON sr.student_id=s.student_id
                               JOIN programs p ON s.program_id=p.program_id WHERE 1=1'''
                params = []
                if program_id:
                    query += ' AND p.program_id=%s'
                    params.append(program_id)
                if selected_semester:
                    query += ' AND sr.student_semester=%s'
                    params.append(selected_semester)
                query += ' ORDER BY sr.student_semester ASC'
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_results(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_marks(student_result_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT srm.*,c.course_name FROM student_result_marks srm
                               JOIN student_course sc ON srm.student_course_id=sc.student_course_id
                               JOIN courses c ON sc.course_id=c.course_id
                               WHERE srm.student_result_id=%s''', (student_result_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_marks(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def update(student_result_id, overall_gpa, result_status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE student_results SET overall_gpa=%s,result_status=%s WHERE student_result_id=%s',
                               (overall_gpa, result_status, student_result_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during grade update(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class FeeModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT sf.*,p.program_name,s.first_name,s.last_name
                               FROM student_fees sf
                               JOIN students s ON sf.student_id=s.student_id
                               JOIN programs p ON sf.program_id=p.program_id''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all fees(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def update_status(student_fees_id, fee_status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE student_fees SET fee_status=%s WHERE student_fees_id=%s', (fee_status, student_fees_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during fee update_status(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def create(student_id, program_id, fee_amount, fee_month, fee_status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO student_fees(student_id,program_id,fee_amount,fee_month,fee_status,update_date)
                               VALUES(%s,%s,%s,%s,%s,NOW())''', (student_id, program_id, fee_amount, fee_month, fee_status))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during fee create(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class SemesterModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM semester WHERE is_deleted=%s', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all semesters(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def create(name, year, start_date, end_date):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO semester(name,year,start_date,end_date,created_at) VALUES(%s,%s,%s,%s,%s)',
                               (name, year, start_date, end_date, datetime.now()))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during semester create(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def update(semester_id, name, year, start_date, end_date):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE semester SET name=%s,year=%s,start_date=%s,end_date=%s,created_at=%s WHERE semester_id=%s',
                               (name, year, start_date, end_date, datetime.now(), semester_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during semester update(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def soft_delete(semester_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE semester SET is_deleted=%s WHERE semester_id=%s', (1, semester_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete semester(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_all_summer():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM summer_semesters ORDER BY year DESC,summer_semesters_id DESC')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all_summer(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_summer_registrations(summer_semesters_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT s.first_name,s.last_name,c.course_name,sr.registration_date
                               FROM summer_registration sr
                               JOIN students s ON sr.student_id=s.student_id
                               JOIN courses c ON sr.course_id=c.course_id
                               WHERE sr.summer_semesters_id=%s''', (summer_semesters_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_summer_registrations(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def create_summer(name, year, start_date, end_date, status, previous_semester_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO summer_semesters(name,year,start_date,end_date,status,previous_semester_id) VALUES(%s,%s,%s,%s,%s,%s)',
                               (name, year, start_date, end_date, status, previous_semester_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during create_summer(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def delete_summer(summer_semesters_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM summer_semesters WHERE summer_semesters_id=%s', (summer_semesters_id,))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during delete_summer(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def get_all_freeze_requests():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT sfr.freeze_id,sfr.semester,sfr.reason,sfr.status,sfr.applied_date,
                               s.first_name,s.last_name,s.student_id
                               FROM semester_freeze_students sfr
                               JOIN students s ON sfr.student_id=s.student_id''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all_freeze_requests(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def update_freeze_status(freeze_id, status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE semester_freeze_students SET status=%s WHERE freeze_id=%s', (status, freeze_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during update_freeze_status(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class TimetableModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT cs.course_schedule_id,cs.day_of_week,cs.start_time,cs.end_time,cs.location,
                               c.course_name,s.section_name
                               FROM course_schedule cs
                               JOIN courses c ON cs.course_id=c.course_id
                               JOIN sections s ON cs.section_id=s.section_id
                               WHERE cs.is_deleted=%s''', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all timetable(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def exists(course_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT course_id FROM course_schedule WHERE course_id=%s', (course_id,))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during timetable exists(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def create(day_of_week, start_time, end_time, location, course_id, section_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO course_schedule(day_of_week,start_time,end_time,location,course_id,section_id) VALUES(%s,%s,%s,%s,%s,%s)',
                               (day_of_week, start_time, end_time, location, course_id, section_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during timetable create(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def update(course_schedule_id, day_of_week, start_time, end_time, location):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE course_schedule SET day_of_week=%s,start_time=%s,end_time=%s,location=%s WHERE course_schedule_id=%s',
                               (day_of_week, start_time, end_time, location, course_schedule_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during timetable update(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def soft_delete(course_schedule_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE course_schedule SET is_deleted=%s WHERE course_schedule_id=%s', (1, course_schedule_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete timetable(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class FYPModel:

    @staticmethod
    def get_all(status_filter=None):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                query = '''SELECT fy.fyp_id,fy.project_title,fy.progress,fy.description,fy.status,
                               fy.last_submission,fy.created_at,fy.student_id,fy.teacher_id,
                               CONCAT(s.first_name,' ',s.last_name) AS student_name,
                               s.email AS student_email,s.contact AS student_contact,
                               p.program_name AS program,sec.semester,
                               CONCAT(t.first_name,' ',t.last_name) AS teacher_name,
                               t.email AS teacher_email,t.contact_num AS teacher_contact
                               FROM fyp_groups fy
                               JOIN students s ON fy.student_id=s.student_id
                               JOIN teachers t ON fy.teacher_id=t.teacher_id
                               JOIN programs p ON s.program_id=p.program_id
                               LEFT JOIN student_section ss ON s.student_id=ss.student_id AND ss.is_deleted=0
                               LEFT JOIN sections sec ON ss.section_id=sec.section_id
                               WHERE fy.is_deleted=0'''
                if status_filter:
                    query += ' AND fy.status=%s'
                    cursor.execute(query, (status_filter,))
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all fyp(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def update_status(fyp_id, status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE fyp_groups SET status=%s WHERE fyp_id=%s', (status, fyp_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during update_status fyp(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def assign_supervisor(fyp_id, teacher_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE fyp_groups SET teacher_id=%s WHERE fyp_id=%s', (teacher_id, fyp_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during assign_supervisor(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class ExamModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT ex.exam_id,ex.exam_category,ex.exam_date,ex.exam_semester,
                               ex.start_time,ex.end_time,ex.location,ex.mode,ex.status,ps.program_name
                               FROM exams ex
                               JOIN programs ps ON ex.program_id=ps.program_id
                               WHERE ex.is_deleted=%s''', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all exams(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def exists(program_id, exam_category, exam_semester, exam_date):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT exam_id FROM exams WHERE program_id=%s AND exam_category=%s AND exam_semester=%s AND exam_date=%s',
                               (program_id, exam_category, exam_semester, exam_date))
                return cursor.fetchone()
        except Exception as e:
            logging.exception(f"Error during exam exists(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def create(program_id, exam_category, exam_date, exam_semester, start_time, end_time, location, mode):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO exams(program_id,exam_category,exam_date,exam_semester,
                               start_time,end_time,location,mode,status)
                               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'Ongoing')''',
                               (program_id, exam_category, exam_date, exam_semester, start_time, end_time, location, mode))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during exam create(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def update(exam_id, exam_category, exam_date, exam_semester, start_time, end_time, location, mode, status):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''UPDATE exams SET exam_category=%s,exam_date=%s,exam_semester=%s,
                               start_time=%s,end_time=%s,location=%s,mode=%s,status=%s
                               WHERE exam_id=%s AND is_deleted=%s''',
                               (exam_category, exam_date, exam_semester, start_time, end_time, location, mode, status, exam_id, 0))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during exam update(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def soft_delete(exam_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE exams SET is_deleted=%s WHERE exam_id=%s', (1, exam_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete exam(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class NotificationModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT id,title,sender_role,receiver_role,status,created_at FROM notifications WHERE is_deleted=%s', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all notifications(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def send(sender_id, sender_role, receiver_id, receiver_role, title, description, related_course_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO notifications
                               (sender_id,sender_role,receiver_id,receiver_role,title,description,related_course_id,status)
                               VALUES(%s,%s,%s,%s,%s,%s,%s,'Pending')''',
                               (sender_id, sender_role, receiver_id, receiver_role, title, description, related_course_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during notification send(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

    @staticmethod
    def soft_delete(notify_id):
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('UPDATE notifications SET is_deleted=%s,status=%s WHERE id=%s', (1, 'Rejected', notify_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during soft_delete notification(admin_models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()


class ProgramModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM programs WHERE is_deleted=%s', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all programs(admin_models): {str(e)}")
            raise
        finally:
            conn.close()


class CourseModel:

    @staticmethod
    def get_all():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT course_id,course_name FROM courses WHERE is_deleted=%s', (0,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_all courses(admin_models): {str(e)}")
            raise
        finally:
            conn.close()


class StudentLogModel:

    @staticmethod
    def get_student_log():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT DISTINCT s.student_id,s.first_name,s.last_name,
                           COUNT(sl.log_id) AS total_visits,
                           MAX(sl.entered_at) AS last_seen,
                           SUM(sl.time_spent_seconds) AS total_time
                           FROM student_activity_log sl
                           JOIN students s ON s.student_id=sl.student_id
                           GROUP BY s.student_id,s.first_name,s.last_name
                           ORDER BY last_seen DESC''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_student_log(admin_models): {str(e)}")
            raise
        finally:
            conn.close()

    @staticmethod
    def acivity_log_student():  
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT sl.*,s.first_name,s.last_name
                           FROM student_activity_log sl
                           JOIN students s ON s.student_id=sl.student_id
                           ORDER BY sl.entered_at DESC''')
                return cursor.fetchall()  
        except Exception as e:
            logging.exception(f"Error during acivity_log_student(admin_models): {str(e)}")
            raise
        finally:
            conn.close()


class TeacherLogModel:

    @staticmethod
    def get_teacher_log():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT DISTINCT t.teacher_id,t.first_name,t.last_name,
                           COUNT(tl.log_id) AS total_visits,
                           MAX(tl.entered_at) AS last_seen,
                           SUM(tl.time_spent_seconds) AS total_time
                           FROM teacher_activity_log tl
                           JOIN teachers t ON t.teacher_id=tl.teacher_id
                           GROUP BY t.teacher_id,t.first_name,t.last_name
                           ORDER BY last_seen DESC''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during get_teacher_log(admin_models): {str(e)}")
            raise
        finally:
            conn.close()
    
    @staticmethod
    def activity_log_teacher():
        try:
            conn = mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT tl.*,t.first_name,t.last_name
                           FROM teacher_activity_log tl
                           JOIN teachers t ON t.teacher_id=tl.teacher_id
                           ORDER BY tl.entered_at DESC''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during activity_log_teacher(admin_models): {str(e)}")
            raise
        finally:
            conn.close()



class EmailLookup:
    @staticmethod
    def _one(query,params):
        conn=None
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute(query,params)
                row=cursor.fetchone()
                return row['email'] if row else None
        except Exception as e:
            logging.exception(f"Error during email lookup(models): {str(e)}")
            return None
        finally:
            if conn:
                conn.close()

    @staticmethod
    def by_freeze_id(freeze_id):
        return EmailLookup._one('''SELECT u.email FROM semester_freeze_students f
            JOIN students s ON f.student_id=s.student_id
            JOIN users u ON s.user_id=u.user_id
            WHERE f.freeze_id=%s''',(freeze_id,))

    @staticmethod
    def by_fyp_id(fyp_id):
        return EmailLookup._one('''SELECT u.email FROM fyp_groups g
            JOIN students s ON g.student_id=s.student_id
            JOIN users u ON s.user_id=u.user_id
            WHERE g.fyp_id=%s''',(fyp_id,))

    @staticmethod
    def by_complaint_id(complaint_id):
        return EmailLookup._one('''SELECT u.email FROM complaint_suggestion c
            JOIN users u ON c.user_id=u.user_id
            WHERE c.complt_sugst_id=%s''',(complaint_id,))