# -*- coding: utf-8 -*-
"""
Created on Mon May  5 18:19:42 2025

@author: acer
"""



import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# =====================================
st.set_page_config(
    page_title="Dashboard de Tiempo Muerto y Confiabilidad",
    page_icon=":bar_chart:",
    layout="wide"
)

st.title("Dashboard de Fallas en Máquinas y Análisis de Confiabilidad")

tab1, tab2 = st.tabs(["📊 Dashboard Principal", "📈 MTBF y MTTR"])

# =====================================
# TAB 1: DASHBOARD PRINCIPAL
# =====================================
with tab1:
    st.header("📊 Dashboard Principal")

    # CARGA DE ARCHIVO
    uploaded_file_tab1 = st.file_uploader("📁 Sube tu archivo Excel para el Dashboard Principal", type=["xlsx"], key="file_uploader_tab1")

    if uploaded_file_tab1:
        # LEER ARCHIVO
        df_tab1 = pd.read_excel(uploaded_file_tab1)
        st.subheader("👀 Vista previa de los datos (Dashboard Principal)")
        st.dataframe(df_tab1)

        # RENOMBRAR COLUMNAS SI EXISTEN
        df_tab1 = df_tab1.rename(columns={
            "Equipo Descrip.": "Maquina",
            "Stop Reason": "Falla",
            "Loss(min)": "Tiempo Muerto",
            "Fecha": "Fecha",
            "turno": "Turno",
            "Razon": "Razón"
        })

        # VALIDAR COLUMNA DE FECHA
        if "Plan Date" in df_tab1.columns:
            df_tab1["Fecha"] = pd.to_datetime(df_tab1["Plan Date"], errors="coerce")
        elif "End Date" in df_tab1.columns:
            df_tab1["Fecha"] = pd.to_datetime(df_tab1["End Date"], errors="coerce")
        elif "Fecha" in df_tab1.columns:
            df_tab1["Fecha"] = pd.to_datetime(df_tab1["Fecha"], errors="coerce")
        else:
            st.error("⚠️ No se encontró ninguna columna de fecha válida (Plan Date, End Date o Fecha).")
            st.stop()

        # LIMPIAR FILAS NULAS
        df_tab1 = df_tab1.dropna(subset=["Maquina", "Falla", "Turno", "Fecha", "Razón", "Tiempo Muerto"])

        # =====================================
        # SIDEBAR DE FILTROS
        # =====================================
        st.sidebar.header("🎛️ Filtros (Dashboard Principal)")

        maquinas_tab1 = df_tab1["Maquina"].dropna().unique()
        maquinas_seleccionadas_tab1 = st.sidebar.multiselect(
            "Selecciona una(s) máquina(s)",
            options=list(maquinas_tab1),
            default=list(maquinas_tab1),
            key="maquinas_tab1"
        )

        fallas_tab1 = df_tab1["Falla"].dropna().unique()
        fallas_seleccionadas_tab1 = st.sidebar.multiselect(
            "Selecciona tipo(s) de falla",
            options=list(fallas_tab1),
            default=list(fallas_tab1),
            key="fallas_tab1"
        )

        fecha_min_tab1 = df_tab1["Fecha"].min()
        fecha_max_tab1 = df_tab1["Fecha"].max()

        fechas_tab1 = st.sidebar.date_input("Selecciona rango de fechas", [fecha_min_tab1, fecha_max_tab1], key="fechas_tab1")
        if isinstance(fechas_tab1, (list, tuple)):
            fecha_inicio_tab1, fecha_fin_tab1 = fechas_tab1
        else:
            fecha_inicio_tab1 = fecha_fin_tab1 = fechas_tab1

        turnos_tab1 = sorted(df_tab1["Turno"].dropna().unique())
        turno_seleccionado_tab1 = st.sidebar.selectbox("Selecciona un turno", options=turnos_tab1, key="turno_tab1")

        # =====================================
        # FILTRO DE DATOS
        # =====================================
        duraciones_turno_tab1 = {
            "1": 570,  # 9.5 horas
            "2": 510,  # 8.5 horas
            "3": 360   # 6 horas
        }

        df_filtrado_tab1 = df_tab1[
            (df_tab1["Fecha"] >= pd.to_datetime(fecha_inicio_tab1)) &
            (df_tab1["Fecha"] <= pd.to_datetime(fecha_fin_tab1)) &
            (df_tab1["Falla"].isin(fallas_seleccionadas_tab1)) &
            (df_tab1["Turno"] == turno_seleccionado_tab1) &
            (df_tab1["Maquina"].isin(maquinas_seleccionadas_tab1))
        ].copy()

        # =====================================
        # KPIs
        # =====================================
        st.subheader("📈 Indicadores Clave (KPIs) - Dashboard Principal")

        total_paros_tab1 = len(df_filtrado_tab1)
        total_minutos_tab1 = df_filtrado_tab1["Tiempo Muerto"].sum()
        maquina_mas_paros_tab1 = df_filtrado_tab1["Maquina"].value_counts().idxmax() if not df_filtrado_tab1.empty else "N/A"
        minutos_por_fila_tab1 = duraciones_turno_tab1.get(str(turno_seleccionado_tab1), 0)
        total_tiempo_turno_tab1 = len(df_filtrado_tab1) * minutos_por_fila_tab1
        disponibilidad_tab1 = 100 * (1 - total_minutos_tab1 / total_tiempo_turno_tab1) if total_tiempo_turno_tab1 > 0 else 0

        col1_tab1, col2_tab1, col3_tab1, col4_tab1 = st.columns(4)
        card_style = """
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 0 10px rgba(255,255,255,0.1);
        """

        with col1_tab1:
            st.markdown(f"""
                <div style="{card_style}">
                    <div style="font-size: 20px; font-weight: bold;">🔧 Total de Paros</div>
                    <div style="font-size: 36px; color: white;">{total_paros_tab1}</div>
                </div>
            """, unsafe_allow_html=True)

        with col2_tab1:
            st.markdown(f"""
                <div style="{card_style}">
                    <div style="font-size: 20px; font-weight: bold;">⏱️ Total Minutos Perdidos</div>
                    <div style="font-size: 36px; color: white;">{total_minutos_tab1:.0f} minutos</div>
                </div>
            """, unsafe_allow_html=True)

        with col3_tab1:
            st.markdown(f"""
                <div style="{card_style}">
                    <div style="font-size: 20px; font-weight: bold;">🏭 Máquina con más Paros</div>
                    <div style="font-size: 28px; color: white;">{maquina_mas_paros_tab1}</div>
                </div>
            """, unsafe_allow_html=True)

        with col4_tab1:
            st.markdown(f"""
                <div style="{card_style}">
                    <div style="font-size: 20px; font-weight: bold;">📉 % de Disponibilidad</div>
                    <div style="font-size: 36px; color: white;">{disponibilidad_tab1:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)

        # =====================================
        # GRÁFICAS
        # =====================================
        st.subheader("📊 Análisis de Tiempo Muerto y Repetitividad - Dashboard Principal")

        def clasificar_tiempo_tab1(tiempo):
            if tiempo >= 120:
                return "Rojo"
            elif tiempo >= 60:
                return "Amarillo"
            else:
                return "Verde"

        tiempo_muerto_por_maquina_tab1 = df_filtrado_tab1.groupby(["Maquina", "Razón"])["Tiempo Muerto"].sum().reset_index()
        tiempo_muerto_por_maquina_tab1["Nivel"] = tiempo_muerto_por_maquina_tab1["Tiempo Muerto"].apply(clasificar_tiempo_tab1)

        color_map_tab1 = {"Rojo": "crimson", "Amarillo": "gold", "Verde": "limegreen"}

        fig1_tab1 = px.bar(
            tiempo_muerto_por_maquina_tab1,
            x="Maquina",
            y="Tiempo Muerto",
            color="Nivel",
            color_discrete_map=color_map_tab1,
            hover_data=["Razón", "Tiempo Muerto"],
            title="⏱️ Tiempo Muerto Total por Máquina",
            labels={"Tiempo Muerto": "Minutos"}
        )
        st.plotly_chart(fig1_tab1, use_container_width=True)

        repetitividad_tab1 = df_filtrado_tab1.groupby(["Maquina", "Falla", "Razón"]).size().reset_index(name="Repeticiones")
        fig2_tab1 = px.bar(
            repetitividad_tab1,
            x="Maquina",
            y="Repeticiones",
            color="Falla",
            hover_data=["Razón"],
            title="🔁 Repetitividad de Fallas por Máquina",
            barmode="stack"
        )
        st.plotly_chart(fig2_tab1, use_container_width=True)

        # =====================================
        # TOP 10
        # =====================================
        st.subheader("🏆 Top 10 - Análisis Detallado - Dashboard Principal")
        col1_top_tab1, col2_top_tab1 = st.columns(2)

        with col1_top_tab1:
            st.markdown("### Top 10 Máquinas con Mayor Tiempo Muerto")
            top_maquinas_tab1 = df_filtrado_tab1.groupby(["Maquina", "Razón"])["Tiempo Muerto"].sum().reset_index()
            top_maquinas_tab1 = top_maquinas_tab1.sort_values(by="Tiempo Muerto", ascending=False).head(10)
            st.dataframe(top_maquinas_tab1, use_container_width=True)

        with col2_top_tab1:
            st.markdown("### Top 10 Fallas Más Repetidas")
            top_fallas_tab1 = df_filtrado_tab1.groupby(["Falla", "Maquina", "Razón"]).size().reset_index(name="Repeticiones")
            top_fallas_tab1 = top_fallas_tab1.sort_values(by="Repeticiones", ascending=False).head(10)
            st.dataframe(top_fallas_tab1, use_container_width=True)

        # =====================================
        # PARETO
        # =====================================
        st.subheader("📉 Gráfico de Pareto - Tiempo Muerto por Falla - Dashboard Principal")

        pareto_tab1 = df_filtrado_tab1.groupby("Falla").agg({
            "Tiempo Muerto": "sum",
            "Razón": lambda x: ", ".join(x.mode())
        }).reset_index()

        pareto_tab1 = pareto_tab1.sort_values(by="Tiempo Muerto", ascending=False)
        pareto_tab1["Porcentaje"] = pareto_tab1["Tiempo Muerto"] / pareto_tab1["Tiempo Muerto"].sum() * 100
        pareto_tab1["Acumulado %"] = pareto_tab1["Porcentaje"].cumsum()
        pareto_tab1["Color"] = pareto_tab1["Acumulado %"].apply(lambda x: "crimson" if x <= 80 else "lightgray")

        fig_pareto_tab1 = px.bar(
            pareto_tab1,
            x="Falla",
            y="Tiempo Muerto",
            color="Color",
            color_discrete_map="identity",
            hover_data=["Razón", "Porcentaje", "Acumulado %"],
            labels={"Tiempo Muerto": "Minutos"},
            title="Pareto de Tiempo Muerto por Falla"
        )

        fig_pareto_tab1.add_scatter(
            x=pareto_tab1["Falla"],
            y=pareto_tab1["Acumulado %"],
            mode="lines+markers",
            name="Acumulado %",
            yaxis="y2"
        )

        fig_pareto_tab1.update_layout(
            yaxis2=dict(overlaying="y", side="right", range=[0, 100], title="% Acumulado"),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_pareto_tab1, use_container_width=True)

        with st.expander("🧠 ¿Cómo interpretar este gráfico de Pareto? - Dashboard Principal"):
            st.markdown("""
            - Este gráfico permite visualizar **qué fallas están generando más tiempo muerto**.
            - Se basa en el principio de Pareto (80/20): **el 80% del problema proviene del 20% de las causas**.
            - Las **barras** muestran el tiempo muerto por tipo de falla.
            - La **línea roja** muestra el porcentaje acumulado.
            - El cruce del 80% indica las **fallas críticas a priorizar**.
            """)

    else:
        st.info("📥 Por favor, sube un archivo Excel en esta pestaña para ver el Dashboard Principal.")



# =====================================
# TAB 2: ANÁLISIS MTBF Y MTTR
# =====================================
with tab2:
    st.header("⚙️ Análisis de Confiabilidad - MTBF y MTTR")

    # Módulo de carga de archivo Excel (TAB 2)
    uploaded_file_tab2 = st.file_uploader("📁 Sube tu archivo Excel para el Análisis MTBF/MTTR", type=["xlsx"], key="file_uploader_tab2")

    if uploaded_file_tab2:
        # ===========================
        # CARGA Y PROCESAMIENTO DE DATOS
        # ===========================
        df_tab2 = pd.read_excel(uploaded_file_tab2)
        st.subheader("👀 Vista previa de los datos (Análisis MTBF/MTTR)")
        st.dataframe(df_tab2)

        # Renombrar columnas
        df_tab2 = df_tab2.rename(columns={
            "Equipo Descrip.": "Maquina",
            "Stop Reason": "Falla",
            "Loss(min)": "Tiempo Muerto",
            "Fecha": "Fecha",
            "turno": "Turno"
        })

        # Procesar columna de fecha
        if "Plan Date" in df_tab2.columns:
            df_tab2["Fecha"] = pd.to_datetime(df_tab2["Plan Date"], errors="coerce")
        elif "End Date" in df_tab2.columns:
            df_tab2["Fecha"] = pd.to_datetime(df_tab2["End Date"], errors="coerce")
        elif "Fecha" in df_tab2.columns:
            df_tab2["Fecha"] = pd.to_datetime(df_tab2["Fecha"], errors="coerce")
        else:
            st.error("⚠️ No se encontró ninguna columna de fecha válida (Plan Date, End Date o Fecha).")
            st.stop()

        # ===========================
        # LIMPIAR FILAS Y FILTROS
        # ===========================
        df_tab2 = df_tab2.dropna(subset=["Maquina", "Falla", "Turno", "Fecha", "Tiempo Muerto"])

        st.markdown("### 📅 Filtros para MTBF y MTTR")

        maquinas_mtbf_tab2 = df_tab2["Maquina"].dropna().unique()
        maquinas_seleccionadas_mtbf_tab2 = st.multiselect(
            "Selecciona máquina(s) para análisis MTBF/MTTR",
            options=list(maquinas_mtbf_tab2),
            default=list(maquinas_mtbf_tab2),
            key="maquinas_mtbf_tab2"
        )

        fecha_min_mtbf_tab2 = df_tab2["Fecha"].min()
        fecha_max_mtbf_tab2 = df_tab2["Fecha"].max()
        fechas_mtbf_tab2 = st.date_input("Selecciona rango de fechas para MTBF/MTTR",
                                         [fecha_min_mtbf_tab2, fecha_max_mtbf_tab2],
                                         key="fechas_mtbf_tab2")

        if isinstance(fechas_mtbf_tab2, (list, tuple)):
            fecha_inicio_mtbf_tab2, fecha_fin_mtbf_tab2 = fechas_mtbf_tab2
        else:
            fecha_inicio_mtbf_tab2 = fecha_fin_mtbf_tab2 = fechas_mtbf_tab2

        turnos_disponibles_tab2 = df_tab2["Turno"].dropna().unique()
        turno_seleccionado_tab2 = st.selectbox("Selecciona el turno para el análisis",
                                               options=["Todos"] + list(turnos_disponibles_tab2),
                                               index=0,
                                               key="turno_seleccionado_tab2")

        # ===========================
        # FILTRAR DATOS SEGÚN SELECCIÓN
        # ===========================
        df_mtbf_filtrado_tab2 = df_tab2[
            (df_tab2["Maquina"].isin(maquinas_seleccionadas_mtbf_tab2)) &
            (df_tab2["Fecha"] >= pd.to_datetime(fecha_inicio_mtbf_tab2)) &
            (df_tab2["Fecha"] <= pd.to_datetime(fecha_fin_mtbf_tab2))
        ].copy()

        if turno_seleccionado_tab2 != "Todos":
            df_mtbf_filtrado_tab2 = df_mtbf_filtrado_tab2[df_mtbf_filtrado_tab2["Turno"] == turno_seleccionado_tab2]

        # ===========================
        # CÁLCULOS MTBF / MTTR
        # ===========================
        if not df_mtbf_filtrado_tab2.empty:
            # Conversión a horas
            df_mtbf_filtrado_tab2["Downtime (hrs)"] = df_mtbf_filtrado_tab2["Tiempo Muerto"] / 60

            # Crear columna mensual
            df_mtbf_filtrado_tab2["Mes"] = df_mtbf_filtrado_tab2["Fecha"].dt.to_period('M')

            # Agrupar por máquina y mes
            grouped_data = df_mtbf_filtrado_tab2.groupby(["Maquina", "Mes"]).agg(
                Fallas=('Falla', 'count'),
                Total_Downtime_hrs=('Downtime (hrs)', 'sum')
            ).reset_index()

            # Calcular tiempo operacional posible por mes (24 horas * días del mes)
            def calcular_tiempo_operacional_mensual(row):
                num_dias = row['Mes'].days_in_month
                return num_dias * 24.0

            grouped_data['Tiempo_Total_Posible_hrs'] = grouped_data.apply(calcular_tiempo_operacional_mensual, axis=1)
            grouped_data['Tiempo_Operacional_Real_hrs'] = grouped_data['Tiempo_Total_Posible_hrs'] - grouped_data['Total_Downtime_hrs']

            # Calcular MTBF y MTTR
            grouped_data["MTBF (hrs)"] = grouped_data.apply(lambda r: r["Tiempo_Operacional_Real_hrs"] / r["Fallas"] if r["Fallas"] > 0 else 0, axis=1)
            grouped_data["MTTR (hrs)"] = grouped_data.apply(lambda r: r["Total_Downtime_hrs"] / r["Fallas"] if r["Fallas"] > 0 else 0, axis=1)

            # Promedios mensuales por máquina
            resultados_tab2 = grouped_data.groupby("Maquina")[["MTBF (hrs)", "Total_Downtime_hrs", "Fallas", "MTTR (hrs)"]].mean().reset_index()
            resultados_tab2["Total_Downtime_Anual_hrs"] = resultados_tab2["Total_Downtime_hrs"] * 12

            # ===========================
            # KPIs
            # ===========================
            st.markdown("#### 🔧 Indicadores Generales (Promedios Mensuales)")
            total_fallas_tab2 = int(resultados_tab2["Fallas"].sum())
            promedio_mtbf_tab2 = resultados_tab2["MTBF (hrs)"].mean()
            downtime_total_tab2 = resultados_tab2["Total_Downtime_hrs"].sum()
            promedio_mttr_tab2 = resultados_tab2["MTTR (hrs)"].mean()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔩 Fallas", f"{total_fallas_tab2}")
            col2.metric("⏱️ MTBF Promedio", f"{promedio_mtbf_tab2:.1f} hrs")
            col3.metric("💥 Downtime (Mensual)", f"{downtime_total_tab2:.1f} hrs")
            col4.metric("🧰 MTTR Promedio", f"{promedio_mttr_tab2:.2f} hrs")

            # ===========================
            # GRÁFICOS
            # ===========================
            st.markdown("#### 📊 Gráficos de Confiabilidad (Promedio Mensual)")

            fig_mtbf = px.bar(resultados_tab2, x="Maquina", y="MTBF (hrs)",
                              title="MTBF por Máquina (Meta > 500 hrs)",
                              labels={"MTBF (hrs)": "Horas"})
            fig_mtbf.add_shape(type="line", x0=-0.5, x1=len(resultados_tab2) - 0.5,
                               y0=500, y1=500, line=dict(color="green", width=2, dash="dash"))
            st.plotly_chart(fig_mtbf, use_container_width=True)

            fig_mttr = px.bar(resultados_tab2, x="Maquina", y="MTTR (hrs)",
                              title="MTTR por Máquina (Meta < 2.5 hrs)",
                              labels={"MTTR (hrs)": "Horas"})
            fig_mttr.add_shape(type="line", x0=-0.5, x1=len(resultados_tab2) - 0.5,
                               y0=2.5, y1=2.5, line=dict(color="orange", width=2, dash="dash"))
            st.plotly_chart(fig_mttr, use_container_width=True)

            fig_downtime = px.bar(resultados_tab2, x="Maquina", y="Total_Downtime_Anual_hrs",
                                  title="Downtime Anualizado por Máquina (Meta < 360 hrs)",
                                  labels={"Total_Downtime_Anual_hrs": "Horas (Anualizado)"})
            fig_downtime.add_shape(type="line", x0=-0.5, x1=len(resultados_tab2) - 0.5,
                                   y0=360, y1=360, line=dict(color="red", width=2, dash="dash"))
            st.plotly_chart(fig_downtime, use_container_width=True)

        else:
            st.warning("⚠️ No hay datos disponibles para las fechas o máquinas seleccionadas.")

    else:
        st.info("📥 Por favor, sube un archivo Excel para realizar el análisis de MTBF y MTTR.")



















































































































































































































































































































































