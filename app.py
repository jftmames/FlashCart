import streamlit as st
import time
import json
import pandas as pd
from datetime import datetime
import sys # Para medir el tamaño real en bytes

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="FlashCart: Analítica de Memoria", layout="wide")

st.title("⚡ FlashCart Pro: Almacenamiento y Analítica NoSQL")
st.caption("Simulador de alto rendimiento Clave-Valor con monitoreo de carga")

# --- 1. INICIALIZACIÓN ---
if 'kv_store' not in st.session_state:
    st.session_state.kv_store = {}

def cleanup_expired():
    now = time.time()
    ttl = 60 
    keys_to_delete = [k for k, v in st.session_state.kv_store.items() if now - v['timestamp'] > ttl]
    for k in keys_to_delete:
        del st.session_state.kv_store[k]
    return len(keys_to_delete)

# --- 2. INTERFAZ ---
col_input, col_monitor = st.columns([1, 1.2])

with col_input:
    st.header("📥 Gestión de Sesiones")
    with st.form("set_data"):
        key = st.text_input("ID Cliente (Clave)", placeholder="cliente_vip_01")
        items = st.text_area("JSON de Carrito", value='{"camisa": 2, "pantalon": 1, "zapatos": 1}')
        total = st.number_input("Valor Total ($)", min_value=0.0, value=250.0)
        
        if st.form_submit_button("Guardar en Caché"):
            if key:
                try:
                    data_obj = json.loads(items)
                    entry = {
                        "data": data_obj,
                        "total": total,
                        "timestamp": time.time(),
                        "time_readable": datetime.now().strftime("%H:%M:%S"),
                        "size_bytes": sys.getsizeof(items) + sys.getsizeof(total)
                    }
                    st.session_state.kv_store[key] = entry
                    st.success(f"Dato '{key}' almacenado.")
                except:
                    st.error("Error: El formato JSON de productos no es válido.")

    st.divider()
    st.header("🔍 Consulta Rápida")
    search = st.text_input("Ingresar ID para búsqueda instantánea")
    if search:
        res = st.session_state.kv_store.get(search)
        if res:
            st.json(res["data"])
            st.metric("Total Carrito", f"{res['total']} $")
        else:
            st.warning("Clave no encontrada.")

with col_monitor:
    st.header("📊 Monitor de Infraestructura")
    
    # Acción de limpieza
    if st.button("🧹 Limpiar Sesiones Expiradas (TTL)"):
        cleanup_expired()
        st.rerun()

    if st.session_state.kv_store:
        # Preparar datos para la tabla y gráfico
        df_list = []
        for k, v in st.session_state.kv_store.items():
            age = int(time.time() - v['timestamp'])
            df_list.append({
                "Cliente": k,
                "Antigüedad (s)": age,
                "Tamaño (Bytes)": v['size_bytes'],
                "Estado": "Activo" if age <= 60 else "Expirado"
            })
        
        df = pd.DataFrame(df_list)

        # Métrica de carga total
        total_mem = df["Tamaño (Bytes)"].sum()
        st.metric("Carga Total en Memoria RAM", f"{total_mem} Bytes")

        # Gráfico de consumo por clave
        st.subheader("Consumo de Memoria por Sesión")
        st.bar_chart(df.set_index("Cliente")["Tamaño (Bytes)"])

        # Tabla de estado
        st.subheader("Detalle de las Claves")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay datos en el almacén de memoria.")
