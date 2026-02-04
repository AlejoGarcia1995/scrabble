/**
 * SCRABBLE AI PRO - Lógica de Frontend
 * Gestiona la interactividad, peticiones a la API y renderizado del tablero.
 */

let seleccionActiva = { fila: 7, col: 7 };
let modoCambioActivo = false;

// --- 1. GESTIÓN DE INTERFAZ Y RENDERIZADO ---

async function actualizar() {
    const res = await fetch('/api/estado');
    const data = await res.json();
    
    // Renderizado del Tablero
    const t = document.getElementById('tablero');
    t.innerHTML = '';
    data.tablero.forEach((fila, f) => {
        fila.forEach((c, col) => {
            const div = document.createElement('div');
            div.className = 'celda' + (c.bono ? ` bono-${c.bono}` : '') + (c.letra ? ' ficha-letra' : '');
            div.textContent = c.letra || c.bono || '';
            
            // Selección de celda para jugar
            div.onclick = () => {
                document.querySelectorAll('.celda').forEach(el => el.classList.remove('selected'));
                div.classList.add('selected');
                seleccionActiva = { fila: f, col: col };
                
                // Actualizar indicadores visuales de fila/columna
                document.getElementById('val-fila').textContent = f + 1;
                document.getElementById('val-col').textContent = col + 1;
            };
            t.appendChild(div);
        });
    });

    // Renderizado del Atril del Usuario
    const au = document.getElementById('atril-user');
    au.innerHTML = '';
    data.atril.forEach(l => {
        const div = document.createElement('div');
        div.className = 'celda ficha-letra' + (modoCambioActivo ? ' seleccionable' : '');
        div.textContent = l;
        div.onclick = () => { 
            if(modoCambioActivo) div.classList.toggle('cambiar-seleccionada'); 
        };
        au.appendChild(div);
    });

    // Actualización de marcadores y bolsa
    document.getElementById('pts-user').textContent = data.puntos_usuario;
    document.getElementById('pts-cpu').textContent = data.puntos_cpu;
    document.getElementById('fichas-bolsa').textContent = data.bolsa_restante;

    // Control del botón de pasar turno
    actualizarBotonPasar(data.bolsa_restante);
}

function actualizarBotonPasar(bolsa_restante) {
    const btnPasar = document.getElementById('btn-pasar');
    if (btnPasar) {
        // Se habilita cuando quedan pocas fichas para evitar bloqueos
        btnPasar.style.display = (bolsa_restante < 10) ? 'block' : 'none';
    }
}

// --- 2. LÓGICA DE JUGABILIDAD ---

async function intentarJugada() {
    const palabra = document.getElementById('input-palabra').value;
    if (!palabra) return mostrarMensaje("Escribe una palabra");

    const res = await fetch('/api/jugada', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            palabra, 
            ...seleccionActiva,
            direccion: document.getElementById('dir-switch').checked ? 'V' : 'H'
        })
    });
    
    const data = await res.json();
    if (data.status === "success") {
        mostrarCartelAnuncio(`¡BIEN! +${data.puntos} PTS`);
        document.getElementById('input-palabra').value = '';
        await actualizar();
        setTimeout(turnoIA, 1500);
    } else {
        mostrarMensaje(data.mensaje);
    }
}

async function pasarTurno() {
    const res = await fetch('/api/pasar', { method: 'POST' });
    const data = await res.json();
    
    if (data.status === "game_over") {
        mostrarCartelFinal(data);
    } else {
        mostrarCartelAnuncio("PASASTE TURNO");
        setTimeout(turnoIA, 1000);
    }
}

// --- 3. LÓGICA DE LA IA ---

async function turnoIA() {
    document.getElementById('nombre-turno').textContent = "CPU...";
    const res = await fetch('/api/ia_juega', { method: 'POST' });
    const data = await res.json();
    
    if (data.accion === "palabra") {
        mostrarCartelAnuncio(`CPU JUGÓ: ${data.palabra} (+${data.puntos})`);
    } else {
        mostrarCartelAnuncio("CPU CAMBIÓ FICHAS");
    }
    
    document.getElementById('nombre-turno').textContent = "TÚ";
    actualizar();
}

// --- 4. GESTIÓN DEL CAMBIO DE FICHAS ---

function animarRobo() {
    if (modoCambioActivo) { 
        cancelarModoCambio(); 
        return; 
    }
    modoCambioActivo = true;
    document.getElementById('btn-confirmar-cambio').style.display = 'block';
    document.getElementById('atril-user').style.background = "rgba(243, 156, 18, 0.3)";
    actualizar();
}

async function confirmarCambio() {
    const seleccionadas = document.querySelectorAll('.cambiar-seleccionada');
    if (seleccionadas.length === 0) return mostrarMensaje("Selecciona fichas");

    const letras = Array.from(seleccionadas).map(f => f.textContent.trim());
    const res = await fetch('/api/cambiar_fichas', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ fichas: letras })
    });

    if (res.ok) {
        mostrarMensaje("Fichas cambiadas", "success");
        cancelarModoCambio();
        await actualizar();
        setTimeout(turnoIA, 1000);
    }
}

function cancelarModoCambio() {
    modoCambioActivo = false;
    document.getElementById('btn-confirmar-cambio').style.display = 'none';
    document.getElementById('atril-user').style.background = "";
    actualizar();
}

// --- 5. NOTIFICACIONES Y FINALIZACIÓN ---

function mostrarCartelFinal(data) {
    const overlay = document.createElement('div');
    overlay.className = 'cartel-final-overlay';
    overlay.style.zIndex = "9999"; 
    
    overlay.innerHTML = `
        <div class="cartel-anuncio-cpu final" style="z-index: 10000; pointer-events: auto;">
            <h2>EL GANADOR ES: ${data.ganador}</h2>
            <p>Tú: ${data.pts_user} - CPU: ${data.pts_cpu}</p>
            <button id="btn-reiniciar" class="btn-nuevo-juego" style="cursor:pointer; position:relative; z-index:10001;">
                JUGAR DE NUEVO
            </button>
        </div>
    `;

    document.body.appendChild(overlay);

    document.getElementById("btn-reiniciar").onclick = async (e) => {
        e.stopPropagation();
        try {
            const res = await fetch('/api/reiniciar', { method: 'POST' }); 
            if (res.ok) window.location.reload(); 
        } catch (error) {
            console.error("Error al reiniciar:", error);
        }
    };
}

function mostrarCartelAnuncio(t) {
    const a = document.createElement('div');
    a.className = 'cartel-anuncio-cpu';
    a.innerText = t;
    document.body.appendChild(a);
    setTimeout(() => a.remove(), 2500);
}

function mostrarMensaje(t) {
    const s = document.getElementById("mensaje-texto");
    s.innerText = t;
    document.getElementById("notificacion-juego").classList.remove("hidden");
    setTimeout(() => document.getElementById("notificacion-juego").classList.add("hidden"), 2000);
}

// --- 6. INICIALIZACIÓN ---

document.addEventListener('DOMContentLoaded', () => {
    actualizar();
    
    // Vinculación de eventos a botones
    document.getElementById('btn-jugar').onclick = intentarJugada;
    document.getElementById('btn-confirmar-cambio').onclick = confirmarCambio;
    document.getElementById('btn-pasar').onclick = pasarTurno;
    document.getElementById('bolsa-zona').onclick = animarRobo;
});