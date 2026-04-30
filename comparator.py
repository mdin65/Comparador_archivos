import io
from collections import Counter
from pathlib import Path
from typing import Optional, Union
import re

# ── Stopwords español ─────────────────────────────────────────────────────────
STOPWORDS_ES = {
    "a", "al", "ante", "bajo", "con", "contra", "de", "del", "desde", "durante",
    "en", "entre", "hacia", "hasta", "mediante", "para", "por", "según", "sin",
    "sobre", "tras", "versus", "vía", "el", "la", "los", "las", "un", "una",
    "unos", "unas", "lo", "y", "e", "ni", "o", "u", "pero", "sino", "aunque",
    "que", "si", "porque", "como", "cuando", "donde", "quien", "cual", "cuales",
    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel",
    "aquella", "aquellos", "aquellas", "mi", "tu", "su", "nuestro", "nuestra",
    "vuestro", "vuestra", "sus", "mis", "tus", "me", "te", "se", "nos", "les",
    "le", "yo", "tú", "él", "ella", "nosotros", "ellos", "ellas", "usted",
    "ustedes", "ser", "es", "son", "era", "fue", "sido", "hay", "haber",
    "estar", "tiene", "han", "más", "muy", "también", "ya", "así", "bien",
    "solo", "sólo", "no", "sí", "todo", "toda", "todos", "todas", "otro",
    "otra", "otros", "otras", "mismo", "misma", "cada", "tanto", "tan",
    "entonces", "además", "después", "antes", "ahora", "aquí", "allí",
    "algo", "alguien", "nada", "nadie", "siempre", "nunca", "vez", "veces",
}


def extraer_keywords_yake(
    texto: str,
    max_keywords: int = 50,
    num_keywords: int = 20,
    language: str = "es",
) -> set[str]:
    """
    Extrae palabras clave de un texto usando YAKE.
    
    Args:
        texto: Texto del cual extraer palabras clave.
        max_keywords: Número máximo de keywords a considerar.
        num_keywords: Número de keywords a retornar.
        language: Idioma del texto ('es' para español, 'en' para inglés).
        
    Returns:
        Conjunto de palabras clave únicas en minúsculas.
        
    Raises:
        ImportError: Si YAKE no está instalado.
    """
    try:
        import yake
    except ImportError:
        raise ImportError(
            "YAKE no está instalado. Instale con: pip install yake"
        )
    
    # Configurar YAKE
    kw_extractor = yake.KeywordExtractor(
        lan=language,
        n=3,  # Máximo n-gramas de 3 palabras
        dedupLim=0.9,
        dedupFunc='seqm',
        windowsSize=1,
        top=max_keywords,
        features=None
    )
    
    # Extraer keywords
    keywords = kw_extractor.extract_keywords(texto)
    
    # Obtener solo los términos (YAKE devuelve (término, score))
    terminos = [kw[0].lower() for kw in keywords[:num_keywords]]
    
    # Limpiar y filtrar términos
    palabras_clave = set()
    for termino in terminos:
        # Limpiar el término de caracteres especiales
        palabras = re.findall(r'\b[a-záéíóúüñ]{3,}\b', termino)
        palabras_clave.update(palabras)
    
    return palabras_clave


def comparar_palabras_clave(
    palabras_a: set[str],
    palabras_b: set[str],
) -> dict:
    """
    Compara dos conjuntos de palabras clave y calcula estadísticas.
    
    Args:
        palabras_a: Conjunto de palabras clave del documento A.
        palabras_b: Conjunto de palabras clave del documento B.
        
    Returns:
        Diccionario con:
            - 'comunes': Lista de palabras en ambos documentos.
            - 'solo_en_a': Lista de palabras exclusivas de A.
            - 'solo_en_b': Lista de palabras exclusivas de B.
            - 'total_a': Total de palabras únicas en A.
            - 'total_b': Total de palabras únicas en B.
            - 'total_comunes': Total de palabras comunes.
            - 'jaccard': Índice de similitud de Jaccard (0.0 a 1.0).
    """
    interseccion = palabras_a & palabras_b
    solo_a = palabras_a - palabras_b
    solo_b = palabras_b - palabras_a
    union = palabras_a | palabras_b
    
    # Calcular índice de Jaccard
    jaccard = len(interseccion) / len(union) if union else 0.0
    
    return {
        "comunes": sorted(interseccion),
        "solo_en_a": sorted(solo_a),
        "solo_en_b": sorted(solo_b),
        "total_a": len(palabras_a),
        "total_b": len(palabras_b),
        "total_comunes": len(interseccion),
        "jaccard": round(jaccard, 4),
    }


def generar_datos_venn(
    palabras_a: set[str],
    palabras_b: set[str],
) -> dict:
    interseccion = palabras_a & palabras_b
    solo_a = palabras_a - palabras_b
    solo_b = palabras_b - palabras_a
    
    return {
        "subset_a": len(solo_a),
        "subset_b": len(solo_b),
        "subset_ab": len(interseccion),
        "palabras_a": sorted(solo_a)[:5], 
        "palabras_b": sorted(solo_b)[:5],
        "palabras_comunes": sorted(interseccion)[:5],
    }

