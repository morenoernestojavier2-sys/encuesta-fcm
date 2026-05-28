import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import plotly.express as px
import os
import io
import requests
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE ZONA HORARIA (ARGENTINA UTC-3) ---
TZ_ARG = timezone(timedelta(hours=-3))

def obtener_hora_arg():
    return datetime.now(TZ_ARG).strftime("%Y-%m-%d %H:%M:%S")

def obtener_fecha_archivo():
    return datetime.now(TZ_ARG).strftime('%Y%m%d')

# --- CONFIGURACIÓN GENERAL ---
URL_DE_TU_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbyoYN3-nC8mhJWiNE14_tEcTjqPlh2q0R10Cy3ucE97DmtRmkLQfWlGcTT93EmWnfn7/exec"
st.set_page_config(page_title="Encuesta de Vacunación", page_icon="🏥", layout="wide")

# --- DISEÑO VISUAL PREMIUM ---
st.markdown("""
<style>
    .stApp {
        background-image: url("https://img.freepik.com/free-vector/cartoon-coronavirus-vaccine-background_23-2148861308.jpg") !important;
        background-size: cover !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }
    .block-container {
        background-color: rgba(255, 255, 255, 0.90) !important; 
        border-radius: 15px;
        box-shadow: 0px 8px 30px rgba(0,0,0,0.9); 
        color: #000000 !important; 
        margin-top: 20px;
        margin-bottom: 20px;
        padding: 40px;
        max-width: 1100px;
    }
    .header-container { text-align: center; margin-bottom: 20px; padding: 10px; border-bottom: 2px solid #0056b3; }
    .main-logo { font-size: 70px; margin-bottom: 0px; }
    h1 { font-size: 34px !important; color: #002e5d !important; font-weight: 800 !important; text-shadow: 1px 1px 2px #FFFFFF !important; margin-top: 0px !important; }
    h2 { font-size: 24px !important; color: #000000 !important; font-weight: 700 !important; text-shadow: 1px 1px 2px #FFFFFF !important; margin-bottom: 15px !important; }
    .stTextInput label, .stSelectbox label, .stRadio label, .stMultiselect label, .stSlider label, h3, h4, .stMetric label { color: #000000 !important; font-weight: 700 !important; text-shadow: 1px 1px 2px #FFFFFF !important; }
    .stTextInput input, .stSelectbox div[role="button"], .stRadio div[role="radiogroup"], .stMultiselect div[role="listbox"], .stSlider div[role="slider"] { border: 3px solid #000000 !important; border-radius: 8px !important; background-color: #FFFFFF !important; color: #000000 !important; opacity: 1.0 !important; box-shadow: 4px 4px 10px rgba(0,0,0,0.8) !important; }
    div.stButton > button:first-child, div.stDownloadButton > button:first-child { background-color: #0056b3 !important; color: #ffffff !important; border-radius: 8px !important; border: 3px solid #000000 !important; box-shadow: 5px 5px 15px rgba(0,0,0,0.8) !important; padding: 12px 24px !important; font-weight: bold !important; font-size: 18px !important; width: 100% !important; margin-top: 20px !important; }
    div.stButton > button:first-child:active, div.stDownloadButton > button:first-child:active { transform: translateY(5px) !important; box-shadow: 0px 0px 0px #003d82 !important; }
    .carnet-oficial { background-color: #FFFFFF !important; border-radius: 12px !important; box-shadow: 0 8px 16px rgba(0,0,0,0.3) !important; border: 4px solid #000000 !important; overflow: hidden !important; margin-bottom: 25px !important; font-family: 'Arial', sans-serif !important; opacity: 1.0 !important; }
    .carnet-header-verde { background-color: #2e7d32 !important; color: white !important; padding: 15px !important; text-align: center !important; border-bottom: 4px solid #1b5e20 !important; }
    .carnet-header-rojo { background-color: #d32f2f !important; color: white !important; padding: 15px !important; text-align: center !important; border-bottom: 4px solid #b71c1c !important; }
    .carnet-body { padding: 20px !important; color: #000000 !important; }
    .fila-dato { border-bottom: 2px solid #000000 !important; padding: 10px 0 !important; font-size: 15px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f0f2f6; border-radius: 10px 10px 0px 0px; padding: 10px 20px; color: #000000; font-weight: bold; border: 2px solid #000000; border-bottom: none; }
    .stTabs [aria-selected="true"] { background-color: #0056b3 !important; color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE DOBLE GUARDADO ---
def guardar_respuesta_doble(datos):
    archivo = 'Base_Respuestas.csv'
    df_nuevo = pd.DataFrame([datos])
    if not os.path.isfile(archivo): df_nuevo.to_csv(archivo, index=False)
    else: df_nuevo.to_csv(archivo, mode='a', header=False, index=False)
    payload_resp = {"tipo": "respuesta"}
    payload_resp.update(datos)
    try: requests.post(URL_DE_TU_GOOGLE_SCRIPT, json=payload_resp)
    except: pass

def registrar_movimiento_doble(seccion_origen, accion_realizada):
    correo_actual = st.session_state.respuestas.get("Email", "SIN_MAIL")
    datos = {"Fecha_Hora": obtener_hora_arg(), "Email": correo_actual, "Seccion_Origen": seccion_origen, "Accion": accion_realizada}
    archivo = 'Historial_Movimientos.csv'
    df_nuevo = pd.DataFrame([datos])
    if not os.path.isfile(archivo): df_nuevo.to_csv(archivo, index=False)
    else: df_nuevo.to_csv(archivo, mode='a', header=False, index=False)
    payload_mov = {"tipo": "movimiento"}
    payload_mov.update(datos)
    try: requests.post(URL_DE_TU_GOOGLE_SCRIPT, json=payload_mov)
    except: pass

def cerrar_sesion():
    st.session_state.modo_admin = False
    st.session_state.pwd_input = ""

def aplicar_cebra(row):
    return ['background-color: #E6F2FF' if row.name % 2 == 0 else 'background-color: #FFFFFF' for _ in row]

# --- MEMORIA DE SESIÓN ---
if 'seccion' not in st.session_state: st.session_state.seccion = 1
if 'seccion_anterior' not in st.session_state: st.session_state.seccion_anterior = 1
if 'respuesta_guardada' not in st.session_state: st.session_state.respuesta_guardada = False
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'es_argentino' not in st.session_state: st.session_state.es_argentino = True

# --- PANEL ADMIN ---
st.sidebar.title("🔐 Panel de Control")
st.sidebar.text_input("Ingresá la clave de admin:", type="password", key="pwd_input")
st.session_state.modo_admin = (st.session_state.pwd_input == "fcm2026")

if st.session_state.modo_admin:
    st.title("📊 Panel Estadístico Clínico (Modo Admin)")
    
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    with col_btn1:
        st.button("⬅️ Volver", on_click=cerrar_sesion, use_container_width=True)
    with col_btn2:
        if st.button("🔄 Actualizar Datos", use_container_width=True):
            st.rerun()
    with col_btn3:
        if st.button("🗑️ Borrar Pruebas", use_container_width=True):
            if os.path.exists('Base_Respuestas.csv'): os.remove('Base_Respuestas.csv')
            if os.path.exists('Historial_Movimientos.csv'): os.remove('Historial_Movimientos.csv')
            st.success("✅ Archivos locales borrados.")
    with col_btn4:
        if st.button("🧪 Enviar Prueba (Test)", use_container_width=True):
            datos_prueba = {
                "Fecha": obtener_hora_arg(),
                "Email": "ALUMNO.PRUEBA@TEST.COM",
                "Edad": "26 a 35 años",
                "Sexo": "Femenino",
                "Nacionalidad": "ARGENTINA",
                "Carrera": "Medicina",
                "Anio": "1er año",
                "Conoce_Calendario": "Si",
                "Medios_Info": "Universidad",
                "Esquema_Completo": "No",
                "Libreta": "Sí, en formato digital",
                "Vacunas": "Hepatitis B, BCG",
                "Lugares_Vacunacion": "Hospitales Públicos",
                "Pago_Vacuna": "No",
                "Conoce_Requeridas": "Si",
                "Info_Facultad": "Si",
                "Vacunas_Obligatorias_Colocadas": "No",
                "Tiempo_Antitetanica": "Hace más de 10 años",
                "Momento_HepB": "De adulto",
                "Serologia_HepB": "Si",
                "Antigripal_Este_Anio": "No",
                "Gripe_Anual": "No",
                "Motivo_Vacunacion": "Obligación",
                "Recomendaria": "Si",
                "Nivel_Necesidad": 10,
                "Metodo_Preventivo": "Si",
                "Nivel_Confianza": 5,
                "Carnet_Exterior": "No aplica",
                "Conocia_Obligatorias_Arg": "No aplica",
                "Facultad_Solicito_Doc": "No aplica",
                "Desea_Mas_Info": "Sí",
                "Vacunas_Faltantes": "Antitetánica, Antigripal"
            }
            guardar_respuesta_doble(datos_prueba)
            st.success("✅ ¡Datos enviados al Excel! Hacé clic en 'Actualizar Datos' para verlos.")
            
    st.write("---")
    
    df = pd.DataFrame()
    df_hist = pd.DataFrame()
    
    try:
        res = requests.get(f"{URL_DE_TU_GOOGLE_SCRIPT}?sheet=Respuestas").json()
        if res: df = pd.DataFrame(res)
    except: pass
    
    try:
        res_mov = requests.get(f"{URL_DE_TU_GOOGLE_SCRIPT}?sheet=Movimientos").json()
        if res_mov: df_hist = pd.DataFrame(res_mov)
    except: pass

    if df.empty and os.path.isfile('Base_Respuestas.csv'): df = pd.read_csv('Base_Respuestas.csv')
    if df_hist.empty and os.path.isfile('Historial_Movimientos.csv'): df_hist = pd.read_csv('Historial_Movimientos.csv')

    if not df.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        
        if "Esquema_Completo" in df.columns:
            s_esq = df["Esquema_Completo"].astype(str).str.lower()
            validos_esq = s_esq[s_esq != 'nan']
            if len(validos_esq) > 0:
                completos = len(validos_esq[validos_esq.str.contains("si|completo", na=False)])
                porcentaje_cob = f"{(completos / len(validos_esq) * 100):.1f}%"
            else: porcentaje_cob = "Sin datos"
        else: porcentaje_cob = "Sin datos"
            
        if "Nivel_Confianza" in df.columns:
            s_conf = pd.to_numeric(df["Nivel_Confianza"], errors='coerce')
            if s_conf.notna().any(): promedio_conf = f"{s_conf.mean():.1f} / 5"
            else: promedio_conf = "Sin datos"
        else: promedio_conf = "Sin datos"

        with col_m1:
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 4px 4px 12px rgba(0,0,0,0.3); border: 3px solid #000000; text-align: center;">
                <span style="font-size: 35px;">📋</span>
                <h4 style="margin: 5px 0; font-size: 15px; color: #000000; font-weight: 700;">TOTAL RESPUESTAS</h4>
                <p style="margin: 0; font-size: 36px; font-weight: 800; color: #0056b3;">{len(df)}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m2:
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 4px 4px 12px rgba(0,0,0,0.3); border: 3px solid #000000; text-align: center;">
                <span style="font-size: 35px;">💉</span>
                <h4 style="margin: 5px 0; font-size: 15px; color: #000000; font-weight: 700;">ESQUEMA COMPLETO</h4>
                <p style="margin: 0; font-size: 36px; font-weight: 800; color: #2e7d32;">{porcentaje_cob}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_m3:
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 20px; border-radius: 12px; box-shadow: 4px 4px 12px rgba(0,0,0,0.3); border: 3px solid #000000; text-align: center;">
                <span style="font-size: 35px;">🛡️</span>
                <h4 style="margin: 5px 0; font-size: 15px; color: #000000; font-weight: 700;">CONFIANZA PROMEDIO</h4>
                <p style="margin: 0; font-size: 36px; font-weight: 800; color: #d32f2f;">{promedio_conf}</p>
            </div>
            """, unsafe_allow_html=True)

        st.write("##")

        solapa_datos, solapa_graficos, solapa_diario = st.tabs(["📋 Tablas y Excel", "📊 Gráficos Generales", "📈 Evolución por Día"])
        
        with solapa_datos:
            st.write("### 🔍 Filtros de Búsqueda Rápida")
            
            if "Carrera" in df.columns:
                lista_carreras = ["TODAS"] + list(df["Carrera"].dropna().unique())
                filtro_carrera = st.selectbox("Filtrar por Carrera:", lista_carreras)
            else:
                filtro_carrera = "TODAS"
                
            filtro_buscar = st.text_input("Buscar por Email del Alumno:").upper()
            
            df_filtrado = df.copy()
            if "Carrera" in df.columns and filtro_carrera != "TODAS":
                df_filtrado = df_filtrado[df_filtrado["Carrera"] == filtro_carrera]
            
            if filtro_buscar:
                condicion = pd.Series(False, index=df_filtrado.index)
                if "Email" in df.columns: condicion = condicion | df_filtrado["Email"].astype(str).str.upper().str.contains(filtro_buscar)
                df_filtrado = df_filtrado[condicion]

            columnas_prioridad = ["Fecha", "Email", "Carrera", "Esquema_Completo", "Vacunas_Faltantes"]
            cols_ordenadas = [c for c in columnas_prioridad if c in df_filtrado.columns] + [c for c in df_filtrado.columns if c not in columnas_prioridad and c != "Nombre"]
            df_filtrado = df_filtrado[cols_ordenadas]

            st.write("---")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Base_Completa', index=False)
                if not df_hist.empty: df_hist.to_excel(writer, sheet_name='Movimientos', index=False)
            st.download_button("📥 Descargar Excel de Diagnósticos", data=buffer.getvalue(), file_name=f"Reporte_FCM_{obtener_fecha_archivo()}.xlsx")
            
            st.dataframe(df_filtrado.style.apply(aplicar_cebra, axis=1), use_container_width=True)
            
            if not df_hist.empty:
                st.write("### 👣 Historial de Movimientos Generales")
                st.dataframe(df_hist.style.apply(aplicar_cebra, axis=1), use_container_width=True)

        with solapa_graficos:
            st.write("### 📊 Análisis Visual Demográfico y Sanitario")
            
            def crear_grafico(df_fuente, keyword, tipo, titulo):
                cols = [c for c in df_fuente.columns if keyword.lower() in str(c).lower()]
                if cols:
                    nombre = cols[0]
                    serie_limpia = df_fuente[nombre].astype(str).replace(['', 'nan', 'None', 'NaN', '<NA>'], 'Sin especificar')
                    df_plot = serie_limpia.value_counts().reset_index()
                    df_plot.columns = [nombre, "Cantidad"]
                    
                    if not df_plot.empty and len(df_plot) > 0:
                        try:
                            if tipo == "torta":
                                fig = px.pie(df_plot, names=nombre, values="Cantidad", title=titulo, hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
                                fig.update_traces(textposition='inside', textinfo='percent+label')
                            else:
                                fig = px.bar(df_plot, x=nombre, y="Cantidad", title=titulo, text_auto=True, color=nombre)
                            st.plotly_chart(fig, use_container_width=True)
                            return
                        except: return
                st.info(f"ℹ️ Aún no hay datos suficientes de '{keyword}' para el gráfico: {titulo}")

            col_g1, col_g2 = st.columns(2)
            with col_g1: crear_grafico(df, "sex", "torta", "Participación por Sexo")
            with col_g2: crear_grafico(df, "edad", "barra", "Distribución por Edades")
            
            col_g3, col_g4 = st.columns(2)
            with col_g3: crear_grafico(df, "esquema", "torta", "Estado de Avance del Esquema")
            with col_g4: crear_grafico(df, "carrera", "barra", "Afluencia por Especialidad / Carrera")

        with solapa_diario:
            st.write("### 📈 Reporte de Respuestas por Día")
            if "Fecha" in df.columns:
                df_fecha = df.copy()
                df_fecha["Fecha_DT"] = pd.to_datetime(df_fecha["Fecha"], errors='coerce')
                df_fecha["Día"] = df_fecha["Fecha_DT"].dt.date
                
                df_diario = df_fecha.dropna(subset=["Fecha_DT"])["Día"].value_counts().reset_index()
                df_diario.columns = ["Día", "Cantidad"]
                df_diario = df_diario.sort_values(by="Día") 
                
                if not df_diario.empty:
                    fig_diario = px.line(df_diario, x="Día", y="Cantidad", title="Cantidad de Encuestas Recibidas por Día", markers=True, text="Cantidad")
                    fig_diario.update_traces(textposition="top center", line=dict(color="#0056b3", width=4))
                    st.plotly_chart(fig_diario, use_container_width=True)
                else:
                    st.info("ℹ️ Esperando fechas de respuestas válidas para graficar el avance diario.")
            else:
                st.info("ℹ️ Columna de Fecha no detectada aún en las respuestas.")

    else:
        st.warning("Aún no hay respuestas guardadas en el sistema para procesar.")

else:
    # --- AUTO-SCROLL A LA CIMA AL CAMBIAR DE SECCIÓN ---
    if st.session_state.seccion != st.session_state.seccion_anterior:
        components.html("""
            <script>
                var appContainer = window.parent.document.querySelector('.stApp');
                if (appContainer) { appContainer.scrollTo(0, 0); }
                window.parent.scrollTo(0, 0);
            </script>
        """, height=0)
        st.session_state.seccion_anterior = st.session_state.seccion

    # --- MODO ALUMNO ---
    st.markdown("""
        <div class="header-container">
            <div class="main-logo">🏥💉</div>
            <h1>Encuesta de Vacunación</h1>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.seccion == 1:
        st.header("SECCIÓN 1 - DATOS GENERALES")
        e = st.text_input("Correo Electrónico *").upper()
        edad = st.selectbox("Edad *", ["18 a 25 años", "26 a 35 años", "36 a 45 años", "46 a 55 años", "56 a 65 años"], index=None)
        sexo = st.radio("Sexo *", ["Femenino", "Masculino"], index=None)
        nac = st.selectbox("Nacionalidad *", ["Argentina", "Colombia", "Venezuela", "Chile", "Perú", "Bolivia", "Ecuador", "Brasil", "Uruguay", "Paraguay", "Otros"], index=None)
        
        nac_final = nac
        if nac == "Otros":
            nac_final = st.text_input("Especificá tu nacionalidad *").upper()
            
        carrera = st.selectbox("Carrera *", ["Medicina", "Enfermería", "Fonoaudiología", "Kinesiología y fisiatría", "Nutrición", "Obstetricia", "Bioimágenes", "Podología", "Anestesia", "Cosmetología", "Hemoterapia", "Instrumentación quirúrgica", "Prácticas cardiológicas", "Radiología", "Docente", "No docente", "Visitante", "Odontología", "Posgrado"], index=None)
        anio = st.selectbox("Año que cursa *", ["1er año", "2do año", "3er año", "4to año", "5to año", "6to año", "Docente", "No docente", "Visitante", "Posgrado"], index=None)

        if st.button("Siguiente ➡️"):
            if e.strip() == "" or None in [edad, sexo, nac, carrera, anio] or (nac == "Otros" and nac_final.strip() == ""):
                st.error("⚠️ Completá todos los campos obligatorios antes de avanzar.")
            else:
                st.session_state.es_argentino = (nac == "Argentina")
                st.session_state.respuestas.update({"Email": e, "Edad": edad, "Sexo": sexo, "Nacionalidad": nac_final, "Carrera": carrera, "Anio": anio})
                registrar_movimiento_doble("Sección 1", "Avanzó a Sección 2")
                st.session_state.seccion = 2
                st.rerun()

    elif st.session_state.seccion == 2:
        st.header("SECCIÓN 2 - CONOCIMIENTOS SOBRE LA VACUNACIÓN EN ARGENTINA")
        cal = st.radio("¿Conoces el Calendario Nacional de Vacunación argentino? *", ["Si", "No", "Parcialmente"], index=None)
        
        medios = st.multiselect("¿Por qué medios recibes información sobre vacunación? *", ["Escuela", "Colegio", "Universidad", "Familia", "Redes sociales", "Campañas de salud (por ejemplo, centros de salud, propagandas, puntos saludables, etc)", "No recibí información", "Otros"])
        medios_final = medios.copy()
        otro_medio = ""
        if "Otros" in medios:
            otro_medio = st.text_input("Especificá por qué otro medio * :").upper()
            if otro_medio:
                medios_final.remove("Otros")
                medios_final.append(otro_medio)

        esquema = st.radio("¿Tienes el esquema de vacunación completo? *", ["Si", "No", "No sé"], index=None)
        libreta = st.radio("¿Tienes libreta, carnet o registro de vacunación? *", ["Sí, en formato físico", "Sí, en formato digital", "No", "No sé dónde está"], index=None)
        vacs = st.multiselect("Selecciona las vacunas que te has colocado *", ["BCG", "Neumococo", "Hepatitis A", "Varicela", "HPV", "Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal", "Otros"])
        
        vacs_final = vacs.copy()
        otra_vacuna = ""
        if "Otros" in vacs:
            otra_vacuna = st.text_input("Especificá qué otra vacuna * :").upper()
            if otra_vacuna:
                vacs_final.remove("Otros")
                vacs_final.append(otra_vacuna)

        lugares = st.multiselect("¿En qué lugares te vacunas habitualmente? *", ["Hospitales Públicos", "Hospitales Privados", "Cesac", "Otros"])
        lugares_final = lugares.copy()
        otro_lugar = ""
        if "Otros" in lugares:
            otro_lugar = st.text_input("Especificá qué otro lugar * :").upper()
            if otro_lugar:
                lugares_final.remove("Otros")
                lugares_final.append(otro_lugar)
                
        pago = st.radio("¿Tuviste que pagar alguna vacuna? *", ["Si", "No", "Otros"], index=None)
        pago_final = pago
        if pago == "Otros":
            pago_final = st.text_input("Especificá qué vacuna o situación * :").upper()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 1
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [cal, esquema, libreta, pago] or not medios or not vacs or not lugares or ("Otros" in medios and not otro_medio) or ("Otros" in lugares and not otro_lugar) or (pago == "Otros" and not pago_final) or ("Otros" in vacs and not otra_vacuna):
                    st.error("⚠️ Completá todas las opciones obligatorias.")
                else:
                    st.session_state.respuestas.update({
                        "Conoce_Calendario": cal, "Medios_Info": ", ".join(medios_final), "Esquema_Completo": esquema, 
                        "Libreta": libreta, "Vacunas": ", ".join(vacs_final), "Lugares_Vacunacion": ", ".join(lugares_final), "Pago_Vacuna": pago_final
                    })
                    registrar_movimiento_doble("Sección 2", "Avanzó a Sección 3")
                    st.session_state.seccion = 3
                    st.rerun()

    elif st.session_state.seccion == 3:
        st.header("SECCIÓN 3 - VACUNACIÓN OBLIGATORIA EN LA FACULTAD DE CIENCIAS MÉDICAS")
        req = st.radio("¿Conoces cuáles son las vacunas requeridas por la Facultad de Ciencias Médicas para realizar prácticas hospitalarias? *", ["Si", "No", "Parcialmente"], index=None)
        info_facu = st.radio("¿Recibiste información por parte de la facultad sobre las vacunas requeridas? *", ["Si", "No", "No recuerdo"], index=None)
        ya_colocadas = st.radio("¿Ya te colocaste las vacunas obligatorias? *", ["Si", "No"], index=None)
        t_anti = st.radio("¿Hace cuánto tiempo te colocaste la vacuna Doble adulto (antitetánica)? *", ["Hace menos de 10 años", "Hace más de 10 años", "No recuerdo"], index=None)
        
        m_hepb = st.radio("¿En qué momento te colocaste la vacuna de la Hepatitis B? *", ["Según calendario de vacunación (3 dosis - 0, 1 y 6 meses de vida)", "De adulto", "Otros"], index=None)
        m_hepb_final = m_hepb
        if m_hepb == "Otros":
            m_hepb_final = st.text_input("Especificá el momento de colocación * :").upper()
            
        s_hepb = st.radio("¿Te hiciste la serología de la Hepatitis B? *", ["Si", "No"], index=None)
        antigripal = st.radio("¿Te colocaste la vacuna Antigripal este año? *", ["Si", "No"], index=None)
        anual = st.radio("¿Te vacunas todos los años contra la gripe? *", ["Si", "No", "Algunos"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 2
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [req, info_facu, ya_colocadas, t_anti, m_hepb, s_hepb, antigripal, anual] or (m_hepb == "Otros" and not m_hepb_final):
                    st.error("⚠️ Completá todas las preguntas obligatorias.")
                else:
                    st.session_state.respuestas.update({"Conoce_Requeridas": req, "Info_Facultad": info_facu, "Vacunas_Obligatorias_Colocadas": ya_colocadas, "Tiempo_Antitetanica": t_anti, "Momento_HepB": m_hepb_final, "Serologia_HepB": s_hepb, "Antigripal_Este_Anio": antigripal, "Gripe_Anual": anual})
                    registrar_movimiento_doble("Sección 3", "Avanzó a Sección 4")
                    st.session_state.seccion = 4
                    st.rerun()

    elif st.session_state.seccion == 4:
        st.header("SECCIÓN 4 - CRITERIOS SOBRE LA VACUNACIÓN")
        motivo = st.radio("¿Te vacunaste para poder cumplir con un requisito o por consideración propia? *", ["Obligación", "Consideración propia", "Otros"], index=None)
        motivo_final = motivo
        if motivo == "Otros":
            motivo_final = st.text_input("Especificá cuál fue el motivo * :").upper()
            
        recom = st.radio("¿Recomendarías vacunarse a tus amigos y familiares? *", ["Si", "No"], index=None)
        st.write("¿Qué tan necesarias consideras las vacunas? (0 Innecesario - 10 Muy necesario) *")
        necesarias = st.select_slider("", options=list(range(11)), value=5)
        prev = st.radio("¿Consideras la aplicación de vacunas como método preventivo de complicación de enfermedades? *", ["Si", "No"], index=None)
        st.write("¿Qué tanto confías en la seguridad y eficacia de las vacunas? (1 Ninguna - 5 Total) *")
        confianza = st.select_slider(" ", options=[1,2,3,4,5], value=3)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 3
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [motivo, recom, prev] or (motivo == "Otros" and not motivo_final):
                    st.error("⚠️ Completá todos los campos obligatorios.")
                else:
                    st.session_state.respuestas.update({"Motivo_Vacunacion": motivo_final, "Recomendaria": recom, "Nivel_Necesidad": necesarias, "Metodo_Preventivo": prev, "Nivel_Confianza": confianza})
                    if st.session_state.es_argentino:
                        registrar_movimiento_doble("Sección 4", "Avanzó a Sección 6 (Salteó la 5)")
                        st.session_state.seccion = 6
                    else:
                        registrar_movimiento_doble("Sección 4", "Avanzó a Sección 5")
                        st.session_state.seccion = 5
                    st.rerun()

    elif st.session_state.seccion == 5:
        st.header("SECCIÓN 5 - EXTRANJEROS / PERSONAS QUE HICIERON SU ESQUEMA FUERA DEL PAÍS")
        carnet_ext = st.radio("¿Cuentas con un registro, libreta o carnet de vacunación de tu país de procedencia? *", ["Si", "No", "No lo sé", "Otros"], index=None)
        carnet_ext_final = carnet_ext
        if carnet_ext == "Otros":
            carnet_ext_final = st.text_input("Especificá tu situación con el carnet * :").upper()
            
        conocia_arg = st.radio("Antes del ingreso al país, ¿conocías las vacunas obligatorias en Argentina? *", ["Si", "No", "Otros"], index=None)
        conocia_arg_final = conocia_arg
        if conocia_arg == "Otros":
            conocia_arg_final = st.text_input("Especificá tu conocimiento * :").upper()
            
        facu_solicito = st.radio("¿La facultad te solicitó documentación sobre vacunación? *", ["Si", "No", "No recuerdo", "Otros"], index=None)
        facu_solicito_final = facu_solicito
        if facu_solicito == "Otros":
            facu_solicito_final = st.text_input("Especificá qué te solicitó la facultad * :").upper()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 4
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [carnet_ext, conocia_arg, facu_solicito] or (carnet_ext == "Otros" and not carnet_ext_final) or (conocia_arg == "Otros" and not conocia_arg_final) or (facu_solicito == "Otros" and not facu_solicito_final):
                    st.error("⚠️ Completá todas las opciones obligatorias.")
                else:
                    st.session_state.respuestas.update({"Carnet_Exterior": carnet_ext_final, "Conocia_Obligatorias_Arg": conocia_arg_final, "Facultad_Solicito_Doc": facu_solicito_final})
                    registrar_movimiento_doble("Sección 5", "Avanzó a Sección 6")
                    st.session_state.seccion = 6
                    st.rerun()

    elif st.session_state.seccion == 6:
        st.header("SECCIÓN 6 - INFORMACIÓN")
        mas_info = st.radio("¿Deseas obtener más información sobre vacunación, esquemas y puntos de atención? *", ["Sí", "No"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                if st.session_state.es_argentino: st.session_state.seccion = 4
                else: st.session_state.seccion = 5
                st.rerun()
        with col2:
            if st.button("Finalizar Encuesta ✅"):
                if mas_info is None:
                    st.error("⚠️ Seleccioná una opción antes de finalizar.")
                else:
                    st.session_state.respuestas.update({"Desea_Mas_Info": mas_info})
                    registrar_movimiento_doble("Sección 6", "Finalizó Encuesta")
                    st.session_state.seccion = 7
                    st.rerun()

    elif st.session_state.seccion == 7:
        st.balloons()
        st.header("¡Gracias por completar la encuesta!")
        
        lista_marcadas = st.session_state.respuestas.get("Vacunas", "")
        todas_las_vacunas = ["BCG", "Neumococo", "Hepatitis A", "Varicela", "HPV", "Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"]
        vacunas_faltantes = [v for v in todas_las_vacunas if v not in lista_marcadas]
        
        if not st.session_state.respuesta_guardada:
            datos_finales = {"Fecha": obtener_hora_arg()}
            st.session_state.respuestas["Vacunas_Faltantes"] = ", ".join(vacunas_faltantes) if vacunas_faltantes else "Ninguna"
            datos_finales.update(st.session_state.respuestas)
            guardar_respuesta_doble(datos_finales)
            st.session_state.respuesta_guardada = True

        html_carnet_verde = f"""
        <div class='carnet-oficial'>
            <div class='carnet-header-verde'>
                <h3 style='margin:0; color: white !important;'>🪪 CARNET DE VACUNACIÓN</h3>
            </div>
            <div class='carnet-body'>
                <div class='fila-dato'><b>Usuario:</b> {st.session_state.respuestas.get('Email', 'No especificado')}</div>
                <div class='fila-dato'><b>Nacionalidad:</b> {st.session_state.respuestas.get('Nacionalidad', '')}</div>
                <br>
                <h4 style='margin-bottom: 5px; color: #2e7d32;'>✔️ Vacunas Declaradas:</h4>
                <p style='font-size: 16px; margin-top:0;'>{lista_marcadas if lista_marcadas else 'Ninguna'}</p>
            </div>
        </div>
        """
        st.markdown(html_carnet_verde, unsafe_allow_html=True)
        
        if len(vacunas_faltantes) == 0:
            st.success("🎉 ¡Felicidades! Esquema obligatorio completo.")
        else:
            html_carnet_rojo = f"""
            <div class='carnet-oficial'>
                <div class='carnet-header-rojo'>
                    <h3 style='margin:0; color: white !important;'>🚨 AVISO DE FALTANTES</h3>
                </div>
                <div class='carnet-body'>
                    <h4 style='margin-top: 0; color: #d32f2f;'>Se requiere la aplicación de:</h4>
                    <ul style='font-size: 16px; line-height: 1.6; margin-top: 10px;'>
            """
            for faltante in vacunas_faltantes:
                html_carnet_rojo += f"<li>💉 <b>{faltante}</b></li>"
            html_carnet_rojo += """
                    </ul>
                    <hr style='border: 1px solid #eee;'>
                    <p style='margin-bottom: 5px;'><b>📍 Podés acercarte a:</b></p>
                    <ul style='font-size: 14px; color: #444;'>
                        <li><b>Hospital de Clínicas:</b> Lun. a Vie. de 8:00 a 13:00 hs.</li>
                        <li><b>CESAC más cercano.</b></li>
                    </ul>
                </div></div>
            """
            st.markdown(html_carnet_rojo, unsafe_allow_html=True)

        st.write("---")
        if st.button("Volver al inicio (Nueva respuesta)"):
            st.session_state.clear()
            st.rerun()