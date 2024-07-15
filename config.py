import os

# Configuración de directorios
UPLOAD_FOLDER = 'known_faces'
TEMP_FOLDER = 'temp_images'

# Crear directorios si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
