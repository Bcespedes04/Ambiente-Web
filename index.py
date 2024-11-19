from flask import Flask, render_template, request, redirect, url_for
import os
import shutil

app = Flask(__name__)

# Ruta donde se encuentran las carpetas de los rostros registrados
ROSTROS_DIR = r"C:\Users\bcespedes\OneDrive - Traarepuestos\Escritorio\U Fide\Ufide 3er cuatri\Ambiente Web\Proyecto\Data"

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/crudRolesUser')
def roles():
    return render_template('crudRolesUser.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/add_faces')
def add_faces():
    return render_template('add_faces.html')

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

@app.route('/test_recognition')
def test_recognition():
    return render_template('test_recognition.html')

if __name__ == '__main__':
    app.run(debug=True)

