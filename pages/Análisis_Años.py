import streamlit as st
from Iniciacion import SetUp
from AnálisisCircuitos import AnalisisCircuitos
from AnálisisAños import AnalisisAños

if 'setup' not in st.session_state:
    with st.spinner('Se están cargando los datos de la aplicación. Por favor, espere. Esto puede tardar unos minutos... 😃'):
        setup = SetUp()
        st.session_state.setup = setup
setup = st.session_state.setup

anal_cir = AnalisisCircuitos(setup)
anal_a = AnalisisAños(setup)
st.title("Análisis de Años")

def graficar_media_pit_stops():
    _ , media_pit_stops = anal_cir.get_media_pitstops()
    anal_a.grafica_barras_animada(media_pit_stops, 'Media_Pit_Stops')

def graficar_adelantamientos():
    _, adelantamientos = anal_cir.get_adelantamientos()
    anal_a.grafica_barras_animada(adelantamientos, 'Adelantamientos')

def graficar_tiempo_vuelta():
    _, tiempo_por_vuelta = anal_cir.get_tiempo_por_vuelta()
    anal_a.grafica_barras_animada(tiempo_por_vuelta, 'Tiempo_medio')

def graficar_velocidad_media():
    _, velocidad_media = anal_cir.get_velocidad_media()
    anal_a.grafica_barras_animada(velocidad_media, 'Velocidad_media')


selected_option = st.selectbox(
    "Selecciona una opción:",
    ("Media Pit Stops", "Adelantamientos", "Tiempo de Vuelta", "Velocidad Media")
)

if selected_option == "Media Pit Stops":
    graficar_media_pit_stops()
elif selected_option == "Adelantamientos":
    graficar_adelantamientos()
elif selected_option == "Tiempo de Vuelta":
    graficar_tiempo_vuelta()
elif selected_option == "Velocidad Media":
    graficar_velocidad_media()
