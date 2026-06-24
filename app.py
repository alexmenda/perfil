import streamlit as st
import qrcode
import io
import cv2
import numpy as np
from datetime import date

# Configuración de la página
st.set_page_config(page_title="Sistema de Asistencia Automatizado IESTP", layout="wide")

# =====================================================================
# 🗄️ BASE DE DATOS INTERNA EN MEMORIA
# =====================================================================
if "alumnos_db" not in st.session_state:
    st.session_state.alumnos_db = {}

if "docentes_db" not in st.session_state:
    st.session_state.docentes_db = {}

if "asistencia_db" not in st.session_state:
    st.session_state.asistencia_db = []

# --- FUNCIÓN PARA GENERAR QR ---
def generar_qr(datos):
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(datos)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# =====================================================================
# 🚪 MENÚ LATERAL INTERACTIVO
# =====================================================================
st.sidebar.title("🚪 Menú de Asistencia")
opcion = st.sidebar.radio("Selecciona una opción:", [
    "🆕 Crear mi Usuario (Alumnos)", 
    "📸 Escanear QR (Docentes)", 
    "👨‍🏫 Registrar Docente",
    "🔑 Panel Creador (Solo Dani)"
])

st.sidebar.markdown("---")

# =====================================================================
# VISTA 1: CREAR USUARIO (Para tus compañeros)
# =====================================================================
if opcion == "🆕 Crear mi Usuario (Alumnos)":
    st.title("🆕 Registro de Nuevo Alumno")
    st.write("Completa tus datos para registrarte y obtener tu código QR oficial:")
    
    with st.form("form_registro", clear_on_submit=True):
        nuevo_dni = st.text_input("Número de DNI o Código de Alumno")
        nuevo_nom = st.text_input("Nombre Completo (Apellidos y Nombres)").upper()
        nueva_carr = st.text_input("Carrera Profesional", value="APSTI")
        nuevo_ciclo = st.selectbox("Ciclo Actual", ["I", "II", "III", "IV", "V", "VI"])
        nuevo_turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
        
        boton_guardar = st.form_submit_button("Registrarme como Alumno")
        
        if boton_guardar:
            if nuevo_dni and nuevo_nom:
                st.session_state.alumnos_db[nuevo_dni] = {
                    "nombre": nuevo_nom, "carrera": nueva_carr, "ciclo": nuevo_ciclo, "turno": nuevo_turno
                }
                st.success(f"¡Usuario creado con éxito para: {nuevo_nom}!")
                st.balloons()
                
                st.markdown("---")
                st.subheader("⬇/ Tu Código QR de Asistencia Generado:")
                qr_bytes = generar_qr(nuevo_dni)
                st.image(qr_bytes, caption=f"DNI: {nuevo_dni}", width=180)
                st.info("💡 Tómale una captura de pantalla a este QR. Este es el que presentarás para marcar tu asistencia.")
            else:
                st.error("⚠️ El DNI/Código y el Nombre Completo son obligatorios.")

