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
    
    /* CONTENEDOR DEL LOGO Y TITULO */
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

    /* TITULO PRINCIPAL MÁS CHICO */
    h1 {
        font-size: 34px !important;
        color: #002e5d !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px #FFFFFF !important;
        margin-top: 0px !important;
    }
    
    /* TITULOS SECUNDARIOS (Secciones) MÁS CHICOS */
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
    div.stButton > button:first-child:active {
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
    
    /* ESTILOS PARA LAS SOLAPAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        padding: 10px 20px;
        color: #000000;
        font-weight: bold;
        border: 2px solid #000000;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0056b3 !important;
        color: #ffffff !important;
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

def cerrar_sesion():
    st.session_state.modo_admin = False
    st.session_state.pwd_input = ""

# --- MEMORIA ---
if 'seccion' not in st.session_state: st.session_state.seccion = 1
if 'respuesta_guardada' not in st.session_state: st.session_state.respuesta_guardada = False
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'es_argentino' not in st.session_state: st.session_state.es_argentino = True

# --- PANEL ADMIN ---
st.sidebar.title("🔐 Panel de Control")
if st.sidebar.text_input("Clave admin:", type="password") == "fcm2026":
    st.title("📊 Panel Estadístico")
    st.button("⬅️ Volver a la Encuesta", on_click=cerrar_sesion)
    
    df = pd.DataFrame()
    df_hist = pd.DataFrame()
    
    # Recolección de datos (Google + Local)
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
        st.metric(label="Total de Encuestas Respondidas", value=len(df))
        
        # ACA CREAMOS LAS DOS SOLAPAS
        solapa_datos, solapa_graficos = st.tabs(["📋 Tablas y Excel", "📊 Gráficos Estadísticos"])
        
        with solapa_datos:
            st.write("### 📋 Base de Datos en Vivo")
            
            # Botón de descarga
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Base_Completa', index=False)
                if not df_hist.empty: df_hist.to_excel(writer, sheet_name='Movimientos', index=False)
            st.download_button("📥 Descargar Excel Completo", data=buffer.getvalue(), file_name=f"Reporte_FCM_{datetime.now().strftime('%Y%m%d')}.xlsx")
            
            st.dataframe(df)
            
            if not df_hist.empty:
                st.write("### 👣 Historial de Navegación")
                st.dataframe(df_hist)

        with solapa_graficos:
            st.write("### 📊 Análisis Visual")
            col_torta, col_barra = st.columns(2)
            
            with col_torta:
                if "Sexo" in df.columns:
                    # Llenamos los vacíos para que no explote
                    df_sexo = df["Sexo"].fillna("Sin especificar").value_counts().reset_index()
                    df_sexo.columns = ["Sexo", "Cantidad"]
                    fig_sexo = px.pie(df_sexo, names="Sexo", values="Cantidad", title="Participación por Sexo", hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_sexo.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_sexo, use_container_width=True)
            
            with col_barra:
                if "Edad" in df.columns:
                    # Llenamos los vacíos para que no explote
                    df_edad = df["Edad"].fillna("Sin especificar").value_counts().reset_index()
                    df_edad.columns = ["Edad", "Cantidad"]
                    fig_edad = px.bar(df_edad, x="Edad", y="Cantidad", title="Distribución por Edades", text_auto=True, color="Edad")
                    st.plotly_chart(fig_edad, use_container_width=True)
                    
    else:
        st.warning("Aún no hay respuestas guardadas en el sistema para procesar.")

else:
    # --- MODO ALUMNO ---
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
        st.header("SECCIÓN 2 - CONOCIMIENTOS")
        cal = st.radio("¿Conoces el Calendario Nacional? *", ["Si", "No", "Parcialmente"], index=None)
        medios = st.multiselect("¿Por qué medios recibes información? *", ["Escuela", "Universidad", "Familia", "Redes sociales", "Campañas de salud", "Otros"])
        esquema = st.radio("¿Tienes el esquema completo? *", ["Si", "No", "No sé"], index=None)
        libreta = st.radio("¿Tienes libreta o registro? *", ["Físico", "Digital", "No", "No sé"], index=None)
        vacs = st.multiselect("Vacunas que te has colocado *", ["BCG", "Neumococo", "Hepatitis A", "Varicela", "HPV", "Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"])
        lugares = st.multiselect("¿Dónde te vacunas habitualmente? *", ["Hospitales Públicos", "Hospitales Privados", "Cesac", "Otros"])
        pago = st.radio("¿Tuviste que pagar alguna vacuna? *", ["Si", "No", "Otros"], index=None)

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
                    st.session_state.respuestas.update({"Conoce_Calendario": cal, "Esquema_Completo": esquema, "Vacunas": ", ".join(vacs)})
                    registrar_movimiento_doble("Sección 2", "Avanzó a Sección 3")
                    st.session_state.seccion = 3
                    st.rerun()

    elif st.session_state.seccion == 3:
        st.header("SECCIÓN 3 - OBLIGATORIAS FCM")
        req = st.radio("¿Conoces las vacunas requeridas por FCM? *", ["Si", "No", "Parcialmente"], index=None)
        info_facu = st.radio("¿Recibiste info de la facultad? *", ["Si", "No", "No recuerdo"], index=None)
        ya_colocadas = st.radio("¿Ya te colocaste las vacunas obligatorias? *", ["Si", "No"], index=None)
        t_anti = st.radio("¿Hace cuánto te diste la Antitetánica? *", ["Hace menos de 10 años", "Hace más de 10 años", "No recuerdo"], index=None)
        m_hepb = st.radio("¿Momento de vacuna Hepatitis B? *", ["Según calendario de vacunación (3 dosis)", "De adulto"], index=None)
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
        st.header("SECCIÓN 4 - CRITERIOS")
        motivo = st.radio("¿Te vacunaste por obligación o decisión propia? *", ["Obligación", "Consideración propia"], index=None)
        recom = st.radio("¿Recomendarías vacunarse? *", ["Si", "No"], index=None)
        st.write("¿Qué tan necesarias consideras las vacunas? (0 Innecesario - 10 Muy necesario) *")
        necesarias = st.select_slider("", options=list(range(11)), value=5)
        prev = st.radio("¿Consideras las vacunas como método preventivo? *", ["Si", "No"], index=None)
        st.write("¿Nivel de confianza en las vacunas? (1 Ninguna - 5 Total) *")
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
        st.header("SECCIÓN 5 - EXTRANJEROS")
        carnet_ext = st.radio("¿Cuentas con registro de tu país de origen? *", ["Si", "No", "No lo sé", "Hice mi esquema en Argentina"], index=None)
        conocia_arg = st.radio("¿Conocías las vacunas obligatorias de Argentina antes de venir? *", ["Si", "No", "Hice mi esquema en Argentina"], index=None)
        facu_solicito = st.radio("¿La facultad te solicitó documentación? *", ["Si", "No", "No recuerdo", "Hice mi esquema en Argentina"], index=None)

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
        mas_info = st.radio("¿Deseas obtener más información sobre vacunación? *", ["Sí", "No"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 4 if st.session_state.es_argentino else 5
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
            datos_finales = {"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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