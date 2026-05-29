import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import plotly.express as px
import os
import io
import requests
import streamlit.components.v1 as components
import time

# --- CONFIGURACIÓN DE ZONA HORARIA (ARGENTINA UTC-3) ---
TZ_ARG = timezone(timedelta(hours=-3))

def obtener_hora_arg():
    return datetime.now(TZ_ARG).strftime("%Y-%m-%d %H:%M:%S")

def obtener_fecha_archivo():
    return datetime.now(TZ_ARG).strftime('%Y%m%d')

# --- CONFIGURACIÓN GENERAL ---
URL_DE_TU_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbyoYN3-nC8mhJWiNE14_tEcTjqPlh2q0R10Cy3ucE97DmtRmkLQfWlGcTT93EmWnfn7/exec"
st.set_page_config(page_title="Encuesta de vacunación", page_icon="🏥", layout="wide")

# --- MOTOR DE AUTO-SCROLL IMPLACABLE Y ESCUDO ANTI-ACTUALIZACIÓN ---
# Al inyectar time.time(), obligamos al navegador a ejecutar este código en cada recarga sin excepción.
components.html(f"""
    <script>
        var parent = window.parent;
        if(parent) {{
            // 1. Escudo para evitar que F5 o deslizar hacia abajo borre los datos por accidente
            if (!parent.window.antiRefreshAdded) {{
                parent.window.addEventListener("beforeunload", function (e) {{
                    var confirmationMessage = "Tienes respuestas sin guardar. ¿Seguro que quieres salir?";
                    (e || parent.window.event).returnValue = confirmationMessage;
                    return confirmationMessage;
                }});
                parent.window.antiRefreshAdded = true;
            }}

            // 2. Scroll de fuerza bruta hacia arriba
            function forzarArriba() {{
                parent.scrollTo(0, 0);
                var main = parent.document.querySelector('.main');
                if(main) {{ main.scrollTop = 0; }}
            }}
            
            forzarArriba();
            setTimeout(forzarArriba, 50);
            setTimeout(forzarArriba, 200);
            setTimeout(forzarArriba, 500);
        }}
        // Timestamp dinámico: {time.time()}
    </script>
""", height=0)

# --- DISEÑO VISUAL ---
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

def cerrar_sesion():
    st.session_state.modo_admin = False
    st.session_state.pwd_input = ""

def aplicar_cebra(row):
    return ['background-color: #E6F2FF' if row.name % 2 == 0 else 'background-color: #FFFFFF' for _ in row]

# --- MEMORIA DE SESIÓN ---
if 'seccion' not in st.session_state: st.session_state.seccion = 1
if 'respuesta_guardada' not in st.session_state: st.session_state.respuesta_guardada = False
if 'respuestas' not in st.session_state: st.session_state.respuestas = {}
if 'es_argentino' not in st.session_state: st.session_state.es_argentino = True

# --- PANEL ADMIN ---
st.sidebar.title("🔐 Panel de control")
st.sidebar.text_input("Ingresá la clave de admin:", type="password", key="pwd_input")
st.session_state.modo_admin = (st.session_state.pwd_input == "fcm2026")

