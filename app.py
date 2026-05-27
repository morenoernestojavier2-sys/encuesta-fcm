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

# --- CONFIGURACIÓN ---
URL_DE_TU_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbyoYN3-nC8mhJWiNE14_tEcTjqPlh2q0R10Cy3ucE97DmtRmkLQfWlGcTT93EmWnfn7/exec"
st.set_page_config(page_title="Encuesta de Vacunación", page_icon="🏥", layout="wide")

# --- DISEÑO VISUAL BLINDADO Y AJUSTE DE TAMAÑOS ---
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
    
    .header-container {
        text-align: center;
        margin-bottom: 20px;
        padding: 10px;
        border-bottom: 2px solid #0056b3;
    }
    
    .main-logo {
        font-size: 70px;
        margin-bottom: 0px;
    }

    h1 {
        font-size: 34px !important;
        color: #002e5d !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px #FFFFFF !important;
        margin-top: 0px !important;
    }
    
    h2 {
        font-size: 24px !important;
        color: #000000 !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px #FFFFFF !important;
        margin-bottom: 15px !important;
    }

    .stTextInput label, .stSelectbox label, .stRadio label, .stMultiselect label, .stSlider label, h3, h4, .stMetric label {
        color: #000000 !important; 
        font-weight: 700 !important; 
        text-shadow: 1px 1px 2px #FFFFFF !important; 
    }
    
    .stTextInput input, .stSelectbox div[role="button"], .stRadio div[role="radiogroup"], .stMultiselect div[role="listbox"], .stSlider div[role="slider"] {
        border: 3px solid #000000 !important; 
        border-radius: 8px !important;
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        opacity: 1.0 !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.8) !important; 
    }

    div.stButton > button:first-child, div.stDownloadButton > button:first-child {
        background-color: #0056b3 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 3px solid #000000 !important; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.8) !important; 
        padding: 12px 24px !important;
        font-weight: bold !important;
        font-size: 18px !important;
        width: 100% !important;
        margin-top: 20px !important;
    }
    div.stButton > button:first-child:active, div.stDownloadButton > button:first-child:active {
        transform: translateY(5px) !important;
        box-shadow: 0px 0px 0px #003d82 !important;
    }
    
    .carnet-oficial {
        background-color: #FFFFFF !important; 
        border-radius: 12px !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3) !important;
        border: 4px solid #000000 !important; 
        overflow: hidden !important;
        margin-bottom: 25px !important;
        font-family: 'Arial', sans-serif !important;
        opacity: 1.0 !important;
    }
    .carnet-header-verde {
        background-color: #2e7d32 !important;
        color: white !important;
        padding: 15px !important;
        text-align: center !important;
        border-bottom: 4px solid #1b5e20 !important;
    }
    .carnet-header-rojo {
        background-color: #d32f2f !important;
        color: white !important;
        padding: 15px !important;
        text-align: center !important;
        border-bottom: 4px solid #b71c1c !important;
    }
    .carnet-body {
        padding: 20px !important;
        color: #000000 !important; 
    }
    .fila-dato {
        border-bottom: 2px solid #000000 !important; 
        padding: 10px 0 !important;
        font-size: 15px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        color: #000000;
        font-weight: bold;
        border: 2px solid #000000;
        border-bottom: none;
    }
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
    st.button("⬅️ Volver a la Encuesta", on_click=cerrar_sesion)
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
        # --- TARJETAS MÉTRICAS 3D FLOTANTES (Con blindaje anti-nulos) ---
        col_m1, col_m2, col_m3 = st.columns(3)
        
        # Blindaje Cobertura
        col_esq = [c for c in df.columns if "esquema" in c.lower()]
        if col_esq:
            s_esq = df[col_esq[0]].astype(str).str.lower()
            validos_esq = s_esq[s_esq != 'nan']
            if len(validos_esq) > 0:
                completos = len(validos_esq[validos_esq.str.contains("si|completo", na=False)])
                porcentaje_cob = f"{(completos / len(validos_esq) * 100):.1f}%"
            else: porcentaje_cob = "Sin datos"
        else: porcentaje_cob = "Sin datos"
            
        # Blindaje Confianza
        col_conf = [c for c in df.columns if "confianza" in c.lower()]
        if col_conf:
            s_conf = pd.to_numeric(df[col_conf[0]], errors='coerce')
            if s_conf.notna().any():
                num_conf = s_conf.mean()
                promedio_conf = f"{num_conf:.1f} / 5"
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

        # SOLAPAS
        solapa_datos, solapa_graficos = st.tabs(["📋 Tablas y Excel", "📊 Gráficos Estadísticos"])
        
        with solapa_datos:
            st.write("### 🔍 Filtros de Búsqueda Rápida")
            c_fil1, c_fil2 = st.columns(2)
            
            col_carrera_opt = [c for c in df.columns if "carrera" in c.lower()]
            if col_carrera_opt:
                lista_carreras = ["TODAS"] + list(df[col_carrera_opt[0]].dropna().unique())
                filtro_carrera = st.selectbox("Filtrar por Carrera:", lista_carreras)
            else:
                filtro_carrera = "TODAS"
                
            filtro_buscar = st.text_input("Buscar por Nombre o Email del Alumno:").upper()
            
            df_filtrado = df.copy()
            if col_carrera_opt and filtro_carrera != "TODAS":
                df_filtrado = df_filtrado[df_filtrado[col_carrera_opt[0]] == filtro_carrera]
            if filtro_buscar:
                col_nom = [c for c in df.columns if "nombre" in c.lower()]
                col_em = [c for c in df.columns if "email" in c.lower() or "mail" in c.lower()]
                condicion = pd.Series(False, index=df_filtrado.index)
                if col_nom: condicion = condicion | df_filtrado[col_nom[0]].astype(str).str.upper().str.contains(filtro_buscar)
                if col_em: condicion = condicion | df_filtrado[col_em[0]].astype(str).str.upper().str.contains(filtro_buscar)
                df_filtrado = df_filtrado[condicion]

            st.write("---")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Base_Completa', index=False)
                if not df_hist.empty: df_hist.to_excel(writer, sheet_name='Movimientos', index=False)
            st.download_button("📥 Descargar Excel de Diagnósticos", data=buffer.getvalue(), file_name=f"Reporte_FCM_{obtener_fecha_archivo()}.xlsx")
            
            st.dataframe(df_filtrado)
            
            if not df_hist.empty:
                st.write("### 👣 Historial de Movimientos Generales")
                st.dataframe(df_hist)

        with solapa_graficos:
            st.write("### 📊 Análisis Visual Demográfico y Sanitario")
            
            # --- FUNCION INTERNA PARA GRÁFICOS BLINDADOS ---
            def crear_grafico(df_fuente, keyword, tipo, titulo):
                cols = [c for c in df_fuente.columns if keyword.lower() in str(c).lower()]
                if cols:
                    nombre = cols[0]
                    # Limpieza maestra de datos nulos y vacíos
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
                        except Exception as e:
                            st.error(f"Error técnico al dibujar {titulo}.")
                            return
                st.info(f"ℹ️ Aún no hay datos suficientes de '{keyword}' para el gráfico: {titulo}")

            # Dibujamos de forma segura
            col_g1, col_g2 = st.columns(2)
            with col_g1: crear_grafico(df, "sex", "torta", "Participación por Sexo")
            with col_g2: crear_grafico(df, "edad", "barra", "Distribución por Edades")
            
            col_g3, col_g4 = st.columns(2)
            with col_g3: crear_grafico(df, "esquema", "torta", "Estado de Avance del Esquema")
            with col_g4: crear_grafico(df, "carrera", "barra", "Afluencia por Especialidad / Carrera")

    else:
        st.warning("Aún no hay respuestas guardadas en el sistema para procesar.")

