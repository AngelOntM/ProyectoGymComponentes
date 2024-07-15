from flask import Flask
from modules.face_recognition import face_recognition_bp
from modules.image_upload import image_upload_bp
from modules.user_images import user_images_bp

app = Flask(__name__)

# Registrar los Blueprints
app.register_blueprint(face_recognition_bp)
app.register_blueprint(image_upload_bp)
app.register_blueprint(user_images_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