# =====================================================================
# VISTA 2: ESCANEAR QR AUTOMÁTICO (¡Cámara Integrada!)
# =====================================================================
elif opcion == "📸 Escanear QR (Docentes)":
    st.title("📸 Escáner de Asistencia por Cámara")
    st.write("Muestra el código QR del alumno frente a la cámara para registrar su entrada de forma automática.")
    
    fecha_hoy = st.date_input("Fecha de Registro:", date.today())
    fecha_str = str(fecha_hoy)
    
    # Selector de docentes
    if st.session_state.docentes_db:
        lista_docentes = {v["nombre"]: k for k, v in st.session_state.docentes_db.items()}
        docente_seleccionado = st.selectbox("Docente en aula:", list(lista_docentes.keys()))
        curso_actual = st.session_state.docentes_db[lista_docentes[docente_seleccionado]]["curso"]
    else:
        st.warning("⚠️ No hay docentes registrados. La asistencia se guardará como 'General'.")
        curso_actual = "General"

    estado_asistencia = st.selectbox("Estado a asignar al escanear:", ["Asistió", "Tardanza", "Faltó"])

    st.markdown("---")
    st.subheader("📷 Enciende tu cámara aquí:")
    
    # Activa la cámara integrada de Streamlit
    foto_camara = st.camera_input("Apunta al código QR del alumno")

    if foto_camara is not None:
        # Convertir la imagen de la cámara para que OpenCV pueda leerla
        bytes_data = foto_camara.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Detector de códigos QR
        detector = cv2.QRCodeDetector()
        dni_detectado, _, _ = detector.detectAndDecode(cv2_img)
        
        if dni_detectado:
            # Si el código QR contiene un DNI válido y registrado
            if dni_detectado in st.session_state.alumnos_db:
                nombre_alumno = st.session_state.alumnos_db[dni_detectado]["nombre"]
                
                # Verificar que no se duplique la asistencia del mismo alumno el mismo día
                ya_registrado = any(a["dni"] == dni_detectado and a["fecha"] == fecha_str for a in st.session_state.asistencia_db)
                
                if not ya_registrado:
                    st.session_state.asistencia_db.append({
                        "fecha": fecha_str,
                        "dni": dni_detectado,
                        "nombre": nombre_alumno,
                        "curso": curso_actual,
                        "estado": estado_asistencia
                    })
                    st.success(f"🎉 ¡Escaneo Exitoso! ✔️ {nombre_alumno} registrado como '{estado_asistencia}' en {curso_actual}.")
                else:
                    st.warning(f"⚠️ El alumno {nombre_alumno} ya cuenta con asistencia registrada el día de hoy.")
            else:
                st.error(f"❌ Código detectado ({dni_detectado}), pero este alumno NO está registrado en el sistema.")
        else:
            st.info("🔍 Cámara activa. Asegúrate de centrar bien el código QR frente al lente para que se procese el marcado.")

# =====================================================================
# VISTA 3: REGISTRAR DOCENTE
# =====================================================================
elif opcion == "👨‍🏫 Registrar Docente":
    st.title("👨‍🏫 Registro de Nuevo Docente")
    
    with st.form("form_docente", clear_on_submit=True):
        cod_docente = st.text_input("Código o DNI del Docente")
        nom_docente = st.text_input("Nombre Completo del Profesor").upper()
        curso_docente = st.text_input("Curso / Unidad Didáctica a Cargo").upper()
        
        btn_doc = st.form_submit_button("Registrar Docente")
        if btn_doc:
            if cod_docente and nom_docente:
                st.session_state.docentes_db[cod_docente] = {
                    "nombre": nom_docente, "curso": curso_docente
                }
                st.success(f"¡Docente {nom_docente} registrado con éxito!")
            else:
                st.error("⚠️ El código y el nombre del docente son obligatorios.")

# =====================================================================
# VISTA 4: PANEL CREADOR (Tu control privado)
# =====================================================================
else:
    st.title("🔑 Control General del Creador")
    password = st.text_input("Introduce tu contraseña de acceso:", type="password")
    
    if password == "admin123":
        st.success("¡Acceso correcto!")
        tab_usuarios, tab_docentes, tab_asistencias = st.tabs(["👥 Alumnos", "👨‍🏫 Docentes", "📅 Historial Asistencias"])
        
        with tab_usuarios:
            if st.session_state.alumnos_db:
                tabla_alumnos = [{"DNI/Código": k, "Nombre": v["nombre"], "Carrera": v["carrera"], "Ciclo": v["ciclo"]} for k, v in st.session_state.alumnos_db.items()]
                st.table(tabla_alumnos)
            else:
                st.info("No hay alumnos creados aún.")
                
        with tab_docentes:
            if st.session_state.docentes_db:
                tabla_docentes = [{"DNI": k, "Nombre": v["nombre"], "Curso": v["curso"]} for k, v in st.session_state.docentes_db.items()]
                st.table(tabla_docentes)
            else:
                st.info("No hay docentes creados aún.")
                
        with tab_asistencias:
            if st.session_state.asistencia_db:
                st.table(st.session_state.asistencia_db)
            else:
                st.info("Nadie ha registrado asistencia hoy.")
