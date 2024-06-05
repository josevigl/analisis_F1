# F1 Analysis Dashboard

This is a Streamlit dashboard for interactive analysis and visualization of Formula 1 race data. It allows exploring various insights across tracks, teams, drivers, and seasons.

## Execution

To run the application, you must install the necessary packages by opening a terminal and typing "pip install -r requirements.txt". It is advisable to create a virtual enviroment before. After that, type the following "streamlit run .\Predicción.py". A browser window with the application will open. It may take a little while to load the data, so please wait until it finishes loading.

Please note that this has been run on version 3.11.1, so if you have a different version, there may be compatibility issues.

## Overview

The goal of this project is to build an easy-to-use web interface for gaining insights from historical F1 data. The dashboard provides interactive graphs and comparisons to analyze different aspects of races, cars, drivers, and trends over time.

The dashboard is built using Python and Streamlit. Historical F1 data comes from Ergast API. The code is structured into modules for data loading, processing, analysis, and visualization.

## Key Files

- `pages/` - Contains Streamlit page scripts for each analysis section 
- `Iniciacion.py` - Handles overall data loading and preprocessing
- `AnálisisCircuitos.py` - Track analysis methods and visuals
- `AnálisisEquipos.py` - Team analysis methods and visuals 
- `AnálisisPilotos.py` - Driver analysis methods and visuals
- `AnálisisAños.py` - Season analysis methods and visuals

## Features

The main features include:

- Aproximate prediction of the stops for a driver in a race
- Interactive selection of year, track, driver, and other filters
- Telemetry comparison between two drivers on a lap 
- Degradation analysis over a stint for two drivers
- Pit stop analysis for teams and tracks
- Overtaking stats for tracks and drivers
- Qualifying position analysis for drivers
- Speed and cornering analysis for tracks
- Animated season comparisons on various metrics

## Usage

The dashboard is designed to be user-friendly and intuitive. Typical usage involves:

1. Running the app with `streamlit run Predicción.py`
2. Selecting an analysis page from the sidebar
3. Choosing filters like year, track, driver etc. 
4. Selecting a chart type and viewing the visualization
5. Repeating steps 3-4 trying different options

The interactive controls make it easy to explore many combinations and dig into the data. The goal is to surface interesting insights from F1 history!
