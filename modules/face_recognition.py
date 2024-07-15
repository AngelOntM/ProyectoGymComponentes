from flask import Blueprint, request, jsonify
import face_recognition
import os
from config import TEMP_FOLDER, UPLOAD_FOLDER

face_recognition_bp = Blueprint('face_recognition', __name__)

def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    for root, dirs, files in os.walk(UPLOAD_FOLDER):
        for file_name in files:
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                image_path = os.path.join(root, file_name)
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    encoding = encodings[0]
                    known_face_encodings.append(encoding)
                    # Extraer solo el user_id, eliminando el uuid
                    user_id = file_name.split('_')[0]
                    known_face_names.append(user_id)

    return known_face_encodings, known_face_names

@face_recognition_bp.route('/recognize', methods=['POST'])
def recognize_face():
    if 'face_image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['face_image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Guardar la imagen temporalmente
    file_path = os.path.join(TEMP_FOLDER, file.filename)
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
    file.save(file_path)

    try:
        # Cargar la imagen a reconocer
        unknown_image = face_recognition.load_image_file(file_path)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        if not unknown_encodings:
            return jsonify({'error': 'No face found in the image'}), 400

        unknown_encoding = unknown_encodings[0]

        known_face_encodings, known_face_names = load_known_faces()

        # Comparar con las imágenes conocidas
        results = face_recognition.compare_faces(known_face_encodings, unknown_encoding)
        distances = face_recognition.face_distance(known_face_encodings, unknown_encoding)

        if True in results:
            match_index = results.index(True)
            return jsonify({'user_id': known_face_names[match_index]}), 200
        else:
            return jsonify({'error': 'User not recognized'}), 404
    finally:
        # Eliminar la imagen temporal
        os.remove(file_path)
