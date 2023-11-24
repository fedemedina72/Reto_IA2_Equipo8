# Modules
import streamlit as st
from datetime import datetime
import requests
import re
import os
import numpy as np
import cv2
from google.cloud import storage
from streamlit_option_menu import option_menu
import pyrebase


def subir_foto(foto, email, password):
    # Tamaño de la imagen
    (width, height) = (130, 100) 

    #Conexion con Google Storage 
    # Llave para autenticacion del cliente
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Credenciales/skilled-orbit-401601-1c9280b4aa9b.json'

    # Inizializar el cliente
    client = storage.Client()
    bucket = client.get_bucket('equipo8-ia2')

    # Streamlit 
    haar_file =  'Credenciales/haarcascade_frontalface_default.xml'
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
                #sub_data = datasets + '/' + user['localId'] + '/'  # nombre del sub-folder donde se guardarán los datos (nombre de la persona)
                # path donde se guardarán las imagenes
                #if not os.path.isdir(sub_data):
                #    os.mkdir(sub_data)
                for (x, y, w, h) in faces: 
                    face = gray[y:y + h, x:x + w] 
                    face_resize = cv2.resize(face, (width, height)) 

                    image_name = f"{user['localId']}.jpg"
                    blob = bucket.blob(f"{'Fotos_caras/'}{image_name}")

                    _, buffer = cv2.imencode('.jpg', face_resize)  # Convierte la imagen a un formato de bytes
                    blob.upload_from_string(buffer.tobytes(), content_type='image/jpg')
                st.success('Foto subida con éxito')
                st.success('Cuenta creada:)')
                st.balloons()
                cont = False
                return user

# %% LOGIN
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

# %% SIGNUP
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
    col1, col2, col3 = st.columns([1,6,1])

    with col1:
        st.image('Imagenes/logo.png', width = 110, output_format = 'PNG')

    with col2:
        st.image('Imagenes/nombre.png', width = 180, output_format = 'PNG')
    
    with col3: st.write('')

    selected_main = option_menu(
        menu_title = None,
        options = ['LogIn','SignUp','LogOut'],
        icons = ['house','book', 'gear'],
        menu_icon = 'cast',
        default_index = 0,
        orientation = 'horizontal',
    )

    st.title("Plataforma de Asistencia")

    if selected_main == 'LogOut':
        return 'LogOut'

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
    # %% Firestore
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

    # %% RESUMEN
    # Database
    db = firebase.database()
    user = main(auth, db)
    if user is not None:
        if user != 'LogOut':
            with open("shared_variable.txt", "w") as file:
                file.write(user['localId'])
            st.info('Selecciona la opción de Plataforma en el menú', icon = '↖️')
        else:
            with open("shared_variable.txt", "w") as file:
                file.write('LogOut')
            st.success('Cuenta cerrada exitosamente')


