import base64
import os
import random
import streamlit as st

st.set_page_config(page_title="Simulador de Triaje START", page_icon="🚑", layout="centered")

CARPETA_SONIDOS = "assets/sonidos"
SONIDOS_DISPONIBLES = ["caos.mp3", "incendio.mp3", "explosiones.mp3"]

COLORES_HEX = {"verde": "#2ecc71", "amarillo": "#f1c40f", "rojo": "#e74c3c", "negro": "#2c3e50"}
RANGO_PRIORIDAD = {"verde": 1, "amarillo": 2, "rojo": 3, "negro": 4}

PRESUPUESTO_INICIAL = 30
COSTO_ACCION = 2
UMBRAL_PRECISION = 2  # 2 acciones RELEVANTES o menos = bono de precisión

PUNTOS_CORRECTO = 10
PUNTOS_SUBTRIAJE = -10
PUNTOS_SOBRETRIAJE = -5
BONO_PRECISION = 5
PENALIDAD_SIN_ABRIR_VIA = -2

UMBRAL_APROBACION_PCT = 0.6


def reproducir_audio_loop(nombre_archivo):
    ruta = os.path.join(CARPETA_SONIDOS, nombre_archivo)
    if not os.path.exists(ruta):
        st.warning(f"⚠️ No se encontró el archivo de sonido: {ruta}.")
        return
    with open(ruta, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f"""<audio autoplay loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>""",
        unsafe_allow_html=True,
    )


def barra_presupuesto(restante, total=PRESUPUESTO_INICIAL):
    restante_mostrado = max(0, restante)
    pct = restante_mostrado / total * 100
    color = "#2ecc71" if restante_mostrado > 15 else ("#f1c40f" if restante_mostrado > 5 else "#e74c3c")
    st.markdown(
        f"""
        <div style='background:#333;border-radius:8px;overflow:hidden;height:22px;width:100%;'>
            <div style='background:{color};width:{pct}%;height:100%;'></div>
        </div>
        <p style='text-align:center;margin:4px 0 0 0;'>⏱️ Presupuesto de tiempo restante: {restante_mostrado}s</p>
        """,
        unsafe_allow_html=True,
    )


