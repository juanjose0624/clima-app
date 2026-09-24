import os
from datetime import datetime
from collections import defaultdict

import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv


# Carga las variables guardadas en el archivo .env,
# como la API Key de OpenWeather.
load_dotenv()


# Crea la aplicación Flask.
app = Flask(__name__)


# Obtiene la API Key desde el archivo .env.
API_KEY = os.getenv("OPENWEATHER_API_KEY")


# URLs de las dos APIs de OpenWeather que utilizaremos:
# una para el clima actual y otra para el pronóstico.
URL_CLIMA_ACTUAL = "https://api.openweathermap.org/data/2.5/weather"
URL_PRONOSTICO = "https://api.openweathermap.org/data/2.5/forecast"


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@app.route("/")
def index():
    # Muestra el archivo index.html al entrar a la página principal.
    return render_template("index.html")


# ============================================================
# API DEL CLIMA
# ============================================================

@app.route("/api/clima")
def obtener_clima():

    # Obtiene los datos enviados desde el frontend.
    # Se puede buscar por nombre de ciudad o por coordenadas.
    ciudad = request.args.get("ciudad")
    lat = request.args.get("lat")
    lon = request.args.get("lon")


    # Verifica que exista una ciudad o una ubicación
    # mediante latitud y longitud.
    if not ciudad and not (lat and lon):
        return jsonify({
            "error": "Debes indicar una ciudad o una ubicación"
        }), 400


    # Parámetros que se utilizan en las peticiones
    # realizadas a OpenWeather.
    params_base = {
        "appid": API_KEY,
        "units": "metric",
        "lang": "es"
    }


    # Si se proporcionó una ciudad, se busca por nombre.
    # Si no, se utilizan las coordenadas.
    if ciudad:
        params_base["q"] = ciudad
    else:
        params_base["lat"] = lat
        params_base["lon"] = lon


    try:

        # ----------------------------------------------------
        # CLIMA ACTUAL
        # ----------------------------------------------------

        # Consulta a OpenWeather para obtener el clima actual.
        respuesta_actual = requests.get(
            URL_CLIMA_ACTUAL,
            params=params_base
        )

        datos_actuales = respuesta_actual.json()


        # Comprueba si OpenWeather respondió correctamente.
        if respuesta_actual.status_code != 200:
            mensaje = datos_actuales.get(
                "message",
                "No se pudo obtener el clima"
            )

            return jsonify({
                "error": mensaje.capitalize()
            }), respuesta_actual.status_code


        # Organiza únicamente los datos que necesita
        # nuestra aplicación para mostrar el clima actual.
        actual = {
            "ciudad": datos_actuales["name"],
            "pais": datos_actuales["sys"]["country"],
            "temperatura": datos_actuales["main"]["temp"],
            "sensacion": datos_actuales["main"]["feels_like"],
            "humedad": datos_actuales["main"]["humidity"],
            "presion": datos_actuales["main"]["pressure"],

            # OpenWeather entrega el viento en m/s.
            # Se convierte a km/h multiplicando por 3.6.
            "viento": round(
                datos_actuales["wind"]["speed"] * 3.6,
                1
            ),

            "descripcion": datos_actuales["weather"][0]["description"],
            "icono": datos_actuales["weather"][0]["icon"],
        }


        # ----------------------------------------------------
        # PRONÓSTICO
        # ----------------------------------------------------

        # Copiamos los parámetros utilizados anteriormente
        # para preparar la segunda petición.
        params_pronostico = dict(params_base)


        # Utilizamos las coordenadas exactas que OpenWeather
        # encontró para la ciudad.
        params_pronostico["lat"] = datos_actuales["coord"]["lat"]
        params_pronostico["lon"] = datos_actuales["coord"]["lon"]


        # Eliminamos la búsqueda por nombre de ciudad,
        # ya que ahora trabajaremos con coordenadas.
        params_pronostico.pop("q", None)


        # Solicita a OpenWeather el pronóstico.
        respuesta_pronostico = requests.get(
            URL_PRONOSTICO,
            params=params_pronostico
        )

        datos_pronostico = respuesta_pronostico.json()


        # Convierte los numerosos registros de 3 horas
        # de OpenWeather en un pronóstico organizado por días.
        pronostico = procesar_pronostico_diario(
            datos_pronostico.get("list", [])
        )


        # Envía al frontend el clima actual y el pronóstico.
        return jsonify({
            "actual": actual,
            "pronostico": pronostico
        })


    # Si existe un problema de conexión con OpenWeather,
    # se devuelve un error al frontend.
    except requests.exceptions.RequestException:
        return jsonify({
            "error": "No se pudo conectar con el servicio de clima"
        }), 500


# ============================================================
# PROCESAR PRONÓSTICO POR DÍAS
# ============================================================

def procesar_pronostico_diario(lista_pronostico):
    """
    OpenWeather proporciona varios pronósticos durante el día
    en intervalos de aproximadamente 3 horas.

    Esta función los agrupa por fecha y obtiene:
    - Temperatura máxima.
    - Temperatura mínima.
    - Icono.
    - Descripción.

    Finalmente devuelve los próximos 5 días.
    """


    # Diccionario donde cada fecha tendrá
    # todos sus registros meteorológicos.
    dias = defaultdict(list)


    # Agrupa los registros según la fecha.
    for item in lista_pronostico:
        fecha = item["dt_txt"].split(" ")[0]
        dias[fecha].append(item)


    resultado = []


    # Obtiene la fecha actual para no repetirla
    # en el pronóstico.
    hoy = datetime.now().strftime("%Y-%m-%d")


    # Recorre cada día agrupado.
    for fecha, items in dias.items():

        # El día actual ya se muestra en la sección
        # principal, por eso no lo incluimos nuevamente.
        if fecha == hoy:
            continue


        # Obtiene todas las temperaturas registradas
        # durante ese día.
        temps = [i["main"]["temp"] for i in items]


        # Busca el registro más cercano a las 12 del mediodía.
        # Se utiliza para elegir un icono y descripción
        # representativos del día.
        item_mediodia = min(
            items,
            key=lambda i: abs(
                int(i["dt_txt"].split(" ")[1].split(":")[0]) - 12
            )
        )


        # Guarda el resumen del día.
        resultado.append({
            "fecha": fecha,
            "temp_max": max(temps),
            "temp_min": min(temps),
            "icono": item_mediodia["weather"][0]["icon"],
            "descripcion": item_mediodia["weather"][0]["description"],
        })


    # Devuelve solamente los primeros 5 días.
    return resultado[:5]


# ============================================================
# EJECUTAR LA APLICACIÓN
# ============================================================

if __name__ == "__main__":

    # Inicia el servidor Flask en modo desarrollo.
    # debug=True permite ver errores y reinicia el servidor
    # automáticamente cuando se modifica el código.
    app.run(debug=True)

