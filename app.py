
import streamlit as st
import requests
import os
from dotenv import load_dotenv
from untils import analyze_image_with_chatgpt

load_dotenv(override=True)

API_URL = os.getenv('URL') or "http://localhost:8000"  # Usar variable de entorno o localhost como fallback
##--------------------------------------------------------
# Verificar conexión con la API
try:
    response = requests.get(f"{API_URL}/samples")
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    st.error(f"No se pudo conectar con la API: {e}")
    st.stop()
##--------------------------------------------------------




# Streamlit app
st.title("Proyecto Aurora")

# Sidebar: Imagen
with st.sidebar:
    st.subheader("Imagen relacionada")
    uploaded_file = st.file_uploader("Selecciona una imagen...", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        st.session_state.uploaded_image = uploaded_file
        st.image(uploaded_file, caption="Imagen subida", use_container_width=True)
        
        # Obtener la respuesta de ChatGPT basada en la imagen
        chatgpt_response = analyze_image_with_chatgpt(uploaded_file.getvalue())
        
        # Guardar y mostrar la respuesta en el chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.chat_history.append((chatgpt_response, True))
        
        # Enviar la imagen al backend
        files = {"file": uploaded_file.getvalue()}
        try:
            response = requests.post(f"{API_URL}/upload_image", files=files)
            response.raise_for_status()
            st.success("Imagen subida correctamente")
        except requests.exceptions.RequestException as e:
            st.error(f"Error al subir la imagen: {e}")
    else:
        st.image("https://via.placeholder.com/400", caption="Imagen relacionada", use_container_width=True)


    image_path = "imagen_recuperada.jpg"
    if os.path.exists(image_path):
        st.image(image_path, caption="Imagen recuperada", use_container_width=True)
    else:
        st.warning("")
            
##--------------------------------------------------------

# Funciones para renderizar mensajes
def user_message(message):
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-end; padding: 5px;">
            <div style="background-color: #196b1c; color: white; padding: 10px; border-radius: 10px; font-size:18px; margin-bottom:10px; margin-left:20px;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def bot_message(message):
    st.markdown(
        f"""
        <div style="display: flex; padding: 5px;">
            <div style="background-color: #074c85; color: white; padding: 10px; border-radius: 10px; font-size:18px; margin-bottom:10px; margin-right:20px;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
##--------------------------------------------------------
# Función para el chat
def chat_ui():
    # Inicializar historial si no existe
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Mostrar historial de mensajes
    for msg, is_bot in st.session_state.chat_history:
        if is_bot:
            bot_message(msg)
        else:
            user_message(msg)


##--------------------------------------------------------
# Llamar al chat UI
chat_ui()
