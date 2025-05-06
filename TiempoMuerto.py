# -*- coding: utf-8 -*-
"""
Created on Mon May  5 18:19:42 2025

@author: acer
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Configura el título y el icono de la página (solo una vez)
st.set_page_config(page_title="Dashboard de Tiempo Muerto", 
                   page_icon=":bar_chart:",  # Icono (puede ser emoji o URL de una imagen)
                   layout="wide")  # Layout "wide" para más espacio en pantalla

st.title("Dashboard de Fallas en Máquinas")

# Módulo 1: Carga de archivo Excel
uploaded_file = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    # Módulo 2: Carga y exploración
    df = pd.read_excel(uploaded_file)

    st.subheader("👀 Vista previa de los datos")
    st.dataframe(df)

    # Renombrar columnas para facilidad
    df = df.rename(columns={
        "Equipo Descrip.": "Maquina",
        "Stop Reason": "Falla",
        "Loss(min)": "Tiempo Muerto",
        "Fecha": "Fecha",
        "turno": "Turno"
    })

    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Sidebar: Filtros
    st.sidebar.header("🎛️ Filtros")

    # Filtro de máquina
    maquinas = df["Maquina"].dropna().unique()
    maquina_seleccionada = st.sidebar.selectbox("Selecciona una máquina", opciones := ["Todas"] + list(maquinas))

    # Filtro de falla
    fallas = df["Falla"].dropna().unique()
    fallas_seleccionadas = st.sidebar.multiselect("Selecciona tipo(s) de falla", options=list(fallas), default=list(fallas))

    # Filtro por fecha
    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()
    fecha_inicio, fecha_fin = st.sidebar.date_input("Selecciona rango de fechas", [fecha_min, fecha_max])

    # Filtro por turno
    turnos = df["Turno"].dropna().unique()
    turnos_seleccionados = st.sidebar.multiselect("Selecciona turno(s)", options=list(turnos), default=list(turnos))

    # Aplicar filtros
    df_filtrado = df[
        (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin)) &
        (df["Falla"].isin(fallas_seleccionadas)) &
        (df["Turno"].isin(turnos_seleccionados))
    ]

    if maquina_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Maquina"] == maquina_seleccionada]

    # Módulo 3: Análisis de datos filtrados
    st.subheader("📊 Análisis de Tiempo Muerto y Repetitividad")

    # Tiempo muerto total por máquina
    tiempo_muerto_por_maquina = df_filtrado.groupby("Maquina")["Tiempo Muerto"].sum().reset_index()

    fig1 = px.bar(tiempo_muerto_por_maquina, 
                  x="Maquina", 
                  y="Tiempo Muerto", 
                  title="⏱️ Tiempo Muerto Total por Máquina",
                  labels={"Tiempo Muerto": "Minutos"},
                  color="Tiempo Muerto")

    st.plotly_chart(fig1, use_container_width=True)

    # Repetitividad de fallas por máquina
    repetitividad = df_filtrado.groupby(["Maquina", "Falla"]).size().reset_index(name="Repeticiones")

    fig2 = px.bar(repetitividad, 
                  x="Maquina", 
                  y="Repeticiones", 
                  color="Falla", 
                  title="🔁 Repetitividad de Fallas por Máquina",
                  barmode="stack")

    st.plotly_chart(fig2, use_container_width=True)





