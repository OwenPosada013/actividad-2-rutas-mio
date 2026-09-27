# ============================================================
# Sistema inteligente de rutas del MIO (Cali)
# Actividad 2. Búsqueda y sistemas basados en reglas
#
# Owen Esteban Posada Rivas
# José Andrés Murillo Manco
# Inteligencia Artificial
# Corporación Universitaria Iberoamericana
# Docente: Sandra Isabel Rodríguez Bautista
# ============================================================
#
# Qué hace este programa
# ----------------------
# Tiene una base pequeña de conocimiento sobre el MIO.
# Con reglas del tipo "si pasa esto, entonces se puede hacer esto",
# arma los caminos entre una estación y otra.
# Después compara esos caminos y se queda con el que menos tarda.
#
# El transbordo (bajarse y cambiar de ruta) suma 5 minutos,
# porque también se pierde tiempo esperando el otro bus.
#
# Los minutos no son el horario oficial de Metro Cali.
# Son tiempos de ejemplo para poder probar el ejercicio.

TIEMPO_TRANSBORDO = 5

# ------------------------------------------------------------
# BASE DE CONOCIMIENTO
# Cada ruta guarda las estaciones en orden.
# El número es cuántos minutos se gastan hasta la siguiente.
# La última estación lleva 0 porque ahí se acaba el tramo.
# ------------------------------------------------------------

RUTAS = {
    "T31": {
        "nombre": "Troncal Calle 5 y centro",
        "paradas": [
            ("Universidades", 4),
            ("Univalle", 5),
            ("Capri", 6),
            ("Unidad Deportiva", 5),
            ("Estadio", 4),
            ("Manzana del Saber", 5),
            ("San Bosco", 4),
            ("Torre de Cali", 5),
            ("Versalles", 7),
            ("Terminal Menga", 8),
            ("Chiminangos", 0),
        ],
    },
    "E21": {
        "nombre": "Expreso sur-norte",
        "paradas": [
            ("Universidades", 8),
            ("Capri", 10),
            ("San Bosco", 12),
            ("Terminal Menga", 9),
            ("Chiminangos", 0),
        ],
    },
    "T47": {
        "nombre": "Troncal Oriental",
        "paradas": [
            ("Andrés Sanín", 5),
            ("Calipso", 5),
            ("Nuevo Latir", 6),
            ("Amanecer", 8),
            ("San Bosco", 0),
        ],
    },
    # Enlace simplificado. Sirve para comparar un viaje directo
    # contra otro que cambia de ruta y, aun así, puede tardar menos.
    "P21": {
        "nombre": "Pretroncal sur-oriente",
        "paradas": [
            ("Universidades", 55),
            ("Andrés Sanín", 0),
        ],
    },
}


def normalizar(texto):
    """Deja el nombre en minúsculas y sin tildes, para comparar."""
    import unicodedata

    limpio = texto.strip().lower()
    sin_tildes = "".join(
        letra
        for letra in unicodedata.normalize("NFD", limpio)
        if unicodedata.category(letra) != "Mn"
    )
    return sin_tildes


def estaciones_disponibles():
    """Lista de estaciones, sin repetir, en el orden en que aparecen."""
    vistas = []
    for datos in RUTAS.values():
        for estacion, _minutos in datos["paradas"]:
            if estacion not in vistas:
                vistas.append(estacion)
    return vistas


def nombre_oficial(texto):
    """Devuelve el nombre bien escrito, o None si no está en la base."""
    buscado = normalizar(texto)
    for estacion in estaciones_disponibles():
        if normalizar(estacion) == buscado:
            return estacion
    return None


# ------------------------------------------------------------
# REGLAS
# La base dice qué estaciones tiene cada ruta.
# Estas reglas convierten eso en viajes que sí se pueden hacer.
# ------------------------------------------------------------

def regla_conexion_directa():
    """
    Regla 1.
    Si dos estaciones van seguidas en la misma ruta,
    entonces se puede viajar entre ellas sin bajarse.
    El bus se toma en los dos sentidos.
    """
    conexiones = {estacion: [] for estacion in estaciones_disponibles()}

    for codigo, datos in RUTAS.items():
        paradas = datos["paradas"]
        for i in range(len(paradas) - 1):
            origen, minutos = paradas[i]
            destino = paradas[i + 1][0]
            conexiones[origen].append(
                {"destino": destino, "ruta": codigo, "minutos": minutos}
            )
            conexiones[destino].append(
                {"destino": origen, "ruta": codigo, "minutos": minutos}
            )
    return conexiones


