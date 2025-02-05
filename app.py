import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv(override=True)

API_URL = os.getenv('URL') or "http://localhost:8000"  # Usar variable de entorno o localhost como fallback

# Verificar conexión con la API
try:
    response = requests.get(f"{API_URL}/samples")
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    st.error(f"No se pudo conectar con la API: {e}")
    st.stop()

# Streamlit app
st.title("Proyecto Aurora")

# Sidebar: Imagen
with st.sidebar:
    st.subheader("Imagen relacionada")
    # Imagen de ejemplo (puedes reemplazar con una generada)
    st.image(
        "https://via.placeholder.com/400",
        caption="Imagen relacionada",
        use_container_width=True,
    )

# Chat en la parte central
st.subheader("ChatBot")

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

    # Input del usuario
    user_input = st.chat_input("Tu mensaje:")
    if user_input:
        # Guardar mensaje del usuario
        st.session_state.chat_history.append((user_input, False))
        user_message(user_input)

        # Llamada al backend
        try:
            response = requests.post(
                #f"{API_URL}/generate_message", json={"message": user_input}
                f"{API_URL}/generate_message_redis", json={"message": user_input}
            )
            response.raise_for_status()
            bot_response = response.json().get("message", "No se recibió respuesta")
        except requests.exceptions.RequestException as e:
            bot_response = f"Hubo un error: {e}"

        # Guardar y mostrar respuesta del bot
        st.session_state.chat_history.append((bot_response, True))
        bot_message(bot_response)

# Llamar al chat UI
chat_ui()
