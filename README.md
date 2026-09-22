# 🌤️ Clima App

Aplicación web que consulta el clima actual y el pronóstico de 5 días de cualquier ciudad del mundo, usando la API de **OpenWeatherMap**.

## Autores

- Juan José Sepúlveda Álvarez
- Sebastián Sierra Vélez

## Funcionalidades

- 🔍 Búsqueda de clima por nombre de ciudad
- 📍 Búsqueda por ubicación actual (geolocalización del navegador)
- 🌡️ Clima actual: temperatura, sensación térmica, humedad, viento y presión
- 📅 Pronóstico de los próximos 5 días
- 🕒 Historial de últimas búsquedas (guardado en el navegador)

## Tecnologías

- **Backend:** Python + Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **API externa:** [OpenWeatherMap](https://openweathermap.org)

## Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/juanjose0624/clima-app.git
cd clima-app
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar la API key

Crea un archivo `.env` en la raíz del proyecto (puedes copiar `.env.example`) y agrega tu propia API key de OpenWeatherMap:

```
OPENWEATHER_API_KEY=tu_api_key_aqui
```

> Puedes conseguir una API key gratis registrándote en [openweathermap.org](https://openweathermap.org/api). La activación de la key puede tardar hasta 2 horas.

### 4. Ejecutar la aplicación

```bash
python app.py
```

Abre tu navegador en [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Estructura del proyecto

```
clima-app/
├── app.py                  # Backend Flask
├── .env.example             # Plantilla de variables de entorno
├── requirements.txt          # Dependencias de Python
├── templates/
│   └── index.html            # Interfaz principal
└── static/
    ├── css/
    │   └── style.css         # Estilos
    └── js/
        └── script.js         # Lógica del frontend
```

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
