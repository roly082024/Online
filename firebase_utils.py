import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

def init_firebase():
    if not firebase_admin._apps:
        service_account_dict = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        }
        
        cred = credentials.Certificate(service_account_dict)
        firebase_admin.initialize_app(cred)
    
    st.session_state.db = firestore.client()
    st.session_state.redirect_uri = os.getenv("REDIRECT_URI")

def load_user_cart(user_id):
    try:
        cart_ref = st.session_state.db.collection('carts').document(user_id)
        cart_doc = cart_ref.get()
        
        if cart_doc.exists:
            cart_data = cart_doc.to_dict()
            st.session_state.cart = cart_data.get('items', [])
        else:
            st.session_state.cart = []
            
    except Exception as e:
        st.error(f"Error al cargar carrito: {str(e)}")
        st.session_state.cart = []

def sync_cart_with_firestore():
    try:
        if 'usuario' in st.session_state:
            user_id = st.session_state['usuario']['uid']
            cart_ref = st.session_state.db.collection('carts').document(user_id)
            
            if 'cart' in st.session_state:
                cart_ref.set({
                    'user_id': user_id,
                    'items': st.session_state.cart,
                    'updated_at': datetime.now()
                }, merge=True)
                
    except Exception as e:
        st.error(f"Error al guardar carrito: {str(e)}")
