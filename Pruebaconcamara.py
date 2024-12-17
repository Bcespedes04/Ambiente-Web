import cv2
import os

# Cargar el clasificador de rostros de OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Cargar los modelos entrenados desde los archivos XML
eigenface_model = cv2.face.EigenFaceRecognizer_create()
fisherface_model = cv2.face.FisherFaceRecognizer_create()
lbph_model = cv2.face.LBPHFaceRecognizer_create()

eigenface_model.read('modeloEigenFace.xml')
fisherface_model.read('modeloFisherFace.xml')
lbph_model.read('modeloLBPHFace.xml')  # Asegúrate de que el nombre del archivo sea correcto

# Lista de nombres de personas, en el mismo orden de las etiquetas de entrenamiento
nombres_personas = ["Astrid", "Brandon"]

# Inicializar la cámara
video_capture = cv2.VideoCapture(0)

while True:
    # Capturar un solo frame de video
    ret, frame = video_capture.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detectar caras en el frame de video
    rostros = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in rostros:
        rostro_recortado = gray_frame[y:y+h, x:x+w]
        
        # Redimensionar el rostro para Eigenfaces y Fisherfaces (requisito de estos modelos)
        rostro_redimensionado = cv2.resize(rostro_recortado, (200, 200))
        
        # Reconocimiento con cada modelo
        label_eigen, confidence_eigen = eigenface_model.predict(rostro_redimensionado)
        label_fisher, confidence_fisher = fisherface_model.predict(rostro_redimensionado)
        label_lbph, confidence_lbph = lbph_model.predict(rostro_recortado)
        
        # Mostrar resultados en el frame
        name_eigen = nombres_personas[label_eigen] if confidence_eigen < 5900 else "Desconocido"
        name_fisher = nombres_personas[label_fisher] if confidence_fisher < 500 else "Desconocido"
        name_lbph = nombres_personas[label_lbph] if confidence_lbph < 90 else "Desconocido"

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, f"Eigen: {name_eigen}", (x, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"Fisher: {name_fisher}", (x, y-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"LBPH: {name_lbph}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Mostrar el frame resultante
    cv2.imshow('Video', frame)

    # Salir del bucle cuando se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar el recurso de la cámara y cerrar ventanas
video_capture.release()
cv2.destroyAllWindows()