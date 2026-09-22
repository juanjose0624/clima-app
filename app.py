import os
from datetime import datetime
from collections import defaultdict

import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
URL_CLIMA_ACTUAL = "https://api.openweathermap.org/data/2.5/weather"
URL_PRONOSTICO = "https://api.openweathermap.org/data/2.5/forecast"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/clima")
def obtener_clima():
    ciudad = request.args.get("ciudad")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not ciudad and not (lat and lon):
        return jsonify({"error": "Debes indicar una ciudad o una ubicación"}), 400

    # Parámetros comunes para las peticiones a OpenWeatherMap
    params_base = {
        "appid": API_KEY,
        "units": "metric",
        "lang": "es"
    }

    if ciudad:
        params_base["q"] = ciudad
    else:
        params_base["lat"] = lat
        params_base["lon"] = lon

    try:
        # ----- Clima actual -----
        respuesta_actual = requests.get(URL_CLIMA_ACTUAL, params=params_base)
        datos_actuales = respuesta_actual.json()

        if respuesta_actual.status_code != 200:
            mensaje = datos_actuales.get("message", "No se pudo obtener el clima")
            return jsonify({"error": mensaje.capitalize()}), respuesta_actual.status_code

        actual = {
            "ciudad": datos_actuales["name"],
            "pais": datos_actuales["sys"]["country"],
            "temperatura": datos_actuales["main"]["temp"],
            "sensacion": datos_actuales["main"]["feels_like"],
            "humedad": datos_actuales["main"]["humidity"],
            "presion": datos_actuales["main"]["pressure"],
            "viento": round(datos_actuales["wind"]["speed"] * 3.6, 1),  # m/s -> km/h
            "descripcion": datos_actuales["weather"][0]["description"],
            "icono": datos_actuales["weather"][0]["icon"],
        }

        # ----- Pronóstico (usamos las mismas coordenadas para consistencia) -----
        params_pronostico = dict(params_base)
        params_pronostico["lat"] = datos_actuales["coord"]["lat"]
        params_pronostico["lon"] = datos_actuales["coord"]["lon"]
        params_pronostico.pop("q", None)

        respuesta_pronostico = requests.get(URL_PRONOSTICO, params=params_pronostico)
        datos_pronostico = respuesta_pronostico.json()

        pronostico = procesar_pronostico_diario(datos_pronostico.get("list", []))

        return jsonify({
            "actual": actual,
            "pronostico": pronostico
        })

    except requests.exceptions.RequestException:
        return jsonify({"error": "No se pudo conectar con el servicio de clima"}), 500


def procesar_pronostico_diario(lista_pronostico):
    """
    OpenWeatherMap free tier da datos cada 3 horas.
    Aquí los agrupamos por día y sacamos max/min, quedándonos
    con el dato más cercano al mediodía para el ícono/descripción.
    """
    dias = defaultdict(list)

    for item in lista_pronostico:
        fecha = item["dt_txt"].split(" ")[0]
        dias[fecha].append(item)

    resultado = []
    hoy = datetime.now().strftime("%Y-%m-%d")

    for fecha, items in dias.items():
        if fecha == hoy:
            continue  # ya mostramos el día actual en la tarjeta principal

        temps = [i["main"]["temp"] for i in items]

        # Buscamos el registro más cercano al mediodía para el ícono
        item_mediodia = min(
            items,
            key=lambda i: abs(int(i["dt_txt"].split(" ")[1].split(":")[0]) - 12)
        )

        resultado.append({
            "fecha": fecha,
            "temp_max": max(temps),
            "temp_min": min(temps),
            "icono": item_mediodia["weather"][0]["icon"],
            "descripcion": item_mediodia["weather"][0]["description"],
        })

    return resultado[:5]


if __name__ == "__main__":
    app.run(debug=True)