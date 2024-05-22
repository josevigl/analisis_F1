import streamlit as st
from Iniciacion import SetUp
from AnálisisPilotos import AnalisisPilotos

if 'setup' not in st.session_state:
    with st.spinner('Se están cargando los datos de la aplicación. Por favor, espere. Esto puede tardar unos minutos... 😃'):
        setup = SetUp()
        st.session_state.setup = setup
setup = st.session_state.setup

anal_pil = AnalisisPilotos(setup)
st.title("Análisis de Pilotos")
st.set_option('deprecation.showPyplotGlobalUse', False)

def graficar_telemetria():
    años = anal_pil.años

    años_selection = st.selectbox("Selecciona un año", años)

    eventos = anal_pil.eventos[años_selection]

    evento_selection = st.selectbox("Selecciona un evento", eventos)

    pilotos = anal_pil.carreras[años_selection][evento_selection].laps["Driver"].unique().tolist()
    laps = anal_pil.carreras[años_selection][evento_selection].laps["LapNumber"].unique().tolist()

    piloto1 = st.selectbox("Selecciona un piloto", pilotos)
            
    piloto2 = st.selectbox("Selecciona otro piloto", pilotos)

    lapNumber = st.selectbox("Selecciona una vuelta", laps)

    anal_pil.get_telemetria(años_selection, evento_selection, piloto1, piloto2, lapNumber)

def graficar_degradacion():
    años = anal_pil.años

    años_selection = st.selectbox("Selecciona un año", años)

    eventos = anal_pil.eventos[años_selection]

    evento_selection = st.selectbox("Selecciona un evento", eventos)

    vueltas = anal_pil.carreras[años_selection][evento_selection].laps

    pilotos = vueltas["Driver"].unique().tolist()

    piloto1 = st.selectbox("Selecciona un piloto", pilotos)

    stint1 = vueltas[vueltas["Driver"] == piloto1]["Stint"].unique().tolist()
            
    piloto2 = st.selectbox("Selecciona otro piloto", pilotos)

    stint2 = vueltas[vueltas["Driver"] == piloto2]["Stint"].unique().tolist()

    stints = list(set(stint1) & set(stint2))

    stint = st.selectbox("Selecciona una vuelta", stints)

    anal_pil.get_degradacion(años_selection, evento_selection, piloto1, piloto2, stint)

def graficar_resultados():
    data = anal_pil.get_resultados()
    anal_pil.grafica_barras(data, "Position", "Abbreviation")

def graficar_adelantamientos():
    data = anal_pil.get_adelantamientos()
    anal_pil.grafica_barras(data, "Adelantamientos", "Abbreviation")

def graficar_posicion_salida():
    data = anal_pil.get_posicion()
    anal_pil.grafica_barras(data, "GridPosition", "Abbreviation")

selected_option = st.selectbox(
    "Selecciona una opción:",
    ("Telemetría", "Degradación", "Resultados", "Adelantamientos", "Posición de Salida")
)

if selected_option == "Telemetría":
    graficar_telemetria()
elif selected_option == "Degradación":
    graficar_degradacion()
elif selected_option == "Resultados":
    graficar_resultados()
elif selected_option == "Adelantamientos":
    graficar_adelantamientos()
elif selected_option == "Posición de Salida":
    graficar_posicion_salida()
