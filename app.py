from flask import Flask, render_template, jsonify, request
from model import MotorScrabble
import os

app = Flask(__name__)

# Inicialización del motor del juego
juego = MotorScrabble(ruta_diccionario="Diccionario.txt")


@app.route("/")
def index():
    """Carga la página principal del juego"""
    return render_template("index.html")


@app.route("/api/estado")
def obtener_estado():
    """Envía al frontend el estado actual del tablero, puntos y fichas"""
    return jsonify(
        {
            "tablero": juego.grid,
            "atril": juego.atril_usuario,
            "puntos_usuario": juego.puntos_usuario,
            "puntos_cpu": juego.puntos_cpu,
            "bolsa_restante": len(juego.bolsa),
        }
    )


@app.route("/api/jugada", methods=["POST"])
def procesar_jugada():
    """Recibe y procesa el intento de palabra del usuario"""
    d = request.json
    res = juego.ejecutar_jugada(
        d.get("palabra", ""), d.get("fila"), d.get("col"), d.get("direccion", "H")
    )

    if res["status"] == "success":
        # Si la jugada es válida, reiniciamos el contador de pases
        juego.pases_consecutivos = 0
        return jsonify({"status": "success", "puntos": res["puntos"]})

    return jsonify({"status": "error", "mensaje": res.get("msj")}), 400


@app.route("/api/ia_juega", methods=["POST"])
def ia_juega():
    """Solicita a la IA que realice su movimiento"""
    res = juego.jugada_ia()
    return jsonify(res)


@app.route("/api/cambiar_fichas", methods=["POST"])
def api_cambiar_fichas():
    """Permite al usuario canjear letras seleccionadas por nuevas de la bolsa"""
    letras = request.json.get("fichas", [])
    juego.cambiar_letras(letras)
    # Cambiar fichas también cuenta como una acción que reinicia pases
    juego.pases_consecutivos = 0
    return jsonify({"status": "success"})


@app.route("/api/pasar", methods=["POST"])
def pasar_turno():
    """Suma un pase y verifica si se cumplen las condiciones de fin de partida"""
    juego.pases_consecutivos += 1

    if juego.pases_consecutivos >= 3:
        # Lógica de determinación del ganador
        if juego.puntos_usuario > juego.puntos_cpu:
            ganador = "USUARIO"
        elif juego.puntos_cpu > juego.puntos_usuario:
            ganador = "CPU"
        else:
            ganador = "EMPATE"

        return jsonify(
            {
                "status": "game_over",
                "ganador": ganador,
                "pts_user": juego.puntos_usuario,
                "pts_cpu": juego.puntos_cpu,
            }
        )

    return jsonify({"status": "success"})


@app.route("/api/reiniciar", methods=["POST"])
def reiniciar():
    """Llama al método de reinicio del motor para empezar de cero"""
    juego.reiniciar_juego()
    return jsonify({"status": "success"})


if __name__ == "__main__":
    # Render usa una variable de entorno llamada PORT
    port = int(os.environ.get("PORT", 5000))
    # Importante: bindear a 0.0.0.0 para que sea accesible externamente
    app.run(host="0.0.0.0", port=port)
