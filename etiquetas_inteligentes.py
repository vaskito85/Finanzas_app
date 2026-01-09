import re
from collections import defaultdict, Counter
import math


def limpiar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-zA-Z0-9áéíóúñ ]", " ", texto)
    return texto.strip()


def entrenar_modelo(movimientos):
    """
    movimientos: lista de dicts con:
    - descripcion
    - etiquetas (lista)
    """
    palabra_por_etiqueta = defaultdict(Counter)
    etiqueta_conteo = Counter()

    for mov in movimientos:
        etiquetas = mov.get("etiquetas", [])
        descripcion = limpiar_texto(mov.get("descripcion", ""))

        palabras = descripcion.split()

        for etiqueta in etiquetas:
            etiqueta_conteo[etiqueta] += 1
            for palabra in palabras:
                palabra_por_etiqueta[etiqueta][palabra] += 1

    return {
        "palabra_por_etiqueta": {k: dict(v) for k, v in palabra_por_etiqueta.items()},
        "etiqueta_conteo": dict(etiqueta_conteo)
    }


def predecir_etiquetas(modelo, descripcion, top_n=3):
    descripcion = limpiar_texto(descripcion)
    palabras = descripcion.split()

    scores = defaultdict(float)

    palabra_por_etiqueta = modelo["palabra_por_etiqueta"]
    etiqueta_conteo = modelo["etiqueta_conteo"]

    total_etiquetas = sum(etiqueta_conteo.values())

    for etiqueta, count in etiqueta_conteo.items():
        prior = count / total_etiquetas
        score = math.log(prior + 1e-9)

        for palabra in palabras:
            freq = palabra_por_etiqueta.get(etiqueta, {}).get(palabra, 0)
            score += math.log((freq + 1) / (count + 1))

        scores[etiqueta] = score

    sugeridas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [etq for etq, _ in sugeridas[:top_n]]