# Campos nuevos por caso:
#   mecanismo_lesion      -> texto narrativo (siempre presente, solo informativo)
#   hemorragia_oculta     -> bool, si True hay algo que solo aparece al "Exponer"
#   descripcion_oculta    -> texto que se revela al exponer (o None si no aplica)
CASOS = [
    {"nombre": "La víctima camina hacia usted quejándose de dolor en el brazo, con un vendaje improvisado",
     "mecanismo_lesion": "Se golpeó el brazo contra una reja al escapar corriendo",
     "hemorragia_oculta": False, "descripcion_oculta": None,
     "consciente": True, "camina": True, "via_aerea_obstruida": False,
     "frecuencia_resp_real": 18, "pulso_radial_real": True, "relleno_capilar_real": 1.0,
     "obedece_ordenes_real": True, "respira_real": True},

    {"nombre": "Víctima tendida en el suelo, grita histéricamente de dolor mientras sostiene su pierna",
     "mecanismo_lesion": "Tropezó y cayó de su propia altura sobre concreto",
     "hemorragia_oculta": False, "descripcion_oculta": None,
     "consciente": True, "camina": False, "via_aerea_obstruida": False,
     "frecuencia_resp_real": 20, "pulso_radial_real": True, "relleno_capilar_real": 1.2,
     "obedece_ordenes_real": True, "respira_real": True},

    {"nombre": "Víctima en completo silencio, tendida boca arriba, sin heridas visibles",
     "mecanismo_lesion": "Fue encontrada así tras el colapso parcial de una pared",
     "hemorragia_oculta": False, "descripcion_oculta": None,
     "consciente": False, "camina": False, "via_aerea_obstruida": True,
     "frecuencia_resp_real": 34, "pulso_radial_real": True, "relleno_capilar_real": 1.5,
     "obedece_ordenes_real": False, "respira_real": True},

    {"nombre": "Víctima con sangrado moderado en la pierna, no puede levantarse, se queja de dolor",
     "mecanismo_lesion": "Un fragmento metálico le cortó la pierna al derrumbarse un estante",
     "hemorragia_oculta": False, "descripcion_oculta": None,
     "consciente": True, "camina": False, "via_aerea_obstruida": False,
     "frecuencia_resp_real": 24, "pulso_radial_real": True, "relleno_capilar_real": 1.5,
     "obedece_ordenes_real": True, "respira_real": True},

    {"nombre": "Víctima inconsciente, sin respuesta a estímulos, piel pálida",
     "mecanismo_lesion": "Fue impactada por un objeto pesado que cayó desde altura",
     "hemorragia_oculta": True, "descripcion_oculta": "Bajo la ropa hay una herida punzante en el abdomen, con signos de sangrado interno",
     "consciente": False, "camina": False, "via_aerea_obstruida": False,
     "frecuencia_resp_real": 26, "pulso_radial_real": False, "relleno_capilar_real": 3.5,
     "obedece_ordenes_real": False, "respira_real": True},

    {"nombre": "Víctima grita pidiendo ayuda con mucha sangre en su ropa, pero se pone de pie y camina hacia la salida",
     "mecanismo_lesion": "Un vidrio le cortó superficialmente el cuero cabelludo, zona muy vascularizada",
     "hemorragia_oculta": False, "descripcion_oculta": None,
     "consciente": True, "camina": True, "via_aerea_obstruida": False,
     "frecuencia_resp_real": 22, "pulso_radial_real": True, "relleno_capilar_real": 1.0,
     "obedece_ordenes_real": True, "respira_real": True},

    {"nombre": "Víctima tendida bajo escombros, completamente inmóvil y silenciosa",
     "mecanismo_lesion": "Quedó atrapada bajo una losa durante varios minutos",
     "hemorragia_oculta": False, "descripcion_oculta": None,
     "consciente": False, "camina": False, "via_aerea_obstruida": True,
     "frecuencia_resp_real": 0, "pulso_radial_real": False, "relleno_capilar_real": 4.0,
     "obedece_ordenes_real": False, "respira_real": False},

    {"nombre": "Víctima consciente, no puede caminar por una fractura de tobillo, tranquila y colaboradora",
     "mecanismo_lesion": "Se torció el tobillo al bajar corriendo unas escaleras",
     "hemorragia_oculta": False, "descripcion_oculta": None,
     "consciente": True, "camina": False, "via_aerea_obstruida": False,
     "frecuencia_resp_real": 18, "pulso_radial_real": True, "relleno_capilar_real": 1.3,
     "obedece_ordenes_real": True, "respira_real": True},

    {"nombre": "Víctima con respiración muy agitada y rápida, no puede moverse, muy angustiada",
     "mecanismo_lesion": "Estuvo expuesta a humo denso durante varios minutos",
     "hemorragia_oculta": False, "descripcion_oculta": None,
     "consciente": True, "camina": False, "via_aerea_obstruida": False,
     "frecuencia_resp_real": 34, "pulso_radial_real": True, "relleno_capilar_real": 1.2,
     "obedece_ordenes_real": True, "respira_real": True},

    {"nombre": "Víctima inmóvil, no responde al hablarle, con pulso débil y piel fría",
     "mecanismo_lesion": "Fue encontrada junto a un vehículo volcado, mecanismo no muy claro",
     "hemorragia_oculta": True, "descripcion_oculta": "Al levantar la ropa se descubre una herida profunda en el costado, con sangrado activo moderado",
     "consciente": False, "camina": False, "via_aerea_obstruida": False,
     "frecuencia_resp_real": 20, "pulso_radial_real": False, "relleno_capilar_real": 3.0,
     "obedece_ordenes_real": False, "respira_real": True},
]


def clasificar(v):
    if v["consciente"] and v["camina"]:
        return "verde", "Camina por sus propios medios"
    if not v["respira_real"]:
        return "negro", "No respira, incluso tras abrir la vía aérea"
    if v["frecuencia_resp_real"] > 30:
        return "rojo", "Respira a más de 30 rpm"
    if not v["pulso_radial_real"] or v["relleno_capilar_real"] > 2:
        return "rojo", "Pulso radial ausente o relleno capilar mayor a 2 segundos"
    if not v["obedece_ordenes_real"]:
        return "rojo", "No sigue órdenes sencillas"
    return "amarillo", "Sigue órdenes sencillas y el RPM está estable"


def leer_respiracion(v, via_abierta):
    if v["via_aerea_obstruida"] and not via_abierta:
        return 0, True
    return v["frecuencia_resp_real"], False


