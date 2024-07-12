import cv2
import face_recognition
import requests
import time

# Dirección del servidor de reconocimiento facial
recognition_url = 'http://127.0.0.1:5002/recognize'

# Inicializar la cámara
cap = cv2.VideoCapture(0)

# Configurar el tiempo de espera entre lecturas (en segundos)
interval = 5
last_capture_time = 0

while True:
    # Capturar frame por frame
    ret, frame = cap.read()

    # Mostrar el frame
    cv2.imshow('Video', frame)

    # Comprobar si ha pasado suficiente tiempo desde la última captura
    if time.time() - last_capture_time >= interval:
        # Convertir el frame a RGB (face_recognition trabaja con RGB)
        rgb_frame = frame[:, :, ::-1]

        # Detectar los rostros en el frame
        face_locations = face_recognition.face_locations(rgb_frame)

        # Si se detecta un rostro
        if face_locations:
            # Codificar el rostro detectado
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # Guardar el frame temporalmente en un archivo
            cv2.imwrite('temp_face.jpg', frame)

            # Leer el archivo como binario
            with open('temp_face.jpg', 'rb') as f:
                files = {'face_image': f}
                response = requests.post(recognition_url, files=files)

            print(response.json())

            # Actualizar el tiempo de la última captura
            last_capture_time = time.time()

    # Salir del bucle con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()