def extraer_palabras_frecuentes(
    texto: str,
    min_frecuencia: int = 4,
    min_longitud: int = 3,
) -> dict[str, int]:
    
    # Extraer solo palabras alfabéticas en minúsculas
    palabras = re.findall(r'\b[a-záéíóúüñ]{%d,}\b' % min_longitud, texto.lower())

    # Filtrar stopwords
    palabras_filtradas = [p for p in palabras if p not in STOPWORDS_ES]

    # Contar frecuencias
    conteo = Counter(palabras_filtradas)

    # Filtrar por mínimo de apariciones
    frecuentes = {
        palabra: freq
        for palabra, freq in conteo.items()
        if freq >= min_frecuencia
    }

    # Ordenar de mayor a menor
    return dict(sorted(frecuentes.items(), key=lambda x: x[1], reverse=True))


def extraer_palabras_unicas(texto: str, min_longitud: int = 3) -> set[str]:
    """
    Extrae todas las palabras únicas de un texto, excluyendo stopwords.

    Args:
        texto: Texto del documento.
        limite: maximo de palabrass únicas a retornar (0 para sin límite).
        min_longitud: Longitud mínima de palabra a considerar.

    Returns:
        Conjunto de palabras únicas en minúsculas, sin stopwords.
    """
    palabras = re.findall(r'\b[a-záéíóúüñ]{%d,}\b' % min_longitud, texto.lower())

    return {p for p in palabras if p not in STOPWORDS_ES}


