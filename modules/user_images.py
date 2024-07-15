from flask import Blueprint, send_from_directory, jsonify
import os
from config import UPLOAD_FOLDER

user_images_bp = Blueprint('user_images', __name__)

@user_images_bp.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@user_images_bp.route('/user/<user_id>/image', methods=['GET'])
def get_user_image(user_id):
    for file_name in os.listdir(UPLOAD_FOLDER):
        if file_name.startswith(f"{user_id}_"):
            return send_from_directory(UPLOAD_FOLDER, file_name)
    return jsonify({'error': 'Image not found'}), 404
