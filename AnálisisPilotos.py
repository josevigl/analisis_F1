import seaborn as sns
from matplotlib import pyplot as plt
import plotly.express as px
import pandas as pd
import streamlit as st
import statsmodels.api as sm
import numpy as np
import pandas as pd
from Iniciacion import SetUp
import fastf1


class AnalisisPilotos:
    def __init__(self,setup) :
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

    def grafica_barras(self, data, variable, variable_pilotos):
        data = data.sort_values(by=variable)
        plt.figure(figsize=(10, 6))
        colores = sns.color_palette("husl", n_colors=len(data))

        bars = plt.bar(range(len(data)), data[variable], color=colores, alpha=0.7)

        plt.legend(bars, data[variable_pilotos], title=variable_pilotos, loc='center left', bbox_to_anchor=(1, 0.5))

        plt.xlabel('Pilotos')
        plt.ylabel(f'{variable.capitalize()}')
        plt.title(f'{variable.capitalize()} por Piloto')
        plt.xticks([])  
        st.pyplot()

    def get_telemetria(self, año, evento, piloto1, piloto2, lapNumber):
        if año not in self.años or evento not in self.eventos[año]:
            st.warning("No se encontraron datos para el año y el evento especificados.")
            return

        carrera = self.carreras[año][evento]
        circuit_info = carrera.get_circuit_info()

        lap1 = carrera.laps.pick_drivers(piloto1).pick_lap(lapNumber)
        tel1 = lap1.get_car_data().add_distance()

        lap2 = carrera.laps.pick_drivers(piloto2).pick_lap(lapNumber)
        tel2 = lap2.get_car_data().add_distance()

        color1 = fastf1.plotting.driver_color(piloto1)
        color2 = fastf1.plotting.driver_color(piloto2)

        st.markdown(f"### Velocidad - {piloto1} vs {piloto2}")

        fig, ax = plt.subplots(figsize=(10, 6))
        v_min = tel1['Speed'].min()
        v_max = tel1['Speed'].max()
        ax.vlines(x=circuit_info.corners['Distance'], ymin=v_min-20, ymax=v_max+20,
                linestyles='dotted', colors='grey')
        ax.fill_between(tel1['Distance'], min(tel1['Speed']), max(tel1['Speed']), color='black')
        ax.plot(tel1['Distance'], tel1['Speed'], color=color1, label=piloto1)
        ax.plot(tel2['Distance'], tel2['Speed'], color=color2, label=piloto2)
        ax.set_xlabel('Distancia en m', color='white')
        ax.set_ylabel('Velocidad (km/h)', color='white')
        ax.set_title(f'Velocidad - {piloto1} vs {piloto2}', color='white')
        ax.legend(facecolor='black', loc='lower right', edgecolor='white', fontsize='small', framealpha=1, labelcolor='white')
        for index, corner in circuit_info.corners.iterrows():
            ax.annotate(f"{corner['Number']}{corner['Letter']}",
                        xy=(corner['Distance'], min(tel1['Speed']) - 30),
                        xytext=(corner['Distance'], min(tel1['Speed']) - 20),
                        ha='center', va='center', color='white', fontsize='small',
                        arrowprops=dict(arrowstyle='-', color='white'))
        ax.grid(True, color='white', linestyle='-', linewidth=0.5)
        ax.set_facecolor('black')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        st.pyplot(fig)

        st.markdown(f"### RPM - {piloto1} vs {piloto2}")

        fig, ax = plt.subplots(figsize=(10, 6))
        rpm_min = tel1['RPM'].min()
        rpm_max = tel1['RPM'].max()
        ax.vlines(x=circuit_info.corners['Distance'], ymin=rpm_min-2000, ymax=rpm_max+2000,
                linestyles='dotted', colors='grey')
        ax.fill_between(tel1['Distance'], min(tel1['RPM']), max(tel1['RPM']), color='black')
        ax.plot(tel1['Distance'], tel1['RPM'], color=color1, label=piloto1)
        ax.plot(tel2['Distance'], tel2['RPM'], color=color2, label=piloto2)
        ax.set_xlabel('Distancia en m', color='white')
        ax.set_ylabel('RPM', color='white')
        ax.set_title(f'RPM - {piloto1} vs {piloto2}', color='white')
        ax.legend(facecolor='black', loc='lower right', edgecolor='white', fontsize='small', framealpha=1, labelcolor='white')
        for index, corner in circuit_info.corners.iterrows():
            ax.annotate(f"{corner['Number']}{corner['Letter']}",
                        xy=(corner['Distance'], 4800),
                        xytext=(corner['Distance'], 5000),
                        ha='center', va='center', color='white', fontsize='small',
                        arrowprops=dict(arrowstyle='-', color='white'))
        ax.grid(True, color='white', linestyle='-', linewidth=0.5)
        ax.set_facecolor('black')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        st.pyplot(fig)

        st.markdown(f"### Marchas (Gear) - {piloto1} vs {piloto2}")

        fig, ax = plt.subplots(figsize=(10, 6))
        gear_min = tel1['nGear'].min()
        gear_max = tel1['nGear'].max()
        ax.vlines(x=circuit_info.corners['Distance'], ymin=gear_min-1, ymax=gear_max+1,
                linestyles='dotted', colors='grey')
        ax.fill_between(tel1['Distance'], min(tel1['nGear']), max(tel1['nGear']), color='black')
        ax.plot(tel1['Distance'], tel1['nGear'], color=color1, label=piloto1)
        ax.plot(tel2['Distance'], tel2['nGear'], color=color2, label=piloto2)
        ax.set_xlabel('Distancia en m', color='white')
        ax.set_ylabel('Marcha (Gear)', color='white')
        ax.set_title(f'Marchas - {piloto1} vs {piloto2}', color='white')
        ax.legend(facecolor='black', loc='lower right', edgecolor='white', fontsize='small', framealpha=1, labelcolor='white')
        for index, corner in circuit_info.corners.iterrows():
            ax.annotate(f"{corner['Number']}{corner['Letter']}",
                        xy=(corner['Distance'], 1.8),
                        xytext=(corner['Distance'], 1.6),
                        ha='center', va='center', color='white', fontsize='small',
                        arrowprops=dict(arrowstyle='-', color='white'))
        ax.grid(True, color='white', linestyle='-', linewidth=0.5)
        ax.set_facecolor('black')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        st.pyplot(fig)

        st.markdown(f"### Throttle - {piloto1} vs {piloto2}")

        fig, ax = plt.subplots(figsize=(10, 6))
        throttle_min = tel1['Throttle'].min()
        throttle_max = tel1['Throttle'].max()
        ax.vlines(x=circuit_info.corners['Distance'], ymin=throttle_min-5, ymax=throttle_max+5,
                linestyles='dotted', colors='grey')
        ax.fill_between(tel1['Distance'], min(tel1['Throttle']), max(tel1['Throttle']), color='black')
        ax.plot(tel1['Distance'], tel1['Throttle'], color=color1, label=piloto1)
        ax.plot(tel2['Distance'], tel2['Throttle'], color=color2, label=piloto2)
        ax.set_xlabel('Distancia en m', color='white')
        ax.set_ylabel('Acelerador (%)', color='white')
        ax.set_title(f'Acelerador - {piloto1} vs {piloto2}', color='white')
        ax.legend(facecolor='black', loc='lower right', edgecolor='white', fontsize='small', framealpha=1, labelcolor='white')
        for index, corner in circuit_info.corners.iterrows():
            ax.annotate(f"{corner['Number']}{corner['Letter']}",
                        xy=(corner['Distance'], -0.6),
                        xytext=(corner['Distance'],-0.4),
                        ha='center', va='center', color='white', fontsize='small',
                        arrowprops=dict(arrowstyle='-', color='white'))
        ax.grid(True, color='white', linestyle='-', linewidth=0.5)
        ax.set_facecolor('black')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        st.pyplot(fig)


    def get_degradacion(self, año, evento, piloto1, piloto2, stint):
        if año not in self.años or evento not in self.eventos[año]:
            st.warning("No se encontraron datos para el año y el evento especificados.")
            return

        carrera = self.carreras[año][evento].laps
        carrera['Laptime'] = carrera['LapTime'].dt.total_seconds()
        primeros_stint = carrera[carrera["Stint"] == stint]

        if primeros_stint["LapNumber"].max() < 10:
            primeros_stint = carrera[carrera["Stint"] == 2]

        stint1 = primeros_stint[primeros_stint["Driver"] == piloto1]
        stint2 = primeros_stint[primeros_stint["Driver"] == piloto2]

        if  stint1.loc[stint1.index[0], "Compound"] == "SOFT":
            color_stint1 = 'red'
        elif  stint1.loc[stint1.index[0], "Compound"] == "MEDIUM":
            color_stint1 = 'yellow'
        elif  stint1.loc[stint1.index[0], "Compound"] == "HARD":
            color_stint1 = 'white'
        elif  stint1.loc[stint1.index[0], "Compound"] == "WET":
            color_stint1 = 'blue'
        elif  stint1.loc[stint1.index[0], "Compound"] == "INTERMEDIATE":
            color_stint1 = 'green'

        if  stint2.loc[stint2.index[0], "Compound"] == "SOFT":
            color_stint2 = 'red'
        elif  stint2.loc[stint2.index[0], "Compound"] == "MEDIUM":
            color_stint2 = 'yellow'
        elif  stint2.loc[stint2.index[0], "Compound"] == "HARD":
            color_stint2 = 'white'
        elif  stint2.loc[stint2.index[0], "Compound"] == "WET":
            color_stint2 = 'blue'
        elif  stint2.loc[stint2.index[0], "Compound"] == "INTERMEDIATE":
            color_stint2 = 'green'

        tiempo_min_1 = stint1["Laptime"].min() * 1.05
        compuestos_1 = stint1[stint1["Laptime"] < tiempo_min_1]

        tiempo_min_2 = stint2["Laptime"].min() * 1.05
        compuestos_2 = stint2[stint2["Laptime"] < tiempo_min_2]

        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6))

        color1 = fastf1.plotting.driver_color(piloto1)
        color2 = fastf1.plotting.driver_color(piloto2)

        sns.scatterplot(x='LapNumber', y='Laptime', data=compuestos_1, color=color_stint1, label='Degradación '+ piloto1, ax=ax)
        sns.scatterplot(x='LapNumber', y='Laptime', data=compuestos_2, color=color_stint2, label='Degradación ' + piloto2, ax=ax)

        lowess_model_1 = sm.nonparametric.lowess(compuestos_1['Laptime'], compuestos_1['LapNumber'], frac=0.4)
        ax.plot(lowess_model_1[:, 0], lowess_model_1[:, 1], color=color1, label='Regresión Local - '+ piloto1)

        lowess_model_2 = sm.nonparametric.lowess(compuestos_2['Laptime'], compuestos_2['LapNumber'], frac=0.4)
        ax.plot(lowess_model_2[:, 0], lowess_model_2[:, 1], color=color2, label='Regresión Local - ' + piloto2)

        ax.set_title('Degradación entre '+ piloto1 + ' y ' + piloto2, fontsize=16)
        ax.set_xlabel('LapNumber', fontsize=14)
        ax.set_ylabel('Laptime', fontsize=14)

        ax.legend(fontsize='12', loc='upper right')

        st.pyplot(fig)

    def get_posicion(self):
        data = {'Año': [], 'Evento': [], 'Abbreviation': [], 'GridPosition': []}

        for año in self.años:
            for evento in self.eventos[año]:
                carrera = self.carreras[año][evento]
                resultados = carrera.results[['Abbreviation', 'GridPosition']]
                
                data['Año'].extend([año] * len(resultados))
                data['Evento'].extend([evento] * len(resultados))
                data['Abbreviation'].extend(resultados['Abbreviation'])
                data['GridPosition'].extend(resultados['GridPosition'])

        df_clasificacion = pd.DataFrame(data)
        df_clasificacion = df_clasificacion.groupby('Abbreviation').mean().reset_index()
        df_clasificacion = df_clasificacion.drop('Año', axis=1)

        return df_clasificacion
    
    def get_resultados(self):
        data = {'Año': [], 'Evento': [], 'Abbreviation': [], 'Position': []}

        for año in self.años:
            for evento in self.eventos[año]:
                carrera = self.carreras[año][evento]
                resultados = carrera.results[['Abbreviation', 'Position']]
                
                data['Año'].extend([año] * len(resultados))
                data['Evento'].extend([evento] * len(resultados))
                data['Abbreviation'].extend(resultados['Abbreviation'])
                data['Position'].extend(resultados['Position'])

        df_carrera = pd.DataFrame(data)
        df_carrera = df_carrera.groupby('Abbreviation').mean().reset_index()
        df_carrera = df_carrera.drop('Año', axis=1)

        return df_carrera
    
    def get_adelantamientos(self):
        data = {'Año': [], 'Evento': [], 'Abbreviation': [], 'Adelantamientos': []}

        for año in self.años:
            for evento in self.eventos[año]:
                vuelta = self.carreras[año][evento].laps

                adelantamientos_por_piloto = vuelta.groupby('Driver')['Position'].diff().lt(0).groupby(vuelta['Driver']).cumsum()

                vuelta['Adelantamientos'] = adelantamientos_por_piloto

                total_adelantamientos_por_piloto = vuelta.groupby('Driver')['Adelantamientos'].max()

                resultados = pd.DataFrame({'Piloto': total_adelantamientos_por_piloto.index, 'Adelantamientos': total_adelantamientos_por_piloto.values})

                data['Año'].extend([año] * len(resultados))
                data['Evento'].extend([evento] * len(resultados))
                data['Abbreviation'].extend(resultados['Piloto'])
                data['Adelantamientos'].extend(resultados['Adelantamientos'])

        df_clasificacion = pd.DataFrame(data)
        df_clasificacion = df_clasificacion.groupby('Abbreviation').mean().reset_index()
        df_clasificacion = df_clasificacion.drop('Año', axis=1)

        return df_clasificacion