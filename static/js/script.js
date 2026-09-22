// ===== Elementos del DOM =====
const ciudadInput = document.getElementById('ciudadInput');
const btnBuscar = document.getElementById('btnBuscar');
const btnUbicacion = document.getElementById('btnUbicacion');
const loader = document.getElementById('loader');
const mensajeError = document.getElementById('mensajeError');

const climaActual = document.getElementById('climaActual');
const ciudadNombre = document.getElementById('ciudadNombre');
const fechaHoy = document.getElementById('fechaHoy');
const iconoClima = document.getElementById('iconoClima');
const temperatura = document.getElementById('temperatura');
const descripcion = document.getElementById('descripcion');
const sensacion = document.getElementById('sensacion');
const humedad = document.getElementById('humedad');
const viento = document.getElementById('viento');
const presion = document.getElementById('presion');

const pronosticoContenedor = document.getElementById('pronostico');
const historialContenedor = document.getElementById('historialContenedor');
const historialDiv = document.getElementById('historial');

// ===== Historial (guardado en localStorage) =====
const MAX_HISTORIAL = 5;

function obtenerHistorial() {
    return JSON.parse(localStorage.getItem('historialClima')) || [];
}

function guardarEnHistorial(ciudad) {
    let historial = obtenerHistorial();
    historial = historial.filter(c => c.toLowerCase() !== ciudad.toLowerCase());
    historial.unshift(ciudad);
    historial = historial.slice(0, MAX_HISTORIAL);
    localStorage.setItem('historialClima', JSON.stringify(historial));
    renderizarHistorial();
}

function renderizarHistorial() {
    const historial = obtenerHistorial();
    historialDiv.innerHTML = '';

    if (historial.length === 0) {
        historialContenedor.classList.add('d-none');
        return;
    }

    historialContenedor.classList.remove('d-none');
    historial.forEach(ciudad => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-sm';
        btn.textContent = ciudad;
        btn.addEventListener('click', () => buscarClima(ciudad));
        historialDiv.appendChild(btn);
    });
}

// ===== Utilidades =====
function mostrarError(mensaje) {
    mensajeError.textContent = mensaje;
    mensajeError.classList.remove('d-none');
}

function ocultarError() {
    mensajeError.classList.add('d-none');
}

function mostrarLoader(mostrar) {
    loader.classList.toggle('d-none', !mostrar);
}

function formatearFecha(fecha) {
    const opciones = { weekday: 'long', day: 'numeric', month: 'long' };
    return fecha.toLocaleDateString('es-ES', opciones);
}

// ===== Renderizar clima actual =====
function renderizarClimaActual(data) {
    ciudadNombre.textContent = `${data.ciudad}, ${data.pais}`;
    fechaHoy.textContent = formatearFecha(new Date());
    iconoClima.src = `https://openweathermap.org/img/wn/${data.icono}@2x.png`;
    temperatura.textContent = `${Math.round(data.temperatura)}°C`;
    descripcion.textContent = data.descripcion;
    sensacion.textContent = `${Math.round(data.sensacion)}°C`;
    humedad.textContent = `${data.humedad}%`;
    viento.textContent = `${data.viento} km/h`;
    presion.textContent = `${data.presion} hPa`;

    climaActual.classList.remove('d-none');
}

// ===== Renderizar pronóstico 5 días =====
function renderizarPronostico(dias) {
    pronosticoContenedor.innerHTML = '';

    dias.forEach(dia => {
        const fecha = new Date(dia.fecha);
        const nombreDia = fecha.toLocaleDateString('es-ES', { weekday: 'short' });

        const col = document.createElement('div');
        col.className = 'col-auto';
        col.innerHTML = `
            <div class="card-pronostico">
                <h6>${nombreDia}</h6>
                <img src="https://openweathermap.org/img/wn/${dia.icono}.png" alt="${dia.descripcion}">
                <div><span class="temp-max">${Math.round(dia.temp_max)}°</span> / <span class="temp-min">${Math.round(dia.temp_min)}°</span></div>
            </div>
        `;
        pronosticoContenedor.appendChild(col);
    });

    pronosticoContenedor.classList.remove('d-none');
}

// ===== Petición al backend (Flask) =====
async function buscarClima(ciudad) {
    ocultarError();
    mostrarLoader(true);
    climaActual.classList.add('d-none');
    pronosticoContenedor.classList.add('d-none');

    try {
        const respuesta = await fetch(`/api/clima?ciudad=${encodeURIComponent(ciudad)}`);
        const data = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(data.error || 'No se pudo obtener el clima');
        }

        renderizarClimaActual(data.actual);
        renderizarPronostico(data.pronostico);
        guardarEnHistorial(data.actual.ciudad);
        ciudadInput.value = '';

    } catch (error) {
        mostrarError(error.message);
    } finally {
        mostrarLoader(false);
    }
}

async function buscarClimaPorCoordenadas(lat, lon) {
    ocultarError();
    mostrarLoader(true);
    climaActual.classList.add('d-none');
    pronosticoContenedor.classList.add('d-none');

    try {
        const respuesta = await fetch(`/api/clima?lat=${lat}&lon=${lon}`);
        const data = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(data.error || 'No se pudo obtener el clima');
        }

        renderizarClimaActual(data.actual);
        renderizarPronostico(data.pronostico);
        guardarEnHistorial(data.actual.ciudad);

    } catch (error) {
        mostrarError(error.message);
    } finally {
        mostrarLoader(false);
    }
}

// ===== Eventos =====
btnBuscar.addEventListener('click', () => {
    const ciudad = ciudadInput.value.trim();
    if (ciudad === '') {
        mostrarError('Escribe el nombre de una ciudad');
        return;
    }
    buscarClima(ciudad);
});

ciudadInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        btnBuscar.click();
    }
});

btnUbicacion.addEventListener('click', () => {
    if (!navigator.geolocation) {
        mostrarError('Tu navegador no soporta geolocalización');
        return;
    }

    mostrarLoader(true);
    navigator.geolocation.getCurrentPosition(
        (posicion) => {
            const { latitude, longitude } = posicion.coords;
            buscarClimaPorCoordenadas(latitude, longitude);
        },
        () => {
            mostrarLoader(false);
            mostrarError('No se pudo acceder a tu ubicación');
        }
    );
});

// ===== Al cargar la página =====
document.addEventListener('DOMContentLoaded', () => {
    renderizarHistorial();
});