else:
    # --- AUTO-SCROLL A LA CIMA AL CAMBIAR DE SECCIÓN ---
    if st.session_state.seccion != st.session_state.seccion_anterior:
        components.html("""
            <script>
                var appContainer = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                if (appContainer) { appContainer.scrollTo(0, 0); }
                var main = window.parent.document.querySelector('.main');
                if (main) { main.scrollTo(0, 0); }
                window.parent.scrollTo(0, 0);
            </script>
        """, height=0)
        st.session_state.seccion_anterior = st.session_state.seccion

    # --- MODO ALUMNO (ENCUESTA DEFINITIVA) ---
    st.markdown("""
        <div class="header-container">
            <div class="main-logo">🏥💉</div>
            <h1>Encuesta de Vacunación</h1>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.seccion == 1:
        st.header("SECCIÓN 1 - DATOS GENERALES")
        n = st.text_input("Nombre y Apellido *").upper()
        e = st.text_input("Correo Electrónico *").upper()
        edad = st.selectbox("Edad *", ["18 a 25 años", "26 a 35 años", "36 a 45 años", "46 a 55 años", "56 a 65 años"], index=None)
        sexo = st.radio("Sexo *", ["Femenino", "Masculino"], index=None)
        nac = st.selectbox("Nacionalidad *", ["Argentina", "Colombia", "Venezuela", "Chile", "Perú", "Bolivia", "Ecuador", "Brasil", "Uruguay", "Paraguay", "Otros:"], index=None)
        nac_final = nac
        if nac == "Otros:":
            nac_final = st.text_input("Especificá tu nacionalidad *").upper()
        carrera = st.selectbox("Carrera *", ["Medicina", "Enfermería", "Fonoaudiología", "Kinesiología y fisiatría", "Nutrición", "Obstetricia", "Bioimágenes", "Podología", "Anestesia", "Cosmetología", "Hemoterapia", "Instrumentación quirúrgica", "Prácticas cardiológicas", "Radiología", "Docente", "No docente", "Visitante", "Odontología", "Posgrado"], index=None)
        anio = st.selectbox("Año que cursa *", ["1er año", "2do año", "3er año", "4to año", "5to año", "6to año", "Docente", "No docente", "Visitante", "Posgrado"], index=None)

        if st.button("Siguiente ➡️"):
            if n.strip() == "" or e.strip() == "" or None in [edad, sexo, nac, carrera, anio]:
                st.error("⚠️ Completá todos los campos antes de avanzar.")
            else:
                st.session_state.es_argentino = (nac == "Argentina")
                st.session_state.respuestas.update({"Nombre": n, "Email": e, "Edad": edad, "Sexo": sexo, "Nacionalidad": nac_final, "Carrera": carrera, "Anio": anio})
                registrar_movimiento_doble("Sección 1", "Avanzó a Sección 2")
                st.session_state.seccion = 2
                st.rerun()

    elif st.session_state.seccion == 2:
        st.header("SECCIÓN 2 - CONOCIMIENTOS SOBRE LA VACUNACIÓN EN ARGENTINA")
        cal = st.radio("¿Conoces el Calendario Nacional de Vacunación argentino? *", ["Si", "No", "Parcialmente"], index=None)
        medios = st.multiselect("¿Por qué medios recibes información sobre vacunación? *", ["Escuela", "Colegio", "Universidad", "Familia", "Redes sociales", "Campañas de salud", "No recibí información", "Otros"])
        medios_final = medios.copy()
        if "Otros" in medios:
            otro_medio = st.text_input("Especificá por qué otro medio:").upper()
            if otro_medio:
                medios_final.remove("Otros")
                medios_final.append(otro_medio)

        esquema = st.radio("¿Tienes el esquema de vacunación completo? *", ["Si", "No", "No sé"], index=None)
        libreta = st.radio("¿Tienes libreta, carnet o registro de vacunación? *", ["Sí, en formato físico", "Sí, en formato digital", "No", "No sé dónde está"], index=None)
        vacs = st.multiselect("Selecciona las vacunas que te has colocado *", ["BCG", "Neumococo", "Hepatitis A", "Varicela", "HPV", "Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"])
        lugares = st.multiselect("¿En qué lugares te vacunas habitualmente? *", ["Hospitales Públicos", "Hospitales Privados", "Cesac", "Otros"])
        lugares_final = lugares.copy()
        if "Otros" in lugares:
            otro_lugar = st.text_input("Especificá qué otro lugar:").upper()
            if otro_lugar:
                lugares_final.remove("Otros")
                lugares_final.append(otro_lugar)
        pago = st.radio("¿Tuviste que pagar alguna vacuna? *", ["Si", "No", "Otros"], index=None)
        pago_final = pago
        if pago == "Otros:":
            pago_final = st.text_input("Especificá qué vacuna o situación:").upper()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 1
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [cal, esquema, libreta, pago] or not medios or not vacs or not lugares:
                    st.error("⚠️ Completá todas las opciones.")
                else:
                    st.session_state.respuestas.update({
                        "Conoce_Calendario": cal, "Medios_Info": ", ".join(medios_final), "Esquema_Completo": esquema, 
                        "Libreta": libreta, "Vacunas": ", ".join(vacs), "Lugares_Vacunacion": ", ".join(lugares_final), "Pago_Vacuna": pago_final
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
        m_hepb = st.radio("¿En qué momento te colocaste la vacuna de la Hepatitis B? *", ["Según calendario de vacunación (3 dosis)", "De adulto"], index=None)
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
                if None in [req, info_facu, ya_colocadas, t_anti, m_hepb, s_hepb, antigripal, anual]:
                    st.error("⚠️ Completá todas las preguntas.")
                else:
                    st.session_state.respuestas.update({"Conoce_Requeridas": req, "Info_Facultad": info_facu, "Vacunas_Obligatorias_Colocadas": ya_colocadas, "Tiempo_Antitetanica": t_anti, "Momento_HepB": m_hepb, "Serologia_HepB": s_hepb, "Antigripal_Este_Anio": antigripal, "Gripe_Anual": anual})
                    registrar_movimiento_doble("Sección 3", "Avanzó a Sección 4")
                    st.session_state.seccion = 4
                    st.rerun()

    elif st.session_state.seccion == 4:
        st.header("SECCIÓN 4 - CRITERIOS SOBRE LA VACUNACIÓN")
        motivo = st.radio("¿Te vacunaste para poder cumplir con un requisito o por consideración propia? *", ["Obligación", "Consideración propia"], index=None)
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
                if None in [motivo, recom, prev]:
                    st.error("⚠️ Completá todos los campos.")
                else:
                    st.session_state.respuestas.update({"Motivo_Vacunacion": motivo, "Recomendaria": recom, "Nivel_Necesidad": necesarias, "Metodo_Preventivo": prev, "Nivel_Confianza": confianza})
                    if st.session_state.es_argentino:
                        registrar_movimiento_doble("Sección 4", "Avanzó a Sección 6 (Salteó la 5)")
                        st.session_state.seccion = 6
                    else:
                        registrar_movimiento_doble("Sección 4", "Avanzó a Sección 5")
                        st.session_state.seccion = 5
                    st.rerun()

    elif st.session_state.seccion == 5:
        st.header("SECCIÓN 5 - EXTRANJEROS / PERSONAS QUE HICIERON SU ESQUEMA FUERA DEL PAÍS")
        carnet_ext = st.radio("¿Cuentas con un registro, libreta o carnet de vacunación de tu país de procedencia? *", ["Si", "No", "No lo sé", "Hice mi esquema en Argentina"], index=None)
        conocia_arg = st.radio("Antes del ingreso al país, ¿conocías las vacunas obligatorias en Argentina? *", ["Si", "No", "Hice mi esquema en Argentina"], index=None)
        facu_solicito = st.radio("¿La facultad te solicitó documentación sobre vacunación? *", ["Si", "No", "No recuerdo", "Hice mi esquema en Argentina"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 4
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [carnet_ext, conocia_arg, facu_solicito]:
                    st.error("⚠️ Completá todas las opciones.")
                else:
                    st.session_state.respuestas.update({"Carnet_Exterior": carnet_ext, "Conocia_Obligatorias_Arg": conocia_arg, "Facultad_Solicito_Doc": facu_solicito})
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
        
        if not st.session_state.respuesta_guardada:
            datos_finales = {"Fecha": obtener_hora_arg()}
            datos_finales.update(st.session_state.respuestas)
            guardar_respuesta_doble(datos_finales)
            st.session_state.respuesta_guardada = True

        lista_marcadas = st.session_state.respuestas.get("Vacunas", "")
        vacunas_obligatorias = ["Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"]
        vacunas_faltantes = [v for v in vacunas_obligatorias if v not in lista_marcadas]
        
        html_carnet_verde = f"""
        <div class='carnet-oficial'>
            <div class='carnet-header-verde'>
                <h3 style='margin:0; color: white !important;'>🪪 CARNET DE VACUNACIÓN</h3>
            </div>
            <div class='carnet-body'>
                <div class='fila-dato'><b>Titular:</b> {st.session_state.respuestas.get('Nombre', 'No especificado')}</div>
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