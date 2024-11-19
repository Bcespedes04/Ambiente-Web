import cv2
import os
import numpy as np

# Directorio con las imágenes de entrenamiento
ruta_imagenes = 'C:\\Users\\bcespedes\\OneDrive - Traarepuestos\\Escritorio\\U Fide\\Ufide 3er cuatri\\Ambiente Web\\Proyecto\\Data'

# Inicializar modelos de reconocimiento
eigenface_model = cv2.face.EigenFaceRecognizer_create()
fisherface_model = cv2.face.FisherFaceRecognizer_create()
lbph_model = cv2.face.LBPHFaceRecognizer_create()

# Preparar datos de entrenamiento
imagenes_entrenamiento = []
etiquetas_entrenamiento = []
nombres_personas = {}
etiqueta_actual = 0

# Recorrer carpetas y cargar imágenes de entrenamiento
for nombre_persona in os.listdir(ruta_imagenes):
    ruta_persona = os.path.join(ruta_imagenes, nombre_persona)
    if not os.path.isdir(ruta_persona):
        continue
    
    # Mapear etiqueta con el nombre de la persona
    nombres_personas[etiqueta_actual] = nombre_persona
    
    # Leer las imágenes de la persona
    for archivo in os.listdir(ruta_persona):
        ruta_imagen = os.path.join(ruta_persona, archivo)
        imagen = cv2.imread(ruta_imagen, cv2.IMREAD_GRAYSCALE)  # Convertir a escala de grises
        if imagen is None:
            continue
        
        # Redimensionar la imagen a 200x200 para Eigenfaces y Fisherfaces
        imagen = cv2.resize(imagen, (200, 200))
        
        # Añadir imagen y etiqueta
        imagenes_entrenamiento.append(imagen)
        etiquetas_entrenamiento.append(etiqueta_actual)
    
    etiqueta_actual += 1

# Convertir listas a matrices de NumPy
imagenes_entrenamiento = np.array(imagenes_entrenamiento)
etiquetas_entrenamiento = np.array(etiquetas_entrenamiento)

# Entrenar cada modelo con las imágenes de entrenamiento
eigenface_model.train(imagenes_entrenamiento, etiquetas_entrenamiento)
fisherface_model.train(imagenes_entrenamiento, etiquetas_entrenamiento)
lbph_model.train(imagenes_entrenamiento, etiquetas_entrenamiento)

# Guardar los modelos entrenados en archivos XML
eigenface_model.write('modeloEigenFace.xml')
fisherface_model.write('modeloFisherFace.xml')
lbph_model.write('modeloLBPHFace.xml')

print("Modelos entrenados y guardados correctamente.")


