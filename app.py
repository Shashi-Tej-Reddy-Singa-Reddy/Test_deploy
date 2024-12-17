import os
import traceback
from flask import Flask, request, jsonify
from PIL import Image
import google.generativeai as genai
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Google API Key
my_api = "AIzaSyAIwrJ_nekXtHomctw2QraDVFQmkDNeYwc"  # Use a real API key here
os.environ['GOOGLE_API_KEY'] = my_api
genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

@app.route('/api/uploadImage', methods=['POST'])
def get_caption():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        
        # Check if the file is an image
        if not image_file.content_type.startswith('image/'):
            return jsonify({'error': 'File is not a valid image'}), 400

        # Open and process the image
        image = Image.open(image_file.stream).convert('RGB')
        text = "a photography of"

        # Image captioning with Google Generative AI (Gemini model)
        vision_model = genai.GenerativeModel('gemini-1.5-pro')
        response = vision_model.generate_content(["Explain the picture?", image])
        google_caption = response.text
        print("Google Caption:", google_caption)

        # Determine if the caption is point-wise or descriptive
        if '* **' in google_caption:
            # Split the caption into point-wise segments by * **
            points = google_caption.split('* **')
            points = [point.strip() for point in points if point.strip()]
            caption_type = 'point-wise'
        else:
            # If no * **, treat it as description with ** rules
            points = [google_caption.strip()]
            caption_type = 'description'

        # Modify ** rules for point-wise behavior
        modified_points = []
        for point in points:
            if '**' in point:
                # If there's **, it should continue after a colon (:)
                subpoints = point.split('**')
                subpoints = [sub.strip() for sub in subpoints if sub.strip()]
                if len(subpoints) > 1:
                    modified_points.append(f"{subpoints[0]}: {subpoints[1]}")
                else:
                    modified_points.append(subpoints[0])
            else:
                modified_points.append(point)

        print("modified_points : ",modified_points)
        return jsonify({
            'caption': modified_points,
            'type': caption_type})

    except Exception as e:
        print("Exception occurred:", e)
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
