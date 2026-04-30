import streamlit as st
from pathlib import Path
import tempfile

# Configuración de la página
st.set_page_config(
    page_title="Comparador de documentos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Título principal centrado
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("Comparador de Documentos")
    
with col1:
    st.image(
        "images/comparador1.png",
        width=200,           # Ancho en píxeles
        use_container_width=False  # True = ocupa todo el ancho
        )
with col3:    
    st.image(
        "images/diagrama venn.png",
        width=200,
        use_container_width=False
    )
st.markdown("---")
st.subheader("Seleccione dos documentos para comparar su contenido y similitud")
st.markdown(":gray[Los documentos deben de ser de igual tipo (ambos PDF o ambas URL) para una comparación válida.]")

             
st.markdown("---")

# Crear dos columnas para las fuentes de datos
col1, col2, col3, col4 = st.columns([1,6, 1,6])

    

with col1:
    st.image(
        "images/fuentes.png",
        width=50,
        use_container_width=False
    )
with col2:
    st.subheader("Fuente A")
    tipo_a = st.radio(
        "Seleccione el tipo de entrada:",
        ("PDF", "URL"),
        key="tipo_a",
        index=0,
        horizontal=True
    )
    st.session_state["tipo_b"] = tipo_a  # Sincronizar tipo_b con tipo_a para evitar confusión
    
    if tipo_a == "PDF":
        archivo_a = st.file_uploader(
            "Cargar archivo PDF",
            type=["pdf"],
            key="pdf_a"
        )
        url_a = None
    else:
        url_a = st.text_input(
            "Ingrese la URL:",
            placeholder="https://ejemplo.com/documento",
            key="url_a"
        )
        archivo_a = None

with col3:
    st.image(
        "images/fuentes.png",
        width=50,
        use_container_width=False
    )
with col4:
    st.subheader("Fuente B")
    tipo_b = st.radio(
        "Seleccione el tipo de entrada:",
        ("PDF", "URL"),
        key="tipo_b",
        index=("PDF", "URL").index(tipo_a),
        horizontal=True
    )
    
    if tipo_b == "PDF":
        archivo_b = st.file_uploader(
            "Cargar archivo PDF",
            type=["pdf"],
            key="pdf_b"
        )
        url_b = None
    else:
        url_b = st.text_input(
            "Ingrese la URL:",
            placeholder="https://ejemplo.com/documento",
            key="url_b"
        )
        archivo_b = None
st.markdown("---")

# Botón de procesamiento
if st.button("🔍 Comparar Documentos", type="primary", use_container_width=True):
    # Validar entradas
    error = False
    
    if tipo_a == "PDF" and not archivo_a:
        st.error("Debe cargar un archivo PDF para la Fuente A")
        error = True
    elif tipo_a == "URL" and not url_a:
        st.error("Debe ingresar una URL para la Fuente A")
        error = True
        
    if tipo_b == "PDF" and not archivo_b:
        st.error("Debe cargar un archivo PDF para la Fuente B")
        error = True
    elif tipo_b == "URL" and not url_b:
        st.error("Debe ingresar una URL para la Fuente B")
        error = True
    
    if not error:
        # Crear pestañas para organizar la visualización
        tab1, tab2 = st.tabs(["⚙️ Configuración/Entrada", "📈 Resultados/Diagrama de Venn"])
        
        with tab1:
            st.success("Datos validados correctamente")
            st.info("Los resultados se mostrarán en la pestaña 'Resultados/Diagrama de Venn'")
            
            # Mostrar resumen de entradas
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Fuente A:**")
                if tipo_a == "PDF":
                    st.write(f"📎 {archivo_a.name}")
                else:
                    st.write(f"🔗 {url_a}")
            
            with col_b:
                st.markdown("**Fuente B:**")
                if tipo_b == "PDF":
                    st.write(f"📎 {archivo_b.name}")
                else:
                    st.write(f"🔗 {url_b}")
        
        with tab2:
            try:
                from pdf_processor import procesar_fuente
                from comparator import (
                    extraer_keywords_yake, comparar_palabras_clave,
                    generar_venn, extraer_palabras_unicas,
                    extraer_palabras_frecuentes,
                )
                
                with st.spinner("⏳ Procesando documentos..."):
                    # Procesar Fuente A
                    st.markdown("#### Procesando Fuente A...")
                    if tipo_a == "PDF":
                        # Guardar el archivo subido temporalmente
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(archivo_a.getvalue())
                            tmp_path = tmp.name
                        doc_a = procesar_fuente("PDF", archivo_pdf=Path(tmp_path))
                        doc_a["nombre"] = archivo_a.name
                        import os
                        os.unlink(tmp_path)  # Limpiar archivo temporal
                    else:
                        doc_a = procesar_fuente("URL", url=url_a)
                    
                    st.success(f"✅ Fuente A procesada: {doc_a['total_caracteres']:,} caracteres")
                    
                    # Procesar Fuente B
                    st.markdown("#### Procesando Fuente B...")
                    if tipo_b == "PDF":
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(archivo_b.getvalue())
                            tmp_path = tmp.name
                        doc_b = procesar_fuente("PDF", archivo_pdf=Path(tmp_path))
                        doc_b["nombre"] = archivo_b.name  
                        os.unlink(tmp_path)
                    else:
                        doc_b = procesar_fuente("URL", url=url_b)
                    
                    st.success(f"✅ Fuente B procesada: {doc_b['total_caracteres']:,} caracteres")
                    
                    # Extraer keywords con YAKE
                    st.markdown("#### Extrayendo palabras clave y analizando texto...")
                    keywords_a = extraer_keywords_yake(doc_a['texto_limpio'])
                    keywords_b = extraer_keywords_yake(doc_b['texto_limpio'])

                    unicas_a = extraer_palabras_unicas(doc_a['texto_limpio'])
                    unicas_b = extraer_palabras_unicas(doc_b['texto_limpio'])
                    # Palabras frecuentes (más de 3 apariciones)
                    frec_a = extraer_palabras_frecuentes(doc_a['texto_limpio'])
                    frec_b = extraer_palabras_frecuentes(doc_b['texto_limpio'])
                    frec_comunes = set(frec_a) & set(frec_b)
                    frec_union   = set(frec_a) | set(frec_b)
                    jaccard_frec = len(frec_comunes) / len(frec_union) if frec_union else 0.0

                    st.info(
                        f"📝 Palabras únicas — A: {len(unicas_a):,}, B: {len(unicas_b):,} | "
                        f"Frecuentes — A: {len(frec_a)}, B: {len(frec_b)}, Comunes: {len(frec_comunes)}"
                    )

                    # Comparar palabras clave YAKE (para veredicto)
                    stats = comparar_palabras_clave(keywords_a, keywords_b)
                    
                    # ── Métricas ───────────────────────────────────────────
                    st.markdown("### 📊 Resultados de la Comparación")
                    inter_total = unicas_a & unicas_b

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Jaccard (frecuentes)", f"{jaccard_frec:.2%}")
                    with col2:
                        st.metric("Palabras comunes", f"{len(inter_total):,}")
                    with col3:
                        st.metric("Palabras únicas A", f"{len(unicas_a):,}")
                    with col4:
                        st.metric("Palabras únicas B", f"{len(unicas_b):,}")

                    # ── Diagrama de Venn ────────────────────────────────────
                    st.markdown("### 📈 Diagrama de Venn")
                    try:
                        imagen_venn = generar_venn(
                            unicas_a, unicas_b,
                            frec_a, frec_b,
                            doc_a['nombre'], doc_b['nombre']
                        
                        )                        
                        st.image(imagen_venn,
                                 use_column_width=True)
                    except Exception as e:
                        st.error(f"Error al generar el diagrama de Venn: {e}")
                    
                    # ── Veredicto ───────────────────────────────────────────
                    st.markdown("### Veredicto")
                    if jaccard_frec >= 0.5:
                        st.success(f"**Alta similitud detectada** ({jaccard_frec:.2%} en palabras frecuentes)")
                        st.write("Los documentos comparten una cantidad significativa de términos frecuentes. " \
                        "Puede que sean el mismo documento o versiones muy similares.")
                    elif jaccard_frec >= 0.2:
                        st.warning(f"**Similitud moderada detectada** ({jaccard_frec:.2%} en palabras frecuentes)")
                        st.write("Los documentos tienen algunos términos frecuentes en común, pero también diferencias notables.")
                    else:
                        st.error(f"**Baja similitud detectada** ({jaccard_frec:.2%} en palabras frecuentes)")
                        st.write("Los documentos comparten pocos términos frecuentes.")

                    # ── Muestra palabras clave YAKE ─────────────────────────
                    with st.expander("Ver muestra de palabras clave- (YAKE)"):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.markdown("**Solo en A:**")
                            st.write(", ".join(stats['solo_en_a'][:10]) or "Ninguna")
                        with col_b:
                            st.markdown("**Comunes:**")
                            st.write(", ".join(stats['comunes'][:10]) or "Ninguna")
                        with col_c:
                            st.markdown("**Solo en B:**")
                            st.write(", ".join(stats['solo_en_b'][:10]) or "Ninguna")
                    
            except ImportError as e:
                st.error(f"❌ Error de importación: {e}")
                st.info("Asegúrese de haber instalado todas las dependencias: pip install -r requirements.txt")
            except Exception as e:
                st.error(f"❌ Error durante el procesamiento: {e}")
                st.exception(e)

# Información en el sidebar
with st.sidebar:
    st.header("ℹ️ Información")
    st.markdown("""
    **Tecnologías utilizadas:**
    - Streamlit (Interfaz)
    - PyMuPDF (Extracción PDF)
    - YAKE (Keywords)
    - Sentence-Transformers (Similitud)
    - OpenAI API (Análisis)
    - Matplotlib-Venn (Visualización)
    """)
    st.markdown("---")
    st.caption("Yasmin Hernández- Sistemas Inteligentes - 2026")
