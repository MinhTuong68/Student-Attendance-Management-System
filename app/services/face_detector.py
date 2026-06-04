import cv2
import os
from mtcnn import MTCNN

dectector = MTCNN()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FACES_DIR = os.path.join(BASE_DIR, 'instance', 'faces')

def crop_and_save_face(frame, student_id, count):
    if frame is None:
        return False, "Camera chưa sẵn sàng."
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = dectector.detect_faces(rgb_frame)

    if results:
        bounding_box = results[0]['box']
        x, y, w, h = bounding_box

        x, y = max(0, x), max(0, y)

        face = frame[y:y+h, x:x+w]

        try:
            face_160 = cv2.resize(face, (160, 160))

            student_dir = os.path.join(FACES_DIR, str(student_id))
            os.makedirs(student_dir, exist_ok=True)

            filename = os.path.join(student_dir, f"{count}.jpg")
            cv2.imwrite(filename, face_160)

            return True, "Thành công"
        except Exception as e:
            return False, f"Lỗi xử lý ảnh: {e}"
        
    return False, "Không nhận diện được khuôn mặt. Hãy nhìn thẳng!"