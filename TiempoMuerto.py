# -*- coding: utf-8 -*-
"""
Created on Mon May  5 18:19:42 2025

@author: acer
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración inicial
st.set_page_config(page_title="Dashboard de Tiempo Muerto", page_icon=":bar_chart:", layout="wide")
st.title("Dashboard de Fallas en Máquinas")

# Carga del archivo Excel
uploaded_file = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Vista previa
    st.subheader("👀 Vista previa de los datos")
    st.dataframe(df)

    # Renombrar columnas
    df = df.rename(columns={
        "Equipo Descrip.": "Maquina",
        "Stop Reason": "Falla",
        "Loss(min)": "Tiempo Muerto",
        "Fecha": "Fecha",
        "turno": "Turno"
    })
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Filtros
    st.sidebar.header("🎛️ Filtros")
    maquinas = df["Maquina"].dropna().unique()
    fallas = df["Falla"].dropna().unique()
    turnos = df["Turno"].dropna().unique()
    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    maquinas_sel = st.sidebar.multiselect("🛠️ Máquina(s)", maquinas, maquinas)
    fallas_sel = st.sidebar.multiselect("⚠️ Tipo(s) de falla", fallas, fallas)
    turnos_sel = st.sidebar.multiselect("🕑 Turno(s)", turnos, turnos)
    fecha_inicio, fecha_fin = st.sidebar.date_input("📅 Rango de fechas", [fecha_min, fecha_max])

    # Filtro de datos
    df_filtrado = df[
        (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin)) &
        (df["Falla"].isin(fallas_sel)) &
        (df["Turno"].isin(turnos_sel)) &
        (df["Maquina"].isin(maquinas_sel))
    ]

    # KPIs
    st.subheader("📌 Indicadores Clave (KPIs)")
    total_paros = len(df_filtrado)
    total_min = df_filtrado["Tiempo Muerto"].sum()
    maquina_top = df_filtrado["Maquina"].value_counts().idxmax() if not df_filtrado.empty else "N/A"
    paros_top = df_filtrado["Maquina"].value_counts().max() if not df_filtrado.empty else 0

    maquinas_activas = df_filtrado["Maquina"].nunique()
    total_disp = maquinas_activas * 24 * 60 if maquinas_activas else 1
    disponibilidad = 100 - (total_min / total_disp * 100)
    disponibilidad = max(min(disponibilidad, 100), 0)

    # Colores para disponibilidad
    color = "green" if disponibilidad >= 95 else "orange" if disponibilidad >= 85 else "red"

    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"### 🔧 Total de Paros\n**{total_paros}**")
    col2.markdown(f"### ⏱️ Minutos Perdidos\n**{total_min:.0f} min**")
    col3.markdown(f"### 🏭 Máquina con más paros\n**{maquina_top} ({paros_top})**")
    col4.markdown(f"<h3>📉 Disponibilidad</h3><h2 style='color:{color}'>{disponibilidad:.2f}%</h2>", unsafe_allow_html=True)

    # Gráficos
    st.subheader("📊 Análisis Visual")

    if not df_filtrado.empty:
        # Gráfico 1: Tiempo Muerto
        tm = df_filtrado.groupby("Maquina")["Tiempo Muerto"].sum().reset_index()
        fig1 = px.bar(tm, x="Maquina", y="Tiempo Muerto", color="Tiempo Muerto",
                      title="⏱️ Tiempo Muerto Total por Máquina")
        st.plotly_chart(fig1, use_container_width=True)

        # Gráfico 2: Repetitividad
        rep = df_filtrado.groupby(["Maquina", "Falla"]).size().reset_index(name="Repeticiones")
        fig2 = px.bar(rep, x="Maquina", y="Repeticiones", color="Falla", barmode="stack",
                      title="🔁 Repetitividad de Fallas por Máquina")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No hay datos disponibles con los filtros seleccionados.")







