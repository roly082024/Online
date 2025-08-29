import streamlit as st
from datetime import datetime

def get_products():
    """Obtiene productos de Firestore o crea muestra inicial"""
    try:
        products_ref = st.session_state.db.collection('products')
        docs = products_ref.stream()
        
        products = []
        for doc in docs:
            product = doc.to_dict()
            product['id'] = doc.id
            products.append(product)
        
        # Si no hay productos, creamos muestra inicial
        if not products:
            sample_products = [
                # VESTIDOS (4 productos)
                {
                    "name": "Vestido Negro Elegante",
                    "price": 89.99,
                    "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8",
                    "description": "Perfecto para ocasiones especiales",
                    "category": "vestidos",
                    "stock": 15
                },
                {
                    "name": "Vestido Floral Veraniego",
                    "price": 65.50,
                    "image": "https://images.unsplash.com/photo-1585487000160-6ebcfceb0d03",
                    "description": "Ideal para días soleados",
                    "category": "vestidos",
                    "stock": 20
                },
                # BLUSAS/TOPS (4 productos)
                {
                    "name": "Blusa de Seda Blanca",
                    "price": 45.99,
                    "image": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c",
                    "description": "Suave y elegante",
                    "category": "blusas",
                    "stock": 25
                },
                {
                    "name": "Top Básico Negro",
                    "price": 29.99,
                    "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27",
                    "description": "Esencial para cualquier armario",
                    "category": "blusas",
                    "stock": 30
                },
                # PANTALONES (4 productos)
                {
                    "name": "Jeans Slim Fit Azul",
                    "price": 79.99,
                    "image": "https://images.unsplash.com/photo-1542272604-787c3835535d",
                    "description": "Ajuste perfecto",
                    "category": "pantalones",
                    "stock": 30
                },
                {
                    "name": "Pantalón Formal",
                    "price": 89.50,
                    "image": "https://plus.unsplash.com/premium_photo-1689977493146-ed929d07d97e",
                    "description": "Para looks profesionales",
                    "category": "pantalones",
                    "stock": 12
                },
                # ZAPATOS (4 productos)
                {
                    "name": "Zapatos Tacón Nude",
                    "price": 95.99,
                    "image": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2",
                    "description": "Elegancia para eventos",
                    "category": "zapatos",
                    "stock": 12
                },
                {
                    "name": "Sneakers Urbanos",
                    "price": 75.00,
                    "image": "https://images.unsplash.com/photo-1600269452121-4f2416e55c28",
                    "description": "Estilo y comodidad",
                    "category": "zapatos",
                    "stock": 18
                },
                # ACCESORIOS (4 productos)
                {
                    "name": "Bolso de Mano Premium",
                    "price": 65.99,
                    "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62",
                    "description": "Elegante y espacioso",
                    "category": "accesorios",
                    "stock": 18
                },
                {
                    "name": "Gafas de Sol Aviador",
                    "price": 49.99,
                    "image": "https://images.unsplash.com/photo-1511499767150-a48a237f0083",
                    "description": "Protección UV400",
                    "category": "accesorios",
                    "stock": 22
                }
            ]
            
            # Guardar en Firestore
            for product in sample_products:
                st.session_state.db.collection('products').add(product)
            
            return sample_products
        
        return products
    
    except Exception as e:
        st.error(f"Error al obtener productos: {str(e)}")
        return []

def add_to_cart(product):
    """Añade un producto al carrito"""
    try:
        if 'cart' not in st.session_state:
            st.session_state.cart = []
            
        # Verificar si el producto ya está en el carrito
        existing_item = next((item for item in st.session_state.cart if item['product_id'] == product['id']), None)
        
        if existing_item:
            existing_item['quantity'] += 1
        else:
            st.session_state.cart.append({
                'product_id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': 1
            })
        
        # Sincronizar con Firestore
        from firebase_utils import sync_cart_with_firestore
        sync_cart_with_firestore()
        
        st.toast(f"✅ {product['name']} añadido al carrito!")
        return True
        
    except Exception as e:
        st.error(f"Error al añadir al carrito: {str(e)}")
        return False
