import streamlit as st
from google.cloud import storage
import pyrebase

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import firestore

from google.cloud import storage
import gcsfs
import os
import pandas as pd
import time
import numpy as np

import altair as alt

import re
# %%% Firebase
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
db_firebase = firebase.database()

# %%% Cloud Storage
# Cloud conexión
# Llave para autenticacion del cliente
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'Credenciales/skilled-orbit-401601-1c9280b4aa9b.json'

# Inizializar el cliente
client = storage.Client()
bucket = client.get_bucket('equipo8-ia2')

# %%% Funciones
def color_survived(val):
    if val == 'Inasistencia': 
        color = '#ff2b2b'
    elif val == 'Bajo': 
        color = '#ffabab'
    elif val == 'Medio': 
        color = '#83c9ff'
    else: color = '#0068c9'
    return f'background-color: {color}'
    
def get_matricula(local_id):
    return db_firebase.child(local_id).child("Matricula").get().val()

def participacion_plot(columnas_b, df_total):
    fechas = [cadena.split("_")[1] for cadena in columnas_b]
    conteo_part = pd.DataFrame(df_total[columnas_b].sum())
    conteo_part.index = fechas
    conteo_part.reset_index(inplace=True)
    conteo_part.columns = ['Fecha', 'Total de participaciones']

    base = alt.Chart(conteo_part).encode(x='Fecha')

    rule = alt.Chart(conteo_part).mark_rule(color='salmon').encode(
        alt.Y('mean(Total de participaciones)',))
    bar = base.mark_bar(cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3).encode(alt.Y('Total de participaciones', title = 'Total de participaciones'))

    chart = (bar + rule).properties(width=600)
    st.altair_chart(chart, theme="streamlit", use_container_width=True)


def asistencia_plot(columnas_a, df_total):

    index, counts = np.unique(
        df_total[columnas_a].to_numpy(), return_counts=True)
    suma = pd.DataFrame(counts,  index)
    suma = suma.reindex(['Inasistencia', 'Bajo', 'Medio', 'Alto'])
    suma.reset_index(inplace=True)
    suma.columns = ['Tipo', 'Asistencias']
    
    selection = alt.selection_point(fields=['Tipo'], bind='legend')
    chart = alt.Chart(suma).mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3
    ).encode(
        alt.X("Tipo", sort= ['Inasistencia', 'Bajo', 'Medio', 'Alto']),
        y='Asistencias',
        color=alt.Color('Tipo', scale = alt.Scale(domain = ['Inasistencia', 'Bajo', 'Medio', 'Alto'], range = ['#ff2b2b','#ffabab','#83c9ff','#0068c9'])),
        opacity=alt.condition(selection, alt.value(0.8), alt.value(0.2))
    ).add_params(selection)
    st.altair_chart(chart, theme="streamlit", use_container_width=True)

# %%% User de login
with open("shared_variable.txt", "r") as file:
    user = file.read()

# %%% Logo
col1, col2, col3 = st.columns([1,6,1])

with col1:
    st.image('Imagenes/logo.png', width = 110, output_format = 'PNG')

with col2:
    st.image('Imagenes/nombre.png', width = 180, output_format = 'PNG')

