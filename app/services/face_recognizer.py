import os
import cv2
import pickle
import numpy as np
from mtcnn import MTCNN
from keras_facenet import FaceNet

detector = MTCNN()
embedder = FaceNet()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EMBEDDING_FILE = os.path.join(BASE_DIR, 'instance', 'embeddings.pkl')
THRESHOLD = 0.80 # Cosine Similarity > 0.8 thì nhận diện

def load_embeddings():
    if not os.path.exists(EMBEDDING_FILE):
        return {}
    with open(EMBEDDING_FILE, 'rb') as f:
        return pickle.load(f)
    
def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

known_database = load_embeddings()

def reload_embeddings_to_ram():
    """Cập nhật lại biến global known_database vào RAM"""
    global known_database
    known_database = load_embeddings()
    print("[INFO] Đã nạp lại khuôn mặt mới vào RAM thành công!")

def recognize_face(frame):

    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = detector.detect_faces(rgb_frame)

        if not results:
            return None, -1
        
        if not known_database:
            return None, 0
        
        res = max(results, key=lambda b: b['box'][2]*b['box'][3])
        x, y, w, h = res['box']

        x1, y1 = max(0, x-10), max(0,y -10)
        x2, y2 = min(frame.shape[1], x + w + 10), min(frame.shape[0], y + h + 10)
        face = frame[y1:y2, x1:x2]

        if face.shape[0] == 0 or face.shape[1] == 0:
            return None, -1
        
        face_resized = cv2.resize(cv2.cvtColor(face, cv2.COLOR_BGR2RGB), (160, 160))
        face_tensor = np.expand_dims(face_resized, axis=0)
        current_vector = embedder.embeddings(face_tensor)[0]

    except Exception as e:
            print(f"Lỗi trích xuất: {e}")
            return None, -1
    
    best_match = None
    best_score = -1.0

    for student_id, saved_vector in known_database.items():
        score = cosine_similarity(current_vector, saved_vector)
        if score > best_score:
            best_score = score
            best_match = student_id
    similarity_percent = float(round(best_score * 100, 1))

    if similarity_percent < 0:
        similarity_percent = 0
    if best_score >= THRESHOLD:
        return best_match, similarity_percent
    else:
        return None, similarity_percent