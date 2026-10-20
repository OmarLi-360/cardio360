"""
Cardio360 · Construye el tablero interactivo a partir de los resultados de los cuadernos.

Uso (desde la carpeta Cardio360):
    python construir_tablero.py

Lee:
    resultados/eda.json, resultados/modelos.json, resultados/latente.json   (los producen los cuadernos 01, 02 y 03)
    recursos/plantilla_tablero.html                                          (diseño e interacción del tablero)
    recursos/plotly.min.js                                                   (librería de gráficos, para usarlo sin internet)
Escribe dos versiones con el mismo contenido:
    tablero/tablero_riesgo_cardiovascular.html   sin internet: la librería va dentro del archivo (doble clic para abrir)
    tablero/index.html                           versión web, liviana: la librería se carga desde un CDN (la usa GitHub Pages)

Solo usa la biblioteca estándar de Python: no requiere instalar nada adicional.
"""
import json
import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
RUTA = lambda *partes: os.path.join(RAIZ, *partes)

SITIO = "https://omarli-360.github.io/cardio360/"
TITULO = "Tablero de Riesgo Cardiovascular · Cardio360"
DESCRIPCION = ("Exploración interactiva de 68.512 exámenes médicos: modelos de aprendizaje automático, "
               "umbral clínico, reducción de dimensionalidad con SHAP, equidad y simulador de riesgo.")

CDN = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.35.2/plotly.min.js"></script>\n'
       '<script>window.Plotly||document.write(\'<script src="https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js"><\\/script>\');</script>')
INICIO = '<a class="home" href="../index.html">← Cardio360 · inicio del proyecto</a>'


def leer_resultados():
    datos = {}
    for clave, archivo in [("eda", "eda.json"), ("modelos", "modelos.json"), ("latente", "latente.json")]:
        ruta = RUTA("resultados", archivo)
        if not os.path.exists(ruta):
            sys.exit(f"Falta {ruta}. Ejecute primero los cuadernos 01, 02 y 03 (o copie sus resultados a la carpeta resultados).")
        with open(ruta, encoding="utf-8") as f:
            datos[clave] = json.load(f)
        print(f"  leído  resultados/{archivo}")
    return datos


def envolver(cuerpo):
    """Documento HTML completo con metadatos para buscadores y para la vista previa al compartir el enlace."""
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{DESCRIPCION}">
<meta name="author" content="Omar Libardo Acelas Angulo">
<meta name="theme-color" content="#b0283f">
<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="../assets/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="../assets/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_CO">
<meta property="og:site_name" content="Cardio360">
<meta property="og:title" content="{TITULO}">
<meta property="og:description" content="{DESCRIPCION}">
<meta property="og:url" content="{SITIO}tablero/">
<meta property="og:image" content="{SITIO}assets/og-cardio360.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<style>html{{color-scheme:light}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
{cuerpo}
</body>
</html>
'''


def construir():
    print("Construyendo el tablero Cardio360…")
    with open(RUTA("recursos", "plantilla_tablero.html"), encoding="utf-8") as f:
        plantilla = f.read()
    datos = json.dumps(leer_resultados(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    pagina = plantilla.replace("__DATA__", datos).replace("<!--INICIO-->", INICIO)
    os.makedirs(RUTA("tablero"), exist_ok=True)

    # Versión web (GitHub Pages): liviana, la librería de gráficos llega desde un CDN.
    with open(RUTA("tablero", "index.html"), "w", encoding="utf-8") as f:
        f.write(envolver(pagina))

    # Versión sin internet: la librería va dentro del archivo.
    ruta_plotly = RUTA("recursos", "plotly.min.js")
    if os.path.exists(ruta_plotly):
        with open(ruta_plotly, encoding="utf-8") as f:
            libreria = f.read().replace("</script", "<\\/script")
        local = pagina.replace(CDN, "<script>" + libreria + "</script>")
    else:
        print("  aviso: no se encontró recursos/plotly.min.js; la versión local necesitará internet")
        local = pagina
    with open(RUTA("tablero", "tablero_riesgo_cardiovascular.html"), "w", encoding="utf-8") as f:
        f.write(envolver(local))

    for nombre in ("index.html", "tablero_riesgo_cardiovascular.html"):
        ruta = RUTA("tablero", nombre)
        print(f"Listo: tablero/{nombre} ({os.path.getsize(ruta) / 1024 / 1024:.1f} MB)")
    print("Para verlo sin internet, abra tablero/tablero_riesgo_cardiovascular.html con doble clic.")


if __name__ == "__main__":
    construir()