def regla_es_transbordo(ruta_actual, ruta_nueva):
    """
    Regla 2.
    Si ya vas en una ruta y el siguiente tramo es de otra,
    entonces hay transbordo y se suman 5 minutos.
    Al subir al primer bus no cuenta como transbordo.
    """
    if ruta_actual is None:
        return False
    return ruta_actual != ruta_nueva


def regla_no_repetir(estacion, visitadas):
    """
    Regla 3.
    Si la estación ya está en el camino,
    entonces no se vuelve a pasar por ahí.
    Así se evitan vueltas infinitas.
    """
    return estacion not in visitadas


CONEXIONES = regla_conexion_directa()


# ------------------------------------------------------------
# BÚSQUEDA
# Parecido al ejemplo de clase: se va armando el camino
# estación por estación. La diferencia es que aquí no nos
# quedamos con el primer camino. Guardamos los que sirvan
# y elegimos el de menor tiempo.
# ------------------------------------------------------------

def buscar_caminos(origen, destino):
    encontrados = []

    def recorrer(actual, ruta_actual, camino, visitadas, tiempo, transbordos, pasos):
        if actual == destino:
            encontrados.append(
                {
                    "camino": list(camino),
                    "tiempo": tiempo,
                    "transbordos": transbordos,
                    "pasos": list(pasos),
                }
            )
            return

        for opcion in CONEXIONES[actual]:
            siguiente = opcion["destino"]
            if not regla_no_repetir(siguiente, visitadas):
                continue

            hay_transbordo = regla_es_transbordo(ruta_actual, opcion["ruta"])
            extra = TIEMPO_TRANSBORDO if hay_transbordo else 0
            pasos.append(
                {
                    "desde": actual,
                    "hasta": siguiente,
                    "ruta": opcion["ruta"],
                    "minutos": opcion["minutos"],
                    "transbordo": hay_transbordo,
                }
            )
            visitadas.add(siguiente)
            recorrer(
                siguiente,
                opcion["ruta"],
                camino + [siguiente],
                visitadas,
                tiempo + opcion["minutos"] + extra,
                transbordos + (1 if hay_transbordo else 0),
                pasos,
            )
            visitadas.remove(siguiente)
            pasos.pop()

    recorrer(origen, None, [origen], {origen}, 0, 0, [])
    encontrados.sort(key=lambda camino: (camino["tiempo"], camino["transbordos"]))
    return encontrados


def elegir_mejor(caminos):
    """La mejor ruta es la que menos minutos suma, espera incluida."""
    if not caminos:
        return None
    return caminos[0]


def texto_ruta(camino):
    return " -> ".join(camino["camino"])


def rutas_del_camino(camino):
    """Códigos de ruta, sin repetir cuando el bus sigue siendo el mismo."""
    usadas = []
    for paso in camino["pasos"]:
        if not usadas or usadas[-1] != paso["ruta"]:
            usadas.append(paso["ruta"])
    return usadas


def explicar_pasos(camino):
    lineas = []
    for i, paso in enumerate(camino["pasos"]):
        nombre = RUTAS[paso["ruta"]]["nombre"]
        if paso["transbordo"]:
            lineas.append(
                f"  Regla 2. En {paso['desde']} te bajas y cambias a la "
                f"{paso['ruta']} ({nombre}) hacia {paso['hasta']}. "
                f"El tramo son {paso['minutos']} min y la espera del "
                f"transbordo suma {TIEMPO_TRANSBORDO} min."
            )
        elif i == 0:
            lineas.append(
                f"  Regla 1. Tomas la {paso['ruta']} ({nombre}), "
                f"de {paso['desde']} a {paso['hasta']} "
                f"({paso['minutos']} min)."
            )
        else:
            lineas.append(
                f"  Regla 1. Sigues en la {paso['ruta']} ({nombre}), "
                f"de {paso['desde']} a {paso['hasta']} "
                f"({paso['minutos']} min)."
            )
    return "\n".join(lineas)