if st.session_state.modo_admin:
    st.title("📊 Panel estadístico clínico")
    
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    with col_btn1:
        st.button("⬅️ Volver", on_click=cerrar_sesion, use_container_width=True)
    with col_btn2:
        if st.button("🔄 Actualizar datos", use_container_width=True):
            st.rerun()
    with col_btn3:
        if st.button("🗑️ Borrar pruebas", use_container_width=True):
            if os.path.exists('Base_Respuestas.csv'): os.remove('Base_Respuestas.csv')
            if os.path.exists('Historial_Movimientos.csv'): os.remove('Historial_Movimientos.csv')
            st.success("✅ Sistema local limpio. ¡Recordá borrar la fila 1 de tu Google Drive!")
    with col_btn4:
        if st.button("🧪 Enviar prueba", use_container_width=True):
            datos_prueba = {
                "Fecha": obtener_hora_arg(),
                "Email": "alumno.prueba@test.com",
                "Edad": "26 a 35 años",
                "Sexo": "Femenino",
                "Nacionalidad": "Uruguay",
                "Carrera": "Medicina",
                "Anio": "1er año",
                "Conoce_Calendario": "Si",
                "Medios_Info": "Universidad",
                "Esquema_Completo": "No",
                "Libreta": "Sí, en formato digital",
                "Vacunas": "Hepatitis B, BCG",
                "Lugares_Vacunacion": "Hospitales públicos",
                "Pago_Vacuna": "Si - Pagué en vacunatorio privado",
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
                "Vacunas_Faltantes": "Doble adulto (Antitetánica), Antigripal"
            }
            guardar_respuesta_doble(datos_prueba)
            st.success("✅ ¡Datos enviados al Excel! Apretá 'Actualizar datos' para verlos.")
            st.rerun()
            
    st.write("---")
    
    df = pd.DataFrame()
    
    try:
        res = requests.get(f"{URL_DE_TU_GOOGLE_SCRIPT}?sheet=Respuestas").json()
        if res: df = pd.DataFrame(res)
    except: pass
    
    if df.empty and os.path.isfile('Base_Respuestas.csv'): df = pd.read_csv('Base_Respuestas.csv')

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

        solapa_datos, solapa_graficos, solapa_diario = st.tabs(["📋 Tablas y Excel", "📊 Gráficos generales", "📈 Evolución por día"])
        
        with solapa_datos:
            st.write("### 🔍 Filtros de búsqueda rápida")
            
            if "Carrera" in df.columns:
                lista_carreras = ["Todas"] + list(df["Carrera"].dropna().unique())
                filtro_carrera = st.selectbox("Filtrar por carrera:", lista_carreras)
            else:
                filtro_carrera = "Todas"
                
            filtro_buscar = st.text_input("Buscar por correo del alumno:").lower()
            
            df_filtrado = df.copy()
            if "Carrera" in df.columns and filtro_carrera != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Carrera"] == filtro_carrera]
            
            if filtro_buscar:
                condicion = pd.Series(False, index=df_filtrado.index)
                if "Email" in df.columns: condicion = condicion | df_filtrado["Email"].astype(str).str.lower().str.contains(filtro_buscar)
                df_filtrado = df_filtrado[condicion]

            st.write("---")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Base_Completa', index=False)
            st.download_button("📥 Descargar Excel de diagnósticos", data=buffer.getvalue(), file_name=f"Reporte_FCM_{obtener_fecha_archivo()}.xlsx")
            
            st.dataframe(df_filtrado.style.apply(aplicar_cebra, axis=1), use_container_width=True)

        with solapa_graficos:
            st.write("### 📊 Análisis visual demográfico y sanitario")
            
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
            with col_g1: crear_grafico(df, "sex", "torta", "Participación por sexo")
            with col_g2: crear_grafico(df, "edad", "barra", "Distribución por edades")
            
            col_g3, col_g4 = st.columns(2)
            with col_g3: crear_grafico(df, "esquema", "torta", "Estado de avance del esquema")
            with col_g4: crear_grafico(df, "carrera", "barra", "Afluencia por especialidad / carrera")

        with solapa_diario:
            st.write("### 📈 Reporte de respuestas por día")
            if "Fecha" in df.columns:
                df_fecha = df.copy()
                df_fecha["Fecha_DT"] = pd.to_datetime(df_fecha["Fecha"], errors='coerce')
                df_fecha["Día"] = df_fecha["Fecha_DT"].dt.date
                
                df_diario = df_fecha.dropna(subset=["Fecha_DT"])["Día"].value_counts().reset_index()
                df_diario.columns = ["Día", "Cantidad"]
                df_diario = df_diario.sort_values(by="Día") 
                
                if not df_diario.empty:
                    fig_diario = px.line(df_diario, x="Día", y="Cantidad", title="Cantidad de encuestas recibidas por día", markers=True, text="Cantidad")
                    fig_diario.update_traces(textposition="top center", line=dict(color="#0056b3", width=4))
                    st.plotly_chart(fig_diario, use_container_width=True)
                else:
                    st.info("ℹ️ Esperando fechas de respuestas válidas para graficar el avance diario.")
            else:
                st.info("ℹ️ Columna de Fecha no detectada aún en las respuestas.")

    else:
        st.warning("Aún no hay respuestas guardadas en el sistema para procesar.")

