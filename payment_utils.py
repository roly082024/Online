import stripe
import os
from datetime import datetime
import streamlit as st

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_order_in_firestore(db, cart, usuario, status='pending'):
    try:
        order_data = {
            'user_id': usuario['uid'],
            'user_email': usuario['email'],
            'items': cart,
            'total': sum(item['price'] * item['quantity'] for item in cart),
            'status': status,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        order_ref = db.collection('orders').document()
        order_ref.set(order_data)
        return order_ref.id
        
    except Exception as e:
        raise Exception(f"Error al crear orden: {str(e)}")

def create_stripe_checkout_session(db, cart, usuario):
    try:
        if not cart:
            raise ValueError("El carrito está vacío")
        
        # Crear orden en Firestore
        order_id = create_order_in_firestore(db, cart, usuario)
        
        # Preparar items para Stripe
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item['name'],
                    'images': [item['image']]
                },
                'unit_amount': int(item['price'] * 100),
            },
            'quantity': item['quantity'],
        } for item in cart]

        # Crear sesión en Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=os.getenv("STRIPE_SUCCESS_URL"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL"),  # URL CORREGIDA
            customer_email=usuario['email'],
            metadata={
                'user_id': usuario['uid'],
                'firestore_order_id': order_id
            }
        )
        
        # Actualizar orden con session_id
        db.collection('orders').document(order_id).update({
            'session_id': session.id,
            'updated_at': datetime.now()
        })
        
        return session.url
        
    except Exception as e:
        if 'order_id' in locals():
            db.collection('orders').document(order_id).update({
                'status': 'failed',
                'error': str(e),
                'updated_at': datetime.now()
            })
        raise Exception(f"Error en checkout: {str(e)}")
