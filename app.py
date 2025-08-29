import streamlit as st
import os
from urllib.parse import urlencode
from auth_utils import google_auth, verificar_o_crear_usuario, google_login_button
from firebase_utils import init_firebase, load_user_cart

# Configuración de la página
st.set_page_config(
    page_title="Fashion Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Cargar estilos CSS
with open("estilos/css_login.html", "r") as file:
    st.markdown(file.read(), unsafe_allow_html=True)

# Inicialización de la aplicación
if 'has_run' not in st.session_state:
    st.session_state.has_run = True
    init_firebase()
    st.session_state.cart = []

# Verificar autenticación con Google OAuth
query_params = st.query_params
code = query_params.get("code")

if 'usuario' not in st.session_state:
    st.session_state.usuario = None

# Manejo de redirecciones
if 'payment' in query_params:
    if query_params['payment'] == 'success':
        # Lógica de pago exitoso (se implementa en payment_utils)
        pass
    elif query_params['payment'] == 'cancelled':
        # REDIRECCIÓN CORREGIDA: Al catálogo si canceló pago
        if 'usuario' in st.session_state and st.session_state.usuario:
            st.switch_page('pages/catalogo.py')

# Lógica principal de autenticación
if not st.session_state.usuario:
    if not code:
        # Mostrar página de login
        st.markdown(f"""
        <div class="main-container">
            <div class="login-card">
                <div class="brand-logo">FASHION STORE</div>
                <div class="brand-subtitle">Luxury Fashion</div>
                <div class="decoration-line"></div>
                <div class="welcome-message">
                    Welcome to the world of exclusive fashion.<br>
                    Sign in to discover your style.
                </div>
                {google_login_button()}
                <div class="legal-text">
                    By continuing, you agree to our <a href="#">Terms of Service</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Procesar callback de Google OAuth
        with st.spinner('Verificando autenticación...'):
            st.session_state.usuario = verificar_o_crear_usuario(code)
            if st.session_state.usuario:
                load_user_cart(st.session_state.usuario['uid'])
            st.query_params.clear()
            st.rerun()
else:
    # Usuario autenticado - redirigir al catálogo
    if 'cart' not in st.session_state:
        load_user_cart(st.session_state.usuario['uid'])
    
    with st.spinner('Todo listo! Redireccionando...'):
        st.session_state.login = True
        st.switch_page('pages/catalogo.py')
