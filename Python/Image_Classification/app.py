from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import io
from PIL import Image
import os

app = Flask(__name__)

# Define the path to the model
model_path = r'C:\Users\danny\Desktop\repos\CuWebsite2024Updated\Python\Image_Classification\Image_classify.h5'

# Check if the model file exists
if os.path.exists(model_path):
    model = load_model(model_path)
    print("Model loaded successfully.")
else:
    raise FileNotFoundError(f"Model file not found at {model_path}")

def preprocess_image(img_bytes):
    try:
        img = Image.open(io.BytesIO(img_bytes))
        img = img.resize((224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        return img_array
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        img_bytes = file.read()
        img_array = preprocess_image(img_bytes)
        
        prediction = model.predict(img_array)
        result = np.argmax(prediction, axis=1)[0]

        if result == 0:
            feedback = "No Chronic Urticaria detected."
        else:
            feedback = "Chronic Urticaria detected. Please consult a specialist."

        return jsonify({'result': feedback})

    except ValueError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)







