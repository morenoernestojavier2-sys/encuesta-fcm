import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io
import requests

# ⚠️ TU LINK DE GOOGLE (YA CONFIGURADO):
URL_DE_TU_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbyoYN3-nC8mhJWiNE14_tEcTjqPlh2q0R10Cy3ucE97DmtRmkLQfWlGcTT93EmWnfn7/exec"

st.set_page_config(page_title="Encuesta FCM", page_icon="🏥", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: url("https://img.freepik.com/free-vector/cartoon-coronavirus-vaccine-background_23-2148861308.jpg") !important; background-size: cover !important; background-attachment: fixed !important; }
    .block-container { background-color: rgba(255, 255, 255, 0.90) !important; border-radius: 15px; box-shadow: 0px 8px 30px rgba(0,0,0,0.9); color: #000000 !important; padding: 40px; }
    h1, h2, h3, .stMetric label { color: #000000 !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES ---
def registrar_movimiento_doble(seccion, accion):
    correo = st.session_state.respuestas.get("Email", "SIN_MAIL")
    payload = {"tipo": "movimiento", "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Email": correo, "Seccion_Origen": seccion, "Accion": accion}
    try: requests.post(URL_DE_TU_GOOGLE_SCRIPT, json=payload)
    except: pass

# --- ESTADO ---
if 'seccion' not in st.session_state: st.session_state.seccion = 1
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'es_argentino' not in st.session_state: st.session_state.es_argentino = True

# --- PANEL ADMIN ---
st.sidebar.title("🔐 Panel de Control")
pwd = st.sidebar.text_input("Clave:", type="password")
if pwd == "fcm2026":
    st.title("📊 Panel Estadístico FCM")
    
    # 1. Intentar cargar datos de Google
    df = pd.DataFrame()
    try:
        res = requests.get(f"{URL_DE_TU_GOOGLE_SCRIPT}?sheet=Respuestas").json()
        df = pd.DataFrame(res)
    except: pass
    
    # 2. Si Google falla o está vacío, intentar cargar local
    if df.empty and os.path.isfile('Base_Respuestas.csv'):
        df = pd.read_csv('Base_Respuestas.csv')

    if not df.empty:
        st.metric("Total Encuestas", len(df))
        
        # FORZAR GRÁFICOS
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Por Sexo")
            fig1 = px.pie(df, names="Sexo", hole=0.3)
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            st.subheader("Por Edad")
            fig2 = px.bar(df["Edad"].value_counts().reset_index(), x="Edad", y="count")
            st.plotly_chart(fig2, use_container_width=True)
            
        st.dataframe(df)
    else:
        st.error("No se encontraron datos ni en Google ni localmente.")
else:
    # --- MODO ALUMNO (Encuesta) ---
    st.title("🏥 Relevamiento FCM")
    # (El resto del código de la encuesta sigue igual...)
    # [Para ahorrar espacio, mantén aquí tu lógica de secciones que ya tenías]