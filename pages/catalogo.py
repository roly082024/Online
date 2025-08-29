import streamlit as st
from datetime import datetime
from firebase_utils import sync_cart_with_firestore
from payment_utils import create_stripe_checkout_session
from product_utils import get_products, add_to_cart

# Verificar autenticación
if 'login' not in st.session_state:
    st.switch_page('app.py')

# Cargar estilos
with open("estilos/css_catalogo.html", "r") as file:
    st.markdown(file.read(), unsafe_allow_html=True)

# Interfaz principal
st.markdown('<div class="main-header"><h1>🛍️ Fashion Store</h1><p>Bienvenido/a a tu tienda de moda</p></div>', unsafe_allow_html=True)

# Sidebar - Carrito
with st.sidebar:
    st.markdown(f"### 👤 {st.session_state['usuario']['nombre']}")
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🛒 Tu Carrito")
    
    if 'cart' in st.session_state and st.session_state.cart:
        total = 0
        for item in st.session_state.cart:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class="cart-item">
                    <strong>{item['name']}</strong><br>
                    ${item['price']:.2f} x {item['quantity']}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("❌", key=f"remove_{item['product_id']}"):
                    st.session_state.cart = [i for i in st.session_state.cart if i['product_id'] != item['product_id']]
                    sync_cart_with_firestore()
                    st.rerun()
            
            total += item['price'] * item['quantity']
        
        st.markdown(f"**Total: ${total:.2f}**")

        if st.button("💳 Pagar con Stripe", use_container_width=True, type="primary"):
            try:
                checkout_url = create_stripe_checkout_session(
                    st.session_state.db,
                    st.session_state.cart,
                    st.session_state.usuario
                )
                st.markdown(f'<a href="{checkout_url}" target="_blank">Haz clic aquí para continuar al checkout</a>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.info("Tu carrito está vacío")

# Catálogo principal
st.markdown("## 🛍️ Catálogo de Productos")

# Filtros
selected_category = st.selectbox(
    "Filtrar por categoría:",
    ["todos", "vestidos", "blusas", "pantalones", "zapatos", "accesorios"],
    index=0
)

# Mostrar productos
products = get_products()
if selected_category != "todos":
    products = [p for p in products if p.get('category') == selected_category]

if not products:
    st.warning("No hay productos disponibles en esta categoría")
else:
    cols = st.columns(3)
    
    for idx, product in enumerate(products):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="product-card">
                <img src="{product['image']}" alt="{product['name']}" style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
                <h3 style="margin:1rem 0 0.5rem 0; color:#333;">{product['name']}</h3>
                <p style="color:#666; margin-bottom:1rem;">{product['description']}</p>
                <div class="price-tag">${product['price']:.2f}</div>
                <p style="color:#999; font-size:0.9rem;">Stock: {product['stock']} unidades</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 Añadir al carrito", key=f"add_{product['id']}", use_container_width=True):
                if add_to_cart(product):
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:2rem;">
    <p>🛍️ Fashion Store - Tu estilo, nuestra pasión</p>
</div>
""", unsafe_allow_html=True)
