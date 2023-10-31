# Modules
import pyrebase
import streamlit as st
from datetime import datetime
import requests
import re
import os
import numpy as np
import uuid

# Create data
import cv2
import sys
import numpy
import time
from google.cloud import storage

# Plataforma
from streamlit_option_menu import option_menu

# Configuration Key
def subir_foto(foto, email, password):
    # Tamaño de la imagen
    (width, height) = (130, 100) 

    #Conexion con Google Storage 
    # Llave para autenticacion del cliente
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/fernandaalcubilla/Desktop/IA-2/Reto/skilled-orbit-401601-1c9280b4aa9b.json'

    # Inizializar el cliente
    client = storage.Client()
    bucket = client.get_bucket('equipo8-ia2')

    # Streamlit 
    haar_file =  '/Users/fernandaalcubilla/Desktop/IA-2/Reto/haarcascade_frontalface_default.xml'
    datasets = 'Fotos_caras'   # nombre del folder donde se guardarán los datos
    # Lee el contenido del archivo como bytes
    cont = True
    while cont:
        if foto:
            file_bytes = foto.read()
            # Convierte los bytes a una matriz NumPy
            image = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), -1)
            image = np.array(image)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
            face_cascade = cv2.CascadeClassifier(haar_file) 
            faces = face_cascade.detectMultiScale(gray, 1.3, 4) 
            if len(faces) == 0:
                st.error('No se detectaron caras, favor de subir una foto correcta')
                cont = False
                return False
            else:
                user = auth.create_user_with_email_and_password(email, password)
                sub_data = datasets + '/' + user['localId'] + '/'  # nombre del sub-folder donde se guardarán los datos (nombre de la persona)
                # path donde se guardarán las imagenes
                if not os.path.isdir(sub_data):
                    os.mkdir(sub_data)
                for (x, y, w, h) in faces: 
                    face = gray[y:y + h, x:x + w] 
                    face_resize = cv2.resize(face, (width, height)) 

                    image_name = f"{user['localId']}.jpg"
                    blob = bucket.blob(f"{sub_data}{image_name}")

                    _, buffer = cv2.imencode('.jpg', face_resize)  # Convierte la imagen a un formato de bytes
                    blob.upload_from_string(buffer.tobytes(), content_type='image/jpg')
                st.success('Foto subida con éxito')
                st.success('Cuenta creada:)')
                st.balloons()
                cont = False
                return user

def login(auth,email,password, db):
    login_butt = st.button('Ingresar')
    if login_butt:
        try:
            user = auth.sign_in_with_email_and_password(email,password)
            return user
        except requests.exceptions.HTTPError as e:
                error = str(e)
                if "INVALID_LOGIN_CREDENTIALS" in error:
                    st.error("Contraseña/Correo incorrecto.")
                else:
                    st.error("Error desconocido: " + error)

def signup(auth, email, password, db,foto):
    st.write('Al crear la cuenta acepto :blue[_términos y condiciones_]')

    submit = st.button('Crear cuenta')
    if submit:
        if '@tec.mx' not in email: # Verificar email
            st.error('Favor de ingresar cuenta institucional')
        elif not foto:
            st.error('Favor de subir una foto')
        else:
            try:
                mat = email.split('@tec.mx')[0].lower() # obtener antes del @tec.mx
                user = subir_foto(foto, email, password)
                if not(user == False):

                    # ROl
                    if 'a0' in mat: 
                        db.child(user['localId']).child("Rol").set('Estudiante')
                    else: db.child(user['localId']).child("Rol").set('Docente')

                    db.child(user['localId']).child("ID").set(user['localId'])
                    db.child(user['localId']).child("Matricula").set(mat)
                    return user                
            except requests.exceptions.HTTPError as e:
                error = str(e)
                if "WEAK_PASSWORD" in error:
                    st.error("Error: La contraseña debe tener al menos 6 caracteres.")
                elif 'EMAIL_EXISTS' in error:
                    st.error('Error: El correo ya se encuentra registrado')
                else:
                    st.error("Error desconocido: " + error)

def main(auth, db):
    selected_main = option_menu(
        menu_title = None,
        options = ['LogIn','SignUp'],
        icons = ['house','book'],
        menu_icon = 'cast',
        default_index = 0,
        orientation = 'horizontal',
    )

    st.title("Plataforma de Asistencia")

    # Obtain User Input for email and password
    email = st.text_input('Correo institucional')
    password = st.text_input('Contraseña',type = 'password')

    # App 
    # Sign up Block
    if selected_main == 'SignUp':
        foto = st.file_uploader("Escoge un archivo", type = ['jpg'])
        user = signup(auth, email, password, db,foto)
        return user

    # Login Block
    if selected_main == 'LogIn':
        user = login(auth, email, password, db)
        return user

if __name__ == '__main__':
    # Firestore
    firebaseConfig = {
    'apiKey': "AIzaSyCe0jECqvsCJbYmsaXnhT9AQnzUBD46LoU",
    'authDomain': "usuariosia8.firebaseapp.com",
    'databaseURL': 'https://usuariosia8-default-rtdb.firebaseio.com',
    'projectId': "usuariosia8",
    'storageBucket': "usuariosia8.appspot.com",
    'messagingSenderId': "145062237299",
    'appId': "1:145062237299:web:eb6f04789919705da68606",
    'measurementId': "G-K1QLESC9MX"
    }
    
    # Firebase Authentication
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()

    # Database
    db = firebase.database()
    user = main(auth, db)
    if user is not None:
        rol = db.child(user['localId']).child("Rol").get().val()
        if rol == 'Docente':
            url = "http://localhost:8500"  # Asegúrate de que la URL sea correcta
            st.write(f"Click [aquí](<{url}>) para abrir la plataforma", unsafe_allow_html=True)
            with open("shared_variable.txt", "w") as file:
                file.write(user['localId'])

        else:
            url = "http://localhost:8504"  # Asegúrate de que la URL sea correcta
            st.write(f"Click [aquí](<{url}>) para abrir la plataforma", unsafe_allow_html=True)
            with open("shared_variable.txt", "w") as file:
                file.write(user['localId'])


