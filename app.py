from flask import Flask, request, jsonify, session, redirect, url_for, render_template
import face_recognition
import numpy as np
import pickle
import cv2
import requests
import time
import mysql.connector
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generar una clave secreta segura

# Configuración de la base de datos MySQL
db_config = {
    'user': 'root',
    'password': '12345678',
    'host': '127.0.0.1',
    'database': 'face_recognition_db'
}

# Cargar el modelo entrenado
with open('models/face_enc', 'rb') as f:
    data = pickle.loads(f.read())
    print(f"Loaded model with {len(data['encodings'])} encodings")

ESP8266_IP = "http://192.168.1.100"  # Dirección IP del ESP8266
last_command_time = 0
command_interval = 5  # Intervalo mínimo entre comandos en segundos
last_token_time = datetime.min
token_interval = timedelta(minutes=1)  # Intervalo mínimo entre solicitudes de token

current_token = None


def send_command_to_esp(endpoint):
    global last_command_time
    current_time = time.time()
    if current_time - last_command_time >= command_interval:
        try:
            response = requests.get(f"{ESP8266_IP}/{endpoint}", timeout=5)
            print(f"Sent command to {endpoint}: {response.text}")
            last_command_time = current_time
        except requests.exceptions.RequestException as e:
            print(f"Error sending command to ESP8266: {e}")


def get_token(id_usuario, fecha_actual):
    global last_token_time, current_token
    if datetime.now() - last_token_time < token_interval:
        print("Token request interval not met")
        return current_token
    url = "https://ow6li79grb.execute-api.us-east-2.amazonaws.com/default/TemporalToken"
    payload = {
        "idusuario": id_usuario,
        "fecha_actual": fecha_actual
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            last_token_time = datetime.now()
            current_token = response.json().get("token")
            return current_token
        else:
            print(f"Failed to get token: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during token request: {e}")
        return None


@app.route('/login', methods=['POST'])
def login():
    try:
        file = request.files['image'].read()
        npimg = np.frombuffer(file, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)

        if encodings:
            print("Encoding found for uploaded image")
            encoding = encodings[0]
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            face_distances = face_recognition.face_distance(data["encodings"], encoding)

            # Encontrar el índice de la mejor coincidencia
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = data["names"][best_match_index]
                print(f"Match found: {name} at index {best_match_index}")
                if name in ["William5", "William11", "William15"]:
                    token = get_token(1, "11/04/2024")
                    return jsonify({'result': 'success', 'id': "William", 'token': token})
                return jsonify({'result': 'success', 'id': "William"})
            else:
                print("No match found")
        else:
            print("No encoding found for uploaded image")

        return jsonify({'result': 'failure'})
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({'result': 'error', 'message': str(e)}), 500


@app.route('/secure_page_login', methods=['POST'])
def secure_page_login():
    try:
        file = request.files['image'].read()
        npimg = np.frombuffer(file, np.uint8)
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)

        if encodings:
            print("Encoding found for uploaded image")
            encoding = encodings[0]
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            face_distances = face_recognition.face_distance(data["encodings"], encoding)

            # Encontrar el índice de la mejor coincidencia
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = data["names"][best_match_index]
                print(f"Match found: {name} at index {best_match_index}")
                if name in ["William5", "William11", "William15"]:
                    send_command_to_esp("motor_right")
                    send_command_to_esp("toggle_led")
                    return jsonify({'result': 'success', 'id': "William5"})
                return jsonify({'result': 'success', 'id': name})
            else:
                print("No match found")
        else:
            print("No encoding found for uploaded image")

        return jsonify({'result': 'failure'})
    except Exception as e:
        print(f"Error during secure_page_login: {e}")
        return jsonify({'result': 'error', 'message': str(e)}), 500


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login_user', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        token = data['token']
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user and token == current_token:
            session['username'] = username
            return jsonify({'status': 'Login successful'})
        else:
            return jsonify({'status': 'Invalid credentials or token'}), 400
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'status': 'Database error', 'message': str(err)}), 500
    except Exception as e:
        print(f"Error during user login: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/secure_page')
def secure_page():
    if 'username' in session:
        return render_template('secure_page.html')
    else:
        return redirect(url_for('index'))


@app.route('/activate_esp', methods=['POST'])
def activate_esp():
    if 'username' in session:
        send_command_to_esp("motor_right")
        send_command_to_esp("toggle_led")
        return jsonify({'status': 'ESP32 activated'})
    else:
        return jsonify({'status': 'Not authorized'}), 403


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
