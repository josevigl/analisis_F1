import pandas as pd
import pandas as pd
from AnálisisCircuitos import AnalisisCircuitos

class ConstruccionDF:
    def __init__(self, setup):
        self.setup = setup
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

    def construccion(self):
        anali = AnalisisCircuitos(self.setup)
        df_circuitos = anali.get_df_circuitos()
        
        data_circuitos = df_circuitos[['Evento','segundos','Tiempo_medio', 
        'Curvas_Lentas','Curvas_Medias', 'Curvas_Rápidas', 
        'DegradacionSoft_Etiqueta', 'DegradacionMedium_Etiqueta', 'DegradacionHard_Etiqueta']]
        data_circuitos = data_circuitos.rename(columns={'segundos': 'Tiempo_Parada', 'Tiempo_medio': 'Tiempo_Por_Vuelta'})


        data = {'Año': [], 'Evento': []}

        for año in self.años:
            for evento in self.eventos[año]:
                carrera = self.carreras[año][evento]

                vueltas = carrera.laps

                tiempo = vueltas.get_weather_data()

                tiempo = tiempo[['Time', 'Rainfall', 'TrackTemp']]

                vueltas.dropna(subset=['TrackStatus', 'Position'], how='any')

                vueltas = vueltas[['Time','Driver', 'LapNumber', 'Sector1Time', 'Sector2Time', 'LapTime', 'Stint', 'PitInTime',
                'Compound', 'TyreLife', 'Team', 'TrackStatus', 'Position']]

                vueltas["t_S1"] = vueltas["Sector1Time"].dt.total_seconds()

                vueltas = vueltas.drop('Sector1Time', axis=1)

                vueltas["t_S2"] = vueltas["Sector2Time"].dt.total_seconds()

                vueltas = vueltas.drop('Sector2Time', axis=1)

                vueltas["Tiempo_Antes_Pit"] = vueltas["t_S1"] + vueltas["t_S2"]

                vueltas = vueltas.drop(['t_S1', 't_S2'], axis=1)

                vueltas['Parada'] = vueltas['PitInTime'].notna()

                vueltas = vueltas.drop('PitInTime', axis=1)

                vueltas = vueltas.sort_values(by=['LapNumber','Position'])

                vueltas["tiempo"] = vueltas["Time"].dt.total_seconds()

                vueltas['Tiempo_Delante'] = vueltas.groupby('LapNumber')['tiempo'].diff(1)
                vueltas['Tiempo_Detras'] = vueltas.groupby('LapNumber')['tiempo'].diff(-1)

                vueltas['Piloto_Delante'] = vueltas.groupby('LapNumber')['Driver'].shift(1)
                vueltas['Piloto_Detras'] = vueltas.groupby('LapNumber')['Driver'].shift(-1)

                vueltas['Parada_Delante'] = ((vueltas['Piloto_Delante'].notnull()) & (vueltas['Stint'] < vueltas['Stint'].shift(1)))
                vueltas['Parada_Detras'] = ((vueltas['Piloto_Detras'].notnull()) & (vueltas['Stint'] < vueltas['Stint'].shift(-1)))

                vueltas = vueltas.reset_index(drop=True)
                tiempo = tiempo.reset_index(drop=True)

                vueltas = pd.concat([vueltas, tiempo.loc[:, ~(tiempo.columns == 'Time')]], axis=1)

                for col in vueltas.columns:
                    data[col] = data.get(col, []) + list(vueltas[col])
                
                data['Año'] += [año] * len(vueltas)
                data['Evento'] += [evento] * len(vueltas)

        data_vueltas = pd.DataFrame(data)

        data_vueltas['Piloto_Delante'].fillna("NADIE", inplace=True)
        data_vueltas['Piloto_Detras'].fillna("NADIE", inplace=True)

        data_vueltas['Tiempo_Antes_Pit'].fillna(999, inplace=True)

        data_vueltas['Tiempo_Delante'].fillna(-99, inplace=True)
        data_vueltas['Tiempo_Detras'].fillna(-99, inplace=True)

        data_vueltas['Position'].fillna(-1, inplace=True)
        data_vueltas['TrackStatus'].fillna(-1, inplace=True)

        data_circuitos = data_circuitos.reset_index(drop=True)
        data_vueltas = data_vueltas.reset_index(drop=True)
        datos = pd.merge(data_circuitos,data_vueltas, on='Evento',how='left')
        datos["Tráfico"] = datos['Tiempo_Detras'].abs() < datos["Tiempo_Parada"]
        datos.rename(columns={'DegradacionSoft_Etiqueta': 'Deg_Blando', 
                            'DegradacionMedium_Etiqueta': 'Deg_Medio',
                            'DegradacionHard_Etiqueta': 'Deg_Duro'}, inplace=True)

        datos = datos.sort_values(by=['Año', 'Evento', 'Position', 'Driver'])

        datos.drop('Time', axis=1, inplace=True)

        self.variable_objetivo(datos)

    def variable_objetivo(self, datos):
        datos['Parar'] = 'no'

        datos["LapTime"] = datos["LapTime"].dt.total_seconds()

        for año in datos['Año'].unique():
            for evento in datos[datos['Año'] == año]['Evento'].unique():
                for piloto in datos[(datos['Año'] == año) & (datos['Evento'] == evento)]['Driver'].unique():

                    filtro = (datos['Año'] == año) & (datos['Evento'] == evento) & (datos['Driver'] == piloto)

                    vueltas_paradas = datos[filtro & datos['Parada']]['LapNumber'].tolist()
                    
                    for vuelta_parada in vueltas_paradas:
                        if vuelta_parada > 5 and datos[(filtro) & (datos['LapNumber'] == vuelta_parada)]['LapTime'].tolist()[0] <= datos[(filtro) & (datos['LapNumber'] == vuelta_parada)]["Tiempo_Por_Vuelta"].tolist()[0]:
                            posicion_parada = datos[(filtro) & (datos['LapNumber'] == vuelta_parada)]['Position'].tolist()[0]
                            posicion_5_vueltas_antes = datos[(filtro) & (datos['LapNumber'] == vuelta_parada - 5)]['Position'].tolist()[0]

                            if posicion_parada <= posicion_5_vueltas_antes:
                                datos.loc[(filtro) & (datos['LapNumber'] == vuelta_parada), 'Parar'] = 'si'
                            
                            elif posicion_parada > posicion_5_vueltas_antes:
                                cambio_posicion = datos[(filtro) & (datos['Position'].diff() > 0) & (datos['LapNumber'] > vuelta_parada - 5) & (datos['LapNumber'] <= vuelta_parada)]
                                
                                if not cambio_posicion.empty:
                                    vuelta_cambio = cambio_posicion['LapNumber'].iloc[0]
                                    datos.loc[(filtro) & (datos['LapNumber'] == vuelta_cambio - 1), 'Parar'] = 'si'

                        else:
                            datos.loc[(filtro) & (datos['LapNumber'] == vuelta_parada), 'Parar'] = 'si'

        datos['CompuestoBueno'] = 'NONE'

        for año in datos['Año'].unique():
            for evento in datos[datos['Año'] == año]['Evento'].unique():
                for piloto in datos[(datos['Año'] == año) & (datos['Evento'] == evento)]['Driver'].unique():

                    filtro = (datos['Año'] == año) & (datos['Evento'] == evento) & (datos['Driver'] == piloto)

                    vueltas_paradas = datos[filtro & (datos['Parar'] == "si")]['LapNumber'].tolist()
                    vuelta_max = datos[filtro]['LapNumber'].max()
                    vueltas_paradas.append(vuelta_max)

                    vueltas_paradas.sort()

                    for i in range(len(vueltas_paradas) - 1):
                        posicion_parada = datos[filtro & (datos["LapNumber"] == vueltas_paradas[i])]["Position"].tolist()[0]
                        tiempo_delante = datos[filtro & (datos["LapNumber"] == vueltas_paradas[i])]["Tiempo_Delante"].tolist()[0]
                        tiempo_delante2 = datos[filtro & (datos["LapNumber"] == vueltas_paradas[i+1])]["Tiempo_Delante"].tolist()[0]
                        posicion_parada2 = datos[filtro & (datos["LapNumber"] == vueltas_paradas[i+1])]["Position"].tolist()[0]

                        if vueltas_paradas[i+1] - vueltas_paradas[i] <= 5:
                            datos.loc[filtro & (datos['LapNumber'] == vueltas_paradas[i]), 'CompuestoBueno'] = datos[filtro & (datos['LapNumber'] == (vueltas_paradas[i+1] + 1))]['Compound'].tolist()[0]

                        elif posicion_parada2 <= posicion_parada and tiempo_delante2 <= tiempo_delante and vueltas_paradas[i] < vuelta_max:
                            datos.loc[filtro & (datos['LapNumber'] == vueltas_paradas[i]), 'CompuestoBueno'] = datos[filtro & (datos['LapNumber'] == (vueltas_paradas[i] + 1))]['Compound'].tolist()[0]

                        else:
                            salir_del_primer_bucle = False
                            otras_paradas = datos[(datos["Año"] == año) & (datos["Evento"] == evento) & 
                                                (datos["Parar"] == "si") & (datos["Driver"] != piloto)]["Driver"].tolist()
                                
                            for driver in otras_paradas:
                                filtro2 = (datos['Año'] == año) & (datos['Evento'] == evento) & (datos['Driver'] == driver)
                                paradas = datos[filtro2 & (datos['Parar'] == "si")]['LapNumber'].tolist()
                                paradas.append(vuelta_max)
                                paradas.sort()

                                for j in range(len(paradas) - 1):
                                    try:
                                        if paradas[j] >= (vueltas_paradas[i] - 2) and paradas[j] <= (vueltas_paradas[i] + 2):
                                            pos_parada = datos[filtro2 & (datos["LapNumber"] == paradas[j])]["Position"].tolist()[0]
                                            temp_delante = datos[filtro2 & (datos["LapNumber"] == paradas[j])]["Tiempo_Delante"].tolist()[0]
                                            temp_delante2 = datos[filtro2 & (datos["LapNumber"] == paradas[j+1])]["Tiempo_Delante"].tolist()[0]
                                            pos_parada2 = datos[filtro2 & (datos["LapNumber"] == paradas[j+1])]["Position"].tolist()[0]

                                            if pos_parada2 <= pos_parada and temp_delante <= temp_delante2 and paradas[j] < vuelta_max:
                                                datos.loc[filtro & (datos['LapNumber'] == vueltas_paradas[i]), 'CompuestoBueno'] = datos[filtro2 & (datos['LapNumber'] == (paradas[j] + 1))]['Compound'].tolist()[0]
                                                salir_del_primer_bucle = True  
                                                break 
                                    except:
                                        datos.loc[filtro & (datos['LapNumber'] == vueltas_paradas[i]), 'CompuestoBueno'] = datos[filtro & (datos['LapNumber'] == (vueltas_paradas[i] + 1))]['Compound'].tolist()[0]
                                if salir_del_primer_bucle:
                                    break  
                        
                            if salir_del_primer_bucle:
                                break 


        otros = datos[(datos["Parar"] == "si") & (datos["CompuestoBueno"] == "NONE")].index
        datos.loc[otros, "CompuestoBueno"] = datos.loc[otros, "Compound"]

        df = datos[datos["CompuestoBueno"] != "NONE"].copy()
        df.sort_values(by=['Año', 'Evento', 'Driver','LapNumber'])
        indices_parada_si = df[df['Parar'] == 'si'].index

        indices_siguientes = indices_parada_si + 1
        comp = df[(df['Parar'] == 'si')].reset_index()
        a = datos.loc[indices_siguientes].reset_index()

        comparacion = comp["CompuestoBueno"] == a["Compound"]

        conteo_verdaderos = comparacion.sum()

        print("Número de compuestos que no cambian:", conteo_verdaderos)

        comparacion = comp["CompuestoBueno"] != a["Compound"]

        conteo_falsos = comparacion.sum()

        print("Número de compuestos que cambian:", conteo_falsos)

        print("Porcentaje de compuestos que no cambian:", conteo_verdaderos / (conteo_falsos + conteo_verdaderos))

        datos.drop('Parada', axis=1, inplace=True)
        datos.drop('tiempo', axis=1, inplace=True)
        datos.drop('LapTime', axis=1, inplace=True)

        datos['Position'] = datos['Position'].astype(int)
        datos['TrackStatus'] = datos['TrackStatus'].astype(int)
        datos['TyreLife'] = datos['TyreLife'].astype(int)
        datos['Stint'] = datos['Stint'].astype(int)
        datos['LapNumber'] = datos['LapNumber'].astype(int)

        datos = datos.sort_index()

        datos2 = datos.copy()
        datos2 = datos2[datos2["Parar"] == "si"]
        datos2 = datos2[(datos2["CompuestoBueno"] != "NONE")]
        datos2.drop('Parar', axis=1, inplace=True)
        datos.drop('CompuestoBueno', axis=1, inplace=True)

        datos.to_csv('datos.csv', index=False)

        datos2.to_csv('datos2.csv', index=False)