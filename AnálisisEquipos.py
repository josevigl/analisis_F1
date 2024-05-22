import seaborn as sns
from matplotlib import pyplot as plt
import plotly.express as px
import streamlit as st
import pandas as pd
import statsmodels.api as sm
import numpy as np
import pandas as pd
from Iniciacion import SetUp


class AnalisisEquipos:
    def __init__(self, setup) :
        self.carreras = setup.carreras
        self.años = setup.años
        self.eventos = setup.eventos
        self.set_carreras()
        self.team_colores = {
            'Toro Rosso':'#0000FF',
            'Mercedes':'#6CD3BF',
            'Red Bull Racing':'#1E5BC6',
            'Ferrari':'#ED1C24',
            'Williams':'#37BEDD',
            'Renault':'#FFD800',
            'McLaren':'#F58020',
            'Haas F1 Team':'#B6BABD',
            'Racing Point':'#F596C8',
            'Aston Martin':'#2D826D',
            'Alfa Romeo':'#B12039',
            'Alfa Romeo Racing':'#B12039',
            'AlphaTauri':'#4E7C9B',
            'Alpine':'#2293D1'
        }

    def set_carreras(self):
        self.drivers = {}
        for año in self.años:
            pilotos = {}
            for evento in self.eventos[año]:
                pilotos[evento] = self.carreras[año][evento].drivers
                self.drivers[año] = pilotos

    def grafico_barras(self, data, variable):
        data['Color'] = data['Equipo'].map(lambda equipo: self.team_colores.get(equipo, '#808080'))
        data = data.sort_values(by=variable)

        st.subheader(f'Gráfico de Barras de {variable.capitalize()} por Equipo')
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(range(len(data)), data[variable], color=data['Color'], alpha=0.7)
        ax.legend(bars, data['Equipo'], title='Equipo', loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_xlabel('Equipos')
        ax.set_ylabel(f'{variable.capitalize()}')
        ax.set_title(f'Gráfico de Barras de {variable.capitalize()} por Equipo')
        ax.set_xticks([])  
        st.pyplot(fig)

    def grafica_diferencia(self, data, variable):
        tiempo_menor = data[variable].min()
        data['diferencia'] = data[variable] - tiempo_menor
        data = data.sort_values('diferencia')
        data['Color'] = data['Equipo'].map(lambda equipo: self.team_colores.get(equipo, '#808080'))

        st.subheader('Gráfico de Barras de Diferencia de Tiempo')
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(range(len(data)), data['diferencia'], color=data['Color'], alpha=0.7)
        for index, value in enumerate(data['diferencia']):
            ax.text(value, index, f'+{value:.2f}', va='center')
        ax.legend(bars, data['Equipo'], title='Equipo', loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_xlabel('Diferencia de Tiempo')
        ax.set_ylabel('Equipos')
        ax.set_title('Gráfico de Barras de Diferencia de Tiempo')
        st.pyplot(fig)

    def get_posicion_media(self):
        data = {'Año': [], 'Evento': [], 'Equipo': [], 'GridPosition': []}

        for año in self.años:
            for evento in self.eventos[año]:
                carrera = self.carreras[año][evento]
                resultados = carrera.results[['TeamName', 'GridPosition']]
                
                data['Año'].extend([año] * len(resultados))
                data['Evento'].extend([evento] * len(resultados))
                data['Equipo'].extend(resultados['TeamName'])
                data['GridPosition'].extend(resultados['GridPosition'])

        df_clasificacion = pd.DataFrame(data)
        df_clasificacion = df_clasificacion.groupby('Equipo').mean().reset_index()
        df_clasificacion = df_clasificacion.drop('Año', axis=1)

        return df_clasificacion
    
    def get_diferencia_tiempo(self):
        paradas = pd.read_csv('Ergast/pit_stops.csv')
        races = pd.read_csv('Ergast/races.csv')
        circuito = pd.read_csv('Ergast/circuits.csv')
        df_drivers = pd.read_csv('Ergast/drivers.csv')

        races = races[["raceId","year","name","circuitId"]]
        races = races.rename(columns={'name':'Evento'})

        circuito = circuito[["circuitId","alt"]]

        df_drivers = df_drivers[["driverId","code"]]

        paradas = paradas[["raceId","driverId","lap","milliseconds"]]
        paradas = paradas[paradas["milliseconds"] < 50000]
        paradas["segundos"] = paradas["milliseconds"] / 1000

        df_join = pd.merge(paradas, races, left_on='raceId', right_on='raceId', how='left')
        df_join = pd.merge(df_join, circuito, left_on='circuitId', right_on='circuitId', how='left')
        df_join = pd.merge(df_join, df_drivers, left_on='driverId', right_on='driverId', how='left')

        df_ergast = df_join[df_join["year"] >= 2019]

        df_ergast = df_ergast[["year","segundos","Evento","code"]]
        df_ergast = df_ergast.reset_index()
        df_ergast = df_ergast.drop('index', axis=1)
        df_ergast = df_ergast.rename(columns={'code': 'Piloto'})
        df_ergast = df_ergast.rename(columns={'year': 'Año'})

        data = {'Año': [], 'Evento': [], 'Piloto': [], 'Equipo': []}

        for año in self.años:
            for evento in self.eventos[año]:
                carrera = self.carreras[año][evento]
                resultados = carrera.results[['Abbreviation', 'TeamName']]

                data['Año'].extend([año] * len(resultados))
                data['Evento'].extend([evento] * len(resultados))
                data['Piloto'].extend(resultados['Abbreviation'])
                data['Equipo'].extend(resultados['TeamName'])

        data = pd.DataFrame(data)
        df_equipos = pd.merge(df_ergast,data, on=['Año', 'Evento', 'Piloto'])

        df_equipos = df_equipos.groupby('Equipo')['segundos'].mean().reset_index()

        return df_equipos


    def get_veces_parada(self):
        paradas = pd.read_csv('Ergast/pit_stops.csv')
        races = pd.read_csv('Ergast/races.csv')
        circuito = pd.read_csv('Ergast/circuits.csv')
        df_drivers = pd.read_csv('Ergast/drivers.csv')

        races = races[["raceId","year","name","circuitId"]]
        races = races.rename(columns={'name':'Evento'})

        circuito = circuito[["circuitId","alt"]]

        df_drivers = df_drivers[["driverId","code"]]

        paradas = paradas[["raceId","driverId","lap","milliseconds"]]
        paradas = paradas[paradas["milliseconds"] < 50000]
        paradas["segundos"] = paradas["milliseconds"] / 1000

        df_join = pd.merge(paradas, races, left_on='raceId', right_on='raceId', how='left')
        df_join = pd.merge(df_join, circuito, left_on='circuitId', right_on='circuitId', how='left')
        df_join = pd.merge(df_join, df_drivers, left_on='driverId', right_on='driverId', how='left')

        df_ergast = df_join[df_join["year"] >= 2019]

        df_ergast = df_ergast[["year","segundos","Evento","code"]]
        df_ergast = df_ergast.reset_index()
        df_ergast = df_ergast.drop('index', axis=1)
        df_ergast = df_ergast.rename(columns={'code': 'Piloto'})
        df_ergast = df_ergast.rename(columns={'year': 'Año'})

        data = {'Año': [], 'Evento': [], 'Piloto': [], 'Equipo': []}

        for año in self.años:
            for evento in self.eventos[año]:
                carrera = self.carreras[año][evento]
                resultados = carrera.results[['Abbreviation', 'TeamName']]

                data['Año'].extend([año] * len(resultados))
                data['Evento'].extend([evento] * len(resultados))
                data['Piloto'].extend(resultados['Abbreviation'])
                data['Equipo'].extend(resultados['TeamName'])

        data = pd.DataFrame(data)
        df_equipos = pd.merge(df_ergast,data, on=['Año', 'Evento', 'Piloto'])
        conteo_equipos = df_equipos['Equipo'].value_counts()

        df_conteo = pd.DataFrame({'Equipo': conteo_equipos.index, 'PitStops': conteo_equipos.values})

        conteo_eventos = df_equipos.groupby(['Equipo', 'Año'])['Evento'].nunique().reset_index(name='Eventos')

        conteo = conteo_eventos.groupby('Equipo')['Eventos'].sum().reset_index(name='Total_Eventos')

        veces_parada = pd.merge(df_conteo, conteo, on='Equipo')

        veces_parada['Ratio'] = veces_parada['PitStops'] / veces_parada['Total_Eventos']

        veces_parada = veces_parada[["Equipo","Ratio"]]
        veces_parada = veces_parada.sort_values('Ratio')

        return veces_parada
