import os
import cv2
import numpy as np
import pickle
from keras_facenet import FaceNet

embedder = FaceNet()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FACES_DIR = os.path.join(BASE_DIR, 'instance', 'faces')
EMBEDDING_FILE = os.path.join(BASE_DIR, 'instance', 'embeddings.pkl')

def extract_and_save_embeddings():
    embeddings_dict = {}

    if not os.path.exists(FACES_DIR):
        return False
    
    for student_id in os.listdir(FACES_DIR):
        student_path = os.path.join(FACES_DIR, student_id)

        if not os.path.isdir(student_path):
            continue

        face_embeddings = []

        for filename in os.listdir(student_path):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(student_path, filename)

                img = cv2.imread(filepath)
                if img is None:
                    continue
                    
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                img_resized = cv2.resize(img_rgb, (160, 160))
                img_tensor = np.expand_dims(img_resized, axis=0)

                embedding = embedder.embeddings(img_tensor)[0]
                face_embeddings.append(embedding)
            
        if face_embeddings:
            avg_embedding = np.mean(face_embeddings, axis=0)
            embeddings_dict[student_id] = avg_embedding

    try:
        with open(EMBEDDING_FILE, 'wb') as f:
            pickle.dump(embeddings_dict, f)
        return True, f"Đã trích xuất đặc trưng và lưu trữ thành công cho {len(embeddings_dict)} sinh viên."
    except Exception as e:
        return False, f"Lỗi khi lưu file embeddings.pkl: {str(e)}"
