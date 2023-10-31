import streamlit as st
from streamlit_option_menu import option_menu
from google.cloud import storage
import pyrebase

# DB
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

# Share files
with open("shared_variable.txt", "r") as file:
    user = file.read()

selected = option_menu(
        menu_title = None,
        options = ['Home','Mis cursos','Estadísticas'],
        icons = ['house','book'],
        menu_icon = 'cast',
        default_index = 0,
        orientation = 'horizontal',
    )

if selected == 'Home':
    st.title('Plataforma Docentes')
    st.subheader('Cuenta: ' + db.child(user).child("Matricula").get().val())


if selected == 'Mis cursos':
    st.title('Cursos')


if selected == 'Estadísticas':
    st.title('Estadisticas')
