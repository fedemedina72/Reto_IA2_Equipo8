import streamlit as st
import cv2
import sys
import numpy
import os 
import time
from google.cloud import storage

#Conexion con Google Storage 
##llave para autenticacion del cliente
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/fernandaalcubilla/Desktop/IA-2/Reto/skilled-orbit-401601-1c9280b4aa9b.json'

#inizializar el cliente
client = storage.Client()
bucket = client.get_bucket('equipo8-ia2')


# Streamlit 

st.title("Obtención de fotos")

haar_file =  '/Users/fernandaalcubilla/Desktop/IA-2/Reto/haarcascade_frontalface_default.xml'

datasets = 'Fotos_caras'   # nombre del folder donde se guardarán los datos
st.subheader('Matrícula', divider = 'rainbow')
mat = st.text_input('Ingresa una matrícula para continuar', placeholder = 'A00')

if mat != '':
    mat = mat.strip() # eliminar espacios en blanco
    sub_data = datasets + '/' + mat + '/'  # nombre del sub-folder donde se guardarán los datos (nombre de la persona)
    # path donde se guardarán las imagenes
    if not os.path.isdir(sub_data):
        os.mkdir(sub_data)
        
    # tamaño de la imagen
    (width, height) = (130, 100)   

    # Iniciar la cámara web
    face_cascade = cv2.CascadeClassifier(haar_file) 
    webcam = cv2.VideoCapture(0)

    # Agregar un botón para iniciar y detener la grabación
    recording = st.checkbox("Iniciar Grabación")

    if recording:
        st.warning("Grabando... Presiona el botón de nuevo para detener.")

    # Captura de video en tiempo real y escritura en el archivo
    foto = 0
    num_fotos = 3
    while recording and foto < num_fotos:
        (_,im) = webcam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY) 
        faces = face_cascade.detectMultiScale(gray, 1.3, 4) 
        for (x, y, w, h) in faces: 
            face = gray[y:y + h, x:x + w] 
            face_resize = cv2.resize(face, (width, height)) 

            image_name = f"{mat}_{foto}.jpg"
            blob = bucket.blob(f"{sub_data}{image_name}")

            _, buffer = cv2.imencode('.png', face_resize)  # Convierte la imagen a un formato de bytes
            blob.upload_from_string(buffer.tobytes(), content_type='image/png')
            
            time.sleep(0.2)
            foto += 1
        if foto == num_fotos: 
            st.write('Fotos tomadas con éxito')
            webcam.release()
            cv2.destroyAllWindows()
        
    # Liberar la cámara y el archivo de video al detener la grabación
    if not recording:
        webcam.release()
        cv2.destroyAllWindows()