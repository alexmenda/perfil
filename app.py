import streamlit as st
import qrcode
import io
from datetime import date

# Configuración de la página
st.set_page_config(page_title="Sistema de Asistencia IESTP", layout="wide")

# =====================================================================
# 🗄️ BASE DE DATOS SIMULADA EN MEMORIA
# =====================================================================
if "alumnos_db" not in st.session_state:
    st.session_state.alumnos_db = {
        "77777777": {"nombre": "DANI FLORES", "carrera": "APSTI", "ciclo": "III", "turno": "Mañana", "campus": "Sullana"}
    }

if "docentes_db" not in st.session_state:
    st.session_state.docentes_db = {
        "DOC-01": {"nombre": "Carlos Mendoza", "cursos": "Desarrollo Web"}
    }

if "asistencia_db" not in st.session_state:
    st.session_state.asistencia_db = [
        {"fecha": "2026-06-23", "dni": "77777777", "curso": "Desarrollo Web", "estado": "Asistió"}
    ]

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
# 🔀 MENÚ LATERAL INTERACTIVO
# =====================================================================
st.sidebar.title("🚪 Sistema IESTP")
rol_principal = st.sidebar.selectbox("Selecciona tu rol:", ["Soy Alumno", "Soy Docente", "🔑 Panel Administrador (Solo Dani)"])

st.sidebar.markdown("---")

# =====================================================================
# 👤 INTERFAZ: ALUMNO (Solo se registra y ve su propio carnet)
# =====================================================================
if rol_principal == "Soy Alumno":
    st.title("👤 Panel de Estudiantes")
    tab1, tab2 = st.tabs(["🪪 Ver Mi Carnet", "🆕 Registrarse por Primera Vez"])
    
    with tab1:
        lista_alumnos = {v["nombre"]: k for k, v in st.session_state.alumnos_db.items()}
        if lista_alumnos:
            alumno_seleccionado = st.selectbox("Selecciona tu nombre para ingresar:", list(lista_alumnos.keys()))
            if alumno_seleccionado:
                dni_actual = lista_alumnos[alumno_seleccionado]
                datos_alumno = st.session_state.alumnos_db[dni_actual]
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    with st.container(border=True):
                        st.markdown("<div style='background-color:#003366; padding:12px; border-radius:5px; text-align:center; color:white; font-weight:bold;'>IESTP Juan José Farfán Céspedes</div>", unsafe_allow_html=True)
                        st.write("")
                        st.image("https://cdn-icons-png.flaticon.com/512/1946/1946429.png", width=95)
                        st.markdown(f"### {datos_alumno['nombre']}")
                        st.text(f"Carrera: {datos_alumno['carrera']}")
                        st.text(f"Ciclo: {datos_alumno['ciclo']} | Turno: {datos_alumno['turno']}")
                        
                        qr_bytes = generar_qr(dni_actual)
                        st.image(qr_bytes, caption=f"DNI: {dni_actual}", width=130)
                        st.markdown("<div style='background-color:#003366; height:6px; border-radius:5px;'></div>", unsafe_allow_html=True)
                with col2:
                    st.subheader("📊 Tu Historial de Asistencias")
                    historial = [a for a in st.session_state.asistencia_db if a["dni"] == dni_actual]
                    if historial:
                        st.table(historial)
                    else:
                        st.info("Aún no tienes asistencias marcadas.")
        else:
            st.info("No hay alumnos en el sistema.")

    with tab2:
        st.subheader("Formulario de Registro para Alumnos")
        with st.form("form_nuevo_alumno"):
            nuevo_dni = st.text_input("Número de DNI")
            nuevo_nom = st.text_input("Nombre Completo").upper()
            nueva_carr = st.text_input("Carrera", value="APSTI")
            nuevo_ciclo = st.selectbox("Ciclo", ["I", "II", "III", "IV", "V", "VI"])
            nuevo_turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
            
            btn_reg = st.form_submit_button("Crear mi Perfil de Alumno")
            if btn_reg and nuevo_dni and nuevo_nom:
                st.session_state.alumnos_db[nuevo_dni] = {
                    "nombre": nuevo_nom, "carrera": nueva_carr, "ciclo": nuevo_ciclo, "turno": nuevo_turno, "campus": "Sullana"
                }
                st.success("¡Te has registrado con éxito! Ya puedes buscar tu carnet en la pestaña de al lado.")
                st.rerun()

