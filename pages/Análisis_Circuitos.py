import streamlit as st
from Iniciacion import SetUp
from AnálisisCircuitos import AnalisisCircuitos
import pandas as pd
import plotly.express as px

if 'setup' not in st.session_state:
    with st.spinner('Se están cargando los datos de la aplicación. Por favor, espere. Esto puede tardar unos minutos... 😃'):
        setup = SetUp()
        st.session_state.setup = setup
setup = st.session_state.setup

anal_cir = AnalisisCircuitos(setup)

st.title("Análisis de Circuitos")


def graficar_media_pit_stops():
    media_pit_stops, _ = anal_cir.get_media_pitstops()
    anal_cir.graficar_media_y_desviacion(media_pit_stops, 'Media_Pit_Stops', 'Desviacion_Pit_Stops')   

def graficar_adelantamientos():
    adelantamientos, _ = anal_cir.get_adelantamientos()
    anal_cir.graficar_media_y_desviacion(adelantamientos, 'Adelantamientos', 'Desviacion_Adelantamientos')
    anal_cir.similitudes(adelantamientos, 'Adelantamientos')

def graficar_tiempo_parada():
    tiempo_parada, _ = anal_cir.get_tiempo_parada()
    anal_cir.graficar_media_y_desviacion(tiempo_parada, 'Media_Tiempo_Parada', 'Desviacion_Tiempo_Parada')
    anal_cir.similitudes(tiempo_parada, 'Media_Tiempo_Parada')

def graficar_tiempo_vuelta():
    tiempo_por_vuelta, _ = anal_cir.get_tiempo_por_vuelta()
    anal_cir.graficar_media_y_desviacion(tiempo_por_vuelta, 'Tiempo_medio', 'Desviacion_tiempo_medio')
    anal_cir.similitudes(tiempo_por_vuelta, 'Tiempo_medio')

def graficar_velocidad_media():
    velocidad_media, _ = anal_cir.get_velocidad_media()
    anal_cir.graficar_media_y_desviacion(velocidad_media, 'Velocidad_media', 'Desviacion_velocidad_media')
    anal_cir.similitudes(velocidad_media, 'Velocidad_media')

def graficar_safety_veces():
    safety_veces, _ = anal_cir.get_safety_veces()
    safety_veces.rename(columns = {'Race': 'Evento'}, inplace = True)
    anal_cir.graficar_media_y_desviacion(safety_veces, 'Safety_Veces', 'Safety_Veces_Desviacion')
    anal_cir.similitudes(safety_veces, 'Safety_Veces')

def graficar_degradacion():
    _, data = anal_cir.get_degradacion()
    normalized_data = (data.iloc[:, 1:] - data.iloc[:, 1:].min()) / (data.iloc[:, 1:].max() - data.iloc[:, 1:].min())
    normalized_data.fillna(1, inplace=True)
    eventos = data["Evento"]

    merged_data = pd.concat([eventos, normalized_data], axis=1)

    selected_evento = st.selectbox("Selecciona un evento:", eventos)

    degradacion = merged_data[merged_data["Evento"] == selected_evento]

    r = degradacion.iloc[:, 1:].values.tolist()[0]

    df = pd.DataFrame(dict(
        r=r,
        theta=['DegradacionSoft', 'DegradacionMedium', 'DegradacionHard']))
    
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                tickfont=dict(color='black') 
                )
            )
    )

    st.plotly_chart(fig)

    anal_cir.get_speed_track(selected_evento)

def graficar_curvas():
    if 'curvas' not in st.session_state:
        with st.spinner('Se están cargando los datos de la aplicación. Por favor, espere. Esto puede tardar unos minutos... 😃'):
            tipos_curvas = anal_cir.get_tipos_curvas()
            st.session_state.curvas = tipos_curvas

    st.session_state.curvas.rename(columns = {'Circuito': 'Evento'}, inplace = True)

    eventos = st.session_state.curvas["Evento"]

    selected_evento = st.selectbox("Selecciona un evento:", eventos)

    degradacion = st.session_state.curvas[st.session_state.curvas["Evento"] == selected_evento]

    r = degradacion.iloc[:, 1:].values.tolist()[0]

    df = pd.DataFrame(dict(
        r=r,
        theta=['Curvas_Lentas', 'Curvas_Medias', 'Curvas_Rápidas']))
    
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                tickfont=dict(color='black') 
                )
            )
    )

    st.plotly_chart(fig)

    anal_cir.get_speed_track(selected_evento)

def graficar_cambios_posiciones():
    selected_año = st.selectbox("Selecciona un año:", anal_cir.años)

    claves_eventos = []

    for año, eventos in anal_cir.carreras.items():
        for evento in eventos:
            claves_eventos.append(evento)
    selected_evento = st.selectbox("Selecciona un evento:", claves_eventos)

    anal_cir.graficar_posiciones(selected_año, selected_evento)
    anal_cir.graficar_cambio_stint(selected_año, selected_evento)

selected_option = st.selectbox(
    "Selecciona una opción:",
    ("Media Pit Stops", "Adelantamientos", "Cambio de Posiciones", "Tiempo de Parada", "Tiempo de Vuelta", "Velocidad Media", "Safety Veces", "Degradación", "Curvas")
)

if selected_option == "Media Pit Stops":
    graficar_media_pit_stops()
elif selected_option == "Adelantamientos":
    graficar_adelantamientos()
elif selected_option == "Cambio de Posiciones":
        graficar_cambios_posiciones()
elif selected_option == "Tiempo de Parada":
    graficar_tiempo_parada()
elif selected_option == "Tiempo de Vuelta":
    graficar_tiempo_vuelta()
elif selected_option == "Velocidad Media":
    graficar_velocidad_media()
elif selected_option == "Safety Veces":
    graficar_safety_veces()
elif selected_option == "Degradación":
    graficar_degradacion()
elif selected_option == "Curvas":
    graficar_curvas()