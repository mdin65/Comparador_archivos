import io
import requests
from pathlib import Path
from typing import Union, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    raise ImportError(
        "PyMuPDF no está instalado. Instale con: pip install PyMuPDF"
    )


def extraer_texto_pdf(archivo_pdf: Union[Path, bytes, io.BytesIO]) -> str:
    """
    Extrae texto de un archivo PDF usando PyMuPDF (fitz).
    
    Args:
        archivo_pdf: Ruta al archivo PDF, bytes del archivo o objeto BytesIO.
        
    Returns:
        Texto extraído del PDF como string.
        
    Raises:
        FileNotFoundError: Si la ruta del archivo no existe.
        ValueError: Si el archivo no es un PDF válido.
    """
    texto_total = []
    
    try:
        # Manejar diferentes tipos de entrada
        if isinstance(archivo_pdf, (Path, str)):
            if not Path(archivo_pdf).exists():
                raise FileNotFoundError(f"No se encontró el archivo: {archivo_pdf}")
            doc = fitz.open(archivo_pdf)
        elif isinstance(archivo_pdf, bytes):
            doc = fitz.open(stream=archivo_pdf, filetype="pdf")
        elif isinstance(archivo_pdf, io.BytesIO):
            doc = fitz.open(stream=archivo_pdf.getvalue(), filetype="pdf")
        else:
            raise ValueError("Tipo de entrada no soportado para PDF")
        
        # Extraer texto página por página
        for num_pagina in range(len(doc)):
            pagina = doc[num_pagina]
            texto = pagina.get_text()
            if texto.strip():
                texto_total.append(f"[Página {num_pagina + 1}]\n{texto}")
        
        doc.close()
        
    except Exception as e:
        raise ValueError(f"Error al procesar el PDF: {e}")
    
    return "\n\n".join(texto_total)


def extraer_texto_url(url: str, timeout: int = 10) -> str:
    """
    Extrae el texto principal de una URL.
    
    Args:
        url: URL de la página web o documento.
        timeout: Tiempo máximo de espera para la solicitud.
        
    Returns:
        Texto extraído de la URL.
        
    Raises:
        ValueError: Si no se puede acceder a la URL o procesar el contenido.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Detectar tipo de contenido
        content_type = response.headers.get("Content-Type", "").lower()
        
        # Si es un PDF en la URL
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            return _extraer_pdf_desde_url(response.content)
        
        # Si es HTML, extraer texto
        if "text/html" in content_type or "text/plain" in content_type:
            return _extraer_texto_html(response.text, url)
        
        # Para otros tipos, intentar como texto plano
        return response.text[:50000]  # Limitar tamaño
        
    except requests.RequestException as e:
        raise ValueError(f"Error al acceder a la URL '{url}': {e}")
    except Exception as e:
        raise ValueError(f"Error procesando la URL '{url}': {e}")


def _extraer_pdf_desde_url(pdf_bytes: bytes) -> str:
    """Extrae texto de un PDF descargado desde una URL."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texto_total = []
        
        for num_pagina in range(len(doc)):
            pagina = doc[num_pagina]
            texto = pagina.get_text()
            if texto.strip():
                texto_total.append(f"[Página {num_pagina + 1}]\n{texto}")
        
        doc.close()
        return "\n\n".join(texto_total)
        
    except Exception as e:
        raise ValueError(f"Error al procesar PDF desde URL: {e}")


