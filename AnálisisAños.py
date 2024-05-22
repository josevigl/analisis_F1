import seaborn as sns
import streamlit as st
from matplotlib import pyplot as plt
import plotly.express as px
import pandas as pd
import statsmodels.api as sm
import numpy as np
import pandas as pd
from Iniciacion import SetUp
from matplotlib.animation import FuncAnimation


class AnalisisAños:
    def __init__(self, setup) :
        self.carreras = setup.carreras
        self.años = setup.años
        self.eventos = setup.eventos
        self.set_carreras()

    def set_carreras(self):
        self.drivers = {}
        for año in self.años:
            pilotos = {}
            for evento in self.eventos[año]:
                pilotos[evento] = self.carreras[año][evento].drivers
                self.drivers[año] = pilotos

    def graficar_eventos(self, eventos):
        años = pd.DataFrame(list(eventos.items()), columns=['Año', 'Grandes_Premios'])
        años = años.explode('Grandes_Premios')
        años.reset_index(drop=True, inplace=True)

        st.subheader('Número de Grandes Premios por Año')
        st.write(años.groupby('Año').size())
        plt.figure(figsize=(10, 6))
        plt.hist(años['Año'], bins=len(años['Año'].unique()), color='green', edgecolor='black')
        plt.title('Número de Grandes Premios por Año')
        plt.xlabel('Año')
        plt.ylabel('Número de Grandes Premios')
        plt.grid(True)
        st.pyplot()

    def graficar_pilotos(self, drivers):
        pilotos_por_año = pd.DataFrame([(year, race, driver) for year, races in drivers.items() for race, drivers_list in races.items() for driver in drivers_list],
                                        columns=['Año', 'Gran Premio', 'Número de Piloto'])

        pilotos_por_año['Número de Piloto'] = pd.to_numeric(pilotos_por_año['Número de Piloto'], errors='coerce')

        num_pilotos_por_año = pilotos_por_año.groupby('Año')['Número de Piloto'].nunique().reset_index()

        st.subheader('Número de Pilotos por Año')
        st.write(num_pilotos_por_año)
        plt.figure(figsize=(10, 6))
        plt.bar(num_pilotos_por_año['Año'], num_pilotos_por_año['Número de Piloto'], color='green')
        plt.title('Número de Pilotos por Año')
        plt.xlabel('Año')
        plt.ylabel('Número de Pilotos Únicos')
        plt.grid(True)
        st.pyplot()

    def grafica_barras_animada(self, data, variable):
        fig = px.bar(data, x=variable, y='Evento', orientation='h', 
                    title=f'Media de {variable.capitalize()} por Evento',
                    animation_frame='Año')
        fig.update_layout(yaxis_title='Evento', xaxis_title=f'Media de {variable.capitalize()}')
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 3000
        fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 2000

        fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        fig.update_layout(barmode='stack', height=len(data["Evento"]) * 5.3)

        st.plotly_chart(fig)