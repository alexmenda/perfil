import streamlit as st
import qrcode
import io
import cv2
import numpy as np
from datetime import date

# Configuración de la página
st.set_page_config(page_title="Sistema de Asistencia Central IESTP", layout="wide")

# =====================================================================
# 🌐 BASE DE DATOS CENTRALIZADA EN EL SERVIDOR (MULTIDISPOSITIVO)
# =====================================================================
# Esto permite que los alumnos se registren en sus celulares y el docente los vea en el suyo
@st.cache_resource
def inicializar_db_central():
    return {"alumnos": {}, "docentes": {}, "asistencias": []}

db_global = inicializar_db_central()

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
# VISTA 1: CREAR USUARIO (Alumnos)
# =====================================================================
if opcion == "🆕 Crear mi Usuario (Alumnos)":
    st.title("🆕 Registro de Alumnos")
    st.write("Completa tus datos para registrarte en el sistema unificado:")
    
    with st.form("form_registro", clear_on_submit=True):
        nuevo_dni = st.text_input("Número de DNI o Código")
        nuevo_nom = st.text_input("Nombre Completo").upper()
        nueva_carr = st.text_input("Carrera", value="APSTI")
        nuevo_ciclo = st.selectbox("Ciclo", ["I", "II", "III", "IV", "V", "VI"])
        nuevo_turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
        
        if st.form_submit_button("Registrarme"):
            if nuevo_dni and nuevo_nom:
                db_global["alumnos"][nuevo_dni] = {"nombre": nuevo_nom, "carrera": nueva_carr, "ciclo": nuevo_ciclo, "turno": nuevo_turno}
                st.success(f"¡Registrado con éxito!")
                st.subheader("⬇ nudge Tu Código QR:")
                st.image(generar_qr(nuevo_dni), width=180)
                st.info("💡 Tómale captura a este QR para mostrárselo al docente.")

# =====================================================================
# VISTA 2: ESCANEAR QR (Optimizado para la Cámara Trasera del Celular del Docente)
# =====================================================================
elif opcion == "📸 Escanear QR (Docentes)":
    st.title("📸 Escáner de Asistencia (Móvil)")
    st.write("Presiona el botón de abajo para activar la cámara trasera de tu celular y capturar el QR.")
    
    fecha_str = str(st.date_input("Fecha de Registro:", date.today()))
    
    if db_global["docentes"]:
        lista_docentes = {v["nombre"]: k for k, v in db_global["docentes"].items()}
        doc_sel = st.selectbox("Docente en aula:", list(lista_docentes.keys()))
        curso_actual = db_global["docentes"][lista_docentes[doc_sel]]["curso"]
    else:
        st.warning("⚠️ No hay docentes registrados. La asistencia se guardará como 'General'.")
        curso_actual = "General"
        
    estado_asistencia = st.selectbox("Estado a asignar:", ["Asistió", "Tardanza", "Faltó"])
    
    st.markdown("---")
    st.subheader("📷 Capturar Código QR:")
    
    # TRUCO MAESTRO: En celulares, 'file_uploader' te da la opción de abrir la CÁMARA TRASERA directamente.
    foto_camara = st.file_uploader("Presiona aquí para abrir tu cámara trasera", type=["png", "jpg", "jpeg"])
    
    if foto_camara is not None:
        bytes_data = foto_camara.read()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        detector = cv2.QRCodeDetector()
        dni_detectado, _, _ = detector.detectAndDecode(cv2_img)
        
        if dni_detectado:
            if dni_detectado in db_global["alumnos"]:
                nombre_alumno = db_global["alumnos"][dni_detectado]["nombre"]
                ya_reg = any(a["dni"] == dni_detectado and a["fecha"] == fecha_str for a in db_global["asistencias"])
                
                if not ya_reg:
                    db_global["asistencias"].append({
                        "fecha": fecha_str, "dni": dni_detectado, "nombre": nombre_alumno, "curso": curso_actual, "estado": estado_asistencia
                    })
                    st.success(f"🎉 ¡Escaneo Exitoso! ✔️ {nombre_alumno} registrado.")
                else:
                    st.warning(f"⚠️ El alumno {nombre_alumno} ya tiene asistencia hoy.")
            else:
                st.error(f"❌ El código QR ({dni_detectado}) no pertenece a ningún alumno registrado.")
        else:
            st.error("🔍 No se detectó un código QR claro. Toma la foto de más cerca y bien enfocada.")

# =====================================================================
# VISTA 3: REGISTRAR DOCENTE
# =====================================================================
elif opcion == "👨‍🏫 Registrar Docente":
    st.title("👨‍🏫 Registro de Docente")
    with st.form("form_doc", clear_on_submit=True):
        cod = st.text_input("DNI Docente")
        nom = st.text_input("Nombre").upper()
        cur = st.text_input("Curso").upper()
        if st.form_submit_button("Registrar"):
            if cod and nom:
                db_global["docentes"][cod] = {"nombre": nom, "curso": cur}
                st.success("Docente registrado con éxito.")

# =====================================================================
# VISTA 4: PANEL CREADOR
# =====================================================================
else:
    st.title("🔑 Panel Creador")
    if st.text_input("Contraseña:", type="password") == "admin123":
        st.write("### Alumnos en el Sistema", db_global["alumnos"])
        st.write("### Historial General de Asistencias", db_global["asistencias"])
