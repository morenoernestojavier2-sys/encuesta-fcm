import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io
import requests
import os

# --- CONFIGURACIÓN ---
URL_DE_TU_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbyoYN3-nC8mhJWiNE14_tEcTjqPlh2q0R10Cy3ucE97DmtRmkLQfWlGcTT93EmWnfn7/exec"
st.set_page_config(page_title="Encuesta FCM", page_icon="🏥", layout="wide")

# --- DISEÑO BLINDADO ---
st.markdown("""
<style>
    .stApp { background-image: url("https://img.freepik.com/free-vector/cartoon-coronavirus-vaccine-background_23-2148861308.jpg") !important; background-size: cover !important; background-attachment: fixed !important; }
    .block-container { background-color: rgba(255, 255, 255, 0.90) !important; border-radius: 15px; box-shadow: 0px 8px 30px rgba(0,0,0,0.9); padding: 40px; }
    h1, h2, h3, .stMetric label { color: #000000 !important; font-weight: 800 !important; text-shadow: 1px 1px 2px #FFFFFF; }
    .stTextInput input, .stSelectbox div[role="button"], .stRadio div[role="radiogroup"] { border: 3px solid #000000 !important; border-radius: 8px !important; background-color: #FFFFFF !important; color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
def registrar_movimiento(seccion, accion):
    correo = st.session_state.respuestas.get("Email", "SIN_MAIL")
    payload = {"tipo": "movimiento", "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Email": correo, "Seccion_Origen": seccion, "Accion": accion}
    try: requests.post(URL_DE_TU_GOOGLE_SCRIPT, json=payload)
    except: pass

def guardar_respuesta(datos):
    payload = {"tipo": "respuesta", "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    payload.update(datos)
    try: requests.post(URL_DE_TU_GOOGLE_SCRIPT, json=payload)
    except: pass

# --- ESTADO ---
if 'seccion' not in st.session_state: st.session_state.seccion = 1
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'es_argentino' not in st.session_state: st.session_state.es_argentino = True

# --- PANEL ADMIN ---
st.sidebar.title("🔐 Panel de Control")
if st.sidebar.text_input("Clave:", type="password") == "fcm2026":
    st.title("📊 Panel Estadístico FCM")
    df = pd.DataFrame()
    try:
        res = requests.get(f"{URL_DE_TU_GOOGLE_SCRIPT}?sheet=Respuestas").json()
        df = pd.DataFrame(res)
    except: pass
    if not df.empty:
        st.metric("Total Encuestas", len(df))
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(px.pie(df, names="Sexo", title="Por Sexo", hole=0.3), use_container_width=True)
        with c2: st.plotly_chart(px.bar(df["Edad"].value_counts().reset_index(), x="Edad", y="count", title="Por Edades"), use_container_width=True)
        st.dataframe(df)
    else: st.warning("No hay datos en Google Drive.")
else:
    # --- ENCUESTA ---
    st.title("🏥 Relevamiento de Vacunación FCM")
    
    # SECCIÓN 1
    if st.session_state.seccion == 1:
        st.header("SECCIÓN 1 - DATOS GENERALES")
        n = st.text_input("Nombre y Apellido *").upper()
        e = st.text_input("Correo Electrónico *").upper()
        edad = st.selectbox("Edad *", ["18 a 25 años", "26 a 35 años", "36 a 45 años", "46 a 55 años", "56 a 65 años"])
        sexo = st.radio("Sexo *", ["Femenino", "Masculino"])
        nac = st.selectbox("Nacionalidad *", ["Argentina", "Colombia", "Venezuela", "Otros:"])
        nac_final = nac if nac != "Otros:" else st.text_input("Especificá tu nacionalidad *").upper()
        carrera = st.selectbox("Carrera *", ["Medicina", "Enfermería", "Fonoaudiología", "Kinesiología y fisiatría", "Nutrición", "Obstetricia", "Bioimágenes", "Podología", "Anestesia", "Cosmetología", "Hemoterapia", "Instrumentación quirúrgica", "Prácticas cardiológicas", "Radiología", "Docente", "No docente", "Visitante", "Odontología", "Posgrado"])
        anio = st.selectbox("Año que cursa *", ["1er año", "2do año", "3er año", "4to año", "5to año", "6to año", "Docente", "No docente", "Visitante", "Posgrado"])
        
        if st.button("Siguiente ➡️"):
            st.session_state.es_argentino = (nac == "Argentina")
            st.session_state.respuestas.update({"Nombre": n, "Email": e, "Edad": edad, "Sexo": sexo, "Nacionalidad": nac_final, "Carrera": carrera, "Anio": anio})
            registrar_movimiento("S1", "Avanzó")
            st.session_state.seccion = 2
            st.rerun()

    # (Acá debés mantener la lógica de tus secciones 2 a 7 que ya tenías)
    # Solo asegurate de que cada vez que hagas un avance, llames a: registrar_movimiento("S[número]", "Avanzó")
    
    # SECCIÓN 7 (Final)
    elif st.session_state.seccion == 7:
        st.balloons()
        if not st.session_state.get('finalizado', False):
            guardar_respuesta(st.session_state.respuestas)
            st.session_state.finalizado = True
        st.header("¡Encuesta finalizada!")