# =====================================================================
# 👨‍🏫 INTERFAZ: DOCENTE (Solo registra asistencias del día)
# =====================================================================
elif rol_principal == "Soy Docente":
    st.title("👨‍🏫 Panel del Docente")
    tab_doc1, tab_doc2 = st.tabs(["📋 Pasar Asistencia", "🆕 Registrar nuevo Docente"])
    
    with tab_doc1:
        lista_docentes = {v["nombre"]: k for k, v in st.session_state.docentes_db.items()}
        if lista_docentes:
            docente_seleccionado = st.selectbox("Docente Activo:", list(lista_docentes.keys()))
            if docente_seleccionado:
                cod_doc_actual = lista_docentes[docente_seleccionado]
                datos_docente = st.session_state.docentes_db[cod_doc_actual]
                st.info(f"Curso asignado: **{datos_docente['cursos']}**")
                
                fecha_clase = st.date_input("Fecha de la Clase", date.today())
                fecha_str = str(fecha_clase)
                
                st.write(f"### 📝 Pasar Lista ({fecha_str})")
                for dni, datos in st.session_state.alumnos_db.items():
                    registro_existente = next((a for a in st.session_state.asistencia_db if a["dni"] == dni and a["fecha"] == fecha_str), None)
                    estado_actual = registro_existente["estado"] if registro_existente else "No Marcado"
                    
                    col_alum, col_estado = st.columns([2, 1])
                    with col_alum:
                        st.write(f"**{datos['nombre']}** (DNI: {dni})")
                    with col_estado:
                        nuevo_estado = st.selectbox("Estado:", ["Asistió", "Faltó", "Tardanza"], key=f"{dni}_{fecha_str}")
                        if registro_existente:
                            registro_existente["estado"] = nuevo_estado
                        else:
                            st.session_state.asistencia_db.append({"fecha": fecha_str, "dni": dni, "curso": datos_docente['cursos'], "estado": nuevo_estado})
                st.success("Cambios guardados provisionalmente.")
        else:
            st.info("No hay docentes registrados.")

    with tab_doc2:
        with st.form("form_docente"):
            nuevo_cod_doc = st.text_input("Código o DNI del Docente")
            nuevo_nom_doc = st.text_input("Nombre Completo")
            curso_doc = st.text_input("Curso a Cargo")
            if st.form_submit_button("Registrar Docente"):
                st.session_state.docentes_db[nuevo_cod_doc] = {"nombre": nuevo_nom_doc, "cursos": curso_doc}
                st.success("¡Docente registrado!")
                st.rerun()

# =====================================================================
# 🔑 INTERFAZ: ADMINISTRADOR PRIVADO (Solo tú tienes acceso)
# =====================================================================
else:
    st.title("🔑 Control de Administrador General")
    st.write("Introduce la contraseña para visualizar la base de datos completa de registros.")
    
    password = st.text_input("Contraseña de Acceso", type="password")
    
    # Puedes cambiar "admin123" por la contraseña que tú quieras
    if password == "admin123":
        st.success("Acceso Concedido, Dani.")
        
        st.subheader("👥 Todos los Alumnos Registrados")
        st.json(st.session_state.alumnos_db)
        
        st.subheader("👨‍🏫 Todos los Docentes Registrados")
        st.json(st.session_state.docentes_db)
        
        st.subheader("📅 Historial Completo de Asistencias Globales")
        st.table(st.session_state.asistencia_db)
    elif password != "":
        st.error("Contraseña incorrecta. Acceso denegado.")