def _extraer_texto_html(html: str, url: str) -> str:
    """
    Extrae el texto principal de un documento HTML.
    
    Args:
        html: Contenido HTML como string.
        url: URL original (para detectar documentos de Google).
        
    Returns:
        Texto plano extraído.
    """
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Eliminar scripts, estilos y elementos no visibles
        for elemento in soup(["script", "style", "nav", "footer", "header"]):
            elemento.decompose()
        
        # Detectar si es un documento de Google
        if "docs.google.com" in url or "drive.google.com" in url:
            return _extraer_texto_google_docs(soup)
        
        # Extraer texto del body
        if soup.body:
            texto = soup.body.get_text(separator="\n")
        else:
            texto = soup.get_text(separator="\n")
        
        # Limpiar líneas vacías múltiples
        lineas = [linea.strip() for linea in texto.split("\n") if linea.strip()]
        return "\n".join(lineas)
        
    except ImportError:
        # Si no está BeautifulSoup, usar extracción básica
        return _extraer_texto_html_basico(html)
    except Exception as e:
        raise ValueError(f"Error al procesar HTML: {e}")


def _extraer_texto_google_docs(soup: "BeautifulSoup") -> str:
    """Extrae texto específicamente de documentos de Google."""
    # Los documentos de Google suelen tener el contenido en estos selectores
    selectores = [
        "div#contents",
        "div.docs-editor-container",
        "div.kix-paginateddocumentplugin",
        "div[role='document']"
    ]
    
    for selector in selectores:
        contenido = soup.select_one(selector)
        if contenido:
            return contenido.get_text(separator="\n")
    
    # Fallback: extraer todo el texto
    return soup.get_text(separator="\n")


def _extraer_texto_html_basico(html: str) -> str:
    """Extracción básica de texto HTML sin BeautifulSoup."""
    import re
    
    # Eliminar tags HTML
    texto = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r'<style[^>]*>.*?</style>', '', texto, flags=re.DOTALL | re.IGNORECASE)
    texto = re.sub(r'<[^>]+>', ' ', texto)
    
    # Limpiar entidades HTML
    texto = texto.replace("&nbsp;", " ")
    texto = texto.replace("&lt;", "<")
    texto = texto.replace("&gt;", ">")
    texto = texto.replace("&amp;", "&")
    
    # Limpiar espacios y saltos de línea
    lineas = [linea.strip() for linea in texto.split("\n") if linea.strip()]
    return "\n".join(lineas)


def limpiar_texto(texto: str) -> str:
    """
    Limpia el texto extraído: elimina espacios extra y caracteres de control.
    
    Args:
        texto: Texto crudo extraído.
        
    Returns:
        Texto limpio y normalizado.
    """
    import re
    
    # Eliminar caracteres de control (excepto saltos de línea)
    texto = re.sub(r'[^\S\n]+', ' ', texto)
    
    # Colapsar múltiples saltos de línea
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    
    return texto.strip()


def procesar_fuente(
    tipo: str,
    archivo_pdf: Optional[Union[Path, io.BytesIO]] = None,
    url: Optional[str] = None,
) -> dict:
    """
    Procesa una fuente de datos (PDF o URL) y retorna el texto extraído.
    
    Args:
        tipo: "PDF" o "URL".
        archivo_pdf: Archivo PDF (si tipo es "PDF").
        url: URL (si tipo es "URL").
        
    Returns:
        Diccionario con 'texto_limpio' y 'nombre'.
    """
    if tipo == "PDF":
        if not archivo_pdf:
            raise ValueError("Debe proporcionar un archivo PDF")
        
        # Determinar nombre del archivo
        if isinstance(archivo_pdf, Path):
            nombre = archivo_pdf.name
        elif hasattr(archivo_pdf, 'name'):
            nombre = archivo_pdf.name
        else:
            nombre = "documento.pdf"
        
        texto_crudo = extraer_texto_pdf(archivo_pdf)
        
    elif tipo == "URL":
        if not url:
            raise ValueError("Debe proporcionar una URL")
        
        nombre = url[:50] + "..." if len(url) > 50 else url
        texto_crudo = extraer_texto_url(url)
        
    else:
        raise ValueError(f"Tipo de fuente no soportado: {tipo}")
    
    texto_limpio = limpiar_texto(texto_crudo)
    
    return {
        "texto_limpio": texto_limpio,
        "nombre": nombre,
        "total_caracteres": len(texto_limpio)
    }
