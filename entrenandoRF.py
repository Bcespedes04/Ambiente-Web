import cv2
import os
import numpy as np

dataPath = 'C:/Users/bcespedes/OneDrive - Traarepuestos/Escritorio/U Fide/Ufide 3er cuatri/Ambiente Web/Proyecto/Data'
peopleList = os.listdir(dataPath)
print('Lista de personas: ', peopleList)

labels = []
facesData = []
label = 0

for nameDir in peopleList:
    personPath = dataPath + '/' + nameDir
    print('Leyendo las imagenes')

    for fileName in os.listdir(personPath):
        print('Rostros: ', nameDir + '/' + fileName)
        labels.append(label)
        facesData.append(cv2.imread(personPath+'/'+fileName,0))
        image = cv2.imread(personPath+'/'+fileName,0)
        #cv2.imshow('image', image)
        #cv2.waitKey(10)
    label = label + 1

#print('labels = ',labels)
#print('Número de etiquetas 0: ',np.count_nonzero(np.array(labels)==0))

#face_recognizer = cv2.face.EigenFaceRecognizer_create()
#face_recognizer = cv2.face.FisherFaceRecognizer_create()
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# Entrenando el reconocedor de rostros
print("Entrenando...")
face_recognizer.train(facesData, np.array(labels))

# Almacenando el modelo obtenido
# face_recognizer.write('modeloEigenFace.xml')
# face_recognizer.write('modeloFisherFace.xml')
face_recognizer.write('modeloLBPHFFace.xml')
print("Modelo almacenado...")






