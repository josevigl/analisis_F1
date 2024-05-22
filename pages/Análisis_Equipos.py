import streamlit as st
from Iniciacion import SetUp
from AnálisisEquipos import AnalisisEquipos

if 'setup' not in st.session_state:
    with st.spinner('Se están cargando los datos de la aplicación. Por favor, espere. Esto puede tardar unos minutos... 😃'):
        setup = SetUp()
        st.session_state.setup = setup
setup = st.session_state.setup

anal_eq = AnalisisEquipos(setup)
st.title("Análisis de Equipos")

def graficar_posicion_media():
    df_posiciones = anal_eq.get_posicion_media()
    anal_eq.grafico_barras(df_posiciones, 'GridPosition')

def graficar_tiempo_parada():
    df_tiempo_parada = anal_eq.get_diferencia_tiempo()
    anal_eq.grafica_diferencia(df_tiempo_parada, 'segundos')

def graficar_numero_paradas():
    df_paradas = anal_eq.get_veces_parada()
    anal_eq.grafico_barras(df_paradas, 'Ratio')

graficar_posicion_media()
graficar_tiempo_parada()
graficar_numero_paradas()