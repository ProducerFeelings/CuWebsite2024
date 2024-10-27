from flask import Flask, render_template, request, jsonify, url_for, session, redirect, flash
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session management

# Set up a consistent path for the database
db_path = r'C:\Users\danny\Desktop\repos\CuWebsite2024Updated\database.db'

# Database initialization
def init_sqlite_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
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
    hashed_password = generate_password_hash(password, method='sha256')

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                           (username, email, hashed_password))
            conn.commit()
            flash("Sign-Up successful! Please log in.")
    except sqlite3.IntegrityError:
        flash("Username or Email already exists.")
    return redirect(url_for('home'))

# User Sign-In
@app.route('/signin', methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash("Username and password are required.")
        return redirect(url_for('home'))

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()

        # Check if user exists
        if user is None:
            flash("Username does not exist. Please sign up.")
            return redirect(url_for('home'))

        # Check if the password is correct
        if check_password_hash(user[3], password):
            session['username'] = username
            flash("You are now logged in!")
            return redirect(url_for('cu_detector'))
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
        hashed_password = generate_password_hash(new_password, method='sha256')

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
model_path = r'C:\\Users\danny\Desktop\repos\CuWebsite2024Updated\Python\Image_Classification\Image_classify.h5'
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