def generar_venn(
    palabras_unicas_a: set[str],
    palabras_unicas_b: set[str],
    frecuentes_a: dict[str, int],
    frecuentes_b: dict[str, int],
    nombre_a: str,
    nombre_b: str,
    ruta_salida: Optional[Union[str, Path]] = None,
) -> bytes:
    """
    Genera un diagrama de Venn con dos capas:
      - Capa base: todas las palabras únicas de cada documento (sin stopwords).
      - Capa destacada: palabras frecuentes (>3 apariciones) en la intersección.

    Args:
        palabras_unicas_a: Todas las palabras únicas del documento A.
        palabras_unicas_b: Todas las palabras únicas del documento B.
        frecuentes_a: Dict {palabra: frecuencia} de palabras frecuentes de A.
        frecuentes_b: Dict {palabra: frecuencia} de palabras frecuentes de B.
        nombre_a: Etiqueta para el conjunto A.
        nombre_b: Etiqueta para el conjunto B.
        ruta_salida: Ruta opcional para guardar la imagen.

    Returns:
        Bytes de la imagen PNG generada.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        from matplotlib_venn import venn2
    except ImportError:
        raise ImportError(
            "Instale: pip install matplotlib matplotlib-venn"
        )

    # ── Capa 1: palabras únicas totales ───────────────────────────────────────
    inter_total   = palabras_unicas_a & palabras_unicas_b
    solo_a_total  = palabras_unicas_a - palabras_unicas_b
    solo_b_total  = palabras_unicas_b - palabras_unicas_a

    # ── Capa 2: palabras frecuentes compartidas ────────────────────────────────
    frec_set_a     = set(frecuentes_a.keys())
    frec_set_b     = set(frecuentes_b.keys())
    frec_comunes   = frec_set_a & frec_set_b          
    frec_solo_a    = frec_set_a - frec_set_b
    frec_solo_b    = frec_set_b - frec_set_a

    # ── Figura ────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(13, 8))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    # Truncar nombres largos (URLs, rutas)
    def _truncar(nombre: str, n: int = 28) -> str:
        return nombre[:n] + "…" if len(nombre) > n else nombre

    label_a = _truncar(nombre_a)
    label_b = _truncar(nombre_b)

    # Venn base con palabras únicas totales
    v = venn2(
        subsets=(len(solo_a_total), len(solo_b_total), len(inter_total)),
        set_labels=(label_a, label_b),
        ax=ax,
    )

    # Colores capa base
    _estilos = {
        "10": ("#e94560", 0.65),   # Solo A — rojo
        "01": ("#1a6fa8", 0.65),   # Solo B — azul
        "11": ("#6a3d9a", 0.70),   # Intersección — morado
    }
    for pid, (color, alpha) in _estilos.items():
        patch = v.get_patch_by_id(pid)
        if patch:
            patch.set_color(color)
            patch.set_alpha(alpha)

    # Etiquetas de conjunto
    for text in v.set_labels:
        if text:
            text.set_color("white")
            text.set_fontsize(11)
            text.set_fontweight("bold")

    # Etiquetas de conteo — mostrar ambos conteos
    conteos = {
        "10": f"{len(solo_a_total):,}\npalabras\n({len(frec_solo_a)} frec.)",
        "01": f"{len(solo_b_total):,}\npalabras\n({len(frec_solo_b)} frec.)",
        "11": f"{len(inter_total):,}\ncomunes\n✦ {len(frec_comunes)} frec.",
    }
    for pid, texto in conteos.items():
        lbl = v.get_label_by_id(pid)
        if lbl:
            lbl.set_text(texto)
            lbl.set_color("white")
            lbl.set_fontsize(9)
            lbl.set_fontweight("bold")


    # ── Leyenda ───────────────────────────────────────────────────────────────
    leyenda = [
        mpatches.Patch(color="#e94560", alpha=0.8, label=f"Solo en A  ({len(solo_a_total):,} palabras)"),
        mpatches.Patch(color="#1a6fa8", alpha=0.8, label=f"Solo en B  ({len(solo_b_total):,} palabras)"),
        mpatches.Patch(color="#6a3d9a", alpha=0.8, label=f"Comunes    ({len(inter_total):,} palabras)"),
        mpatches.Patch(color="#c8a8ff", alpha=0.9, label=f"Frec. comunes  ({len(frec_comunes)})"),
    ]
    ax.legend(handles=leyenda, loc="upper center",
              bbox_to_anchor=(0.5, -0.22), ncol=2,
              facecolor="#1c1c2e", edgecolor="#444", labelcolor="white",
              fontsize=8.5)

    plt.title(
        f"Diagrama de Venn — Palabras del Texto y Frecuentes\n{label_a}  vs  {label_b}",
        color="white", fontsize=12, pad=16
    )
    plt.tight_layout(rect=[0, 0.12, 1, 1])

    # Guardar
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close()
    buffer.seek(0)
    imagen_bytes = buffer.getvalue()

    if ruta_salida:
        Path(ruta_salida).write_bytes(imagen_bytes)

    return imagen_bytes


def analizar_con_openai(
    texto_a: str,
    texto_b: str,
    nombre_a: str,
    nombre_b: str,
    api_key: Optional[str] = None,
    model: str = "gpt-4-turbo-preview",
    max_chars: int = 8000,
) -> dict:
    """
    Usa OpenAI API para comparar semánticamente dos textos.
    
    Args:
        texto_a: Texto del primer documento.
        texto_b: Texto del segundo documento.
        nombre_a: Nombre del primer documento.
        nombre_b: Nombre del segundo documento.
        api_key: API key de OpenAI. Si es None, usa OPENAI_API_KEY del entorno.
        model: Modelo de OpenAI a usar.
        max_chars: Máximo de caracteres por texto.
        
    Returns:
        Diccionario con el análisis estructurado.
        
    Raises:
        ImportError: Si openai no está instalado.
        ValueError: Si no se puede obtener la API key.
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError(
            "OpenAI no está instalado. Instale con: pip install openai"
        )
    
    import os
    import json
    
    # Obtener API key
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise ValueError(
            "Se requiere una API key de OpenAI. "
            "Defínala con la variable de entorno OPENAI_API_KEY "
            "o pásala como argumento api_key."
        )
    
    # Truncar textos si son muy largos
    limite = max_chars // 2
    texto_a_recortado = texto_a[:limite] + ("..." if len(texto_a) > limite else "")
    texto_b_recortado = texto_b[:limite] + ("..." if len(texto_b) > limite else "")
    
    # Construir prompt
    prompt = f"""Eres un analista experto en comparación de documentos. 
Analiza los siguientes dos documentos y proporciona una comparación detallada.

DOCUMENTO A: "{nombre_a}"
---
{texto_a_recortado}
---

DOCUMENTO B: "{nombre_b}"
---
{texto_b_recortado}
---

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown, sin explicaciones fuera del JSON) 
con exactamente esta estructura:

{{
  "resumen_general": "Descripción breve de ambos documentos en 2-3 oraciones",
  "similitudes": ["similitud 1", "similitud 2", "..."],
  "diferencias": ["diferencia 1", "diferencia 2", "..."],
  "temas_exclusivos_a": ["tema solo en doc A", "..."],
  "temas_exclusivos_b": ["tema solo en doc B", "..."],
  "temas_comunes": ["tema compartido 1", "..."],
  "puntuacion_similitud": 0.75,
  "conclusion": "Conclusión final sobre la relación entre los documentos"
}}

La puntuacion_similitud debe ser un número entre 0.0 (completamente diferentes) 
y 1.0 (idénticos en contenido).
"""
    
    # Llamar a OpenAI API
    client = OpenAI(api_key=key)
    
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Eres un analista experto en documentos. Responde solo con JSON válido."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    
    # Procesar respuesta
    respuesta_texto = response.choices[0].message.content.strip()
    
    try:
        datos = json.loads(respuesta_texto)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"La API devolvió una respuesta no parseable como JSON: {e}\n"
            f"Respuesta cruda:\n{respuesta_texto[:500]}"
        )
    
    return datos
