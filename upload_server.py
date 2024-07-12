from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
import face_recognition
from PIL import Image

app = Flask(__name__)

# Directorio donde se guardarán las imágenes
UPLOAD_FOLDER = 'known_faces'
TEMP_FOLDER = 'temp_images'

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

def remove_existing_images(user_id):
    """Eliminar imágenes existentes del mismo user_id."""
    for existing_file in os.listdir(UPLOAD_FOLDER):
        if existing_file.startswith(f"{user_id}_"):
            os.remove(os.path.join(UPLOAD_FOLDER, existing_file))

def save_temp_image(file):
    """Guardar la imagen temporalmente y devolver la ruta."""
    temp_path = os.path.join(TEMP_FOLDER, f"temp_{uuid.uuid4().hex}.jpg")
    file.save(temp_path)
    return temp_path

def detect_face(image_path):
    """Detectar y recortar el rostro en la imagen."""
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return None
    top, right, bottom, left = face_locations[0]
    face_image = image[top:bottom, left:right]
    return Image.fromarray(face_image)

def save_face_image(face_image, user_id):
    """Guardar la imagen del rostro recortada con el nombre user_id.jpg."""
    file_name = f"{user_id}_{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, file_name)
    face_image.save(file_path)
    return file_name

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'face_image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    if 'user_id' not in request.form:
        return jsonify({'error': 'No user_id part'}), 400

    file = request.files['face_image']
    user_id = request.form['user_id']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and user_id:
        # Eliminar imágenes existentes del mismo user_id
        remove_existing_images(user_id)

        # Guardar la imagen temporalmente
        temp_path = save_temp_image(file)

        # Detectar y recortar el rostro
        face_image = detect_face(temp_path)
        if not face_image:
            os.remove(temp_path)
            return jsonify({'error': 'No face found in the image'}), 400

        # Guardar la imagen del rostro recortada
        unique_filename = save_face_image(face_image, user_id)

        # Eliminar el archivo temporal
        os.remove(temp_path)

        image_url = request.host_url + 'images/' + unique_filename

        return jsonify(
            {'message': 'Image uploaded successfully', 'user_id': user_id, 'file_name': unique_filename, 'image_url': image_url}), 200

@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
