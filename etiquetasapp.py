import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Etiquetas Farmacia", layout="wide")
st.title("Generador de Etiquetas de Precio")

# 1. Cargar la base de datos de productos
@st.cache_data
def cargar_base_datos():
    # Sustituye 'productos.xlsx' por la ruta de tu archivo de inventario
    try:
        df = pd.read_excel("productos.xlsx")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Descripcion", "Laboratorio", "Precio"])
    return df

base_datos = cargar_base_datos()

# Inicializar la lista de etiquetas de la sesión actual
if "etiquetas_sesion" not in st.session_state:
    st.session_state.etiquetas_sesion = []

# 2. Formulario de Selección y Búsqueda
st.subheader("Buscar o Agregar Producto")

opciones_productos = base_datos["Descripcion del producto"].tolist() if not base_datos.empty else []
busqueda = st.selectbox("Selecciona un producto (o escribe para buscar):", [""] + opciones_productos)

if busqueda:
    # Obtener datos del producto seleccionado
    info_prod = base_datos[base_datos["Descripcion del producto"] == busqueda].iloc[0]
    lab_def = info_prod.get("Laboratorio", "")
    precio_def = float(info_prod.get("Precio", 0.0))
else:
    lab_def = ""
    precio_def = 0.0

col1, col2, col3 = st.columns(3)

with col1:
    descripcion_input = st.text_input("Descripción del Producto:", value=busqueda if busqueda else "")
with col2:
    fecha_input = st.date_input("Fecha:", datetime.now())
with col3:
    precio_input = st.number_input("Precio (Ref):", value=precio_def, format="%.2f")

if st.button("Agregar a la lista de impresión"):
    if descripcion_input:
        nueva_etiqueta = {
            "Descripcion": descripcion_input,
            "Fecha": fecha_input.strftime("%d/%m/%Y"),
            "Precio": f"Ref: {precio_input:.2f}"
        }
        st.session_state.etiquetas_sesion.append(nueva_etiqueta)
        st.success(f"Producto '{descripcion_input}' agregado.")
    else:
        st.warning("Debes colocar una descripción.")

# 3. Vista Previa y Exportación a la Cuadrícula de Excel
if st.session_state.etiquetas_sesion:
    st.subheader("Etiquetas listas para imprimir")
    st.write(pd.DataFrame(st.session_state.etiquetas_sesion))
    
    if st.button("Generar Excel de Etiquetas"):
        # Lógica para acomodar en cuadrícula de 3 columnas
        num_etiquetas = len(st.session_state.etiquetas_sesion)
        filas = []
        for i in range(0, num_etiquetas, 3):
            grupo = st.session_state.etiquetas_sesion[i:i+3]
            # Completar fila con vacíos si hay menos de 3 en la última línea
            while len(grupo) < 3:
                grupo.append({"Descripcion": "", "Fecha": "", "Precio": ""})
            
            filas.append({
                "Col_A_Desc": grupo[0]["Descripcion"], "Col_A_Fecha": grupo[0]["Fecha"], "Col_A_Precio": grupo[0]["Precio"],
                "Col_B_Desc": grupo[1]["Descripcion"], "Col_B_Fecha": grupo[1]["Fecha"], "Col_B_Precio": grupo[1]["Precio"],
                "Col_C_Desc": grupo[2]["Descripcion"], "Col_C_Fecha": grupo[2]["Fecha"], "Col_C_Precio": grupo[2]["Precio"],
            })
        
        df_export = pd.DataFrame(filas)
        df_export.to_excel("Etiquetas_Para_Imprimir.xlsx", index=False)
        st.success("Archivo 'Etiquetas_Para_Imprimir.xlsx' generado con éxito en el formato de 3 columnas.")
