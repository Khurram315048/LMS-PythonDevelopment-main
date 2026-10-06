import logging
from utils.db import mysql
from datetime import datetime

class TeacherModel:
    @staticmethod
    def get_profile(teacher_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM teachers WHERE teacher_id=%s AND is_deleted=0',(teacher_id,))
                result=cursor.fetchone()
                return result
        except Exception as e:
            logging.exception(f"Error during get profile teacher(models): {str(e)}")
            raise
        finally:
            conn.close()    


    @staticmethod
    def get_by_email(email:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM users WHERE email=%s AND is_deleted=0',(email,))
                    user=cursor.fetchone()
                    return  user
        except Exception as e:
            logging.exception(f"Error during get by email(models): {str(e)}")
            raise
        finally:
            conn.close()


    @staticmethod
    def get_by_user_id(user_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT * FROM teachers WHERE user_id=%s AND is_deleted=0',(user_id,))
                teacher=cursor.fetchone()
                return teacher
        except Exception as e:
            logging.exception(f"Error furing user by id(models): {str(e)}")
            raise
        finally:
            conn.close()    



    @staticmethod
    def get_full_schedule(teacher_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                query='''SELECT tc.teacher_course_id,p.program_coordinator AS coordinator_name,
                    p.program_name AS class_name,c.course_id,c.course_name,
                    s.semester,s.section_id,s.section_name AS section,cs.day_of_week,cs.start_time as start,cs.end_time as end
                FROM teacher_course tc
                JOIN courses c ON tc.course_id=c.course_id
                JOIN programs p ON c.program_id=p.program_id
                JOIN sections s ON c.course_id=s.course_id
                JOIN course_schedule cs ON s.section_id=cs.section_id
                WHERE tc.teacher_id=%s
                ORDER BY FIELD(cs.day_of_week,'Monday','Tuesday','Wednesday','Thursday','Friday'),cs.start_time;
                '''
                cursor.execute(query,(teacher_id,))
                result=cursor.fetchall()
                return result
        except Exception as e:
            logging.exception(f"Error during full schdl(models): {str(e)}")
        finally:
            conn.close()        



    @staticmethod
    def get_class_structure(section_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                query='''SELECT c.course_id AS class_id,p.program_coordinator,p.program_name,s.semester, 
                    c.course_name,s.section_name,s.section_id,
                    s.assignments_enabled,s.quizzes_enabled,  
                    (SELECT COUNT(*) FROM student_section WHERE section_id=s.section_id) as total_enroll
                    FROM sections s
                    JOIN courses c ON s.course_id=c.course_id
                    JOIN programs p ON c.program_id=p.program_id
                    WHERE s.section_id=%s
                '''
                cursor.execute(query,(section_id,))
                result=cursor.fetchall()
                return result
        except Exception as e:
            logging.exception(f"Error during class strctr(models): {str(e)}")    
        finally:
            conn.close()    



    @staticmethod
    def toggle_upload_status(section_id:int,upload_type:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                column="assignments_enabled" if upload_type == 'assignment' else "quizzes_enabled"
                query=f"UPDATE sections SET {column} = 1 - {column} WHERE section_id=%s"
                cursor.execute(query,(section_id,))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during toggle(models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()



    @staticmethod
    def get_attendance_meta(section_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT c.course_name,c.course_id,cs.course_schedule_id,s.section_id,s.semester,s.section_name,
                    cs.end_time,cs.day_of_week
                    FROM sections s
                    JOIN courses c ON s.course_id=c.course_id
                    JOIN course_schedule cs ON s.section_id=cs.section_id
                    WHERE s.section_id=%s LIMIT 1''',(section_id,))
                result=cursor.fetchone()
                return result
        except Exception as e:
            logging.exception(f"Error during attndnc meta(models): {str(e)}")
            raise
        finally:
            conn.close()



    @staticmethod
    def get_lecture_no(course_schedule_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(DISTINCT attendance_date) AS total_lectures FROM course_attendance_log WHERE course_schedule_id=%s',(course_schedule_id,))
                res=cursor.fetchone()
                return res
        except Exception as e:
            logging.exception(f"Error during lec no(models): {str(e)}")   
            raise
        finally:
            conn.close()



    @staticmethod
    def check_attendance_marked(schedule_id:int,attendance_date:datetime):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT COUNT(*) as count FROM attendance WHERE course_schedule_id=%s AND attendance_date=%s', 
                (schedule_id,attendance_date))
                count=cursor.fetchone()['count']
                return count > 0
        except Exception as e:
            logging.exception(f"Error during chk attndc mark(models): {str(e)}")
            raise
        finally:
            conn.close()    



    @staticmethod
    def get_student_list_for_attendance(section_id:int,course_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT ss.student_id, CONCAT(s.first_name, ' ', s.last_name) AS student_name,sc.student_course_id
                    FROM student_section ss
                    JOIN student_course sc ON ss.student_id=sc.student_id
                    JOIN students s ON ss.student_id=s.student_id
                    WHERE ss.section_id=%s AND sc.course_id=%s''',(section_id,course_id))
                result=cursor.fetchall()
                return result
        except Exception as e:
            logging.exception(f"Error during stndt lst attndc(models): {str(e)}")
            raise
        finally:
            conn.close()    



    @staticmethod
    def save_bulk_attendance(attendance_data:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                query='INSERT INTO attendance(student_course_id,course_schedule_id,attendance_date,attendance_status,student_id) VALUES (%s,%s,%s,%s,%s)'
                cursor.executemany(query,attendance_data)
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during sv blk attndc(models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()



    @staticmethod
    def save_course_attendance_log(teacher_id:int,course_id:int,course_schedule_id:int,attendance_date:datetime,semester:int,attendance_data:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                total_students=len(attendance_data)
                total_present =sum(1 for row in attendance_data if row[3] == 'Present')
                total_absent=total_students - total_present
                cursor.execute('''SELECT log_id FROM course_attendance_log
                WHERE course_schedule_id=%s AND attendance_date=%s
                ''',(course_schedule_id,attendance_date))
                existing=cursor.fetchone()

                if existing:
                    cursor.execute('''UPDATE course_attendance_log
                    SET total_students=%s,total_present=%s,total_absent=%s
                    WHERE log_id=%s
                    ''',(total_students,total_present,total_absent,existing['log_id']))
                else:
                    cursor.execute('''
                        INSERT INTO course_attendance_log 
                        (teacher_id,course_id,course_schedule_id,attendance_date,semester,total_students,total_present,total_absent)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        ''', (teacher_id,course_id,course_schedule_id,attendance_date,semester,
                        total_students,total_present,total_absent))

                conn.commit()
        except Exception as e:
            logging.exception(f"Error during save crs attndc(models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()

       

    @staticmethod
    def get_fyp_groups(teacher_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                query="""SELECT f.*,s.first_name,s.last_name,s.student_id as reg_num,s.contact,s.email,p.program_name,sec.semester
                    FROM fyp_groups f
                    JOIN students s ON f.student_id=s.student_id
                    LEFT JOIN programs p ON s.program_id=p.program_id
                    LEFT JOIN student_section ss ON s.student_id=ss.student_id
                    LEFT JOIN sections sec ON ss.section_id=sec.section_id
                    WHERE f.teacher_id=%s
                    GROUP BY f.fyp_id"""
                cursor.execute(query,(teacher_id,))
                groups=cursor.fetchall()
                for group in groups:
                    cursor.execute("SELECT * FROM fyp_messages WHERE fyp_id=%s ORDER BY created_at ASC",(group['fyp_id'],))
                    group['messages']=cursor.fetchall()

                return groups
        except Exception as e:
            logging.exception(f"Error during fyp grps(models): {str(e)}")   
            raise
        finally:
            conn.close() 



    @staticmethod
    def update_fyp_status(fyp_id:int,status:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute("UPDATE fyp_groups SET status=%s WHERE fyp_id=%s",(status,fyp_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during updt fyp(models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()        
                


    @staticmethod
    def add_fyp_message(fyp_id:int,teacher_id:int,message_text:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT student_id FROM fyp_groups WHERE fyp_id=%s",(fyp_id,))
                res=cursor.fetchone()
                if res:
                    cursor.execute("""
                        INSERT INTO fyp_messages(fyp_id,teacher_id,student_id,sender_role,message)
                        VALUES (%s,%s,%s,'teacher',%s)""",(fyp_id,teacher_id,res['student_id'],message_text))
                    conn.commit()
        except Exception as e:
            logging.exception(f"Error during add fyp msg(models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()



    @staticmethod
    def update_submission_marks(sub_id:int,marks:int,total:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute("UPDATE student_submissions SET marks=%s,total_marks=%s WHERE submission_id=%s",(marks,total,sub_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during updt submssn(models): {str(e)}")
            raise
        finally:
            conn.close()



    @staticmethod
    def get_submissions_by_type(section_id:int,sub_type:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                query="""SELECT sub.submission_id,sub.student_id,sub.file_path,sub.upload_date,sub.marks,sub.total_marks,sub.submission_status,s.first_name,s.last_name 
                FROM student_submissions sub
                JOIN students s ON sub.student_id=s.student_id
                WHERE sub.section_id=%s AND LOWER(sub.submission_type)=LOWER(%s)"""
                cursor.execute(query,(section_id,sub_type))
                subs=cursor.fetchall()
                cursor.execute('''SELECT c.course_name,s.section_name FROM sections s JOIN courses c ON s.course_id=c.course_id
                WHERE s.section_id=%s''',(section_id,))
                meta=cursor.fetchone()
                return subs,meta
        except Exception as e:
            logging.exception(f"Error during submsn type(models): {str(e)}")
            raise
        finally:
            conn.close()    



    @staticmethod
    def get_grading_data(course_id:int,section_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT s.student_id,s.first_name,s.last_name,srm.marks_id AS has_result,srm.student_grade,srm.total_marks
                FROM students s
                JOIN student_section ss ON s.student_id=ss.student_id
                JOIN student_course sc ON s.student_id=sc.student_id AND sc.course_id=%s
                LEFT JOIN student_result_marks srm ON (sc.student_course_id=srm.student_course_id)
                WHERE ss.section_id=%s''', (course_id,section_id))
                res=cursor.fetchall()
                return res
        except Exception as e:
            logging.exception(f"Error during grading data(models): {str(e)}")
            raise
        finally:
            conn.close()    


    @staticmethod
    def is_section_owned_by_teacher(section_id:int,teacher_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT tc.teacher_course_id 
                    FROM teacher_course tc
                    JOIN sections s ON tc.course_id=s.course_id
                    WHERE s.section_id=%s AND tc.teacher_id=%s
                    """, (section_id,teacher_id))
                result=cursor.fetchone()
                return result is not None
        except Exception as e:
            logging.exception(f"Error during is sct owned(models): {str(e)}")
            raise
        finally:
            conn.close()    


    @staticmethod
    def process_student_result(sid:int,section_id:int,course_id:int,semester:int,data:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('SELECT student_course_id FROM student_course WHERE student_id=%s AND course_id=%s',
                               (sid,course_id))
                sc_record=cursor.fetchone()
                if not sc_record: 
                    logging.error(f"Error during stnd crs id(models) for student id: {sid}")
                    return
                
                cursor.execute('SELECT student_result_id FROM student_results WHERE student_id=%s AND student_semester=%s',
                               (sid,semester))
                res_parent=cursor.fetchone()
                res_id=res_parent['student_result_id'] if res_parent else None
                
                if not res_id:
                    cursor.execute('INSERT INTO student_results(student_id,student_semester,result_status,overall_gpa) VALUES (%s,%s,%s,%s)', 
                                (sid, semester, data['status'], data['gpa']))
                    
                    res_id=cursor.lastrowid

                cursor.execute('''
                    INSERT INTO student_result_marks(student_course_id,student_result_id,total_marks,student_grade,status,student_semester,sessional_marks,mid_marks,final_marks,subject_gpa)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE total_marks=%s,student_grade=%s,status=%s,sessional_marks=%s,mid_marks=%s,final_marks=%s,subject_gpa=%s
                ''', (sc_record['student_course_id'],res_id,data['total'],data['grade'],data['status'],semester,data['sessional'],data['mids'],data['final'],data['gpa'],
                data['total'],data['grade'],data['status'],data['sessional'],data['mids'],data['final'],data['gpa']))
                conn.commit()
        except Exception as e:
                logging.exception(f"Error during prcs stnd res(models): {str(e)}")
                conn.rollback()
                raise
        finally:        
                conn.close()



    @staticmethod
    def insert_complaint_suggestion(title:str,description:str,user_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO complaint_suggestion(title,description,user_id) VALUES(%s,%s,%s)',
                               (title,description,user_id))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during inst complnt suggst(models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()




class Notifications:

    @staticmethod
    def get_active_notifications(user_id:int,role:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute("""SELECT id,title,description,created_at
                    FROM notifications
                    WHERE (receiver_id=%s OR receiver_id IS NULL)
                    AND receiver_role=%s
                    AND is_deleted=%s
                    AND status='Pending'
                    """, (user_id,role,0))
                notifications=cursor.fetchall()
                return notifications 
        except Exception as e:
            logging.exception(f"Error during actv notf(models): {str(e)}")
            raise
        finally:
            conn.close()       




class ActivityModel:

    @staticmethod
    def log_enter(teacher_id:int,page_name:str,page_url:str,ip_address:str):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''INSERT INTO teacher_activity_log(teacher_id,page_name,page_url,entered_at,ip_address)
                            VALUES(%s,%s,%s,NOW(),%s)''',(teacher_id,page_name,page_url,ip_address))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logging.exception(f"Error during log enter(models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()    
            



    @staticmethod
    def log_exit(log_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''UPDATE teacher_activity_log
                            SET exited_at=NOW(),
                            time_spent_seconds=TIMESTAMPDIFF(SECOND,entered_at,NOW())
                            WHERE log_id=%s''',(log_id,))
                conn.commit()
        except Exception as e:
            logging.exception(f"Error during log exit(models): {str(e)}")
            conn.rollback()
            raise
        finally:
            conn.close()        



    @staticmethod
    def get_all_activity():
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT tal.log_id,tal.page_name,tal.page_url,tal.entered_at,
                            tal.exited_at,tal.time_spent_seconds,tal.ip_address,
                            t.first_name,t.last_name,t.teacher_id
                            FROM teacher_activity_log tal
                            JOIN teachers t ON tal.teacher_id=t.teacher_id
                            ORDER BY tal.entered_at DESC''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during all actvt(models): {str(e)}")
            raise
        finally:
            conn.close()    



    @staticmethod
    def get_activity_by_teacher(teacher_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT log_id,page_name,page_url,entered_at,exited_at,time_spent_seconds
                FROM teacher_activity_log
                WHERE teacher_id=%s ORDER BY entered_at DESC''',(teacher_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during actvtt stnd(models): {str(e)}")
            raise
        finally:
            conn.close()    



    @staticmethod
    def get_page_summary():
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT page_name,COUNT(*) AS total_visits,
                            AVG(time_spent_seconds) AS avg_seconds,
                            MAX(time_spent_seconds) AS max_seconds
                            FROM teacher_activity_log
                            WHERE time_spent_seconds IS NOT NULL
                            GROUP BY page_name ORDER BY total_visits DESC''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during pge smmr(models): {str(e)}")
            raise
        finally:
            conn.close()    



    @staticmethod
    def get_teacher_page_summary(teacher_id:int):
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT page_name,COUNT(*) AS total_visits,
                            SUM(time_spent_seconds) AS total_seconds,
                            AVG(time_spent_seconds) AS avg_seconds
                            FROM teacher_activity_log
                            WHERE teacher_id=%s AND time_spent_seconds IS NOT NULL
                            GROUP BY page_name ORDER BY total_seconds DESC''',(teacher_id,))
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during tchr smmr(models): {str(e)}")
            raise
        finally:
            conn.close()


    @staticmethod
    def get_active_now():
        try:
            conn=mysql.get_dict_connection()
            with conn.cursor() as cursor:
                cursor.execute('''SELECT tal.log_id,tal.page_name,tal.entered_at,tal.ip_address,
                            t.first_name,t.last_name,t.teacher_id
                            FROM teacher_activity_log tal
                            JOIN teachers t ON tal.teacher_id=t.teacher_id
                            WHERE tal.exited_at IS NULL
                            ORDER BY tal.entered_at DESC''')
                return cursor.fetchall()
        except Exception as e:
            logging.exception(f"Error during active now(models): {str(e)}")
            raise
        finally:
            conn.close()    