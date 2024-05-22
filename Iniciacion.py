import pickle
import pandas as pd
import fastf1
import fastf1.plotting
import lzma
import os

class SetUp:
    def __init__(self):
        self.seed = 42
        fastf1.plotting.setup_mpl(misc_mpl_mods=False)
        self.años = [2019, 2020, 2021, 2022, 2023, 2024]
        self.eventos = self.get_eventos()
        self.carreras = self.get_carreras()

    def actualizar_eventos(self):
        eventos = {}
        for año in self.años:
            try:
                df = fastf1.get_event_schedule(year=año, include_testing=False, backend='ergast')
                eventos[año] = df['EventName'].tolist()
            except Exception as e:
                print(f"Todavia no hay datos para el calendario entero para el año {año}, se cogen los datos que se tienen")
        
        eventos[2024] = ['Bahrain Grand Prix', 'Saudi Arabian Grand Prix', 'Australian Grand Prix', 'Japanese Grand Prix']

        self.guardar_eventos(eventos)
        self.eventos = self.get_eventos()

    def guardar_eventos(self, eventos):
        path = os.path.join('eventos.pkl')
        with open(path,'wb') as file:
            pickle.dump(eventos,file)

    def get_eventos(self):
        path = os.path.join('eventos.pkl')
        with open(path,'rb') as file:
            eventos = pickle.load(file)
        return eventos
    

    def actualizar_carreras(self):
        self.actualizar_eventos()
        carreras = {}
        for año in self.años:
            carrera = {}
            for evento in self.eventos[año]:
                sesion = fastf1.get_session(año,evento,'R')
                sesion.load()
                carrera[evento] = sesion
                carreras[año] = carrera

        self.guardar_carreras(carreras)
        self.carreras = self.get_carreras()

    def guardar_carreras(self, carreras):
        path = 'carreras2324.xz'
        with lzma.open(path,'wb') as file:
            pickle.dump(carreras,file)

    def get_carreras(self):
        path = 'carreras1920.xz'
        with lzma.open(path, 'rb') as file:
            carreras1 = pickle.load(file)

        path = 'carreras21.xz'
        with lzma.open(path, 'rb') as file:
            carreras2 = pickle.load(file)

        path = 'carreras22.xz'
        with lzma.open(path, 'rb') as file:
            carreras3 = pickle.load(file)

        path = 'carreras2324.xz'
        with lzma.open(path, 'rb') as file:
            carreras4 = pickle.load(file)

        carreras = {**carreras1, **carreras2, **carreras3, **carreras4}
        return carreras