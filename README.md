# Comparador de Similitud de Textos (PDF y Web)

Este proyecto tiene como propósito principal comparar el contenido de archivos PDF y páginas web (URLs) para analizar y verificar el nivel de similitud entre sus textos. Es una herramienta útil para identificar si dos fuentes de información distintas tratan sobre el mismo tema o comparten contenido clave.

## Características Principales

- **Análisis Multiformato:** Extracción y comparación de texto tanto de documentos locales (PDFs) como de rutas de internet.
- **Comparación Visual:** Generación de un **Diagrama de Venn** al finalizar el proceso, lo que permite observar gráficamente las similitudes y diferencias entre los textos analizados.
- **Resumen Descriptivo:** El análisis visual es acompañado por un breve informe de texto que concluye si los documentos tratan de lo mismo o si su contenido es parecido.
- **Interfaz Web Interactiva:** Construido utilizando Streamlit para una experiencia fluida.
- **Analisis de IA**: Análisis de gemini considerando el contexto de ambos textos, genera una comparación y una conclusión

## Instalación y Ejecución

Para correr este proyecto en tu máquina local, sigue estos pasos:

1. **Clona el repositorio** (opcional si ya tienes el código localmente):
   ```bash
   git clone https://github.com/mdin65/Comparador_archivos.git
   cd Comparador_archivos

2. Instala las dependencias:
Asegúrate de tener Python instalado. Luego, instala los paquetes necesarios ejecutando:

        pip install -r requirements.txt

4. Generar ambiente de llave:
Genera un nuevo archivo en el proyecto denominado .env, en este deberás agregar la siguiente linea reemplazando el interior de las comillas por la llave real de gemini:

        GEMINI_API_KEY="LLAVE_DE_GEMINI"

6. Modelo de IA:
Una vez generada la llave, comparator.py necesitará el modelo a utilizar. Para saber cual modelo tienes o utilizarás puedes ejecutar "test_gemini.py". Aparecerá un listado, reemplaza el modelo a libre disposición.

7. Ejecuta la aplicación:
Una vez instaladas las dependencias, y definidos los parámetros de la IA levanta el servidor local de Streamlit con el siguiente comando:
        streamlit run app.py

    
