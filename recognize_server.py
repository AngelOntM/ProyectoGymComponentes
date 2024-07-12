from flask import Flask, request, jsonify
import face_recognition
import os

app = Flask(__name__)

# Directorio donde se guardarán las imágenes faciales conocidas
KNOWN_FACES_DIR = 'known_faces'
if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

# Cargar imágenes faciales conocidas y sus codificaciones
def load_known_faces():
    known_face_encodings = []
    known_face_names = []

    for root, dirs, files in os.walk(KNOWN_FACES_DIR):
        for file_name in files:
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                image_path = os.path.join(root, file_name)
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    encoding = encodings[0]
                    known_face_encodings.append(encoding)
                    known_face_names.append(os.path.splitext(file_name)[0])

    return known_face_encodings, known_face_names

@app.route('/recognize', methods=['POST'])
def recognize_face():
    if 'face_image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['face_image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Guardar la imagen temporalmente
    file_path = os.path.join('temp', file.filename)
    if not os.path.exists('temp'):
        os.makedirs('temp')
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

if __name__ == '__main__':
    app.run(debug=True, port=5002)
