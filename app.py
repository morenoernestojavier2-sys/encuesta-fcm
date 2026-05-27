import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os
import io
import requests

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
        max-width: 1000px;
    }
    
    /* TITULO PRINCIPAL MÁS CHICO */
    h1 {
        font-size: 34px !important;
        color: #000000 !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px #FFFFFF !important;
        text-align: center;
    }
    
    /* TITULOS SECUNDARIOS (Secciones) MÁS CHICOS */
    h2 {
        font-size: 24px !important;
        color: #000000 !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px #FFFFFF !important;
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

    div.stButton > button:first-child {
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
    datos = {"Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Email": correo_actual, "Seccion_Origen": seccion_origen, "Accion": accion_realizada}
    archivo = 'Historial_Movimientos.csv'
    df_nuevo = pd.DataFrame([datos])
    if not os.path.isfile(archivo): df_nuevo.to_csv(archivo, index=False)
    else: df_nuevo.to_csv(archivo, mode='a', header=False, index=False)
    payload_mov = {"tipo": "movimiento"}
    payload_mov.update(datos)
    try: requests.post(URL_DE_TU_GOOGLE_SCRIPT, json=payload_mov)
    except: pass

# --- MEMORIA ---
if 'seccion' not in st.session_state: st.session_state.seccion = 1
if 'respuesta_guardada' not in st.session_state: st.session_state.respuesta_guardada = False
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'es_argentino' not in st.session_state: st.session_state.es_argentino = True

# --- PANEL ADMIN ---
st.sidebar.title("🔐 Panel de Control")
if st.sidebar.text_input("Clave de admin:", type="password") == "fcm2026":
    st.title("📊 Panel Estadístico")
    df = pd.DataFrame()
    try:
        res = requests.get(f"{URL_DE_TU_GOOGLE_SCRIPT}?sheet=Respuestas").json()
        if res: df = pd.DataFrame(res)
    except: pass
    if df.empty and os.path.isfile('Base_Respuestas.csv'): df = pd.read_csv('Base_Respuestas.csv')

    if not df.empty:
        st.metric(label="Total de Encuestas", value=len(df))
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(px.pie(df, names="Sexo", title="Por Sexo", hole=0.3), use_container_width=True)
        with c2: st.plotly_chart(px.bar(df["Edad"].value_counts().reset_index(), x="Edad", y="count", title="Por Edades"), use_container_width=True)
        st.write("### 📋 Datos en Vivo")
        st.dataframe(df)
    else:
        st.warning("Aún no hay respuestas guardadas.")
else:
    # --- MODO ALUMNO ---
    st.title("Encuesta de Vacunación")
    st.write("---")

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
        carrera = st.selectbox("Carrera *", ["Medicina", "Enfermería", "Fonoaudiología", "Kinesiología", "Nutrición", "Obstetricia", "Bioimágenes", "Podología", "Otros"], index=None)
        anio = st.selectbox("Año que cursa *", ["1er año", "2do año", "3er año", "4to año", "5to año", "6to año", "Docente", "No docente", "Visitante", "Posgrado"], index=None)

        if st.button("Siguiente ➡️"):
            if n.strip() == "" or e.strip() == "" or None in [edad, sexo, nac, carrera, anio]:
                st.error("⚠️ Completá todos los campos antes de avanzar.")
            else:
                st.session_state.es_argentino = (nac == "Argentina")
                st.session_state.respuestas.update({"Nombre": n, "Email": e, "Edad": edad, "Sexo": sexo, "Nacionalidad": nac_final, "Carrera": carrera, "Anio": anio})
                registrar_movimiento_doble("Sección 1", "Avanzó")
                st.session_state.seccion = 2
                st.rerun()

    elif st.session_state.seccion == 2:
        st.header("SECCIÓN 2 - CONOCIMIENTOS")
        cal = st.radio("¿Conoces el Calendario Nacional? *", ["Si", "No", "Parcialmente"], index=None)
        medios = st.multiselect("¿Por qué medios recibes información? *", ["Escuela", "Universidad", "Familia", "Redes sociales", "Campañas de salud", "Otros"])
        esquema = st.radio("¿Tienes el esquema completo? *", ["Si", "No", "No sé"], index=None)
        libreta = st.radio("¿Tienes libreta o carnet? *", ["Físico", "Digital", "No", "No sé"], index=None)
        vacs = st.multiselect("Vacunas que te has colocado *", ["BCG", "Hepatitis B", "Antitetánica", "Antigripal", "HPV", "Varicela", "Hepatitis A"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 1
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [cal, esquema, libreta] or not medios or not vacs:
                    st.error("⚠️ Completá todas las opciones.")
                else:
                    st.session_state.respuestas.update({"Conoce_Calendario": cal, "Esquema_Completo": esquema, "Vacunas": ", ".join(vacs)})
                    registrar_movimiento_doble("Sección 2", "Avanzó")
                    st.session_state.seccion = 3
                    st.rerun()

    elif st.session_state.seccion == 3:
        st.header("SECCIÓN 3 - OBLIGATORIAS FCM")
        req = st.radio("¿Conoces las vacunas requeridas por FCM? *", ["Si", "No", "Parcialmente"], index=None)
        ya_col = st.radio("¿Ya te colocaste las vacunas obligatorias? *", ["Si", "No"], index=None)
        anti = st.radio("¿Hace cuánto te diste la Antitetánica? *", ["Menos de 10 años", "Más de 10 años", "No recuerdo"], index=None)
        hepb = st.radio("¿Momento de vacuna Hepatitis B? *", ["De niño (3 dosis)", "De adulto"], index=None)
        gripe = st.radio("¿Te vacunaste contra la gripe este año? *", ["Si", "No"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 2
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [req, ya_col, anti, hepb, gripe]:
                    st.error("⚠️ Completá todo.")
                else:
                    st.session_state.respuestas.update({"Antitetanica": anti, "Gripe": gripe})
                    registrar_movimiento_doble("Sección 3", "Avanzó")
                    st.session_state.seccion = 4
                    st.rerun()

    elif st.session_state.seccion == 4:
        st.header("SECCIÓN 4 - CRITERIOS")
        motivo = st.radio("¿Vacunación por obligación o propia? *", ["Obligación", "Propia"], index=None)
        recom = st.radio("¿Recomendarías vacunarse? *", ["Si", "No"], index=None)
        st.write("¿Qué tan necesarias consideras las vacunas? (0 Innecesario - 10 Vital) *")
        necesarias = st.select_slider("", options=list(range(11)), value=5)
        prev = st.radio("¿Consideras las vacunas como preventivas? *", ["Si", "No"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 3
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [motivo, recom, prev]:
                    st.error("⚠️ Completá todo.")
                else:
                    st.session_state.respuestas.update({"Motivo": motivo, "Nivel_Necesidad": necesarias})
                    registrar_movimiento_doble("Sección 4", "Avanzó")
                    st.session_state.seccion = 6 if st.session_state.es_argentino else 5
                    st.rerun()

    elif st.session_state.seccion == 5:
        st.header("SECCIÓN 5 - EXTRANJEROS")
        con_arg = st.radio("¿Conocías las vacunas de Argentina antes de venir? *", ["Si", "No", "Hice mi esquema acá"], index=None)
        doc_sol = st.radio("¿La facultad te pidió documentación? *", ["Si", "No", "No recuerdo"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 4
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [con_arg, doc_sol]:
                    st.error("⚠️ Completá todo.")
                else:
                    st.session_state.respuestas.update({"Conocia_Argentina": con_arg})
                    registrar_movimiento_doble("Sección 5", "Avanzó")
                    st.session_state.seccion = 6
                    st.rerun()

    elif st.session_state.seccion == 6:
        st.header("SECCIÓN 6 - INFORMACIÓN FINAL")
        mas_info = st.radio("¿Deseas más información sobre puntos de atención? *", ["Sí", "No"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 4 if st.session_state.es_argentino else 5
                st.rerun()
        with col2:
            if st.button("Finalizar Encuesta ✅"):
                if mas_info is None:
                    st.error("⚠️ Seleccioná una opción.")
                else:
                    st.session_state.respuestas.update({"Mas_Info": mas_info})
                    registrar_movimiento_doble("Sección 6", "Terminó")
                    st.session_state.seccion = 7
                    st.rerun()

    elif st.session_state.seccion == 7:
        st.balloons()
        st.header("¡Encuesta Enviada!")
        if not st.session_state.respuesta_guardada:
            datos_fin = {"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            datos_fin.update(st.session_state.respuestas)
            guardar_respuesta_doble(datos_fin)
            st.session_state.respuesta_guardada = True
        
        st.write("---")
        if st.button("Volver al inicio"):
            st.session_state.clear()
            st.rerun()