if user != 'LogOut':
    rol = db_firebase.child(user).child("Rol").get().val()

    # %% DOCENTE
    if rol == 'Docente':
        with col3:
            st.image('Imagenes/docente.png', width = 180, output_format = 'PNG')
        # %%% PRIMER FILTRO - Selección de cursos
        # Selección de cursos a la cual le usuarie tiene acceso
        cursos = sorted(db_firebase.child(user).child("Materias").get().val().split('_'))
        filtro1, filtro2, filtro3 = st.columns(3)

        if not cursos:
            st.error(
                'No tienes cursos asignados, por favor contacta al departamento de soporte')

        else:
            # %%% SELECCIÓN DE CURSOS
            with filtro1:
                curso = st.selectbox("Selecciona un curso", cursos, index=None)
                if curso:
                    # clave y gpo del curso seleccionado
                    curso_selec = curso.split('.')
                    # Folder del curso seleccionado
                    folder = bucket.list_blobs(
                        prefix='Cursos/'+curso_selec[0]+'/' + curso_selec[1] + '/')

                    # Nombres de los parquets (fechas) del curso
                    parquets_curso = [document.name for document in folder]

            # %% Fechas registradas en ese curso
            with filtro2:
                fechas_curso = []
                if curso:
                    for fecha in parquets_curso:
                        fechas_curso.append(fecha[fecha.rfind("/") + 1:-8])
                    if not fechas_curso:
                        st.error('No hay reportes de este curso, intenta otro día')
                    else:
                        fecha_selec = st.selectbox(
                            "Selecciona una fecha", ['Todas las fechas'] + fechas_curso, index=None)
                        if fecha_selec == 'Todas las fechas':
                            df_total = pd.DataFrame({'LocalID': pd.read_parquet(
                                "gs://equipo8-ia2/" + parquets_curso[0])['LocalID']})
                            for parquet in parquets_curso:
                                df = pd.read_parquet(
                                    "gs://equipo8-ia2/" + parquet)[['Asistencia', 'Participacion']]
                                df_total['Asistencia_' +
                                        parquet.split('/')[-1].split('.')[0]] = df['Asistencia']
                                df_total['Participacion_' +
                                        parquet.split('/')[-1].split('.')[0]] = df['Participacion']
                            df_total.insert(loc=0, column="Matrícula",
                                            value=df_total['LocalID'].apply(get_matricula))
                            df_total.drop('LocalID', axis=1, inplace=True)
                            with filtro3:
                                alumnx_selec = st.multiselect("Selecciona unx alumnx", options=np.insert(
                                    df_total['Matrícula'].to_numpy(), 0, 'Todxs'), default=['Todxs'])

            # %% FILTRO ALUMNXS
            if fechas_curso and fecha_selec:
                st.title('Registro de clase')

                # %% Todxs alumnxs
                if (fecha_selec == 'Todas las fechas'):
                    st.write(
                        'Si desea editar la información favor de seleccionar una fecha individualmente')
                    if alumnx_selec and ('Todxs' in alumnx_selec):
                        part, asist, todo = st.tabs(
                            ['Participación', 'Asistencia', 'Todo'])

                        with part:
                            columnas_b = [
                                columna for columna in df_total.columns if columna.startswith('P')]
                            df_part = df_total[columnas_b +
                                            ['Matrícula']].set_index('Matrícula')
                            df_part.columns = fechas_curso
                            st.write(df_part)

                            participacion_plot(columnas_b, df_total)
                        with asist:
                            columnas_a = [
                                columna for columna in df_total.columns if columna.startswith('A')]
                            df_asist = df_total[columnas_a +
                                                ['Matrícula']].set_index('Matrícula')
                            df_asist.columns = fechas_curso
                            st.table(df_asist.style.applymap(color_survived, subset=pd.IndexSlice[:, fechas_curso]))
                            conteo_por_columna_a = df_total[columnas_a].value_counts()
                            asistencia_plot(columnas_a, df_total)

                        with todo:
                            #st.write(df_total.set_index('Matrícula'))
                            st.table(df_total.set_index('Matrícula').style.applymap(color_survived, subset=pd.IndexSlice[:, columnas_a]))

                    # %% Ciertxs alumnxs
                    elif alumnx_selec and ~('Todxs' in alumnx_selec):
                        df_graf = df_total[df_total['Matrícula'].isin(
                            alumnx_selec)]
                        part, asist, todo = st.tabs(
                            ['Participación', 'Asistencia', 'Todo'])

                        with part:
                            columnas_b = [
                                columna for columna in df_graf.columns if columna.startswith('P')]
                            df_part = df_graf[columnas_b +
                                            ['Matrícula']].set_index('Matrícula')
                            df_part.columns = fechas_curso
                            st.write(df_part)

                            participacion_plot(columnas_b, df_graf)
                        with asist:
                            columnas_a = [
                                columna for columna in df_graf.columns if columna.startswith('A')]
                            df_asist = df_graf[columnas_a +
                                            ['Matrícula']].set_index('Matrícula')
                            df_asist.columns = fechas_curso
                            st.table(df_asist.style.applymap(color_survived, subset=pd.IndexSlice[:, fechas_curso]))
                            conteo_por_columna_a = df_graf[columnas_a].value_counts()
                            asistencia_plot(columnas_a, df_graf)

                        with todo:
                            st.table(df_graf.set_index('Matrícula').style.applymap(color_survived, subset=pd.IndexSlice[:, columnas_a]))
                            #st.write(df_graf.set_index('Matrícula'))

                # %% FECHA ÚNICA
                elif fecha_selec:
                    col1, col2 = st.columns([0.45,0.55])

                    with col1:
                        # Leer el parquet y convertirlo en df
                        path = '/'.join(parquets_curso[0].split('/')
                                        [0:-1]) + '/' + fecha_selec + '.parquet'
                        df = pd.read_parquet("gs://equipo8-ia2/" + path)
                        df["Matrícula"] = df["LocalID"].apply(get_matricula)
                        st.write('Haga click en la celda de asistencia o participación para modificar el valor')
                        edited_df = st.data_editor(df[['Matrícula', 'Asistencia', 'Participacion']],
                                                hide_index=True,
                                                disabled=['Matrícula'],
                                                column_config={
                            "Participacion": st.column_config.NumberColumn(
                                label = 'Participación',
                                help='Ingresa un valor numérico',
                                min_value=0),

                            'Asistencia': st.column_config.SelectboxColumn(
                                help='Selecciona una opción',
                                options=['Inasistencia', 'Bajo', 'Medio', 'Alto'])
                        })
                        save = st.button('Guardar cambios')
                        if save:
                            blob = bucket.blob(path)
                            df['Asistencia'] = edited_df['Asistencia']
                            df['Participacion'] = edited_df['Participacion']
                            blob.upload_from_string(df.drop('Matrícula', axis=1).to_parquet(
                                compression='gzip'), '.parquet')
                            st.toast('¡Cambios guardados!')

                        df_final = df[['Matrícula', 'Asistencia', 'Participacion']]

                    with col2:
                        asistencia_plot(['Asistencia'], df_final)

    # %% ESTUDIANTE
    elif rol == 'Estudiante':
        with col3:
            st.image('Imagenes/estudiante.png', width = 180, output_format = 'PNG')
        # %%% PRIMER FILTRO - Selección de cursos
        # Selección de cursos a la cual le usuarie tiene acceso
        cursos = sorted(db_firebase.child(user).child(
            "Materias").get().val().split('_'))
        filtro1, filtro2 = st.columns(2)

        if not cursos:
            st.error(
                'No tienes cursos asignados, por favor contacta al departamento de soporte')

        else:
            # %%% SELECCIÓN DE CURSOS
            with filtro1:
                curso = st.selectbox("Selecciona un curso", cursos, index=None)
                if curso:
                    # clave y gpo del curso seleccionado
                    curso_selec = curso.split('.')
                    # Folder del curso seleccionado
                    folder = bucket.list_blobs(
                        prefix='Cursos/'+curso_selec[0]+'/' + curso_selec[1] + '/')

                    # Nombres de los parquets (fechas) del curso
                    parquets_curso = [document.name for document in folder]

            # %% Fechas registradas en ese curso
            with filtro2:
                fechas_curso = []
                if curso:
                    for fecha in parquets_curso:
                        fechas_curso.append(fecha[fecha.rfind("/") + 1:-8])
                    if not fechas_curso:
                        st.error('No hay reportes de este curso, intenta otro día')
                    else:
                        fecha_selec = st.selectbox(
                            "Selecciona una fecha", ['Todas las fechas'] + fechas_curso, index=None)
                        if fecha_selec == 'Todas las fechas':
                            df_total = pd.DataFrame({'LocalID': [user]})
                            for parquet in parquets_curso:
                                df = pd.read_parquet(
                                    "gs://equipo8-ia2/" + parquet)[['LocalID','Asistencia', 'Participacion']]
                                df = df[df['LocalID'] == user]
                                df_total['Asistencia_' +
                                        parquet.split('/')[-1].split('.')[0]] = df['Asistencia'].values
                                df_total['Participacion_' +
                                        parquet.split('/')[-1].split('.')[0]] = df['Participacion'].values
                                
                            df_total.drop('LocalID', axis=1, inplace=True)

            # %% FILTRO ALUMNXS
            if fechas_curso and fecha_selec:
                st.title('Registro de clase')

                # %% Todxs alumnxs
                if (fecha_selec == 'Todas las fechas'):
                    part, asist = st.tabs(
                        ['Participación', 'Asistencia'])

                    with part:
                        columnas_b = [
                            columna for columna in df_total.columns if columna.startswith('P')]
                        df_part = df_total[columnas_b]
                        df_part.columns = fechas_curso
                        participacion_plot(columnas_b, df_total)
                    with asist:
                        columnas_a = [
                            columna for columna in df_total.columns if columna.startswith('A')]
                        df_asist = df_total[columnas_a]
                        df_asist.columns = fechas_curso
                        st.table(df_asist.style.applymap(color_survived, subset=pd.IndexSlice[:, fechas_curso]))
                        asistencia_plot(columnas_a, df_total)

                # %% FECHA ÚNICA
                elif fecha_selec:
                    # Leer el parquet y convertirlo en df
                    path = '/'.join(parquets_curso[0].split('/')
                                    [0:-1]) + '/' + fecha_selec + '.parquet'
                    df = pd.read_parquet("gs://equipo8-ia2/" + path)
                    df = df[df["LocalID"] == user]                

                    asist = df['Asistencia'].values[0]
                    part = df['Participacion'].values[0]

                    col1, col2,col3 = st.columns(3)
                    with col1:
                        st.subheader('Asistencia')
                        if asist == 'Alto':
                            st.markdown(f'<p style="background-color:#0068c9;color:##222222;font-size:20px;border-radius:2%;text-align: center">{asist}</p>', unsafe_allow_html=True)
                        elif asist == 'Bajo':
                            st.markdown(f'<p style="background-color:#ffabab;color:##222222;font-size:20px;border-radius:2%;text-align: center">{asist}</p>', unsafe_allow_html=True)
                        elif asist == 'Inasistencia':
                            st.markdown(f'<p style="background-color:#ff2b2b;color:##222222;font-size:20px;border-radius:2%;text-align: center">{asist}</p>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<p style="background-color:#83c9ff;color:##222222;font-size:20px;border-radius:2%;text-align: center">{asist}</p>', unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader('Participación')
                        if part == 0:
                            st.markdown(f'<p style="background-color:#ff2b2b;color:##222222;font-size:20px;border-radius:2%;text-align: center">{part}</p>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<p style="background-color:#02AA6D;color:##222222;font-size:20px;border-radius:2%;text-align: center">{part}</p>', unsafe_allow_html=True)
                    
    else:
        with col3:
            st.write('')
        st.info(' Favor de ingresar con una cuenta', icon = '⚠️')

else:
    with col3:
        st.write('')
    st.info(' Favor de ingresar con una cuenta', icon = '⚠️')
