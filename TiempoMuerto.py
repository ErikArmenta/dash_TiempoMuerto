# -*- coding: utf-8 -*-
"""
Created on Mon May  5 18:19:42 2025

@author: acer
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Configura el título y el icono de la página
st.set_page_config(page_title="Dashboard de Tiempo Muerto",
                    page_icon=":bar_chart:",
                    layout="wide")
st.title("Dashboard de Fallas en Máquinas")

# Módulo 1: Carga de archivo Excel
uploaded_file = st.file_uploader("📁 Sube tu archivo Excel", type=["xlsx"])
if uploaded_file:
    # Módulo 2: Carga y exploración
    df = pd.read_excel(uploaded_file)
    st.subheader("👀 Vista previa de los datos")
    st.dataframe(df)

    # Renombrar columnas
    df = df.rename(columns={
        "Equipo Descrip.": "Maquina",
        "Stop Reason": "Falla",
        "Loss(min)": "Tiempo Muerto",
        "Fecha": "Fecha",
        "turno": "Turno",
        "Razon": "Razón"
    })

    # Convertir Fecha a datetime
    df["Fecha"] = pd.to_datetime(df["Fecha"])

    # Eliminar filas con valores nulos en columnas clave
    df = df.dropna(subset=["Maquina", "Falla", "Turno", "Fecha", "Razón", "Tiempo Muerto"])

    # Sidebar: Filtros
    st.sidebar.header("🎛️ Filtros")

    maquinas = df["Maquina"].dropna().unique()
    maquinas_seleccionadas = st.sidebar.multiselect(
        "Selecciona una(s) máquina(s)",
        options=list(maquinas),
        default=list(maquinas)
    )

    fallas = df["Falla"].dropna().unique()
    fallas_seleccionadas = st.sidebar.multiselect(
        "Selecciona tipo(s) de falla",
        options=list(fallas),
        default=list(fallas)
    )

    fecha_min = df["Fecha"].min()
    fecha_max = df["Fecha"].max()

    # Manejo robusto de fechas en el filtro
    fechas = st.sidebar.date_input("Selecciona rango de fechas", [fecha_min, fecha_max])
    if isinstance(fechas, (list, tuple)):
        fecha_inicio, fecha_fin = fechas
    else:
        fecha_inicio = fecha_fin = fechas

    turnos = sorted(df["Turno"].dropna().unique())
    turno_seleccionado = st.sidebar.selectbox("Selecciona un turno", options=turnos)

    # Mapeo de minutos por turno
    duraciones_turno = {
        "1": 570,  # 9.5 horas
        "2": 510,  # 8.5 horas
        "3": 360   # 6.0 horas
    }

    # Filtro por datos seleccionados
    df_filtrado = df[
        (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (df["Fecha"] <= pd.to_datetime(fecha_fin)) &
        (df["Falla"].isin(fallas_seleccionadas)) &
        (df["Turno"] == turno_seleccionado) &
        (df["Maquina"].isin(maquinas_seleccionadas))
    ].copy() # Usamos .copy() para evitar SettingWithCopyWarning

    # Guardar el DataFrame filtrado en el estado de la sesión
    st.session_state['df_filtrado'] = df_filtrado

    # Módulo 3: KPIs
    st.subheader("📈 Indicadores Clave (KPIs)")

    total_paros = len(df_filtrado)
    total_minutos = df_filtrado["Tiempo Muerto"].sum()
    maquina_mas_paros = df_filtrado["Maquina"].value_counts().idxmax() if not df_filtrado.empty else "N/A"
    minutos_por_fila = duraciones_turno.get(str(turno_seleccionado), 0)
    total_tiempo_turno = len(df_filtrado) * minutos_por_fila
    disponibilidad = 100 * (1 - total_minutos / total_tiempo_turno) if total_tiempo_turno > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    card_style = """
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 0 10px rgba(255,255,255,0.1);
    """

    with col1:
        st.markdown(f"""
            <div style="{card_style}">
                <div style="font-size: 20px; font-weight: bold;">🔧 Total de Paros</div>
                <div style="font-size: 36px; color: white;">{total_paros}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="{card_style}">
                <div style="font-size: 20px; font-weight: bold;">⏱️ Total Minutos Perdidos</div>
                <div style="font-size: 36px; color: white;">{total_minutos:.0f} minutos</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="{card_style}">
                <div style="font-size: 20px; font-weight: bold;">🏭 Máquina con más Paros</div>
                <div style="font-size: 28px; color: white;">{maquina_mas_paros}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style="{card_style}">
                <div style="font-size: 20px; font-weight: bold;">📉 % de Disponibilidad</div>
                <div style="font-size: 36px; color: white;">{disponibilidad:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    # Módulo 4: Gráficas
    st.subheader("📊 Análisis de Tiempo Muerto y Repetitividad")

    # Función para clasificar el tiempo muerto
    def clasificar_tiempo(tiempo):
        if tiempo >= 120:  # mucho tiempo muerto
            return "Rojo"
        elif tiempo >= 60:  # nivel intermedio
            return "Amarillo"
        else:
            return "Verde"

    # Agrupar tiempo muerto por máquina y razón
    tiempo_muerto_por_maquina = df_filtrado.groupby(["Maquina", "Razón"])["Tiempo Muerto"].sum().reset_index()
    tiempo_muerto_por_maquina["Nivel"] = tiempo_muerto_por_maquina["Tiempo Muerto"].apply(clasificar_tiempo)

    color_map = {
        "Rojo": "crimson",
        "Amarillo": "gold",
        "Verde": "limegreen"
    }

    # Gráfico de barras con color por nivel
    fig1 = px.bar(
        tiempo_muerto_por_maquina,
        x="Maquina",
        y="Tiempo Muerto",
        color="Nivel",
        color_discrete_map=color_map,
        hover_data=["Razón", "Tiempo Muerto"],
        title="⏱️ Tiempo Muerto Total por Máquina",
        labels={"Tiempo Muerto": "Minutos"}
    )

    st.plotly_chart(fig1, use_container_width=True)

    # Gráfica 2: Repetitividad de fallas
    repetitividad = df_filtrado.groupby(["Maquina", "Falla", "Razón"]).size().reset_index(name="Repeticiones")
    fig2 = px.bar(repetitividad, x="Maquina", y="Repeticiones", color="Falla",
                  hover_data=["Razón"], title="🔁 Repetitividad de Fallas por Máquina", barmode="stack")
    st.plotly_chart(fig2, use_container_width=True)

    # Módulo 5: Tablas TOP 10
    st.subheader("🏆 Top 10 - Análisis Detallado")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Top 10 Máquinas con Mayor Tiempo Muerto")
        top_maquinas = df_filtrado.groupby(["Maquina", "Razón"])["Tiempo Muerto"].sum().reset_index()
        top_maquinas = top_maquinas.sort_values(by="Tiempo Muerto", ascending=False).head(10)
        st.dataframe(top_maquinas, use_container_width=True)

    with col2:
        st.markdown("### Top 10 Fallas Más Repetidas")
        top_fallas = df_filtrado.groupby(["Falla", "Maquina", "Razón"]).size().reset_index(name="Repeticiones")
        top_fallas = top_fallas.sort_values(by="Repeticiones", ascending=False).head(10)
        st.dataframe(top_fallas, use_container_width=True)
    # Módulo 6: Gráfico de Pareto
    st.subheader("📉 Gráfico de Pareto - Tiempo Muerto por Falla")

    pareto = df_filtrado.groupby("Falla").agg({
        "Tiempo Muerto": "sum",
        "Razón": lambda x: ", ".join(x.mode())  # Razón más frecuente
    }).reset_index()

    pareto = pareto.sort_values(by="Tiempo Muerto", ascending=False)
    pareto["Porcentaje"] = pareto["Tiempo Muerto"] / pareto["Tiempo Muerto"].sum() * 100
    pareto["Acumulado %"] = pareto["Porcentaje"].cumsum()
    pareto["Color"] = pareto["Acumulado %"].apply(lambda x: "crimson" if x <= 80 else "lightgray")

    fig_pareto = px.bar(
        pareto,
        x="Falla",
        y="Tiempo Muerto",
        color="Color",
        color_discrete_map="identity",
        hover_data=["Razón", "Porcentaje", "Acumulado %"],
        labels={"Tiempo Muerto": "Minutos"},
        title="Pareto de Tiempo Muerto por Falla"
    )

    fig_pareto.add_scatter(
        x=pareto["Falla"],
        y=pareto["Acumulado %"],
        mode="lines+markers",
        name="Acumulado %",
        yaxis="y2"
    )

    fig_pareto.update_layout(
        yaxis2=dict(
            overlaying="y",
            side="right",
            range=[0, 100],
            title="% Acumulado"
        ),
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_pareto, use_container_width=True)

    # Explicación del Pareto
    with st.expander("🧠 ¿Cómo interpretar este gráfico de Pareto?"):
        st.markdown("""
        - Este gráfico de Pareto permite visualizar **qué fallas están generando más tiempo muerto**.
        - Se basa en el principio de Pareto (80/20), que dice que **el 80% del problema proviene del 20% de las causas**.
        - Las **barras** muestran el tiempo muerto total por tipo de falla.
        - La **línea roja** muestra el porcentaje acumulado de impacto.
        - Al observar el cruce del 80%, podemos detectar cuáles son las **fallas críticas a priorizar**.

        👉 **Recomendación**: Concentrarse en eliminar las primeras fallas del gráfico suele dar el mayor beneficio en menos tiempo.
        """)

# =====================================
# NUEVA PESTAÑA: ANÁLISIS MTBF Y MTTR
# =====================================
st.subheader("⚙️ Análisis de Confiabilidad - MTBF y MTTR")

tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 MTBF y MTTR"])

with tab2:
    st.markdown("### 📅 Filtros para MTBF y MTTR")

    # Validación antes de continuar
    if df is not None and not df.empty and "Maquina" in df.columns and fecha_inicio and fecha_fin:
        maquinas_mtbf = df["Maquina"].dropna().unique()
        maquinas_seleccionadas_mtbf = st.multiselect("Selecciona máquina(s) para análisis MTBF/MTTR",
                                                      options=list(maquinas_mtbf),
                                                      default=list(maquinas_mtbf))

        if maquinas_seleccionadas_mtbf:
            df_mtbf = df[
                (df["Maquina"].isin(maquinas_seleccionadas_mtbf)) &
                (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
                (df["Fecha"] <= pd.to_datetime(fecha_fin))
            ].copy()

            if not df_mtbf.empty:
                # Conversión a horas
                df_mtbf["Downtime (hrs)"] = df_mtbf["Tiempo Muerto"] / 60

                # Cálculo total downtime y total fallas por máquina
                resultados = df_mtbf.groupby("Maquina").agg({
                    "Downtime (hrs)": "sum",
                    "Falla": "count"
                }).rename(columns={"Falla": "Fallas"}).reset_index()

                # Supuesto de tiempo total operativo (turnos * duración turno en horas)
                resultados["Horas Turno"] = df_mtbf.groupby("Maquina")["Turno"].count().values
                resultados["Total Operacional (hrs)"] = resultados["Horas Turno"] * 8  # ajusta si tus turnos no son de 8h

                # Fórmulas
                resultados["MTBF (hrs)"] = (resultados["Total Operacional (hrs)"] - resultados["Downtime (hrs)"]) / resultados["Fallas"]
                resultados["MTTR (hrs)"] = resultados["Downtime (hrs)"] / resultados["Fallas"]

                # KPIs agregados
                st.markdown("#### 🔧 Indicadores Generales (KPIs)")

                total_fallas = int(resultados["Fallas"].sum())
                promedio_mtbf = resultados["MTBF (hrs)"].mean()
                downtime_total = resultados["Downtime (hrs)"].sum()
                promedio_mttr = resultados["MTTR (hrs)"].mean()

                col1, col2, col3, col4 = st.columns(4)

                col1.metric("🔩 Fallas", f"{total_fallas}")
                col2.metric("⏱️ MTBF Promedio", f"{promedio_mtbf:.1f} hrs")
                col3.metric("💥 Downtime Total", f"{downtime_total:.1f} hrs")
                col4.metric("🧰 MTTR Promedio", f"{promedio_mttr:.2f} hrs")

                # =============================
                # GRAFICO PLOTLY MTBF Y MTTR
                # =============================
                st.markdown("#### 📉 Gráficos de Confiabilidad")

                fig_mtbf = px.bar(resultados, x="Maquina", y="MTBF (hrs)", title="MTBF por Máquina (Meta > 500 hrs)",
                                  labels={"MTBF (hrs)": "Horas"})
                fig_mtbf.add_shape(type="line", x0=-0.5, x1=len(resultados)-0.5, y0=500, y1=500,
                                   line=dict(color="green", width=2, dash="dash"), name="Meta")

                fig_mttr = px.bar(resultados, x="Maquina", y="MTTR (hrs)", title="MTTR por Máquina (Meta < 2.5 hrs)",
                                  labels={"MTTR (hrs)": "Horas"})
                fig_mttr.add_shape(type="line", x0=-0.5, x1=len(resultados)-0.5, y0=2.5, y1=2.5,
                                   line=dict(color="orange", width=2, dash="dash"), name="Meta")

                fig_downtime = px.bar(resultados, x="Maquina", y="Downtime (hrs)", title="Total Downtime (Meta < 360 hrs)",
                                      labels={"Downtime (hrs)": "Horas"})
                fig_downtime.add_shape(type="line", x0=-0.5, x1=len(resultados)-0.5, y0=360, y1=360,
                                       line=dict(color="red", width=2, dash="dash"), name="Meta")

                st.plotly_chart(fig_mtbf, use_container_width=True)
                st.plotly_chart(fig_mttr, use_container_width=True)
                st.plotly_chart(fig_downtime, use_container_width=True)
            else:
                st.warning("⚠️ No hay datos disponibles para las fechas o máquinas seleccionadas.")
        else:
            st.info("Por favor selecciona al menos una máquina.")
    else:
        st.error("⚠️ Aún no se han cargado los datos correctamente o falta seleccionar un rango de fechas.")

















