def iniciar_juego():
    st.session_state.mazo = random.sample(CASOS, len(CASOS))
    st.session_state.puntos_totales = 0
    st.session_state.puntos_maximos = len(CASOS) * PUNTOS_CORRECTO
    st.session_state.terminado = False
    st.session_state.sonido_random = random.choice(SONIDOS_DISPONIBLES)
    nueva_ronda()


def nueva_ronda():
    if not st.session_state.mazo:
        st.session_state.terminado = True
        return
    st.session_state.v = st.session_state.mazo.pop()
    st.session_state.presupuesto = PRESUPUESTO_INICIAL
    st.session_state.acciones_relevantes = 0  # cuenta solo R-P-M, no mecanismo/exposición/trampa
    st.session_state.via_abierta = False
    st.session_state.hallazgos = []
    st.session_state.resultado = None


def usar_accion(costo, texto_hallazgo, relevante=True):
    st.session_state.presupuesto -= costo
    if relevante:
        st.session_state.acciones_relevantes += 1
    st.session_state.hallazgos.append(texto_hallazgo)


def elegir_color(color_elegido):
    v = st.session_state.v
    color_correcto, motivo = clasificar(v)

    if color_elegido == color_correcto:
        tipo = "correcto"
        puntos = PUNTOS_CORRECTO
        if st.session_state.acciones_relevantes <= UMBRAL_PRECISION:
            puntos += BONO_PRECISION
    elif RANGO_PRIORIDAD[color_elegido] < RANGO_PRIORIDAD[color_correcto]:
        tipo = "subtriaje"
        puntos = PUNTOS_SUBTRIAJE
    else:
        tipo = "sobretriaje"
        puntos = PUNTOS_SOBRETRIAJE

    penalidad_via = False
    if v["via_aerea_obstruida"] and not st.session_state.via_abierta:
        puntos += PENALIDAD_SIN_ABRIR_VIA
        penalidad_via = True

    st.session_state.puntos_totales += puntos

    st.session_state.resultado = {
        "color_elegido": color_elegido, "color_correcto": color_correcto, "motivo": motivo,
        "tipo": tipo, "puntos": puntos, "penalidad_via": penalidad_via,
        "acciones_relevantes": st.session_state.acciones_relevantes,
    }


# --- Inicio ---
if "iniciado" not in st.session_state:
    st.session_state.iniciado = False

if not st.session_state.iniciado:
    st.title("🚑 Simulador de Triaje START")
    st.write("Investiga cada víctima con los botones de evaluación, y clasifícala según R-P-M. Cuidado: no todos los botones son útiles.")
    st.write(f"Vas a enfrentar **{len(CASOS)} casos**, cada uno una sola vez.")
    st.info("El sonido ambiente comienza al iniciar (los navegadores no permiten audio automático sin un clic previo).")
    if st.button("▶ Comenzar simulación", use_container_width=True):
        st.session_state.iniciado = True
        iniciar_juego()
        st.rerun()
    st.stop()

# --- Pantalla final ---
if st.session_state.terminado:
    puntos = st.session_state.puntos_totales
    maximo = st.session_state.puntos_maximos
    pct = puntos / maximo if maximo else 0
    aprobado = pct >= UMBRAL_APROBACION_PCT
    color_nota = "#2ecc71" if aprobado else "#e74c3c"
    texto_nota = "APROBADO" if aprobado else "REPROBADO"

    st.title("🏁 Resultado final")
    st.markdown(
        f"""<div style='background-color:{color_nota}; padding:30px; border-radius:12px; text-align:center;'>
        <h1 style='color:white; margin:0;'>{puntos} / {maximo} pts</h1>
        <h2 style='color:white; margin:0;'>{texto_nota}</h2></div>""",
        unsafe_allow_html=True,
    )
    st.write("")
    st.write(f"Umbral de aprobación: **{int(UMBRAL_APROBACION_PCT*100)}%** del puntaje máximo.")
    if st.button("🔁 Jugar de nuevo", use_container_width=True):
        iniciar_juego()
        st.rerun()
    st.stop()

# --- Juego ---
reproducir_audio_loop(st.session_state.sonido_random)

st.title("🚑 Simulador de Triaje START")
casos_restantes = len(st.session_state.mazo) + 1
st.caption(f"Caso {len(CASOS) - casos_restantes + 1} de {len(CASOS)} — Puntaje: {st.session_state.puntos_totales} pts")

v = st.session_state.v
st.subheader(v["nombre"])
barra_presupuesto(st.session_state.presupuesto)

