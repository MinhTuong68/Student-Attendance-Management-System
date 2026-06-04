import pandas as pd
from datetime import timedelta
from app.models.attendance import Attendance
from app.models.student import Student

def get_attendance_dataframe(start_date_vn, end_date_vn, class_name=None):
    start_utc = start_date_vn - timedelta(hours=7)
    end_utc =end_date_vn - timedelta(hours=7)

    if class_name and class_name != 'all':
        all_students = Student.query.filter_by(class_name=class_name).all()
    else:
        all_students = Student.query.all()

    attendance = Attendance.query.filter(
        Attendance.timestamp >= start_utc,
        Attendance.timestamp <= end_utc
    ).all()

    attended_dict = {}
    for att in attendance:
        if att.student_id not in attended_dict:
            attended_dict[att.student_id] = att

    data = []
    for idx, s in enumerate(all_students, start=1):
        att = attended_dict.get(s.id)
        if att:
            local_time = att.timestamp + timedelta(hours=7)
            data.append({
                "STT": idx,
                "MSSV": s.student_id,
                "Họ và tên": s.full_name,
                "Trạng thái": "Có mặt",
                "Giờ vào": local_time.strftime('%H:%M:%S'),
                "Độ khớp": f"{round(att.similarity * 100, 1)}%" if att.similarity else "",
                "Phương thức": "Tự động" if att.method == 'auto' else "Thủ công"
            })
        else:
            data.append({
                "STT": idx,
                "MSSV": s.student_id,
                "Họ và tên": s.full_name,
                "Trạng thái": "Vắng mặt",
                "Giờ vào": "",
                "Độ khớp": "",
                "Phương thức": ""
            })
    return pd.DataFrame(data)

def get_summary_dataframe(start_date_vn, end_date_vn):
    """Hàm xuất báo cáo tổng hợp dạng ma trận từ ngày đến ngày"""
    start_utc = start_date_vn - timedelta(hours=7)
    end_utc = end_date_vn - timedelta(hours=7)

    all_students = Student.query.all()
    attendances = Attendance.query.filter(
        Attendance.timestamp >= start_utc,
        Attendance.timestamp <= end_utc
    ).all()

    # 1. Tạo danh sách các ngày trong khoảng thời gian đã chọn (Làm tiêu đề cột)
    date_list = []
    current_date = start_date_vn
    while current_date <= end_date_vn:
        date_list.append(current_date.strftime('%d/%m'))
        current_date += timedelta(days=1)

    # 2. Tạo Dictionary tra cứu nhanh lịch sử đi học
    attendance_map = {}
    for att in attendances:
        local_time = att.timestamp + timedelta(hours=7)
        date_str = local_time.strftime('%d/%m')
        attendance_map[(att.student_id, date_str)] = True

    # 3. Lắp ráp dữ liệu thành dạng ma trận
    data = []
    for idx, s in enumerate(all_students, start=1):
        row = {
            "STT": idx,
            "MSSV": s.student_id,
            "Họ và tên": s.full_name,
            "Lớp": s.class_name
        }
        
        absent_count = 0
        # Quét qua từng ngày xem sinh viên có đi học không
        for d in date_list:
            if (s.id, d) in attendance_map:
                row[d] = "V"  # Chữ V: Đi học
            else:
                row[d] = "x"  # Chữ x: Vắng mặt
                absent_count += 1
        
        # Thêm cột tổng kết
        row["Tổng vắng"] = absent_count
        total_days = len(date_list)
        if total_days > 0 and (absent_count / total_days) > 0.2:
            row["Đánh giá"] = "Cấm thi (Vắng > 20%)"
        else:
            row["Đánh giá"] = "Đủ điều kiện"

        data.append(row)

    return pd.DataFrame(data)