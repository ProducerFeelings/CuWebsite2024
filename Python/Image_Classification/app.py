from flask import Flask, render_template  # Import render_template
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import io
from PIL import Image
import os

app = Flask(__name__)



# Home route 

@app.route('/')
def home():
    return render_template('index.html')  # Ensure you have 'index.html' in your 'templates' folder.



#Cu Dectector Route
@app.route('/CuDetector')  # Fix the route to start with '/'
def cu_detector():
    return render_template('CuDetector.html')  # Ensure 'CuDetector.html' is in your 'templates' folder.

#Load the ML model 
model_path = r'C:\Users\danny\Desktop\repos\CuWebsite2024Updated\Python\Image_Classification\Image_classify.h5'


# Check if the model file exists and load it
if os.path.exists(model_path):
    model = load_model(model_path)
    print("Model loaded successfully.")
else:
    raise FileNotFoundError(f"Model file not found at {model_path}")


# Function preprocess the image
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

# Predicte route for image  classification 

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


#Run the flask app 

if __name__ == '__main__':
    app.run(debug=True)







