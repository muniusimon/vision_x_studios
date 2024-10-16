from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .app import client

api = Blueprint('api', __name__)

@api.route('/generate-image', methods=['POST'])
@jwt_required()
def generate_image():
    user_id = get_jwt_identity()
    data = request.json
    prompt = data.get('prompt')
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        generated_art_url = response.data[0].url
        return jsonify({"image_url": generated_art_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ... add more API endpoints for other features ...
