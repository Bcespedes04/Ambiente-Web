from flask import Flask, render_template, request, redirect, url_for, session
import os
import shutil
import cv2
import imutils
import numpy as np
import base64
from flask import jsonify
'''db connection'''
from flask_mysqldb import MySQL
import MySQLdb.cursors # type: ignore
import MySQLdb.cursors, re, hashlib # type: ignore
'''session from flask'''

app = Flask(__name__)

'''bd connection details'''
app.secret_key = 'abcd1234'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PASSWORD'] = 'bucza4-qejxov' #password database schema
app.config['MYSQL_DB'] = 'ambienteWeb' #schema

mysql = MySQL(app) #db initialization
login_user = False
# Ruta donde se encuentran las carpetas de los rostros registrados
ROSTROS_DIR = r"C:\Users\bcespedes\OneDrive - Traarepuestos\Escritorio\U Fide\Ufide 3er cuatri\Ambiente Web\Proyecto\Data"

@app.route('/login', methods=['GET', 'POST']) #GET no sensitive data / POST sensitive data
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.callproc('passwordUsernameVerification', [username, password])
        account = cursor.fetchone()
        if account:
            session['Loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('Loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/login/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            return redirect(url_for('signup.html'))
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return redirect(url_for('signup.html'))
        elif not re.match(r'[A-Za-z0-9]+', username):
            return redirect(url_for('signup.html'))
        elif not username or not password or not email:
            return redirect(url_for('signup.html'))
        else:
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
    elif request.method == 'POST':
        return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/crudRolesUser')
def roles():
    return render_template('crudRolesUser.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    if 'Loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return render_template('login.html')

@app.route('/contact_us')
def contact_us():
    return render_template('contact_us.html')

@app.route('/add_faces', methods=['GET', 'POST'])
def add_faces():
    if request.method == 'POST':
        # Obtén el nombre del usuario y el archivo de video subido
        person_name = request.form['person_name']
        video_file = request.files['video']

        # Validar que se suba un archivo de video
        if not video_file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            return "El archivo subido no es un video válido. Usa formatos: MP4, AVI, MOV, MKV.", 400

        # Crear carpeta para el usuario si no existe
        person_path = os.path.join(ROSTROS_DIR, person_name)
        if not os.path.exists(person_path):
            os.makedirs(person_path)

        # Guardar el archivo de video temporalmente
        video_path = os.path.join(person_path, video_file.filename)
        video_file.save(video_path)

        # Procesar el video para extraer rostros
        try:
            extraer_rostros(video_path, person_path)
        except Exception as e:
            return f"Error al procesar el video: {e}", 500

        # Entrenar modelos con los rostros capturados
        try:
            entrenar_modelos(ROSTROS_DIR)
        except Exception as e:
            return f"Error al entrenar los modelos: {e}", 500

        # Retorna la plantilla con un mensaje de éxito
        return render_template('add_faces.html', success=True, person_name=person_name)

    return render_template('add_faces.html', success=False)

def extraer_rostros(video_path, person_path):
    cap = cv2.VideoCapture(video_path)
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = imutils.resize(frame, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aux_frame = frame.copy()

        # Detectar caras
        faces = face_classifier.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            rostro = aux_frame[y:y+h, x:x+w]
            rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
            rostro_path = os.path.join(person_path, f'rostro_{count}.jpg')
            cv2.imwrite(rostro_path, rostro)
            count += 1

        if count >= 500:  # Límite de rostros capturados
            break

    cap.release()
    if count == 0:
        raise ValueError("No se detectaron rostros en el video.")

def entrenar_modelos(ruta_imagenes):
    eigenface_model = cv2.face.EigenFaceRecognizer_create()
    fisherface_model = cv2.face.FisherFaceRecognizer_create()
    lbph_model = cv2.face.LBPHFaceRecognizer_create()

    imagenes_entrenamiento = []
    etiquetas_entrenamiento = []
    nombres_personas = {}
    etiqueta_actual = 0

    for nombre_persona in os.listdir(ruta_imagenes):
        ruta_persona = os.path.join(ruta_imagenes, nombre_persona)
        if not os.path.isdir(ruta_persona):
            continue

        nombres_personas[etiqueta_actual] = nombre_persona

        for archivo in os.listdir(ruta_persona):
            ruta_imagen = os.path.join(ruta_persona, archivo)
            imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)
            if imagen is None:
                continue

            imagen = cv2.resize(imagen, (200, 200))
            imagenes_entrenamiento.append(imagen)
            etiquetas_entrenamiento.append(etiqueta_actual)

        etiqueta_actual += 1

    imagenes_entrenamiento = np.array(imagenes_entrenamiento)
    etiquetas_entrenamiento = np.array(etiquetas_entrenamiento)

    eigenface_model.train(imagenes_entrenamiento, etiquetas_entrenamiento)
    fisherface_model.train(imagenes_entrenamiento, etiquetas_entrenamiento)
    lbph_model.train(imagenes_entrenamiento, etiquetas_entrenamiento)

    eigenface_model.write(os.path.join(ROSTROS_DIR, 'modeloEigenFace.xml'))
    fisherface_model.write(os.path.join(ROSTROS_DIR, 'modeloFisherFace.xml'))
    lbph_model.write(os.path.join(ROSTROS_DIR, 'modeloLBPHFace.xml'))

    print("Modelos entrenados y guardados correctamente.")

@app.route('/delete_faces', methods=['GET', 'POST'])
def delete_faces():
    if request.method == 'POST':
        # Obtener el nombre del rostro seleccionado para eliminar
        face_to_delete = request.form.get('face')
        face_path = os.path.join(ROSTROS_DIR, face_to_delete)

        # Verificar si la carpeta existe y eliminarla
        if os.path.exists(face_path) and os.path.isdir(face_path):
            shutil.rmtree(face_path)  # Eliminar la carpeta y su contenido
            return redirect(url_for('delete_faces'))
        else:
            return "Carpeta no encontrada o ya eliminada.", 404

    # Obtener todas las carpetas (rostros registrados) en la ruta especificada
    folders = [f for f in os.listdir(ROSTROS_DIR) if os.path.isdir(os.path.join(ROSTROS_DIR, f))]
    return render_template('delete_faces.html', folders=folders)

@app.route('/test_recognition', methods=['GET', 'POST'])
def test_recognition():
    if request.method == 'POST':
        # Esta lógica puede ser usada si necesitas subir un archivo o enviar datos al servidor
        pass
    return render_template('test_recognition.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        # Obtener datos del frame enviado
        data = request.get_json()
        frame_data = data['frame']

        # Convertir la imagen base64 a un formato que OpenCV pueda procesar
        frame_data = frame_data.split(',')[1]
        frame_bytes = base64.b64decode(frame_data)
        frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
        frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

        # Procesar el frame para reconocimiento facial
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        rostros = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

        if len(rostros) == 0:
            return jsonify({"name": "No se detectó ningún rostro."})

        # Seleccionar el primer rostro detectado para reconocimiento
        x, y, w, h = rostros[0]
        rostro_recortado = gray_frame[y:y+h, x:x+w]
        rostro_redimensionado = cv2.resize(rostro_recortado, (200, 200))

        # Cargar los modelos
        eigenface_model = cv2.face.EigenFaceRecognizer_create()
        fisherface_model = cv2.face.FisherFaceRecognizer_create()
        lbph_model = cv2.face.LBPHFaceRecognizer_create()

        eigenface_model.read('modeloEigenFace.xml')
        fisherface_model.read('modeloFisherFace.xml')
        lbph_model.read('modeloLBPHFace.xml')

        nombres_personas = ["Astrid", "Brandon"]

        # Predicciones
        label_lbph, confidence_lbph = lbph_model.predict(rostro_recortado)
        name_lbph = nombres_personas[label_lbph] if confidence_lbph < 90 else "Desconocido"

        return jsonify({"name": name_lbph})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

