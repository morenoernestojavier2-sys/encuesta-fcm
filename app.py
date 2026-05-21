import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import io

# --- CONFIGURACIÓN Y DISEÑO ---
st.set_page_config(page_title="Encuesta FCM", page_icon="🏥", layout="centered")

st.markdown("""
<style>
    /* Aplicamos el fondo a toda la aplicación */
    .stApp {
        background-image: url("https://img.freepik.com/free-vector/cartoon-coronavirus-vaccine-background_23-2148861308.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Recuadro principal blanco semitransparente para que se lean las preguntas */
    .block-container {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.1);
    }

    /* Estilo 3D para botones */
    div.stButton > button:first-child, div.stDownloadButton > button:first-child {
        background-color: #0056b3;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        box-shadow: 0px 5px 0px #003d82;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.1s;
        width: 100%;
    }
    div.stButton > button:first-child:active, div.stDownloadButton > button:first-child:active {
        transform: translateY(5px);
        box-shadow: 0px 0px 0px #003d82;
    }
    
    /* --- DISEÑO DE LOS CARNETS REALES --- */
    .carnet-oficial {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border: 1px solid #ddd;
        overflow: hidden;
        margin-bottom: 25px;
        font-family: 'Arial', sans-serif;
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
        color: #333;
    }
    .fila-dato {
        border-bottom: 1px dashed #ccc;
        padding: 8px 0;
        font-size: 15px;
    }
    .lista-vacunas {
        font-size: 16px;
        line-height: 1.6;
        margin-top: 10px;
    }
    .carnet-footer {
        background-color: #f1f1f1;
        padding: 10px;
        text-align: center;
        font-size: 12px;
        color: #666;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIÓN AUXILIAR PARA REGISTRAR MOVIMIENTOS ---
def registrar_movimiento(seccion_origen, accion_realizada):
    registro = {
        "Fecha_Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Seccion_Origen": seccion_origen,
        "Accion": accion_realizada
    }
    df_mov = pd.DataFrame([registro])
    if not os.path.isfile("Historial_Movimientos.csv"):
        df_mov.to_csv("Historial_Movimientos.csv", index=False)
    else:
        df_mov.to_csv("Historial_Movimientos.csv", mode='a', header=False, index=False)

# --- FUNCIÓN SEGURA PARA CERRAR SESIÓN ---
def cerrar_sesion():
    st.session_state.modo_admin = False
    st.session_state.pwd_input = ""

# --- MEMORIA DE LA APP ---
if 'seccion' not in st.session_state: st.session_state.seccion = 1
if 'respuesta_guardada' not in st.session_state: st.session_state.respuesta_guardada = False
if 'modo_admin' not in st.session_state: st.session_state.modo_admin = False

if 'nombre_seguro' not in st.session_state: st.session_state.nombre_seguro = ""
if 'email_seguro' not in st.session_state: st.session_state.email_seguro = ""
if 'nacionalidad_segura' not in st.session_state: st.session_state.nacionalidad_segura = ""
if 'edad_segura' not in st.session_state: st.session_state.edad_segura = ""
if 'sexo_seguro' not in st.session_state: st.session_state.sexo_seguro = ""
if 'carrera_segura' not in st.session_state: st.session_state.carrera_segura = ""
if 'anio_seguro' not in st.session_state: st.session_state.anio_seguro = ""
if 'vacunas_seguras' not in st.session_state: st.session_state.vacunas_seguras = []
if 'pwd_input' not in st.session_state: st.session_state.pwd_input = ""

# --- BARRA LATERAL SECRETA PARA ADMINISTRADORES ---
st.sidebar.title("🔐 Panel de Control")
st.sidebar.text_input("Ingresá la clave de admin para ver estadísticas:", type="password", key="pwd_input")

if st.session_state.pwd_input == "fcm2026":
    st.session_state.modo_admin = True
else:
    st.session_state.modo_admin = False

# --- RENDERIZADO SEGÚN EL MODO ---
if st.session_state.modo_admin:
    st.title("📊 Panel Estadístico FCM (Modo Admin)")
    
    st.button("⬅️ Volver a la Encuesta", on_click=cerrar_sesion)
        
    st.write("---")
    
    if os.path.isfile("Base_Respuestas.csv"):
        df = pd.read_csv("Base_Respuestas.csv")
        
        col_metrica, col_descarga = st.columns([1, 1])
        with col_metrica:
            st.metric(label="Total de Encuestas Respondidas", value=len(df))
        with col_descarga:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Base_Completa', index=False)
                
                conteo_nac_excel = df["Nacionalidad"].value_counts().reset_index()
                conteo_nac_excel.columns = ['Nacionalidad', 'Cantidad']
                conteo_nac_excel.to_excel(writer, sheet_name='Estadisticas_Nacionalidad', index=False)
                
                conteo_edad_excel = df["Edad"].value_counts().reset_index()
                conteo_edad_excel.columns = ['Rango de Edad', 'Cantidad']
                conteo_edad_excel.to_excel(writer, sheet_name='Estadisticas_Edad', index=False)
                
                if os.path.isfile("Historial_Movimientos.csv"):
                    df_historial = pd.read_csv("Historial_Movimientos.csv")
                    df_historial.to_excel(writer, sheet_name='Auditoria_Movimientos', index=False)
            
            excel_data = buffer.getvalue()
            st.download_button(
                label="📥 Descargar Excel Oficial",
                data=excel_data,
                file_name=f"Reporte_Completo_FCM_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.write("### 🍰 Distribución por Nacionalidad (Porcentajes)")
        fig_torta = px.pie(df, names='Nacionalidad', hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_torta)
        
        st.write("### 📊 Respuestas por Rangos de Edad")
        conteo_edad = df["Edad"].value_counts()
        st.bar_chart(conteo_edad)
        
        st.write("### 📋 Tabla General de Datos Limpios")
        st.dataframe(df)
        
        if os.path.isfile("Historial_Movimientos.csv"):
            st.write("### 👣 Últimos movimientos de usuarios registrados (Auditoría)")
            st.dataframe(pd.read_csv("Historial_Movimientos.csv"))
        
    else:
        st.warning("Aún no hay ninguna respuesta registrada en el archivo para generar estadísticas.")

else:
    # --- MODO ALUMNO: LA ENCUESTA NORMAL ---
    st.title("🏥 Relevamiento de Vacunación FCM")
    st.write("---")

    if st.session_state.seccion == 1:
        st.header("SECCIÓN 1 - DATOS GENERALES")
        # --- ACÁ AGREGAMOS NOMBRE Y MAIL ---
        nombre = st.text_input("Nombre y Apellido *")
        email = st.text_input("Correo Electrónico *")
        edad = st.selectbox("Edad *", ["18 a 25 años", "26 a 35 años", "36 a 45 años", "46 a 55 años", "56 a 65 años"])
        sexo = st.radio("Sexo *", ["Femenino", "Masculino"])
        nac = st.selectbox("Nacionalidad *", ["Argentina", "Colombia", "Venezuela", "Chile", "Perú", "Bolivia", "Ecuador", "Brasil", "Uruguay", "Paraguay", "Otros"])
        carrera = st.selectbox("Carrera *", ["Medicina", "Enfermería", "Fonoaudiología", "Kinesiología y fisiatría", "Nutrición", "Obstetricia", "Bioimágenes", "Podología", "Anestesia", "Cosmetología", "Hemoterapia", "Instrumentación quirúrgica", "Prácticas cardiológicas", "Radiología"])
        anio = st.selectbox("Año que cursa *", ["1er año", "2do año", "3er año", "4to año", "5to año", "6to año"])

        st.write("---")
        if st.button("Siguiente ➡️"):
            st.session_state.nombre_seguro = nombre
            st.session_state.email_seguro = email
            st.session_state.edad_segura = edad
            st.session_state.sexo_seguro = sexo
            st.session_state.nacionalidad_segura = nac
            st.session_state.carrera_segura = carrera
            st.session_state.anio_seguro = anio
            
            registrar_movimiento("Sección 1", "Avanzó a Sección 2")
            st.session_state.seccion = 2
            st.rerun()

    elif st.session_state.seccion == 2:
        st.header("SECCIÓN 2 - INFORMACIÓN GENERAL")
        st.multiselect("¿Por qué medios recibiste información sobre vacunación? *", ["Escuela", "Colegio", "Universidad", "Familia", "Redes sociales", "Campañas de salud (centros de salud, propagandas, etc)", "No recibí información", "Otros"])
        st.radio("¿Tienes el esquema de vacunación completo? *", ["Si", "No", "No sé"])
        st.radio("¿Tienes libreta, carnet o registro de vacunación? *", ["Sí, en formato físico", "Sí, en formato digital", "No", "No sé dónde está"])
        
        vacs = st.multiselect("Selecciona las vacunas que te has colocado *", ["BCG", "Neumococo", "Hepatitis A", "Varicela", "HPV", "Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"])
        
        st.multiselect("¿En qué lugares te has vacunado? *", ["Hospitales Públicos", "Hospitales Privados", "Cesac", "Otros"])
        st.radio("¿Tuviste que pagar alguna vacuna? *", ["Si", "No"])

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                registrar_movimiento("Sección 2", "Retrocedió a Sección 1")
                st.session_state.seccion = 1
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                st.session_state.vacunas_seguras = vacs
                registrar_movimiento("Sección 2", "Avanzó a Sección 3")
                st.session_state.seccion = 3
                st.rerun()

    elif st.session_state.seccion == 3:
        st.header("SECCIÓN 3 - VACUNACIÓN OBLIGATORIA EN LA FACULTAD")
        st.radio("¿Conoces cuáles son las vacunas requeridas por la FCM para realizar prácticas? *", ["Si", "No", "Parcialmente"])
        st.radio("¿Ya te colocaste las vacunas obligatorias? *", ["Si", "No"])

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                registrar_movimiento("Sección 3", "Retrocedió a Sección 2")
                st.session_state.seccion = 2
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if st.session_state.nacionalidad_segura == "Argentina":
                    registrar_movimiento("Sección 3", "Avanzó a Sección 5 (Salteo Argentino)")
                    st.session_state.seccion = 5
                else:
                    registrar_movimiento("Sección 3", "Avanzó a Sección 4 (Extranjeros)")
                    st.session_state.seccion = 4
                st.rerun()

    elif st.session_state.seccion == 4:
        st.header("SECCIÓN 4 - EXTRANJEROS / ESQUEMA FUERA DEL PAÍS")
        st.radio("¿Cuentas con un registro, libreta o carnet de vacunación de tu país de procedencia? *", ["Si", "No", "No lo sé", "Hice mi esquema en Argentina"])

        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                registrar_movimiento("Sección 4", "Retrocedió a Sección 3")
                st.session_state.seccion = 3
                st.rerun()
        with col2:
            if st.button("Finalizar ✅"):
                registrar_movimiento("Sección 4", "Finalizó Encuesta")
                st.session_state.seccion = 5
                st.rerun()

    elif st.session_state.seccion == 5:
        st.balloons()
        st.header("¡Gracias por completar la encuesta!")
        
        if not st.session_state.respuesta_guardada:
            # --- ACÁ GUARDAMOS NOMBRE Y MAIL EN LA BASE DE DATOS ---
            datos_respuesta = {
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Nombre": st.session_state.nombre_seguro,
                "Email": st.session_state.email_seguro,
                "Edad": st.session_state.edad_segura,
                "Sexo": st.session_state.sexo_seguro,
                "Nacionalidad": st.session_state.nacionalidad_segura,
                "Carrera": st.session_state.carrera_segura,
                "Año": st.session_state.anio_seguro,
                "Vacunas": ", ".join(st.session_state.vacunas_seguras)
            }
            
            df_nuevo = pd.DataFrame([datos_respuesta])
            
            if not os.path.isfile("Base_Respuestas.csv"):
                df_nuevo.to_csv("Base_Respuestas.csv", index=False)
            else:
                df_nuevo.to_csv("Base_Respuestas.csv", mode='a', header=False, index=False)
                
            if st.session_state.nacionalidad_segura == "Argentina":
                registrar_movimiento("Sección 5", "Finalizó Encuesta (Camino Corto)")
                
            st.session_state.respuesta_guardada = True

        vacunas_obligatorias = ["Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"]
        lista_marcadas = st.session_state.vacunas_seguras
        vacunas_faltantes = [v for v in vacunas_obligatorias if v not in lista_marcadas]
        
        # --- CARNET 1: VACUNAS REGISTRADAS (VERDE) ---
        html_carnet_verde = f"""
        <div class='carnet-oficial'>
            <div class='carnet-header-verde'>
                <h3 style='margin:0;'>🪪 CARNET DE VACUNACIÓN</h3>
                <span style='font-size:14px; opacity:0.9;'>Certificado de Aplicación Regular</span>
            </div>
            <div class='carnet-body'>
                <div class='fila-dato'><b>Titular:</b> {st.session_state.nombre_seguro if st.session_state.nombre_seguro else "No especificado"}</div>
                <div class='fila-dato'><b>Correo:</b> {st.session_state.email_seguro if st.session_state.email_seguro else "No especificado"}</div>
                <div class='fila-dato'><b>Nacionalidad:</b> {st.session_state.nacionalidad_segura}</div>
                <br>
                <h4 style='margin-bottom: 5px; color: #2e7d32;'>✔️ Vacunas Declaradas:</h4>
        """
        
        if len(lista_marcadas) > 0:
            html_carnet_verde += "<ul class='lista-vacunas'>"
            for vac in lista_marcadas:
                html_carnet_verde += f"<li>{vac}</li>"
            html_carnet_verde += "</ul>"
        else:
            html_carnet_verde += "<p style='color: #666;'><i>El titular no registra ninguna vacuna en esta encuesta.</i></p>"
            
        html_carnet_verde += """
            </div>
            <div class='carnet-footer'>Documento generado por el Sistema de Relevamiento FCM</div>
        </div>
        """
        st.markdown(html_carnet_verde, unsafe_allow_html=True)
        
        # --- CARNET 2: VACUNAS FALTANTES (ROJO) ---
        if len(vacunas_faltantes) == 0:
            st.success("🎉 ¡Felicidades! Tenés tu esquema de obligatorias completo, no se registran faltantes.")
        else:
            html_carnet_rojo = f"""
            <div class='carnet-oficial'>
                <div class='carnet-header-rojo'>
                    <h3 style='margin:0;'>🚨 AVISO DE FALTANTES</h3>
                    <span style='font-size:14px; opacity:0.9;'>Requisitos Obligatorios Incompletos</span>
                </div>
                <div class='carnet-body'>
                    <h4 style='margin-top: 0; color: #d32f2f;'>Se requiere la aplicación de:</h4>
                    <ul class='lista-vacunas'>
            """
            for faltante in vacunas_faltantes:
                html_carnet_rojo += f"<li>💉 <b>{faltante}</b></li>"
                
            html_carnet_rojo += """
                    </ul>
                    <hr style='border: 1px solid #eee;'>
                    <p style='margin-bottom: 5px;'><b>📍 Podés acercarte a vacunarte de forma gratuita a:</b></p>
                    <ul style='font-size: 14px; color: #444;'>
                        <li><b>Vacunatorio Hospital de Clínicas:</b> Lun. a Vie. de 8:00 a 13:00 hs.</li>
                        <li><b>CESAC más cercano:</b> Consultá horarios según tu comuna.</li>
                    </ul>
                </div>
                <div class='carnet-footer'>Por favor, regularice su situación a la brevedad.</div>
            </div>
            """
            st.markdown(html_carnet_rojo, unsafe_allow_html=True)

        st.write("---")
        if st.button("Volver al inicio (Nueva respuesta)"):
            for key in ["seccion", "respuesta_guardada", "nombre_seguro", "email_seguro", "nacionalidad_segura", "edad_segura", "sexo_seguro", "carrera_segura", "anio_seguro", "vacunas_seguras"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()