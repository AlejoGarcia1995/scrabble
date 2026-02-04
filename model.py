import random
import unicodedata
import os


class MotorScrabble:
    def __init__(self, ruta_diccionario="Diccionario.txt"):
        """Inicialización de constantes, tablero y estados de juego"""

        # Valores de puntuación oficial para Scrabble en español
        self.VALORES_LETRAS = {
            "A": 1,
            "E": 1,
            "O": 1,
            "I": 1,
            "S": 1,
            "N": 1,
            "R": 1,
            "U": 1,
            "L": 1,
            "T": 1,
            "D": 2,
            "G": 2,
            "C": 3,
            "B": 3,
            "M": 3,
            "P": 3,
            "H": 4,
            "F": 4,
            "V": 4,
            "Y": 4,
            "CH": 5,
            "Q": 5,
            "J": 8,
            "LL": 8,
            "Ñ": 8,
            "RR": 8,
            "X": 8,
            "Z": 10,
        }

        # Coordenadas de los bonos en el tablero 15x15
        self.BONOS = {
            "3P": [
                (0, 0),
                (0, 7),
                (0, 14),
                (7, 0),
                (7, 14),
                (14, 0),
                (14, 7),
                (14, 14),
            ],
            "2P": [
                (1, 1),
                (2, 2),
                (3, 3),
                (4, 4),
                (1, 13),
                (2, 12),
                (3, 11),
                (4, 10),
                (10, 4),
                (11, 3),
                (12, 2),
                (13, 1),
                (10, 10),
                (11, 11),
                (12, 12),
                (13, 13),
            ],
            "3L": [
                (1, 5),
                (1, 9),
                (5, 1),
                (5, 5),
                (5, 9),
                (5, 13),
                (9, 1),
                (9, 5),
                (9, 9),
                (9, 13),
                (13, 5),
                (13, 9),
            ],
            "2L": [
                (0, 3),
                (0, 11),
                (2, 6),
                (2, 8),
                (3, 0),
                (3, 7),
                (3, 14),
                (6, 2),
                (6, 6),
                (6, 8),
                (6, 12),
                (7, 3),
                (7, 11),
                (8, 2),
                (8, 6),
                (8, 8),
                (8, 12),
                (11, 0),
                (11, 7),
                (11, 14),
                (12, 6),
                (12, 8),
                (14, 3),
                (14, 11),
            ],
        }

        # Estado inicial del tablero, diccionario y fichas
        self.grid = [
            [{"letra": None, "bono": self._obtener_bono_pos(f, c)} for c in range(15)]
            for f in range(15)
        ]
        self.diccionario = self._cargar_diccionario(ruta_diccionario)
        self.bolsa = self._inicializar_bolsa()

        self.puntos_usuario = 0
        self.puntos_cpu = 0
        self.atril_usuario = []
        self.atril_cpu = []
        self.pases_consecutivos = 0

        # Reparto inicial de fichas
        self.rellenar_atril(self.atril_usuario)
        self.rellenar_atril(self.atril_cpu)

    def reiniciar_juego(self):
        """Resetea todos los valores para comenzar una partida nueva"""
        self.grid = [
            [{"letra": None, "bono": self._obtener_bono_pos(f, c)} for c in range(15)]
            for f in range(15)
        ]
        self.bolsa = self._inicializar_bolsa()
        self.puntos_usuario = 0
        self.puntos_cpu = 0
        self.atril_usuario = []
        self.atril_cpu = []
        self.pases_consecutivos = 0
        self.rellenar_atril(self.atril_usuario)
        self.rellenar_atril(self.atril_cpu)

    def normalizar(self, texto):
        """Limpia acentos y estandariza a mayúsculas protegiendo la Ñ"""
        if not texto:
            return ""
        texto = texto.upper()
        s = "".join(
            c
            for c in unicodedata.normalize("NFD", texto)
            if unicodedata.category(c) != "Mn" or c == "\u0303"
        )
        return unicodedata.normalize("NFC", s)

    def tokenizar(self, palabra):
        """Divide la palabra reconociendo dígrafos (LL, CH, RR) como una sola ficha"""
        tokens, i, p = [], 0, palabra.upper()
        while i < len(p):
            if i + 1 < len(p) and p[i : i + 2] in ["LL", "CH", "RR"]:
                tokens.append(p[i : i + 2])
                i += 2
            else:
                tokens.append(p[i])
                i += 1
        return tokens

    def _obtener_bono_pos(self, f, c):
        """Devuelve el tipo de bono según la coordenada"""
        for tipo, coords in self.BONOS.items():
            if (f, c) in coords:
                return tipo
        return None

    def _cargar_diccionario(self, ruta):
        """Lee el archivo de palabras y lo carga en memoria"""
        ruta_abs = os.path.join(os.path.dirname(__file__), ruta)
        try:
            with open(ruta_abs, "r", encoding="utf-8") as f:
                return {self.normalizar(linea.strip()) for linea in f if linea.strip()}
        except:
            return {"CASA", "HOLA", "SOL", "PAPA", "MAMA", "GATO", "PERRO"}

    def _inicializar_bolsa(self):
        """Crea la bolsa de fichas con la distribución oficial española"""
        dist = {
            "A": 12,
            "E": 12,
            "O": 9,
            "I": 6,
            "S": 6,
            "N": 5,
            "R": 5,
            "U": 5,
            "L": 4,
            "T": 4,
            "D": 5,
            "G": 2,
            "C": 4,
            "B": 2,
            "M": 2,
            "P": 2,
            "H": 2,
            "F": 2,
            "V": 2,
            "Y": 1,
            "CH": 1,
            "Q": 1,
            "J": 1,
            "LL": 1,
            "Ñ": 1,
            "RR": 1,
            "X": 1,
            "Z": 1,
        }
        bolsa = [l for l, c in dist.items() for _ in range(c)]
        random.shuffle(bolsa)
        return bolsa

    def rellenar_atril(self, atril):
        """Toma fichas de la bolsa hasta completar 7 en el atril"""
        while len(atril) < 7 and self.bolsa:
            atril.append(self.bolsa.pop())

    def cambiar_letras(self, letras_viejas, es_usuario=True):
        """Ejecuta el canje de fichas devolviendo las usadas a la bolsa"""
        atril = self.atril_usuario if es_usuario else self.atril_cpu
        for letra in letras_viejas:
            if letra in atril:
                atril.remove(letra)
                self.bolsa.append(letra)
        random.shuffle(self.bolsa)
        self.rellenar_atril(atril)
        return True

    def validar_integridad(self, palabra, fila, col, direccion):
        """Árbitro: Verifica reglas de conexión, bordes y palabras resultantes"""
        tokens = self.tokenizar(palabra)
        tablero_vacio = all(
            self.grid[r][c]["letra"] is None for r in range(15) for c in range(15)
        )
        toca_existente = False
        letras_colocadas = 0

        # Validación de palabra extendida (Evitar "TATACA")
        df_inicio, dc_inicio = (fila - 1, col) if direccion == "V" else (fila, col - 1)
        prefijo = ""
        while (
            0 <= df_inicio < 15
            and 0 <= dc_inicio < 15
            and self.grid[df_inicio][dc_inicio]["letra"]
        ):
            prefijo = self.grid[df_inicio][dc_inicio]["letra"] + prefijo
            if direccion == "V":
                df_inicio -= 1
            else:
                dc_inicio -= 1

        df_fin, dc_fin = (
            (fila + len(tokens), col) if direccion == "V" else (fila, col + len(tokens))
        )
        sufijo = ""
        while (
            0 <= df_fin < 15 and 0 <= dc_fin < 15 and self.grid[df_fin][dc_fin]["letra"]
        ):
            sufijo += self.grid[df_fin][dc_fin]["letra"]
            if direccion == "V":
                df_fin += 1
            else:
                dc_fin += 1

        palabra_total = prefijo + palabra + sufijo
        if len(palabra_total) > len(palabra):
            if palabra_total not in self.diccionario:
                return False
            toca_existente = True

        # Validación de celdas ocupadas y cruces perpendiculares
        for i, letra in enumerate(tokens):
            f, c = fila + (i if direccion == "V" else 0), col + (
                i if direccion == "H" else 0
            )
            if not (0 <= f < 15 and 0 <= c < 15):
                return False
            if self.grid[f][c]["letra"] and self.grid[f][c]["letra"] != letra:
                return False

            if not self.grid[f][c]["letra"]:
                letras_colocadas += 1
                cruce = self._verificar_cruce(f, c, direccion, letra)
                if cruce:
                    if cruce not in self.diccionario:
                        return False
                    toca_existente = True
            else:
                toca_existente = True

            if tablero_vacio and f == 7 and c == 7:
                toca_existente = True

        return toca_existente and letras_colocadas > 0

    def _verificar_cruce(self, f, c, dir_principal, letra):
        """Busca palabras formadas perpendicularmente a la jugada principal"""
        d_perp = "V" if dir_principal == "H" else "H"
        palabra = [letra]
        pasos = [(-1, 0), (1, 0)] if d_perp == "V" else [(0, -1), (0, 1)]
        for df, dc in pasos:
            nf, nc = f + df, c + dc
            while 0 <= nf < 15 and 0 <= nc < 15 and self.grid[nf][nc]["letra"]:
                if df + dc < 0:
                    palabra.insert(0, self.grid[nf][nc]["letra"])
                else:
                    palabra.append(self.grid[nf][nc]["letra"])
                nf, nc = nf + df, nc + dc
        return "".join(palabra) if len(palabra) > 1 else None

    def ejecutar_jugada(self, palabra, f, c, d, es_usuario=True):
        """Procesa el movimiento, descuenta fichas y suma puntos si es válido"""
        p_norm = self.normalizar(palabra)
        if p_norm not in self.diccionario:
            return {"status": "error", "msj": "No existe."}
        if not self.validar_integridad(p_norm, f, c, d):
            return {"status": "error", "msj": "Inválida."}

        tokens = self.tokenizar(p_norm)
        atril = self.atril_usuario if es_usuario else self.atril_cpu
        temp_atril = list(atril)

        # Verificar disponibilidad de fichas
        for i, letra in enumerate(tokens):
            nf, nc = f + (i if d == "V" else 0), c + (i if d == "H" else 0)
            if not self.grid[nf][nc]["letra"]:
                if letra in temp_atril:
                    temp_atril.remove(letra)
                else:
                    return {"status": "error", "msj": f"No tienes {letra}"}

        puntos = self._calcular_puntos(tokens, f, c, d)

        # Colocación definitiva en el tablero
        for i, letra in enumerate(tokens):
            self.grid[f + (i if d == "V" else 0)][c + (i if d == "H" else 0)][
                "letra"
            ] = letra

        if es_usuario:
            self.puntos_usuario += puntos
            self.atril_usuario = temp_atril
            self.rellenar_atril(self.atril_usuario)
        else:
            self.puntos_cpu += puntos
            self.atril_cpu = temp_atril
            self.rellenar_atril(self.atril_cpu)

        return {"status": "success", "puntos": puntos}

    def _calcular_puntos(self, tokens, f, c, d):
        """Calcula el valor de la jugada aplicando bonos de letra y palabra"""
        p, m = 0, 1
        for i, letra in enumerate(tokens):
            nf, nc = f + (i if d == "V" else 0), c + (i if d == "H" else 0)
            v = self.VALORES_LETRAS.get(letra, 1)
            b = self.grid[nf][nc]["bono"]
            if b == "2L":
                v *= 2
            elif b == "3L":
                v *= 3
            elif b == "2P":
                m *= 2
            elif b == "3P":
                m *= 3
            p += v
        return p * m

    def jugada_ia(self):
        """Lógica de decisión de la CPU para buscar palabras o cambiar fichas"""
        tablero_vacio = all(
            self.grid[r][c]["letra"] is None for r in range(15) for c in range(15)
        )
        candidatas = [p for p in self.diccionario if 2 <= len(p) <= 6]
        random.shuffle(candidatas)

        if tablero_vacio:
            for p in candidatas:
                res = self.ejecutar_jugada(p, 7, 7 - (len(p) // 2), "H", False)
                if res["status"] == "success":
                    return {
                        "status": "success",
                        "accion": "palabra",
                        "palabra": p,
                        "puntos": res["puntos"],
                    }

        # Búsqueda de anclajes en el tablero
        anclas = [
            (f, c) for f in range(15) for c in range(15) if self.grid[f][c]["letra"]
        ]
        random.shuffle(anclas)
        for f, c in anclas[:15]:
            letra = self.grid[f][c]["letra"]
            for p in candidatas[:100]:
                if letra in p:
                    indices = [i for i, l in enumerate(self.tokenizar(p)) if l == letra]
                    for idx in indices:
                        for d in ["H", "V"]:
                            fi, ci = f - (idx if d == "V" else 0), c - (
                                idx if d == "H" else 0
                            )
                            res = self.ejecutar_jugada(p, fi, ci, d, False)
                            if res["status"] == "success":
                                return {
                                    "status": "success",
                                    "accion": "palabra",
                                    "palabra": p,
                                    "puntos": res["puntos"],
                                }

        # Si no encuentra palabra, cambia hasta 3 fichas
        fichas_cambio = random.sample(self.atril_cpu, min(len(self.atril_cpu), 3))
        self.cambiar_letras(fichas_cambio, es_usuario=False)
        return {"status": "success", "accion": "cambio", "msj": "CPU cambió fichas"}
