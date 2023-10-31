import streamlit as st
from streamlit_option_menu import option_menu
from google.cloud import storage
import pyrebase

# DB
firebaseConfig = {
    'apiKey': "",
    'authDomain': "",
    'databaseURL': '',
    'projectId': "",
    'storageBucket': "",
    'messagingSenderId': "",
    'appId': "",
    'measurementId': ""
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
    menu_title=None,
    options=['Home', 'Mis cursos'],
    icons=['house', 'book'],
    menu_icon='cast',
    default_index=0,
    orientation='horizontal',
)

if selected == 'Home':
    st.title('Plataforma Estudiantes')
    st.subheader('Cuenta: ' + db.child(user).child("Matricula").get().val())

if selected == 'Mis cursos':
    st.title('Cursos')
