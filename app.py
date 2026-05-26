import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io

# --- CONFIGURACIÓN Y DISEÑO ---
st.set_page_config(page_title="Encuesta FCM", page_icon="🏥", layout="centered")

# --- CSS BLINDADO PARA LECTURA PERFECTA ---
st.markdown("""
<style>
    /* 1. FONDO DE PANTALLA (solo se verá en los bordes) */
    .stApp {
        background-image: url("https://img.freepik.com/free-vector/cartoon-coronavirus-vaccine-background_23-2148861308.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* 2. CAJA PRINCIPAL SÓLIDA (SIN TRANSPARENCIA) */
    .block-container {
        background-color: #FFFFFF !important; /* Blanco puro SÓLIDO */
        opacity: 1.0 !important; /* 100% Sólido - Nada de transparencia */
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0px 8px 30px rgba(0,0,0,0.6); /* Sombra más fuerte para que resalte */
        color: #000000; /* Texto negro base */
    }
    
    /* 3. RESALTAR PREGUNTAS (Títulos) */
    .stTextInput label, .stSelectbox label, .stRadio label, .stMultiselect label, h2, h3 {
        color: #000000 !important; /* Negro Puro */
        font-weight: 700 !important; /* Más gruesa (Negrita) */
        font-size: 16px !important;
        margin-bottom: 8px !important;
    }
    
    /* 4. RESALTAR MUCHO LOS RECUADROS DE RESPUESTAS (Inputs) */
    .stTextInput input, .stSelectbox div[role="button"], .stRadio div[role="radiogroup"], .stMultiselect div[role="listbox"], .stSlider div[role="slider"] {
        background-color: #F8F9FA !important; /* Fondo gris súper claro pero SÓLIDO */
        border: 2px solid #6C757D !important; /* Borde MUCHO más grueso y oscuro */
        border-radius: 8px !important;
        color: #000000 !important; /* Texto que escribe el alumno en negro */
        opacity: 1.0 !important;
    }
    
    /* Efecto al hacer clic en un recuadro */
    .stTextInput input:focus, .stSelectbox div[role="button"]:focus {
        border-color: #0056b3 !important;
        box-shadow: 0 0 0 0.2rem rgba(0,86,179,.25) !important;
    }

    /* 5. BOTONES GRANDES Y RESALTADOS */
    div.stButton > button:first-child, div.stDownloadButton > button:first-child {
        background-color: #0056b3;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        box-shadow: 0px 5px 0px #003d82;
        padding: 12px 24px;
        font-weight: bold;
        font-size: 18px;
        transition: all 0.1s;
        width: 100%;
        margin-top: 20px;
    }
    div.stButton > button:first-child:active, div.stDownloadButton > button:first-child:active {
        transform: translateY(5px);
        box-shadow: 0px 0px 0px #003d82;
    }
    
    /* 6. CARNETS SÓLIDOS AL FINAL */
    .carnet-oficial {
        background-color: #FFFFFF !important; /* Blanco Puro SÓLIDO para el carnet */
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border: 2px solid #ddd;
        overflow: hidden;
        margin-bottom: 25px;
        font-family: 'Arial', sans-serif;
        opacity: 1.0 !important;
    }
    .carnet-header-verde {
        background-color: #2e7d32;
        color: white;
        padding: 15px;
        text-align: center;
        border-bottom: 4px solid #1b5e20;
    }
    .carnet-header-rojo {
        background-color: #d32f2f;
        color: white;
        padding: 15px;
        text-align: center;
        border-bottom: 4px solid #b71c1c;
    }
    .carnet-body {
        padding: 20px;
        color: #000000; /* Texto negro en el carnet */
    }
    .fila-dato {
        border-bottom: 1px dashed #666;
        padding: 8px 0;
        font-size: 15px;
    }
    .carnet-footer {
        background-color: #F8F9FA;
        padding: 10px;
        text-align: center;
        font-size: 12px;
        color: #444;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE GUARDADO LOCAL ---
def guardar_respuesta_local(datos):
    archivo = 'Base_Respuestas.csv'
    df_nuevo = pd.DataFrame([datos])
    if not os.path.isfile(archivo):
        df_nuevo.to_csv(archivo, index=False)
    else:
        df_nuevo.to_csv(archivo, mode='a', header=False, index=False)

def registrar_movimiento(seccion_origen, accion_realizada):
    archivo = 'Historial_Movimientos.csv'
    datos = {
        "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Seccion_Origen": seccion_origen,
        "Accion": accion_realizada
    }
    df_nuevo = pd.DataFrame([datos])
    if not os.path.isfile(archivo):
        df_nuevo.to_csv(archivo, index=False)
    else:
        df_nuevo.to_csv(archivo, mode='a', header=False, index=False)

def cerrar_sesion():
    st.session_state.modo_admin = False
    st.session_state.pwd_input = ""

# --- MEMORIA (ESTADO) ---
if 'seccion' not in st.session_state: st.session_state.seccion = 1
if 'respuesta_guardada' not in st.session_state: st.session_state.respuesta_guardada = False
if 'modo_admin' not in st.session_state: st.session_state.modo_admin = False
if 'pwd_input' not in st.session_state: st.session_state.pwd_input = ""
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'es_argentino' not in st.session_state: st.session_state.es_argentino = True

# --- BARRA LATERAL SECRETA ---
st.sidebar.title("🔐 Panel de Control")
st.sidebar.text_input("Ingresá la clave de admin:", type="password", key="pwd_input")
st.session_state.modo_admin = (st.session_state.pwd_input == "fcm2026")

# --- RENDERIZADO ---
if st.session_state.modo_admin:
    st.title("📊 Panel Estadístico FCM (Modo Admin)")
    st.button("⬅️ Volver a la Encuesta", on_click=cerrar_sesion)
    st.write("---")
    
    if os.path.isfile('Base_Respuestas.csv'):
        df = pd.read_csv('Base_Respuestas.csv')
        st.metric(label="Total de Encuestas Respondidas", value=len(df))
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Base_Completa', index=False)
        st.download_button("📥 Descargar Excel", data=buffer.getvalue(), file_name=f"Reporte_FCM_{datetime.now().strftime('%Y%m%d')}.xlsx")
        
        st.write("### 📋 Tabla General de Datos")
        st.dataframe(df)
    else:
        st.warning("Aún no hay respuestas guardadas en esta sesión.")

else:
    # --- MODO ALUMNO ---
    st.title("🏥 Relevamiento de Vacunación FCM")
    st.write("---")

    if st.session_state.seccion == 1:
        st.header("SECCIÓN 1 - DATOS GENERALES")
        n = st.text_input("Nombre y Apellido *")
        e = st.text_input("Correo Electrónico *")
        edad = st.selectbox("Edad *", ["18 a 25 años", "26 a 35 años", "36 a 45 años", "46 a 55 años", "56 a 65 años"])
        sexo = st.radio("Sexo *", ["Femenino", "Masculino"])
        
        nac = st.selectbox("Nacionalidad *", ["Argentina", "Colombia", "Venezuela", "Chile", "Perú", "Bolivia", "Ecuador", "Brasil", "Uruguay", "Paraguay", "Otros:"])
        nac_final = nac
        if nac == "Otros:":
            nac_final = st.text_input("Especificá tu nacionalidad *")
            
        carrera = st.selectbox("Carrera *", ["Medicina", "Enfermería", "Fonoaudiología", "Kinesiología y fisiatría", "Nutrición", "Obstetricia", "Bioimágenes", "Podología", "Anestesia", "Cosmetología", "Hemoterapia", "Instrumentación quirúrgica", "Prácticas cardiológicas", "Radiología", "Docente", "No docente", "Visitante", "Odontología", "Posgrado"])
        anio = st.selectbox("Año que cursa *", ["1er año", "2do año", "3er año", "4to año", "5to año", "6to año", "Docente", "No docente", "Visitante", "Posgrado"])

        st.write("---")
        if st.button("Siguiente ➡️"):
            st.session_state.es_argentino = (nac == "Argentina")
            st.session_state.respuestas.update({"Nombre": n, "Email": e, "Edad": edad, "Sexo": sexo, "Nacionalidad": nac_final, "Carrera": carrera, "Anio": anio})
            registrar_movimiento("Sección 1", "Avanzó a Sección 2")
            st.session_state.seccion = 2
            st.rerun()

    elif st.session_state.seccion == 2:
        st.header("SECCIÓN 2 - CONOCIMIENTOS SOBRE LA VACUNACIÓN EN ARGENTINA")
        cal = st.radio("¿Conoces el Calendario Nacional de Vacunación argentino? *", ["Si", "No", "Parcialmente"])
        
        medios = st.multiselect("¿Por qué medios recibes información sobre vacunación? (Seleccione las opciones correctas) *", [
            "Escuela", "Colegio", "Universidad", "Familia", "Redes sociales", 
            "Campañas de salud (por ejemplo, centros de salud, propagandas, puntos saludables, etc)", 
            "No recibí información", "Otros:"
        ])
        medios_final = medios.copy()
        if "Otros:" in medios:
            otro_medio = st.text_input("Especificá por qué otro medio:")
            if otro_medio:
                medios_final.remove("Otros:")
                medios_final.append(otro_medio)

        esquema = st.radio("¿Tienes el esquema de vacunación completo? *", ["Si", "No", "No sé"])
        libreta = st.radio("¿Tienes libreta, carnet o registro de vacunación? *", ["Sí, en formato físico", "Sí, en formato digital", "No", "No sé dónde está"])
        vacs = st.multiselect("Selecciona las vacunas que te has colocado (Seleccione las opciones correctas) *", ["BCG", "Neumococo", "Hepatitis A", "Varicela", "HPV", "Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"])
        
        lugares = st.multiselect("¿En qué lugares te vacunas habitualmente? (Seleccione las opciones correctas) *", ["Hospitales Públicos", "Hospitales Privados", "Cesac", "Otros:"])
        lugares_final = lugares.copy()
        if "Otros:" in lugares:
            otro_lugar = st.text_input("Especificá qué otro lugar:")
            if otro_lugar:
                lugares_final.remove("Otros:")
                lugares_final.append(otro_lugar)

        pago = st.radio("¿Tuviste que pagar alguna vacuna? *", ["Si", "No", "Otros:"])
        pago_final = pago
        if pago == "Otros:":
            pago_final = st.text_input("Especificá qué vacuna o situación:")

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 1
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                st.session_state.respuestas.update({
                    "Conoce_Calendario": cal, 
                    "Medios_Info": ", ".join(medios_final), 
                    "Esquema_Completo": esquema, 
                    "Libreta": libreta, 
                    "Vacunas": ", ".join(vacs), 
                    "Lugares_Vacunacion": ", ".join(lugares_final), 
                    "Pago_Vacuna": pago_final
                })
                registrar_movimiento("Sección 2", "Avanzó a Sección 3")
                st.session_state.seccion = 3
                st.rerun()

    elif st.session_state.seccion == 3:
        st.header("SECCIÓN 3 - VACUNACIÓN OBLIGATORIA EN LA FACULTAD DE CIENCIAS MÉDICAS")
        req = st.radio("¿Conoces cuáles son las vacunas requeridas por la Facultad de Ciencias Médicas para realizar prácticas hospitalarias? *", ["Si", "No", "Parcialmente"])
        info_facu = st.radio("¿Recibiste información por parte de la facultad sobre las vacunas requeridas? *", ["Si", "No", "No recuerdo"])
        ya_colocadas = st.radio("¿Ya te colocaste las vacunas obligatorias? *", ["Si", "No"])
        t_anti = st.radio("¿Hace cuánto tiempo te colocaste la vacuna Doble adulto (antitetánica)? *", ["Hace menos de 10 años", "Hace más de 10 años", "No recuerdo"])
        
        m_hepb = st.radio("¿En qué momento te colocaste la vacuna de la Hepatitis B? *", [
            "Según calendario de vacunación (3 dosis - 0, 1 y 6 meses de vida)", "De adulto"
        ])
        
        s_hepb = st.radio("¿Te hiciste la serología de la Hepatitis B? *", ["Si", "No"])
        antigripal = st.radio("¿Te colocaste la vacuna Antigripal este año? *", ["Si", "No"])
        anual = st.radio("¿Te vacunas todos los años contra la gripe? *", ["Si", "No", "Algunos"])

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 2
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                st.session_state.respuestas.update({"Conoce_Requeridas": req, "Info_Facultad": info_facu, "Vacunas_Obligatorias_Colocadas": ya_colocadas, "Tiempo_Antitetanica": t_anti, "Momento_HepB": m_hepb, "Serologia_HepB": s_hepb, "Antigripal_Este_Anio": antigripal, "Gripe_Anual": anual})
                registrar_movimiento("Sección 3", "Avanzó a Sección 4")
                st.session_state.seccion = 4
                st.rerun()

    elif st.session_state.seccion == 4:
        st.header("SECCIÓN 4 - CRITERIOS SOBRE LA VACUNACIÓN")
        motivo = st.radio("¿Te vacunaste para poder cumplir con un requisito o por consideración propia? *", ["Obligación", "Consideración propia"])
        recom = st.radio("¿Recomendarías vacunarse a tus amigos y familiares? *", ["Si", "No"])
        
        st.write("¿Qué tan necesarias consideras las vacunas? En una escala donde 0 es 'Innecesario' a 10 'Muy necesario' *")
        necesarias = st.select_slider("", options=list(range(11)), value=5)
        
        prev = st.radio("¿Consideras la aplicación de vacunas como método preventivo de aplicación de enfermedades? *", ["Si", "No"])
        
        st.write("¿Qué tanto confías en la seguridad y eficacia de las vacunas? En una escala donde 1 es 'Ninguna confianza' a 5 es 'Total confianza' *")
        confianza = st.select_slider(" ", options=[1,2,3,4,5], value=3)

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 3
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                st.session_state.respuestas.update({"Motivo_Vacunacion": motivo, "Recomendaria": recom, "Nivel_Necesidad": necesarias, "Metodo_Preventivo": prev, "Nivel_Confianza": confianza})
                
                # Salto inteligente si es argentino
                if st.session_state.es_argentino:
                    registrar_movimiento("Sección 4", "Avanzó a Sección 6 (Salteó la 5)")
                    st.session_state.seccion = 6
                else:
                    registrar_movimiento("Sección 4", "Avanzó a Sección 5")
                    st.session_state.seccion = 5
                
                st.rerun()

    elif st.session_state.seccion == 5:
        st.header("SECCIÓN 5 - EXTRANJEROS / PERSONAS QUE HICIERON SU ESQUEMA DE VACUNACIÓN FUERA DEL PAÍS")
        carnet_ext = st.radio("¿Cuentas con un registro, libreta o carnet de vacunación de tu país de procedencia? *", ["Si", "No", "No lo sé", "Hice mi esquema en Argentina"])
        conocia_arg = st.radio("Antes del ingreso al país, ¿conocías las vacunas obligatorias en Argentina? *", ["Si", "No", "Hice mi esquema en Argentina"])
        facu_solicito = st.radio("¿La facultad te solicitó documentación sobre vacunación? *", ["Si", "No", "No recuerdo", "Hice mi esquema en Argentina"])

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 4
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                st.session_state.respuestas.update({"Carnet_Exterior": carnet_ext, "Conocia_Obligatorias_Arg": conocia_arg, "Facultad_Solicito_Doc": facu_solicito})
                registrar_movimiento("Sección 5", "Avanzó a Sección 6")
                st.session_state.seccion = 6
                st.rerun()

    elif st.session_state.seccion == 6:
        st.header("SECCIÓN 6 - INFORMACIÓN")
        mas_info = st.radio("¿Deseas obtener más información sobre vacunación, esquemas y puntos de atención? *", ["Sí", "No"])

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                if st.session_state.es_argentino:
                    st.session_state.seccion = 4
                else:
                    st.session_state.seccion = 5
                st.rerun()
        with col2:
            if st.button("Finalizar Encuesta ✅"):
                st.session_state.respuestas.update({"Desea_Mas_Info": mas_info})
                registrar_movimiento("Sección 6", "Finalizó Encuesta")
                st.session_state.seccion = 7
                st.rerun()

    elif st.session_state.seccion == 7:
        st.balloons()
        st.header("¡Gracias por completar la encuesta!")
        
        if not st.session_state.respuesta_guardada:
            datos_finales = {"Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            datos_finales.update(st.session_state.respuestas)
            guardar_respuesta_local(datos_finales)
            st.session_state.respuesta_guardada = True

        lista_marcadas = st.session_state.respuestas.get("Vacunas", "")
        vacunas_obligatorias = ["Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"]
        vacunas_faltantes = [v for v in vacunas_obligatorias if v not in lista_marcadas]
        
        html_carnet_verde = f"""
        <div class='carnet-oficial'>
            <div class='carnet-header-verde'>
                <h3 style='margin:0;'>🪪 CARNET DE VACUNACIÓN</h3>
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
                    <h3 style='margin:0;'>🚨 AVISO DE FALTANTES</h3>
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