if st.session_state.resultado is None:
    st.markdown("### Evaluación R-P-M")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        if st.button("Abrir Vía Aérea", disabled=st.session_state.via_abierta, use_container_width=True):
            st.session_state.via_abierta = True
            texto = "Vía aérea despejada" if v["via_aerea_obstruida"] else "Vía aérea ya estaba permeable"
            usar_accion(COSTO_ACCION, f"Abrir vía aérea → {texto}")
            st.rerun()

    with col2:
        if st.button("Contar Respiraciones", use_container_width=True):
            valor, _ = leer_respiracion(v, st.session_state.via_abierta)
            texto = "No se detecta respiración" if valor == 0 else f"{valor} rpm"
            usar_accion(COSTO_ACCION, f"Respiración → {texto}")
            st.rerun()

    with col3:
        if st.button("Tomar Pulso / Llenado Capilar", use_container_width=True):
            texto = f"Pulso radial: {'Presente' if v['pulso_radial_real'] else 'Ausente'}, Relleno capilar: {v['relleno_capilar_real']}s"
            usar_accion(COSTO_ACCION, f"Perfusión → {texto}")
            st.rerun()

    with col4:
        if st.button("Hablar / Dar Orden", use_container_width=True):
            texto = "Sigue la orden correctamente" if v["obedece_ordenes_real"] else "No logra seguir la orden"
            usar_accion(COSTO_ACCION, f"Estado mental → {texto}")
            st.rerun()

    st.markdown("### Evaluación complementaria")
    col5, col6, col7 = st.columns(3)

    with col5:
        if st.button("Preguntar Mecanismo de Lesión", use_container_width=True):
            usar_accion(COSTO_ACCION, f"Mecanismo de lesión → {v['mecanismo_lesion']}", relevante=False)
            st.rerun()

    with col6:
        if st.button("Exponer y Buscar Lesiones Ocultas", use_container_width=True):
            if v["hemorragia_oculta"]:
                texto = v["descripcion_oculta"]
            else:
                texto = "No se encuentran lesiones adicionales relevantes"
            usar_accion(COSTO_ACCION, f"Exposición → {texto}", relevante=False)
            st.rerun()

    with col7:
        if st.button("Tomar Temperatura Corporal", use_container_width=True):
            usar_accion(COSTO_ACCION, "Temperatura → 36.5°C (dato no relevante para clasificar con START)", relevante=False)
            st.rerun()

    if st.session_state.hallazgos:
        st.markdown("### 🔎 Hallazgos")
        for h in st.session_state.hallazgos:
            st.write(f"- {h}")

    st.markdown("### Clasificación")
    color_cols = st.columns(4)
    for i, c in enumerate(["verde", "amarillo", "rojo", "negro"]):
        with color_cols[i]:
            if st.button(c.upper(), key=f"color_{c}", use_container_width=True):
                elegir_color(c)
                st.rerun()

else:
    r = st.session_state.resultado
    if r["tipo"] == "correcto":
        st.success("✅ Clasificación correcta")
    elif r["tipo"] == "subtriaje":
        st.error("🔴 Sub-triaje: le diste MENOS prioridad de la que necesitaba. En la realidad, esta demora podría costarle la vida.")
    else:
        st.warning("🟡 Sobre-triaje: le diste MÁS prioridad de la que necesitaba. Esto puede saturar recursos que un paciente más crítico necesita.")

    st.write(f"**Tu elección:** {r['color_elegido'].upper()}")
    st.markdown(
        f"**Color correcto:** <span style='color:{COLORES_HEX[r['color_correcto']]}; font-weight:bold'>{r['color_correcto'].upper()}</span>",
        unsafe_allow_html=True,
    )
    st.write(f"**Motivo:** {r['motivo']}")
    st.write(f"**Acciones R-P-M usadas:** {r['acciones_relevantes']}" + (" 🎯 Bono de precisión aplicado" if r["tipo"] == "correcto" and r["acciones_relevantes"] <= UMBRAL_PRECISION else ""))
    if r["penalidad_via"]:
        st.warning("⚠️ No intentaste abrir la vía aérea antes de clasificar.")
    st.write(f"**Puntos obtenidos en este caso:** {r['puntos']:+d}")

    etiqueta_boton = "Siguiente víctima ▶" if st.session_state.mazo else "Ver resultado final 🏁"
    if st.button(etiqueta_boton, use_container_width=True):
        nueva_ronda()
        st.rerun()