else:
    # --- MODO ALUMNO ---
    st.markdown("""
        <div class="header-container">
            <div class="main-logo">🏥💉</div>
            <h1>Encuesta de vacunación</h1>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.seccion == 1:
        st.header("Sección 1 - Datos generales")
        e = st.text_input("Correo electrónico *")
        edad = st.selectbox("Edad *", ["18 a 25 años", "26 a 35 años", "36 a 45 años", "46 a 55 años", "56 a 65 años"], index=None)
        sexo = st.radio("Sexo *", ["Femenino", "Masculino"], index=None)
        
        nac = st.selectbox("Nacionalidad *", ["Argentina", "Colombia", "Venezuela", "Chile", "Perú", "Bolivia", "Ecuador", "Brasil", "Uruguay", "Paraguay", "Otros"], index=None)
        nac_final = nac
        if nac == "Otros":
            nac_final = st.text_input("Especificá tu país *")
            
        carrera = st.selectbox("Carrera *", ["Medicina", "Enfermería", "Fonoaudiología", "Kinesiología y fisiatría", "Nutrición", "Obstetricia", "Bioimágenes", "Podología", "Anestesia", "Cosmetología", "Hemoterapia", "Instrumentación quirúrgica", "Prácticas cardiológicas", "Radiología", "Docente", "No docente", "Visitante", "Odontología", "Posgrado"], index=None)
        anio = st.selectbox("Año que cursa *", ["1er año", "2do año", "3er año", "4to año", "5to año", "6to año", "Docente", "No docente", "Visitante", "Posgrado"], index=None)

        if st.button("Siguiente ➡️"):
            if e.strip() == "" or None in [edad, sexo, nac, carrera, anio] or (nac == "Otros" and (not nac_final or nac_final.strip() == "")):
                st.error("⚠️ Completá todos los campos obligatorios antes de avanzar.")
            else:
                st.session_state.es_argentino = (nac_final.strip().capitalize() == "Argentina")
                st.session_state.respuestas.update({"Email": e.lower().strip(), "Edad": edad, "Sexo": sexo, "Nacionalidad": nac_final.capitalize(), "Carrera": carrera, "Anio": anio})
                st.session_state.seccion = 2
                st.rerun()

    elif st.session_state.seccion == 2:
        st.header("Sección 2 - Conocimientos sobre la vacunación en Argentina")
        cal = st.radio("¿Conoces el calendario nacional de vacunación argentino? *", ["Si", "No", "Parcialmente"], index=None)
        medios = st.multiselect("¿Por qué medios recibes información sobre vacunación? *", ["Escuela", "Colegio", "Universidad", "Familia", "Redes sociales", "Campañas de salud (por ejemplo, centros de salud, propagandas, puntos saludables, etc.)", "No recibí información"])
        esquema = st.radio("¿Tienes el esquema de vacunación completo? *", ["Si", "No", "No sé"], index=None)
        libreta = st.radio("¿Tienes libreta, carnet o registro de vacunación? *", ["Sí, en formato físico", "Sí, en formato digital", "No", "No sé dónde está"], index=None)
        vacs = st.multiselect("Selecciona las vacunas que te has colocado *", ["BCG", "Neumococo", "Hepatitis A", "Varicela", "HPV", "Hepatitis B", "Doble adulto (Antitetánica)", "Antigripal"])
        lugares = st.multiselect("¿En qué lugares te vacunas habitualmente? *", ["Hospitales públicos", "Hospitales privados", "Cesac"])
        
        pago = st.radio("¿Tuviste que pagar alguna vacuna? *", ["Si", "No"], index=None)
        pago_final = pago
        detalle_pago = ""
        if pago == "Si":
            detalle_pago = st.text_input("Especificá qué vacuna o situación de pago *")
            pago_final = f"Si - {detalle_pago}"

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 1
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [cal, esquema, libreta, pago] or not medios or not vacs or not lugares or (pago == "Si" and (not detalle_pago or detalle_pago.strip() == "")):
                    st.error("⚠️ Completá todas las opciones obligatorias.")
                else:
                    st.session_state.respuestas.update({
                        "Conoce_Calendario": cal, "Medios_Info": ", ".join(medios), "Esquema_Completo": esquema, 
                        "Libreta": libreta, "Vacunas": ", ".join(vacs), "Lugares_Vacunacion": ", ".join(lugares), "Pago_Vacuna": pago_final
                    })
                    st.session_state.seccion = 3
                    st.rerun()

    elif st.session_state.seccion == 3:
        st.header("Sección 3 - Vacunación obligatoria en la Facultad de Ciencias Médicas")
        req = st.radio("¿Conoces cuáles son las vacunas requeridas por la Facultad de Ciencias Médicas para realizar prácticas hospitalarias? *", ["Si", "No", "Parcialmente"], index=None)
        info_facu = st.radio("¿Recibiste información por parte de la facultad sobre las vacunas requeridas? *", ["Si", "No", "No recuerdo"], index=None)
        ya_colocadas = st.radio("¿Ya te colocaste las vacunas obligatorias? *", ["Si", "No"], index=None)
        t_anti = st.radio("¿Hace cuánto tiempo te colocaste la vacuna doble adulto (antitetánica)? *", ["Hace menos de 10 años", "Hace más de 10 años", "No recuerdo"], index=None)
        m_hepb = st.radio("¿En qué momento te colocaste la vacuna de la Hepatitis B? *", ["Según calendario de vacunación (3 dosis - 0, 1 y 6 meses de vida)", "De adulto"], index=None)
        s_hepb = st.radio("¿Te hiciste la serología de la Hepatitis B? *", ["Si", "No"], index=None)
        antigripal = st.radio("¿Te colocaste la vacuna antigripal este año? *", ["Si", "No"], index=None)
        anual = st.radio("¿Te vacunas todos los años contra la gripe? *", ["Si", "No", "Algunos"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 2
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [req, info_facu, ya_colocadas, t_anti, m_hepb, s_hepb, antigripal, anual]:
                    st.error("⚠️ Completá todas las preguntas obligatorias.")
                else:
                    st.session_state.respuestas.update({"Conoce_Requeridas": req, "Info_Facultad": info_facu, "Vacunas_Obligatorias_Colocadas": ya_colocadas, "Tiempo_Antitetanica": t_anti, "Momento_HepB": m_hepb, "Serologia_HepB": s_hepb, "Antigripal_Este_Anio": antigripal, "Gripe_Anual": anual})
                    st.session_state.seccion = 4
                    st.rerun()

    elif st.session_state.seccion == 4:
        st.header("Sección 4 - Criterios sobre la vacunación")
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
                    st.error("⚠️ Completá todos los campos obligatorios.")
                else:
                    st.session_state.respuestas.update({"Motivo_Vacunacion": motivo, "Recomendaria": recom, "Nivel_Necesidad": necesarias, "Metodo_Preventivo": prev, "Nivel_Confianza": confianza})
                    if st.session_state.es_argentino:
                        st.session_state.seccion = 6
                    else:
                        st.session_state.seccion = 5
                    st.rerun()

    elif st.session_state.seccion == 5:
        st.header("Sección 5 - Extranjeros / personas que hicieron su esquema fuera del país")
        carnet_ext = st.radio("¿Cuentas con un registro, libreta o carnet de vacunación de tu país de procedencia? *", ["Si", "No", "No lo sé"], index=None)
        conocia_arg = st.radio("Antes del ingreso al país, ¿conocías las vacunas obligatorias en Argentina? *", ["Si", "No"], index=None)
        facu_solicito = st.radio("¿La facultad te solicitó documentación sobre vacunación? *", ["Si", "No", "No recuerdo"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                st.session_state.seccion = 4
                st.rerun()
        with col2:
            if st.button("Siguiente ➡️"):
                if None in [carnet_ext, conocia_arg, facu_solicito]:
                    st.error("⚠️ Completá todas las opciones obligatorias.")
                else:
                    st.session_state.respuestas.update({"Carnet_Exterior": carnet_ext, "Conocia_Obligatorias_Arg": conocia_arg, "Facultad_Solicito_Doc": facu_solicito})
                    st.session_state.seccion = 6
                    st.rerun()

    elif st.session_state.seccion == 6:
        st.header("Sección 6 - Información")
        mas_info = st.radio("¿Deseas obtener más información sobre vacunación, esquemas y puntos de atención? *", ["Sí", "No"], index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Atrás"):
                if st.session_state.es_argentino: st.session_state.seccion = 4
                else: st.session_state.seccion = 5
                st.rerun()
        with col2:
            if st.button("Finalizar encuesta ✅"):
                if mas_info is None:
                    st.error("⚠️ Seleccioná una opción antes de finalizar.")
                else:
                    st.session_state.respuestas.update({"Desea_Mas_Info": mas_info})
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
                <h4 style='margin-bottom: 5px; color: #2e7d32;'>✔️ Vacunas declaradas:</h4>
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
                        <li><b>Cesac más cercano.</b></li>
                    </ul>
                </div></div>
            """
            st.markdown(html_carnet_rojo, unsafe_allow_html=True)

        st.write("---")
        
        components.html("""
            <script>
                var parent = window.parent;
                if(parent) { parent.window.onbeforeunload = null; }
            </script>
        """, height=0)
        
        if st.button("Volver al inicio (Nueva respuesta)"):
            st.session_state.clear()
            st.rerun()