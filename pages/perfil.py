import streamlit as st
from datetime import datetime

# Verificar autenticación
if 'login' not in st.session_state or not st.session_state.login:
    st.switch_page('app.py')

# Cargar estilos
try:
    with open("estilos/css_catalogo.html", "r") as file:
        st.markdown(file.read(), unsafe_allow_html=True)
except FileNotFoundError:
    pass

st.title("👤 Mi Perfil")

if 'usuario' in st.session_state:
    usuario = st.session_state.usuario
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(usuario.get('foto', 'https://via.placeholder.com/150'), width=150)
    
    with col2:
        st.markdown(f"""
        **Nombre:** {usuario.get('nombre', 'N/A')}  
        **Email:** {usuario.get('email', 'N/A')}  
        **Miembro desde:** {usuario.get('created_at').strftime('%d/%m/%Y') if 'created_at' in usuario else 'N/A'}  
        **Último acceso:** {usuario.get('last_login').strftime('%d/%m/%Y %H:%M') if 'last_login' in usuario else 'N/A'}
        """)
    
    st.divider()
    
    # Historial de pedidos
    st.subheader("📦 Mis Pedidos")
    
    try:
        orders_ref = st.session_state.db.collection('orders')
        user_orders = orders_ref.where('user_id', '==', usuario['uid']).order_by('created_at', direction='DESCENDING').stream()
        
        orders = []
        for order in user_orders:
            order_data = order.to_dict()
            order_data['id'] = order.id
            orders.append(order_data)
        
        if orders:
            for order in orders[:5]:  # Mostrar últimos 5 pedidos
                with st.expander(f"Pedido {order.get('order_number', order['id'][-8:])} - ${order.get('total', 0):.2f} - {order.get('status', 'pending')}"):
                    st.markdown(f"""
                    **Fecha:** {order.get('created_at').strftime('%d/%m/%Y %H:%M')}  
                    **Estado:** {order.get('status', 'pending')}  
                    **Total:** ${order.get('total', 0):.2f}
                    """)
                    
                    for item in order.get('items', []):
                        st.markdown(f"- {item['name']} x{item['quantity']} (${item['price']:.2f} c/u)")
        else:
            st.info("Aún no has realizado ningún pedido.")
            
    except Exception as e:
        st.error(f"Error al cargar pedidos: {str(e)}")
    
    st.divider()
    
    # Cerrar sesión
    if st.button("🚪 Cerrar Sesión", type="primary"):
        st.session_state.clear()
        st.rerun()

else:
    st.error("No se encontró información del usuario.")
    st.switch_page('app.py')
