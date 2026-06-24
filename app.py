import streamlit as st
import qrcode
import io

# Configuración de la página
st.set_page_config(page_title="Registro de Asistencia IESTP", layout="wide")

# =====================================================================
# 🗄️ BASE DE DATOS INTERNA (En la memoria del servidor)
# =====================================================================
if "alumnos_db" not in st.session_state:
    st.session_state.alumnos_db = {}

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
# 🚪 MENÚ LATERAL OCULTO (Para ti como Creador)
# =====================================================================
st.sidebar.title("⚙️ Control de Acceso")
rol = st.sidebar.radio("Menú:", ["Formulario de Registro", "🔑 Panel Creador (Ver Todos)"])

# =====================================================================
# 🆕 VISTA 1: LO QUE VEN TUS COMPAÑEROS (Sólo registrarse)
# =====================================================================
if rol == "Formulario de Registro":
    st.title("🆕 Registro de Nuevo Usuario")
    st.write("Por favor, completa tus datos para registrarte en el sistema de asistencia:")

    with st.form("form_solo_registro", clear_on_submit=True):
        nuevo_dni = st.text_input("Número de DNI o Código de Alumno")
        nuevo_nom = st.text_input("Nombre Completo (Apellidos y Nombres)").upper()
        nueva_carr = st.text_input("Carrera Profesional", value="APSTI")
        nuevo_ciclo = st.selectbox("Ciclo Actual", ["I", "II", "III", "IV", "V", "VI"])
        nuevo_turno = st.selectbox("Turno", ["Mañana", "Tarde", "Noche"])
        
        boton_guardar = st.form_submit_button("Crear mi Usuario")
        
        if boton_guardar:
            if nuevo_dni and nuevo_nom:
                # Guardar el alumno en la base de datos interna
                st.session_state.alumnos_db[nuevo_dni] = {
                    "nombre": nuevo_nom, 
                    "carrera": nueva_carr, 
                    "ciclo": nuevo_ciclo, 
                    "turno": nuevo_turno
                }
                
                st.success(f"¡Usuario creado con éxito para: {nuevo_nom}!")
                st.balloons() # Animación de globos
                
                # Le muestra su QR individual al alumno al terminar
                st.markdown("---")
                st.subheader("⬇️ Tu Código QR de Asistencia:")
                qr_bytes = generar_qr(nuevo_dni)
                st.image(qr_bytes, caption=f"DNI: {nuevo_dni}", width=180)
                st.info("💡 Tómarle una captura a este QR para marcar tu asistencia.")
            else:
                st.error("⚠️ El número de DNI y tu Nombre Completo son obligatorios.")

# =====================================================================
# 🔑 VISTA 2: LO QUE VES TÚ (El panel oculto)
# =====================================================================
else:
    st.title("🔑 Panel Privado del Creador")
    st.write("Introduce tu contraseña para ver la lista completa de registrados:")
    
    password = st.text_input("Contraseña de Administrador", type="password")
    
    # Tu clave de acceso
    if password == "admin123":
        st.success("Acceso concedido.")
        
        st.subheader("👥 Lista de Usuarios Registrados en Tiempo Real")
        
        if st.session_state.alumnos_db:
            # Mostramos los datos ordenados en una tabla limpia
            tabla_datos = []
            for dni, info in st.session_state.alumnos_db.items():
                tabla_datos.append({
                    "DNI/Código": dni,
                    "Nombre Completo": info["nombre"],
                    "Carrera": info["carrera"],
                    "Ciclo": info["ciclo"],
                    "Turno": info["turno"]
                })
            st.table(tabla_datos)
            st.write(f"**Total registrados:** {len(tabla_datos)} alumnos.")
        else:
            st.info("Aún no se ha registrado ningún compañero.")
            
    elif password != "":
        st.error("Contraseña incorrecta. Acceso denegado.")