def describir_consulta(origen, destino):
    """Arma el texto con el resultado, listo para imprimir o guardar."""
    lineas = []
    lineas.append("=" * 62)
    lineas.append(f"Origen:  {origen}")
    lineas.append(f"Destino: {destino}")
    lineas.append("-" * 62)

    origen_ok = nombre_oficial(origen)
    destino_ok = nombre_oficial(destino)

    if origen_ok is None or destino_ok is None:
        faltan = []
        if origen_ok is None:
            faltan.append(origen)
        if destino_ok is None:
            faltan.append(destino)
        lineas.append(
            "No encontré esta estación en la base: " + ", ".join(faltan) + "."
        )
        lineas.append("Estaciones que sí están cargadas:")
        for estacion in estaciones_disponibles():
            lineas.append(f"  - {estacion}")
        lineas.append("=" * 62)
        return "\n".join(lineas)

    if origen_ok == destino_ok:
        lineas.append(f"Ya estás en {origen_ok}. No necesitas tomar el MIO.")
        lineas.append("=" * 62)
        return "\n".join(lineas)

    caminos = buscar_caminos(origen_ok, destino_ok)
    if not caminos:
        lineas.append("No existe una ruta entre esas dos estaciones.")
        lineas.append("=" * 62)
        return "\n".join(lineas)

    mejor = elegir_mejor(caminos)
    lineas.append(f"Caminos revisados: {len(caminos)}")
    lineas.append("")
    lineas.append("Opciones, de la más corta a la más larga:")
    mostrar = caminos[:6]
    for i, camino in enumerate(mostrar, start=1):
        marca = "  <- mejor" if camino is mejor else ""
        rutas = ", ".join(rutas_del_camino(camino))
        lineas.append(
            f"  {i}. {camino['tiempo']} min, "
            f"{camino['transbordos']} transbordo(s), ruta(s) {rutas}{marca}"
        )
        lineas.append(f"     {texto_ruta(camino)}")
    if len(caminos) > len(mostrar):
        lineas.append(f"  ... y {len(caminos) - len(mostrar)} camino(s) más, más lentos.")

    lineas.append("")
    lineas.append("Mejor ruta encontrada:")
    lineas.append(f"  {texto_ruta(mejor)}")
    lineas.append(f"  Tiempo estimado: {mejor['tiempo']} minutos")
    lineas.append(f"  Transbordos: {mejor['transbordos']}")
    lineas.append(f"  Estaciones: {len(mejor['camino'])}")
    lineas.append("")
    lineas.append("Cómo se aplicaron las reglas:")
    lineas.append(explicar_pasos(mejor))
    lineas.append("=" * 62)
    return "\n".join(lineas)


def ejecutar_pruebas():
    """Pruebas fijas. Sirven para el informe y para el video."""
    pruebas = [
        (
            "Prueba 1. Viaje corto en el sur",
            "Universidades",
            "Capri",
            "Hay dos formas sin transbordo. Debe ganar la E21, porque tarda 8 minutos y la T31 tarda 9.",
        ),
        (
            "Prueba 2. Del sur al norte, por la troncal o por el expreso",
            "Universidades",
            "Chiminangos",
            "Las dos rutas principales no piden transbordo. Debe ganar la E21, que hace menos paradas.",
        ),
        (
            "Prueba 3. Un transbordo puede convenir",
            "Universidades",
            "Andrés Sanín",
            "La P21 va directo, pero tarda 55 minutos. Cambiar en San Bosco suma espera y aun así queda en menos tiempo.",
        ),
        (
            "Prueba 4. La persona ya está en la estación",
            "Estadio",
            "Estadio",
            "No debe armar un viaje. El origen y el destino son el mismo.",
        ),
        (
            "Prueba 5. Una estación que no está en la base",
            "Universidades",
            "Paso del Comercio",
            "Debe avisar que esa estación no está cargada y mostrar la lista.",
        ),
        (
            "Prueba 6. Misma consulta, escrita distinto",
            "  terminal menga ",
            "chiminangos",
            "Debe entender el nombre aunque vaya en minúsculas y con espacios.",
        ),
    ]

    bloques = []
    bloques.append("SISTEMA INTELIGENTE DE RUTAS DEL MIO")
    bloques.append("Estaciones disponibles:")
    bloques.append("  " + " | ".join(estaciones_disponibles()))
    bloques.append("")
    bloques.append(
        "Criterio: gana el camino con menos minutos. "
        f"Cada transbordo suma {TIEMPO_TRANSBORDO} minutos."
    )
    bloques.append("")

    for titulo, origen, destino, esperado in pruebas:
        bloques.append(titulo)
        bloques.append(f"Qué esperamos: {esperado}")
        bloques.append(describir_consulta(origen, destino))
        bloques.append("")

    return "\n".join(bloques)


if __name__ == "__main__":
    print(ejecutar_pruebas())
