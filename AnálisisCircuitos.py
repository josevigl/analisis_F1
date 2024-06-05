import seaborn as sns
import streamlit as st
from matplotlib import pyplot as plt
import plotly.express as px
import pandas as pd
from functools import reduce
import statsmodels.api as sm
import matplotlib as mpl
import numpy as np
from matplotlib.collections import LineCollection
import pandas as pd
import fastf1.plotting


fastf1.plotting.setup_mpl(misc_mpl_mods=False)

class AnalisisCircuitos:
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

    def grafica_barras(self, data, variable):
        st.subheader(f'{variable.capitalize()} por Evento')
        fig, ax = plt.subplots(figsize=(12, len(data["Evento"]) * 0.25))
        bars = ax.barh(data["Evento"], data[variable], color='green')
        for bar in bars:
            width = bar.get_width()
            ax.annotate(f'{width:.2f}', xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(3, 0),  # 3 points horizontal offset
                        textcoords="offset points",
                        ha='left', va='center')
        ax.set_xlabel(f'{variable.capitalize()}')
        ax.set_ylabel('Evento')
        ax.set_title(f'{variable.capitalize()} por Evento')
        ax.grid(axis='x')
        st.pyplot(fig)

    def graficar_media_y_desviacion(self, data, media, desviacion):
        st.subheader(f'Media y Desviación Estándar de {media.capitalize()} por Evento')
        fig, ax = plt.subplots(figsize=(12, len(data["Evento"]) * 0.25))
        
        bars_media = ax.barh(data["Evento"], data[media], color='red', label='Media')

        bars_desviacion = ax.barh(data["Evento"], data[desviacion], color='white',  label='Desviación', alpha=0.7)

        for bar in bars_media:
            width = bar.get_width()
            ax.annotate(f'{width:.2f}', 
                        xy=(width, bar.get_y() + bar.get_height() / 2),
                        xytext=(3, 0),
                        textcoords="offset points",
                        ha='left', va='center',
                        color='white')

        for bar in bars_desviacion:
            width = bar.get_width()
            ax.annotate(f'{width:.2f}', 
                        xy=(bar.get_x() + width, bar.get_y() + bar.get_height() / 2),
                        xytext=(3, 0),  
                        textcoords="offset points",
                        ha='left', va='center',
                        color='black')

        ax.set_xlabel(media.capitalize())
        ax.set_ylabel('Evento')
        ax.set_title(f'Media y Desviación Estándar de {media.capitalize()} por Evento')
        ax.grid(axis='x')
        ax.legend()

        st.pyplot(fig)

    def grafico_burbujas(self, data, variable1, variable2, variable3, variable4):
        st.subheader('Gráfico de Burbujas')
        fig = px.scatter(data, x=variable1, y=variable2,
                         size=variable3, hover_name=variable4, log_x=True, size_max=60)
        st.plotly_chart(fig)

    def mapa_correlacion(self, data):
        st.subheader('Mapa de Correlación')
        plt.figure(figsize=(8, 6))
        sns.heatmap(data, annot=True, cmap="coolwarm", linewidths=.5)
        st.pyplot(plt)

    def get_media_pitstops(self):
        resultados = []
        for año in self.años:
            for evento in self.eventos[año]:
                vuelta = self.carreras[año][evento].laps

                pit_stops = vuelta[vuelta['Stint'].diff() != 0]
                total_pit_stops = pit_stops.groupby('Driver')['Stint'].nunique()
                media_pit_stops = total_pit_stops.mean()
                desviacion_pit_stops = total_pit_stops.std()

                resultado_actual = {
                    'Año': año,
                    'Evento': evento,
                    'Media_Pit_Stops': media_pit_stops,
                    'Desviacion_Pit_Stops': desviacion_pit_stops
                }

                resultados.append(resultado_actual)

        df_resultados = pd.DataFrame(resultados)
        pit_stops = df_resultados
        media_pit_stops_por_evento = df_resultados.groupby('Evento').agg({'Media_Pit_Stops': 'mean', 'Desviacion_Pit_Stops': 'mean'}).reset_index()

        return media_pit_stops_por_evento, pit_stops
    
    def get_adelantamientos(self):
        resultados = []
        for año in self.años:
            for evento in self.eventos[año]:
                vuelta = self.carreras[año][evento].laps

                adelantamientos_por_piloto = vuelta.groupby('Driver')['Position'].diff().gt(0).groupby(vuelta['Driver']).cumsum()
                adelantamientos = adelantamientos_por_piloto.groupby(vuelta['Driver']).max().sum()
                desviacion_adelantamientos = adelantamientos_por_piloto.groupby(vuelta['Driver']).max().std()

                resultado_actual = {
                    'Año': año,
                    'Evento': evento,
                    'Adelantamientos': adelantamientos,
                    'Desviacion_Adelantamientos': desviacion_adelantamientos
                }

                resultados.append(resultado_actual)

        df_resultados = pd.DataFrame(resultados)
        adelantamientos_por_evento = df_resultados.groupby('Evento').agg({'Adelantamientos': 'mean', 'Desviacion_Adelantamientos': 'mean'}).reset_index()

        return adelantamientos_por_evento, df_resultados
    
    def get_temperatura(self):
        resultados = []
        for año in self.años:
            for evento in self.eventos[año]:
                vuelta = self.carreras[año][evento]

                tiempo_info = vuelta.laps.get_weather_data()
                temp_pista = tiempo_info["TrackTemp"].mean()
                temp_aire = tiempo_info["AirTemp"].mean()
                    
                resultado_actual = {
                    'Año': año,
                    'Evento': evento,
                    'TrackTemp': temp_pista,
                    'AirTemp': temp_aire 
                }

                resultados.append(resultado_actual)

        df_resultados = pd.DataFrame(resultados)

        _, pit_stops = self.get_media_pitstops()

        df_temp = pd.merge(df_resultados, pit_stops, on=['Año', 'Evento'], how='left')

        return df_temp
    
    def etiquetar_degradacion(self, valor):
        if np.isfinite(valor) and valor > -0.001:
            return "ALTA"
        elif np.isfinite(valor) and valor <= (-0.001) and valor >= (-0.01):
            return "MEDIA"
        elif np.isfinite(valor) and valor <= (-0.01):
            return "BAJA"
        else:
            return "ALTA"
    
    def get_degradacion(self):
        degradacion = {'Año': [], 'Evento': [], 'DegradacionSoft': [], 'DegradacionMedium': [], 'DegradacionHard': []}

        for año in self.años:
            for evento in self.eventos[año]:
                degradacion['Año'].append(año)
                degradacion['Evento'].append(evento)

                degradacion_soft = None
                degradacion_medium = None
                degradacion_hard = None

                carrera = self.carreras[año][evento].laps
                carrera['Laptime'] = carrera['LapTime'].dt.total_seconds()

                primeros_stint = carrera[carrera["Stint"] == 1]

                if primeros_stint["LapNumber"].max() < 10:
                    primeros_stint = carrera[carrera["Stint"] == 2]

                for compuesto in ["SOFT", "MEDIUM", "HARD"]:
                    compuesto_data = primeros_stint[primeros_stint["Compound"] == compuesto]

                    tiempo_min = compuesto_data["Laptime"].min() * 1.05
                    compuesto_data = compuesto_data[compuesto_data["Laptime"] < tiempo_min]

                    if len(compuesto_data) > 5:
                        lowess_model = sm.nonparametric.lowess(compuesto_data['Laptime'], compuesto_data['LapNumber'], frac=0.3)

                        # Obtener los puntos ajustados por el modelo
                        fitted_values = lowess_model[:, 1]

                        adjusted_data = pd.DataFrame({'LapNumber': compuesto_data['LapNumber'], 'FittedValues': fitted_values})

                        # Calcular la diferencia entre los valores ajustados consecutivos
                        adjusted_data['Difference'] = adjusted_data['FittedValues'].diff()

                        # Calcular la pendiente media
                        pendiente = adjusted_data['Difference'].mean()

                        if compuesto == "SOFT":
                            degradacion_soft = pendiente
                        elif compuesto == "MEDIUM":
                            degradacion_medium = pendiente
                        elif compuesto == "HARD":
                            degradacion_hard = pendiente

                degradacion['DegradacionSoft'].append(degradacion_soft)
                degradacion['DegradacionMedium'].append(degradacion_medium)
                degradacion['DegradacionHard'].append(degradacion_hard)

        df_degradacion = pd.DataFrame(degradacion)

        columnas_degradacion = ['DegradacionSoft', 'DegradacionMedium', 'DegradacionHard']
        df_degradacion = df_degradacion.groupby('Evento')[columnas_degradacion].mean().reset_index()
        df_degradacion2 = df_degradacion.copy()


        for columna in ['DegradacionSoft', 'DegradacionMedium', 'DegradacionHard']:
            df_degradacion[columna + '_Etiqueta'] = df_degradacion[columna].apply(lambda x: self.etiquetar_degradacion(x))

        return df_degradacion, df_degradacion2
    
    def get_tiempo_parada(self):
        paradas = pd.read_csv('Ergast/pit_stops.csv')
        races = pd.read_csv('Ergast/races.csv')
        circuito = pd.read_csv('Ergast/circuits.csv')

        races = races[["raceId","year","name","circuitId"]]
        races = races.rename(columns={'name':'Evento'})
        circuito = circuito[["circuitId","alt"]]
        paradas = paradas[["raceId","driverId","lap","milliseconds"]]
        paradas = paradas[paradas["milliseconds"] < 50000]
        paradas["segundos"] = paradas["milliseconds"] / 1000

        df_join = pd.merge(paradas, races, left_on='raceId', right_on='raceId', how='left')
        df_join = pd.merge(df_join, circuito, left_on='circuitId', right_on='circuitId', how='left')

        df_ergast = df_join[df_join["year"] >= 2019]
        df_paradas = df_ergast.groupby('Evento')['segundos'].agg(['mean', 'std']).reset_index()
        df_paradas = df_paradas.rename(columns={'mean': 'Media_Tiempo_Parada', 'std': 'Desviacion_Tiempo_Parada'})

        return df_paradas, df_ergast
    
    def get_tiempo_por_vuelta(self):
        resultados = []
        for año in self.años:
            for evento in self.eventos[año]:

                carrera = self.carreras[año][evento].laps
                carrera['Laptime'] = carrera['LapTime'].dt.total_seconds()
                tiempo_por_vuelta = carrera.groupby('Driver')['Laptime'].mean()
                tiempo_evento = tiempo_por_vuelta.mean()
                desviacion_tiempo_evento = tiempo_por_vuelta.std()

                resultado_actual = {
                    'Año': año,
                    'Evento': evento,
                    'Tiempo_medio': tiempo_evento,
                    'Desviacion_tiempo_medio': desviacion_tiempo_evento
                }

                resultados.append(resultado_actual)

        df_resultados = pd.DataFrame(resultados)
        tiempo_por_evento = df_resultados.groupby('Evento').agg({'Tiempo_medio': 'mean', 'Desviacion_tiempo_medio': 'mean'}).reset_index()

        return tiempo_por_evento, df_resultados
    
    def get_velocidad_media(self):
        resultados = []
        for año in self.años:
            for evento in self.eventos[año]:
                lista_velocidad = []
                for piloto in self.drivers[año][evento]:
                    carrera = self.carreras[año][evento].laps.pick_driver(piloto).pick_fastest()
                    try:
                        media_velocidad = carrera.get_car_data()["Speed"].mean()
                        lista_velocidad.append(media_velocidad)
                    except Exception as e:
                        pass

                velocidad_media = np.mean(lista_velocidad)
                desviacion_velocidad_media = np.std(lista_velocidad)

                resultado_actual = {
                    'Año': año,
                    'Evento': evento,
                    'Velocidad_media': velocidad_media,
                    'Desviacion_velocidad_media': desviacion_velocidad_media
                }

                resultados.append(resultado_actual)

        df_resultados = pd.DataFrame(resultados)
        velocidad_por_evento = df_resultados.groupby('Evento').agg({'Velocidad_media': 'mean', 'Desviacion_velocidad_media': 'mean'}).reset_index()

        return velocidad_por_evento, df_resultados
    
    def get_safety_veces(self):
        safety = pd.read_csv('Others/safety_cars.csv')

        filas = [(f"{gp}") for año, gps in self.eventos.items() for gp in gps]


        columnas = ['Race']
        df_conts = pd.DataFrame(filas, columns=columnas)

        safety_df = safety[safety['Race'].str.contains('|'.join(df_conts['Race']))]
        conteo_por_categoria = safety_df.groupby('Race').size().reset_index(name='Safety_Veces')
        conteo_por_categoria['Race'] = conteo_por_categoria['Race'].str.replace('\d{4} ', '', regex=True)
        saftey_por_evento = conteo_por_categoria.groupby('Race')['Safety_Veces'].agg(['mean', 'std']).reset_index()
        saftey_por_evento.columns = ['Race', 'Safety_Veces', 'Safety_Veces_Desviacion']


        return saftey_por_evento, conteo_por_categoria
    
    def extraer_numeros(self, cadena):
        numeros = ''.join(filter(str.isdigit, str(cadena)))
        return int(numeros) if numeros else 0

    def get_tipos_curvas(self):
        df_velocidades_curvas = pd.DataFrame(columns=['Circuito', 'Curva', 'Velocidad_Media'])

        for año in self.años:
            for evento in self.eventos[año]:
                carrera = self.carreras[año][evento]
                try:
                    lap = carrera.laps.pick_fastest()
                    circuit_info = carrera.get_circuit_info()   
                    x = lap.telemetry['X']              
                    y = lap.telemetry['Y']              

                    for _, corner in circuit_info.corners.iterrows():
                        puntos_en_curva = lap.telemetry[((x - corner['X'])**2 + (y - corner['Y'])**2) <= 100**2]  

                        velocidad_promedio_en_curva = np.mean(puntos_en_curva['Speed'])

                        df_velocidades_curvas = df_velocidades_curvas.append({
                            'Circuito': evento,
                            'Curva': f"{corner['Number']}{corner['Letter']}",
                            'Velocidad_Media': velocidad_promedio_en_curva
                        }, ignore_index=True)
                except Exception as e:
                    pass

        df_velocidades_curvas = df_velocidades_curvas.groupby(['Circuito', 'Curva'], as_index=False)['Velocidad_Media'].mean()

        df_velocidades_curvas['Curva_Num'] = df_velocidades_curvas['Curva'].apply(self.extraer_numeros)

        df_velocidades_curvas = df_velocidades_curvas.sort_values(by=['Circuito', 'Curva_Num'])

        df_velocidades_curvas = df_velocidades_curvas.drop('Curva_Num', axis=1)

        intervalos = [0, 150, 250, float('inf')]
        categorias = ['Curvas_Lentas', 'Curvas_Medias', 'Curvas_Rápidas']

        # Discretizar 'Velocidad_Media' y agregar una nueva columna 'Categoría'
        df_velocidades_curvas['Categoría'] = pd.cut(df_velocidades_curvas['Velocidad_Media'], bins=intervalos, labels=categorias, right=False)

        df_velocidades_curvas.drop(columns=['Categoría'], inplace=True)

        for categoria in categorias:
            df_velocidades_curvas[categoria] = (df_velocidades_curvas['Velocidad_Media']
                                                .between(intervalos[categorias.index(categoria)],
                                                        intervalos[categorias.index(categoria) + 1],
                                                        inclusive='left')).astype(int)

        tipos_curvas_df = df_velocidades_curvas.groupby(['Circuito'], as_index=False).sum()[['Circuito'] + categorias]

        return tipos_curvas_df
    
    def similitudes(self, data, variable):
        data2, _ = self.get_media_pitstops()
        data = pd.merge(data, data2, on='Evento', how='inner')
        
        correlation = np.corrcoef(data[variable], data['Media_Pit_Stops'])[0, 1]
        
        fig = px.scatter(data, x=variable, y='Media_Pit_Stops', color='Evento', size_max=30, hover_name='Evento')

        fig.update_layout(
            title=f'Relación entre {variable} y Media Pit Stops (Correlación: {correlation:.2f})',
            xaxis_title=f'{variable}',
            yaxis_title='Media Pit Stops',
            paper_bgcolor='black',
            plot_bgcolor='black',   
            font=dict(color='white')
        )

        st.plotly_chart(fig)
 
    def matriz_correlacion(self, df_circuitos):
        matriz_correlacion = df_circuitos.corr()

        plt.figure(figsize=(8, 6))
        sns.heatmap(matriz_correlacion, annot=True, cmap="coolwarm", linewidths=.5)
        plt.title("Mapa de Correlación")
        plt.show()

    def get_df_circuitos(self):
        media_pit_stops_por_evento, _ = self.get_media_pitstops()
        adelantamientos_por_evento, _ = self.get_adelantamientos()
        df_temp = self.get_temperatura()
        df_paradas, _ = self.get_tiempo_parada()
        tiempo_por_evento, _ = self.get_tiempo_por_vuelta()
        velocidad_por_evento, _ = self.get_velocidad_media()
        safety_por_evento, _ = self.get_safety_veces()
        tipos_curvas_df = self.get_tipos_curvas()
        df_degradacion, _ = self.get_degradacion()

        df_temperatura = df_temp.groupby('Evento').mean().reset_index()
        tipos_curvas_df.rename(columns={'Circuito': 'Evento'}, inplace=True)
        safety_por_evento.rename(columns={'Race': 'Evento'}, inplace=True)
        df_temperatura = df_temperatura[["Evento","TrackTemp"]]
        df_degradacion = df_degradacion[["Evento","DegradacionSoft_Etiqueta","DegradacionMedium_Etiqueta", "DegradacionHard_Etiqueta"]]
                
        lista_dfs = [media_pit_stops_por_evento, adelantamientos_por_evento, df_temperatura, df_paradas,
             tiempo_por_evento, velocidad_por_evento, safety_por_evento, tipos_curvas_df, df_degradacion]
        
        df_circuitos = reduce(lambda left, right: pd.merge(left, right, on='Evento'), lista_dfs)

        return df_circuitos
    
    def get_speed_track(self, evento):
        colormap = mpl.cm.plasma
        for año in self.años:
            if evento in self.carreras[año]:
                carrera = self.carreras[año][evento]
                break
        lap = carrera.laps.pick_fastest()

        x = lap.telemetry['X']             
        y = lap.telemetry['Y']             
        color = lap.telemetry['Speed'] 

        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
        fig.suptitle(f'Mapa de velocidad del circuito {evento}', fontsize=16)
        
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
        ax.axis('off')

        ax.plot(lap.telemetry['X'], lap.telemetry['Y'],
                color='black', linestyle='-', linewidth=16, zorder=0)

        norm = plt.Normalize(color.min(), color.max())
        lc = LineCollection(segments, cmap=colormap, norm=norm,
                            linestyle='-', linewidth=5)

        lc.set_array(color)

        line = ax.add_collection(lc)

        cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
        normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
        legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap,
                                            orientation="horizontal")

        st.pyplot(fig)


    def graficar_posiciones(self, año, evento):
        carrera = self.carreras[año][evento]
        fig, ax = plt.subplots(figsize=(8.0, 4.9))

        for drv in carrera.drivers:
            drv_laps = carrera.laps.pick_driver(drv)

            abb = drv_laps['Driver'].iloc[0]
            try:
                color = fastf1.plotting.driver_color(abb)
            except Exception:
                color = 'black'

            ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                    label=abb, color=color)
            
        ax.set_ylim([20.5, 0.5])
        ax.set_yticks([1, 5, 10, 15, 20])
        ax.set_xlabel('Lap')
        ax.set_ylabel('Position')
        ax.legend(bbox_to_anchor=(1.0, 1.02))
        plt.tight_layout()

        st.pyplot(fig)

    def graficar_cambio_stint(self, año, evento):
        carrera = self.carreras[año][evento]
        laps = carrera.laps
        drivers = carrera.drivers
        drivers = [carrera.get_driver(driver)["Abbreviation"] for driver in drivers]

        stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
        stints = stints.groupby(["Driver", "Stint", "Compound"])
        stints = stints.count().reset_index()

        stints = stints.rename(columns={"LapNumber": "StintLength"})

        fig, ax = plt.subplots(figsize=(5, 10))

        for driver in drivers:
            driver_stints = stints.loc[stints["Driver"] == driver]

            previous_stint_end = 0
            for idx, row in driver_stints.iterrows():
                plt.barh(
                    y=driver,
                    width=row["StintLength"],
                    left=previous_stint_end,
                    color=fastf1.plotting.COMPOUND_COLORS[row["Compound"]],
                    edgecolor="black",
                    fill=True
                )

                previous_stint_end += row["StintLength"]

        plt.title(f"{evento} Strategies", color='white')  
        plt.xlabel("Lap Number", color='white')
        plt.grid(False)

        ax.set_facecolor('black')  

        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')

        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')

        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        plt.tight_layout()

        st.pyplot(fig)