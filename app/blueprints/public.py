import cv2
import time
from flask import Blueprint, render_template, Response, jsonify
from app.services.face_recognizer import recognize_face
from app.models import db
from app.models.attendance import Attendance
from app.models.student import Student
from datetime import datetime, timedelta

public_bp = Blueprint('public', __name__)

latest_frame =  None
last_recognized_time = {}
def generate_frames():
    global latest_frame
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        latest_frame = frame.copy()

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


@public_bp.route('/')
def index():
    return render_template('public/index.html')

@public_bp.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@public_bp.route('/recognize', methods=['POST'])
def recognize():
    global latest_frame, last_recognized_time

    if latest_frame is None:
        return jsonify({'status' : 'no_frame'})
    
    student_id, similarity = recognize_face(latest_frame)

    if student_id is None:
        # Nếu trả về -1 nghĩa là khung hình trống không có mặt ai
        if similarity == -1:
            return jsonify({'status': 'no_face'}) 
        # Nếu có % nhưng lại là None, nghĩa là có mặt người lạ
        else:
            return jsonify({'status': 'unknown', 'similarity': similarity})
    
    now = time.time()
    last_time = last_recognized_time.get(student_id, 0)
    student = Student.query.filter_by(student_id=student_id).first()

    # Báo đã điểm danh nếu < 10 giây
    if now - last_time < 10:
        return jsonify({
            'status': 'already',
            'name': student.full_name if student else student_id,
            'student_id': student_id,
            'similarity': similarity
        })

    # Ghi vào Database
    if student:
        log = Attendance(
            student_id=student.id,
            similarity=similarity / 100, # Lưu vào DB dạng 0.xx
            method='auto'
        )
        db.session.add(log)
        db.session.commit()
        last_recognized_time[student_id] = now
        
    return jsonify({
        'status': 'success',
        'name': student.full_name if student else student_id,
        'student_id': student_id,
        'similarity': similarity
    })

@public_bp.route('/get_recent_attendance', methods=['GET'])
def get_recent_attendance():
    try:
        now_utc = datetime.utcnow()
        start_of_day_vn = (now_utc + timedelta(hours=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_utc = start_of_day_vn - timedelta(hours=7)
        
        attended_logs = Attendance.query.filter(Attendance.timestamp >= start_utc).all()
        attended_ids = {log.student_id for log in attended_logs}

        logs = db.session.query(Attendance.id, Attendance.timestamp, Attendance.similarity, Student.full_name, Student.student_id)\
            .join(Student)\
            .filter(Attendance.timestamp >= start_utc)\
            .order_by(Attendance.timestamp.desc())\
            .limit(5).all()
        present_list = []
        
        for log_id, timestamp, similarity, name, mssv in logs:
            initials = "".join([n[0] for n in name.split()[-2:]]).upper()
            local_time = timestamp + timedelta(hours=7)

            present_list.append({
                'log_id': log_id,
                'name' : name,
                'mssv' : mssv,
                'initials': initials,
                'time' : local_time.strftime('%H:%M:%S'),
                'similarity': f"{round(similarity * 100, 1)}%" if similarity is not None else "0%"
            })

        
        all_students = Student.query.all()
        total_students = len(all_students)
        total_present = len(attended_ids)

        # Đếm số sinh viên chưa có ảnh
        no_face_count = sum(1 for s in all_students if not s.face_saved)

        # Tính tỷ lệ % lớp
        present_percent = int((total_present / total_students * 100) if total_students > 0 else 0)
        absent_percent = 100 - present_percent if total_students > 0 else 0

        # Tính độ chính xác trung bình (cosine similarity) của những người đã điểm danh
        avg_similarity = 0
        if attended_logs:
            # Lọc bỏ những log có similarity là None (có thể do lỗi nhận diện)
            valid_sims = [log.similarity for log in attended_logs if log.similarity is not None]
            if valid_sims:
                avg_similarity = int((sum(valid_sims) / len(valid_sims)) * 100)

        absent_list = []
        for s in all_students:
            if s.id not in attended_ids:
                absent_initials = "".join([n[0] for n in s.full_name.split()[-2:]]).upper()
                absent_list.append({
                    'name': s.full_name,
                    'mssv': s.student_id,
                    'initials': absent_initials
                })

        return jsonify({
            'present': present_list, 
            'absent': absent_list,
            'total_students': len(all_students),
            'total_present': len(attended_ids),
            'total_absent': len(absent_list),

            'no_face_count': no_face_count,
            'present_percent': present_percent,
            'absent_percent': absent_percent,
            'avg_similarity': avg_similarity
        })
    
    except Exception as e:
        print(f"Lỗi API get_recent_attendance: {e}")
        return jsonify({'error': 'Không thể lấy dữ liệu'}), 500