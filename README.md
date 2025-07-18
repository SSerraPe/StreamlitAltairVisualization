# Dashboard Interactivo – Sarampión y Rubéola 2024

**Autor:** Serra Peña Sebastián  
**Curso:** MESIO Summer School – Fundamentals of Data Visualization  
**Entrega:** Julio 18, 2025

---

## 🧭 Objetivo del proyecto

Este proyecto responde a las preguntas clave del curso en torno a los casos de sarampión y rubéola reportados en el año 2024, utilizando datos provisionales publicados por la OMS. El objetivo principal es construir un conjunto de visualizaciones interactivas que permitan explorar, entender y comparar la distribución temporal y geográfica de los casos a nivel mundial, con énfasis en claridad, consistencia y utilidad.

---

## 📁 Estructura de la carpeta

| Archivo/Carpeta                | Descripción |
|-------------------------------|-------------|
| `cases_month_clean.csv`       | Datos mensuales limpios para 2024 |
| `cases_year_clean.csv`        | Datos anuales limpios para 2024 |
| `measles_data_cleaning.ipynb` | Notebook que realiza la limpieza y guardado de los archivos `.csv` desde los datos originales del TidyTuesday |
| `alt_measles.ipynb`           | Notebook principal que documenta el proceso de diseño y construcción de cada visualización respondiendo las 4 preguntas clave |
| `st_dashboard.py`             | Script ejecutable con Streamlit que presenta el dashboard interactivo final |
| `requirements.txt`            | Archivo para crear un entorno virtual reproducible con las dependencias necesarias |
| `.venv/`                       | Entorno virtual local con los paquetes necesarios (opcional, se puede regenerar con `requirements.txt`) |

---

## ✅ ¿Cómo este proyecto responde a los requerimientos?

El proyecto entrega todo lo solicitado en la propuesta:

- ✅ **Visualizaciones diseñadas para cada una de las 4 preguntas del proyecto** (ver notebook `alt_measles.ipynb`).
- ✅ **Visualizaciones interactivas implementadas con Altair**, integradas en un dashboard navegable vía Streamlit (`st_dashboard.py`).
- ✅ **Interacciones cruzadas** (por país, región, tipo de enfermedad) que permiten explorar los datos en múltiples dimensiones.
- ✅ **Explicación detallada del diseño** (tipo de gráfico, decisiones estéticas, utilidad para el usuario) documentada dentro del notebook.
- ✅ **Datos limpiados y guardados localmente** como archivos `.csv` según la instrucción.
- ✅ **Entrega reproducible** en Google Colab a través del notebook `alt_measles.ipynb` (compatible con Altair y archivos `.csv`).
- ✅ **Dashboard funcional públicamente publicado** (en caso de problemas de ejecución local, consultar link público proporcionado en la entrega).

---

## 🚀 Instrucciones de ejecución

### En local
1. Crear y activar un entorno virtual (opcional):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # o .venv\\Scripts\\activate en Windows
   pip install -r requirements.txt
   ```

2. Ejecutar el dashboard:

   ```bash
   streamlit run st_dashboard.py
   ```

### En Google Colab

* Abrir `alt_measles.ipynb` en Colab y subir los archivos `.csv`.
* Ejecutar todas las celdas para visualizar los pasos de diseño y las visualizaciones por separado.

---

## 🌐 Dashboard en línea

En caso de dificultades para ejecutar localmente el Streamlit, el dashboard está disponible públicamente en la plataforma [Streamlit Community Cloud](https://project-measles-rubeola-dataviz-ssp.streamlit.app/). El enlace se encuentra adjunto en la plataforma de entrega.

---

## 📌 Fuente de los datos

Los datos fueron descargados desde el repositorio oficial de [TidyTuesday - Semana 25 de 2025](https://github.com/rfordatascience/tidytuesday/tree/main/data/2025/2025-06-24), los cuales se basan en los reportes provisionales de la Organización Mundial de la Salud (OMS).

---

## ✍️ Notas finales

Este proyecto fue desarrollado de forma individual como parte de la **MESIO Summer School** y refleja tanto el proceso exploratorio como la entrega final del dashboard interactivo. Todas las herramientas utilizadas son de código abierto y permiten su ejecución en Colab o en local.
