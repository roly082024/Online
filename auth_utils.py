import streamlit as st
import requests
import re
from datetime import datetime
from urllib.parse import urlencode
import os

def google_auth():
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": os.getenv("REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline"
    }
    return f"{auth_url}?{urlencode(params)}"

def exchange_code_for_tokens(auth_code):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_SECRET_ID"),
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": os.getenv("REDIRECT_URI")
    }
    
    response = requests.post(token_url, data=data)
    return response.json() if response.status_code == 200 else None

def get_user_info(access_token):
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers)
    return response.json() if response.status_code == 200 else None

def verificar_o_crear_usuario(code):
    try:
        tokens = exchange_code_for_tokens(code)
        if not tokens or "access_token" not in tokens:
            return None
        
        user_info = get_user_info(tokens["access_token"])
        if not user_info:
            return None
        
        google_id = user_info.get('id')
        email = user_info.get('email')
        nombre = user_info.get('name')
        foto = user_info.get('picture')
        
        if not all([google_id, email, nombre, foto]):
            return None
        
        # Verificar/crear usuario en Firebase
        doc_ref = st.session_state.db.collection('usuarios').document(google_id)
        doc = doc_ref.get()
        
        if doc.exists:
            usuario_data = doc.to_dict()
            usuario_data['last_login'] = datetime.now()
            doc_ref.update({'last_login': datetime.now()})
            return usuario_data
        else:
            nuevo_usuario = {
                'uid': google_id,
                'email': email,
                'nombre': re.sub(r"\s*\(.*?\)", "", nombre).strip(),
                'foto': foto,
                'verified_email': user_info.get('verified_email', False),
                'locale': user_info.get('locale', 'en'),
                'created_at': datetime.now(),
                'last_login': datetime.now()
            }
            doc_ref.set(nuevo_usuario)
            return nuevo_usuario
            
    except Exception as e:
        st.error(f"Error durante autenticación: {str(e)}")
        return None

def google_login_button():
    google_svg = """<svg class="google-icon" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>"""

    button_html = f"""<button class="google-login-btn">{google_svg}Continue with Google</button>"""
    return f"""<a href="{google_auth()}" style="text-decoration: none;">{button_html}</a>"""
