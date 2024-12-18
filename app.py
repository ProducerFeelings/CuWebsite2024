from flask import Flask, render_template, request, jsonify, url_for, session, redirect, flash
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import io
from flask_cors import CORS



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management
# Enable CORS for all routes
CORS(app)
# Set up a consistent path for the database
db_path = 'database.db'

# Database initialization
def init_sqlite_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE ,           
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_sqlite_db()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Cu Detector Route (restricted access)
@app.route('/CuDetector')
def cu_detector():
    if 'username' in session:
        return render_template('CuDetector.html')
    else:
        flash("Please log in to access the Cu Detector.")
        return redirect(url_for('home'))

# User Sign-Up
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password,method='pbkdf2:sha256')

    
    print(f"Sign-up attempt: Username={username}, Email={email}")

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Check if the username or email already exists
            cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                flash("Username or Email already exists.")
                return redirect(url_for(                                                                                                                                       'home'))
            
            # If user does not exist, proceed with registration
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                           (username, email, hashed_password))
            conn.commit()
            # Convert to dictionary and return a sucess message to client
            return jsonify({'status': 'success', 'message': 'Sign-Up successful! Please log in.'})
    except sqlite3.IntegrityError:
        flash("An error occurred while signing up. Please try again.")
    return redirect(url_for('home'))

# User Sign-In
@app.route('/signin', methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({'status': 'fail', 'message': 'Sign-In failed! Please Sign In.'})
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone() 
            print(user)

        # Check if user does not exists
        if user is None:
           return jsonify({'status': 'fail', 'message': 'Sign-In failed! Credentials cant be found.'})

 # Check if the password is correct
        if check_password_hash(user[3], password):
            session['username'] = username # adding session
            flash("You are now logged in!") # remove
            return jsonify({'status': 'success', 'message': 'You are now logged in!', 'redirect_url': url_for('cu_detector')})
        else:
            flash("Invalid password. Please try again.")
            return redirect(url_for('home'))

    except sqlite3.Error as e:
        flash(f"Database error: {str(e)}")
        return redirect(url_for('home'))

# Password Reset
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password,
method='pbkdf2:sha256')

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()

            if user:
                cursor.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_password, email))
                conn.commit()
                flash("Password reset successful. Please log in.")
            else:
                flash("Email not found. Please try again.")
        return redirect(url_for('home'))
    else:
        return render_template('reset_password.html')
# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('home'))

# Load the ML model
model_path = r'Python\Image_Classification\Image_classify.h5'
if os.path.exists(model_path):
    model = load_model(model_path)
    print("Model loaded successfully.")
else:
    raise FileNotFoundError(f"Model file not found at {model_path}")

# Image preprocessing function
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

# Prediction route for image classification
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































# Prediction route for image classification
###—----------------------------------------- from hee
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Debugging: Log that the /predict endpoint has been hit
        print("DEBUG: /predict endpoint called.")


        # Check if the file is in the request
        if 'file' not in request.files:
            print("DEBUG: No file provided in the request.")
            return jsonify({'error': 'No file provided'}), 400


        file = request.files['file']


        # Debugging: Log file details
        print(f"DEBUG: Received file - {file.filename}")


        # Read the file and preprocess the image
        img_bytes = file.read()
        print(f"DEBUG: File read successfully. Size: {len(img_bytes)} bytes.")


        img_array = preprocess_image(img_bytes)
        print("DEBUG: Image preprocessing complete.")


        # Perform the prediction
        prediction = model.predict(img_array)
        print(f"DEBUG: Model prediction raw output - {prediction}")


        result = np.argmax(prediction, axis=1)[0]
        print(f"DEBUG: Prediction result (class index) - {result}")


        # Map prediction result to feedback
        if result == 0:
            feedback = "No Chronic Urticaria detected."
        else:
            feedback = "Chronic Urticaria detected. Please consult a specialist."


        # Debugging: Log feedback
        print(f"DEBUG: Feedback generated - {feedback}")


        return jsonify({'result': feedback})


    except ValueError as e:
        # Debugging: Log the error details
        print(f"DEBUG: ValueError encountered - {str(e)}")
        return jsonify({'error': str(e)}), 500


    except Exception as e:
        # Debugging: Log the unexpected error details
        print(f"DEBUG: Unexpected error encountered - {str(e)}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500




if __name__ == '__main__':
    app.run(debug=True)
