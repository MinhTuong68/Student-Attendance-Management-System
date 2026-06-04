import pickle
import os

# Đường dẫn tới file embeddings.pkl của bạn
filepath = os.path.join('instance', 'embeddings.pkl')

if not os.path.exists(filepath):
    print("File không tồn tại! Hãy kiểm tra lại đường dẫn.")
else:
    # Mở file ở chế độ 'rb' (Read Binary)
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    
    print("=========================================")
    print(f"📊 TỔNG QUAN DỮ LIỆU AI ĐÃ HUẤN LUYỆN")
    print("=========================================")
    print(f"Kiểu dữ liệu tổng quát : {type(data)}")
    print(f"Số lượng sinh viên     : {len(data)} người\n")
    
    # Duyệt qua từng người trong danh bạ để xem chi tiết
    for student_id, vector in data.items():
        print(f"👤 Sinh viên (MSSV)    : {student_id}")
        print(f"📐 Kích thước vector   : {vector.shape} (Chuẩn 512 số của FaceNet)")
        print(f"🧬 5 chỉ số sinh học đầu tiên: {vector[:5]}")
        print("-" * 40)