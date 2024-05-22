import streamlit as st
from collections import Counter
import pandas as pd
import os
import joblib
from PIL import Image
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import make_column_transformer
from keras.models import load_model
import numpy as np
from Iniciacion import SetUp
from sklearn.utils import all_estimators
from sklearn.model_selection import train_test_split

st.set_page_config(page_title="Predicción", page_icon="🏎️", initial_sidebar_state="collapsed")

st.markdown("""
<style>
body {
    background-color: black;
}
</style>
""", unsafe_allow_html=True)

st.markdown(""" <style>  
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)

padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)


if 'setup' not in st.session_state:
    with st.spinner('Se están cargando los datos de la aplicación. Por favor, espere. Esto puede tardar unos minutos... 😃'):
        setup = SetUp()
        st.session_state.setup = setup


st.markdown("<h1 style='text-align: center; color: gray;'>Predicción de paradas</h1>", unsafe_allow_html=True)
st.write("")
st.write("")

if 'carga_datos' not in st.session_state:
    st.session_state.carga_datos = True
    rf_model1 = joblib.load('modelos/best_random_forest_model1.pkl')
    svm_model1 = joblib.load('modelos/best_svm_model1.pkl')
    best_model_nn1 = load_model('modelos/best_model_nn1.keras')

    rf_model2 = joblib.load('modelos/best_random_forest_model2.pkl')
    svm_model2 = joblib.load('modelos/best_svm_model2.pkl')
    best_model_nn2 = load_model('modelos/best_model_nn2.keras')

    label_encoder = LabelEncoder()

    datos = pd.read_csv('datos.csv')

    datos2 = pd.read_csv('datos2.csv')

    X, y = datos.drop("Parar", axis="columns"), datos["Parar"]

    v_continuas = ['Tiempo_Parada', 'Tiempo_Por_Vuelta', 'Curvas_Lentas', 'Curvas_Medias', 'Curvas_Rápidas', 
                            'Año', 'LapNumber', 'Stint', 'TyreLife', 'TrackStatus', 'Position', 'Tiempo_Antes_Pit', 
                            'Tiempo_Delante', 'Tiempo_Detras', 'TrackTemp']

    v_discretas =  ['Evento','Deg_Blando','Deg_Medio','Deg_Duro','Driver','Compound','Team','Piloto_Delante',
                    'Piloto_Detras','Parada_Delante','Parada_Detras', 'Rainfall', 'Tráfico']

    X_train, _, _, _ = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


    type_filter = ["classifier", "transformer"] 

    arguments = {"type_filter": type_filter}
    estimators = all_estimators(**arguments)
    estimators = dict(estimators) 

    standarscaler = estimators["StandardScaler"]()

    columnTransformerAvanzado = make_column_transformer((standarscaler, v_continuas),
                                                        (OneHotEncoder(handle_unknown='ignore'), v_discretas))

    st.session_state.X = X
    st.session_state.columnTransformerAvanzado = columnTransformerAvanzado
    st.session_state.rf_model1 = rf_model1
    st.session_state.svm_model1 = svm_model1
    st.session_state.best_model_nn1 = best_model_nn1
    st.session_state.rf_model2 = rf_model2
    st.session_state.svm_model2 = svm_model2
    st.session_state.best_model_nn2 = best_model_nn2
    st.session_state.datos2 = datos2
    st.session_state.X_train = X_train

    data_dict = {}

    for index, row in X.iterrows():
        value_col1 = row['Evento']
        value_col2 = row['Tiempo_Parada']
        value_col3 = row['Tiempo_Por_Vuelta']
        value_col4 = row['Curvas_Lentas']
        value_col5 = row['Curvas_Medias']
        value_col6 = row['Curvas_Rápidas']
        value_col7 = row['Deg_Blando']
        value_col8 = row['Deg_Medio']
        value_col9 = row['Deg_Duro']
        
        if value_col1 not in data_dict:
            data_dict[value_col1] = {}
            
            data_dict[value_col1] = (value_col2, value_col3, value_col4, value_col5, value_col6, value_col7, value_col8, value_col9)

    st.session_state.data_dict = data_dict

def ensemble(data):
    rf_model1 = st.session_state.rf_model1
    svm_model1 = st.session_state.svm_model1
    best_model_nn1 = st.session_state.best_model_nn1
    rf_model2 = st.session_state.rf_model2
    svm_model2 = st.session_state.svm_model2
    best_model_nn2 = st.session_state.best_model_nn2
    columnTransformerAvanzado = st.session_state.columnTransformerAvanzado

    X_train = st.session_state.X_train

    X_train1 = X_train.copy()

    rf_predictions = rf_model1.predict(data) 

    svm_predictions = svm_model1.predict(data)

    X_train_processed = columnTransformerAvanzado.fit_transform(X_train1)

    data_processed = columnTransformerAvanzado.transform(data)
    data_processed_tensor = tf.convert_to_tensor(data_processed.todense(), dtype=tf.float32)

    y_test_pred = best_model_nn1.predict(data_processed_tensor)
    nn_predictions = np.argmax(y_test_pred, axis=1)

    final_predictions = []

    for rf_pred, svm_pred, nn_pred in zip(rf_predictions, svm_predictions, nn_predictions):
        all_preds = [svm_pred]
        class_counts = Counter(all_preds)
        majority_class = class_counts.most_common(1)[0][0]
        
        if majority_class == 0:
            final_predictions.append("no")
        else:
            final_predictions.append("si")

    if final_predictions[0] == "si":

        datos2 = st.session_state.datos2
        
        columnas = datos2.columns.tolist()
        columnas2 = columnas.copy()
        columnas2 = columnas2.remove('CompuestoBueno')

        X_trainA = X_train.copy()

        X_train2 = X_trainA.merge(datos2[columnas], on=columnas2, how='inner')

        X_train2 = X_train2[X_train2['CompuestoBueno'] != 'UNKNOWN']

        X_train2 = X_train2.drop("CompuestoBueno", axis=1)

        X_train_processed2 = columnTransformerAvanzado.fit_transform(X_train2)

        rf_predictions = rf_model2.predict(data) 

        svm_predictions = svm_model2.predict(data) 

        data_processed2 = columnTransformerAvanzado.transform(data)
        data_processed_tensor2 = tf.convert_to_tensor(data_processed2.todense(), dtype=tf.float32)

        y_test_pred = best_model_nn2.predict(data_processed_tensor2)
        nn_predictions = np.argmax(y_test_pred, axis=1)
   
        # Hacer el voto por mayoría para cada instancia
        final_predictions = []

        for rf_pred, svm_pred, nn_pred in zip(rf_predictions, svm_predictions, nn_predictions):
            all_preds = [rf_pred, svm_pred, nn_pred]
            class_counts = Counter(all_preds)
            majority_class = class_counts.most_common(1)[0][0]
            
            # En caso de un triple empate
            if len(class_counts) == 3:
                dry_tyres = ['HARD', 'MEDIUM', 'SOFT']
                wet_tyres = ['INTERMEDIATE', 'WET']
                dry_counts = sum(class_counts.get(tyre, 0) for tyre in dry_tyres)
                wet_counts = sum(class_counts.get(tyre, 0) for tyre in wet_tyres)
                
                if dry_counts == 1 and wet_counts == 2:
                    majority_class = 'INTERMEDIATE'
                elif dry_counts == 2 and wet_counts == 1:
                    majority_class = rf_pred
                elif dry_counts == 3:
                    majority_class = rf_pred
            
            final_predictions.append(majority_class)
            

    return final_predictions[0]


X = st.session_state.X

col1, col2, col3, col4 = st.columns(4)

dict_track_status = {
    "Clear": 1,
    "Safety Car": 4,
    "Yellow Flag": 2,
    "Red Flag": 5,
    "VSC": 6
}

track_status_values = ["Clear", "Safety Car", "Yellow Flag", "Red Flag", "VSC"]

with col1:
    evento = st.selectbox("Evento", X["Evento"].unique().tolist())
    driver = st.selectbox("Driver", X["Driver"].unique().tolist())  
    compound = st.selectbox("Compound", ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"])
    piloto_delante = st.selectbox("Piloto Delante", X["Piloto_Delante"].unique().tolist())
    parada_delante = st.checkbox("Parada Delante")
    
with col2:
    año = st.selectbox("Año", X["Año"].unique().tolist())
    lap_number = st.number_input("Lap Number", min_value=1, max_value=100, value=1)
    tyre_life = st.number_input("Tyre Life", min_value=0, max_value=100, value=0) 
    tiempo_antes_pit = st.number_input("Tiempo Antes Pit (seg.)", min_value=0.0, max_value=100.0, value=0.0)
    parada_detras = st.checkbox("Parada Detras")

with col3:  
    stint = st.number_input("Stint", min_value=1, max_value=10, value=1)
    team = st.selectbox("Team", X["Team"].unique().tolist())
    track_status = st.selectbox("Track Status", track_status_values)
    track_status = dict_track_status[track_status]
    position = st.number_input("Position", min_value=1, max_value=20, value=1)
    rainfall = st.checkbox("Rainfall")

with col4:
    piloto_detras = st.selectbox("Piloto Detras", X["Piloto_Detras"].unique().tolist()) 
    tiempo_delante = st.number_input("Tiempo Delante (seg.)", min_value=0.0, max_value=X["Tiempo_Delante"].max(), value=0.0)  
    tiempo_detras = st.number_input("Tiempo Detras (seg.)", min_value=0.0, max_value=X["Tiempo_Detras"].max(), value=0.0)
    track_temp = st.number_input("Track Temp", min_value=10, max_value=50, value=20)
    trafico = st.checkbox("Trafico")

data_dict = st.session_state.data_dict
datos = {
        "Evento": [evento],
        "Tiempo_Parada": [data_dict[evento][0]],
        "Tiempo_Por_Vuelta": [data_dict[evento][1]],
        "Curvas_Lentas": [data_dict[evento][2]],
        "Curvas_Medias": [data_dict[evento][3]],
        "Curvas_Rápidas": [data_dict[evento][4]],
        "Deg_Blando": [data_dict[evento][5]],
        "Deg_Medio": [data_dict[evento][6]],
        "Deg_Duro": [data_dict[evento][7]],
        "Año": [año],
        "Driver": [driver],
        "LapNumber": [lap_number],
        "Stint": [stint],
        "Compound": [compound],
        "TyreLife": [tyre_life],
        "Team": [team],
        "TrackStatus": [track_status],
        "Position": [position],
        "Tiempo_Antes_Pit": [tiempo_antes_pit],
        "Tiempo_Delante": [tiempo_delante],
        "Tiempo_Detras": [tiempo_detras],
        "Piloto_Delante": [piloto_delante],
        "Piloto_Detras": [piloto_detras],
        "Parada_Delante": [parada_delante],
        "Parada_Detras": [parada_detras],
        "Rainfall": [rainfall],
        "TrackTemp": [track_temp],
        "Tráfico": [trafico]
    }

df = pd.DataFrame(datos)

st.session_state.prediccion = False

st.write("")
st.write("")

def mostrar_imagenes(prediccion):
    st.write("")
    _, col2, _ = st.columns([14, 16, 12])
    try:
        with col2:
            if prediccion == "no":
                st.write("No hay que parar con esos datos")
            elif prediccion == "SOFT":
                path = os.path.join("images/soft.png")
                image = Image.open(path)
                st.image(image, caption='Se debe parar y poner blandos')
            elif prediccion == "MEDIUM":
                path = os.path.join("images/medium.png")
                image = Image.open(path)
                st.image(image, caption='Se debe parar y poner medios')
            elif prediccion == "HARD":
                path = os.path.join("images/hard.png")
                image = Image.open(path)
                st.image(image, caption='Se debe parar y poner duros')
            elif prediccion == "INTERMEDIATE":
                path = os.path.join("images/intermediate.png")
                image = Image.open(path)
                st.image(image, caption='Se debe parar y poner intermedios')
            elif prediccion == "WET":
                path = os.path.join("images/wet.png")
                image = Image.open(path)
                st.image(image, caption='Se debe parar y poner lluvia extrema')

    except Exception:
        st.write("Exception")

_, col2, _ = st.columns([16, 8, 13])

with col2:
    if st.button("Predict"):
        prediccion = ensemble(df)
        st.session_state.prediccion = True

if st.session_state.prediccion:
    mostrar_imagenes(prediccion)
    st.session_state.prediccion = False
