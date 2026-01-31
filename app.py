import streamlit as st
import time
import json
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="FlashCart: Motor Clave-Valor", layout="wide")

st.title("⚡ FlashCart Analytics")
st.subheader("Simulador de Base de Datos Key-Value con TTL")

# --- 1. INICIALIZACIÓN DEL ALMACÉN (SIMULANDO REDIS/MEMORIA RAM) ---
if 'kv_store' not in st.session_state:
    st.session_state.kv_store = {}

# --- 2. LÓGICA DE LIMPIEZA POR EXPIRACIÓN (TTL) ---
def cleanup_expired():
    now = time.time()
    # Definimos el tiempo de vida (TTL) en 60 segundos
    ttl = 60 
    keys_to_delete = [
        k for k, v in st.session_state.kv_store.items() 
        if now - v['timestamp'] > ttl
    ]
    for k in keys_to_delete:
        del st.session_state.kv_store[k]
    return len(keys_to_delete)

# --- 3. INTERFAZ: GESTIÓN DE DATOS ---
col_input, col_monitor = st.columns([1, 1])

with col_input:
    st.header("📥 Entrada de Datos (SET)")
    
    with st.form("set_data"):
        key = st.text_input("ID del Cliente (Key)", placeholder="user_123")
        
        st.write("Datos del Carrito (Value - Formato JSON)")
        items = st.text_area("Productos", value='["Laptop", "Mouse"]', help="Escribe una lista en formato JSON")
        total = st.number_input("Total Compra ($)", min_value=0.0, value=1200.0)
        
        submitted = st.form_submit_button("Guardar en Caché")
        
        if submitted:
            if key:
                # Creamos el valor como un objeto flexible
                value_object = {
                    "data": {
                        "productos": json.loads(items) if items else [],
                        "total": total
                    },
                    "timestamp": time.time(),
                    "time_readable": datetime.now().strftime("%H:%M:%S")
                }
                # Operación de escritura (SET) O(1)
                st.session_state.kv_store[key] = value_object
                st.success(f"✅ Clave '{key}' guardada exitosamente.")
            else:
                st.error("La clave no puede estar vacía.")

    st.divider()
    
    st.header("🔍 Recuperación (GET)")
    search_key = st.text_input("Buscar por ID de Cliente")
    if st.button("Consultar"):
        # Operación de lectura (GET) O(1) - Velocidad instantánea
        result = st.session_state.kv_store.get(search_key)
        if result:
            st.json(result["data"])
            st.info(f"Dato guardado a las: {result['time_readable']}")
        else:
            st.warning("Clave no encontrada o expirada.")

with col_monitor:
    st.header("📊 Monitor de Memoria")
    
    # Botón de limpieza manual (Simulando el proceso de TTL de NoSQL)
    if st.button("🧹 Ejecutar Limpieza TTL (Borrar expirados)"):
        eliminados = cleanup_expired()
        st.write(f"Sesiones limpiadas: {eliminados}")
    
    # Visualización del almacén de datos
    if st.session_state.kv_store:
        # Transformamos para mostrar en tabla
        display_data = []
        for k, v in st.session_state.kv_store.items():
            age = int(time.time() - v['timestamp'])
            display_data.append({
                "Key (ID)": k,
                "Creado": v['time_readable'],
                "Antigüedad": f"{age} seg",
                "Estado": "🔥 Activo" if age <= 60 else "💀 Expirado (Pendiente de limpieza)"
            })
        
        st.table(display_data)
    else:
        st.info("El almacén está vacío.")

# --- 4. EXPLICACIÓN TEÓRICA ---
with st.expander("❓ ¿Qué está pasando aquí detrás?"):
    st.write("""
    1. **Acceso O(1):** No importa si hay 10 o 10 millones de carritos. Buscar por clave siempre tarda lo mismo.
    2. **Estructura Flexible:** El campo 'Productos' es una lista JSON que puede cambiar sin alterar una tabla.
    3. **TTL (Time To Live):** En Big Data, los carritos no se guardan para siempre. Si el usuario no compra en un tiempo X, el dato se auto-elimina para ahorrar RAM.
    """)
