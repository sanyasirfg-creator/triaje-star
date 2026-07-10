import base64
import os
import random
import streamlit as st

st.set_page_config(page_title="Simulador de Triaje STAR", page_icon="🚑", layout="centered")

CARPETA_SONIDOS = "assets/sonidos"
SONIDOS_DISPONIBLES = ["caos.mp3", "incendio.mp3", "explosiones.mp3"]


def reproducir_audio_loop(nombre_archivo):
    """Incrusta un audio en loop. Se llama solo DESPUÉS de un clic del usuario
    (botón Comenzar), que es lo que los navegadores exigen para permitir audio."""
    ruta = os.path.join(CARPETA_SONIDOS, nombre_archivo)
    if not os.path.exists(ruta):
        st.warning(f"⚠️ No se encontró el archivo de sonido: {ruta}. Revisa que lo hayas subido a esa carpeta.")
        return
    with open(ruta, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <audio autoplay loop>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True,
    )

COLORES_HEX = {"verde": "#2ecc71", "amarillo": "#f1c40f", "rojo": "#e74c3c", "negro": "#2c3e50"}

CASOS = [
    {"nombre": "Mujer joven con corte superficial en la mano, camina sin dificultad",
     "consciente": True, "camina": True, "respira": True, "frecuencia_resp": 16,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.2, "obedece_ordenes": True},

    {"nombre": "Hombre con esguince de tobillo, camina cojeando pero se moviliza solo",
     "consciente": True, "camina": True, "respira": True, "frecuencia_resp": 18,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.0, "obedece_ordenes": True},

    {"nombre": "Hombre con fractura cerrada de fémur, no puede levantarse",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 22,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.8, "obedece_ordenes": True},

    {"nombre": "Mujer con quemaduras leves en ambos brazos, no puede caminar por el dolor",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 20,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": True},

    {"nombre": "Mujer embarazada con contracciones, estable, prefiere no moverse",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 18,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.3, "obedece_ordenes": True},

    {"nombre": "Hombre con dificultad respiratoria evidente, respira muy rápido",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 34,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": True},

    {"nombre": "Mujer con respiración muy lenta y superficial",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 8,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": True},

    {"nombre": "Hombre con palidez extrema y piel fría, pulso radial no palpable",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 22,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": False, "relleno_capilar": 3.0, "obedece_ordenes": True},

    {"nombre": "Mujer desorientada y agitada, no responde a órdenes simples",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 20,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": False},

    {"nombre": "Hombre con herida por arma blanca en abdomen, sangrado activo importante",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 24,
     "via_aerea_obstruida": False, "hemorragia_severa": True,
     "pulso_radial": True, "relleno_capilar": 1.8, "obedece_ordenes": True},

    {"nombre": "Mujer con amputación traumática de pierna y sangrado masivo",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 26,
     "via_aerea_obstruida": False, "hemorragia_severa": True,
     "pulso_radial": True, "relleno_capilar": 2.0, "obedece_ordenes": True},

    {"nombre": "Hombre atrapado bajo escombros, sin respiración, no responde tras liberar vía aérea",
     "consciente": False, "camina": False, "respira": False, "frecuencia_resp": 0,
     "via_aerea_obstruida": True, "hemorragia_severa": False,
     "pulso_radial": False, "relleno_capilar": 4.0, "obedece_ordenes": False},

    {"nombre": "Mujer inconsciente que no respiraba y mejora tras maniobra de apertura de vía aérea",
     "consciente": False, "camina": False, "respira": True, "frecuencia_resp": 32,
     "via_aerea_obstruida": True, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 2.0, "obedece_ordenes": False},

    {"nombre": "Hombre consciente pero muy confundido, no logra seguir instrucciones simples",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 20,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": False},

    {"nombre": "Mujer inconsciente en shock, piel fría y pulso débil",
     "consciente": False, "camina": False, "respira": True, "frecuencia_resp": 26,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": False, "relleno_capilar": 3.5, "obedece_ordenes": False},

    {"nombre": "Hombre mayor con fractura de cadera, no puede movilizarse pero está estable",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 18,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": True},

    {"nombre": "Mujer con herida abierta en tórax y dificultad para respirar",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 32,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.8, "obedece_ordenes": True},

    {"nombre": "Hombre con lesiones incompatibles con la vida, sin respiración pese a maniobras",
     "consciente": False, "camina": False, "respira": False, "frecuencia_resp": 0,
     "via_aerea_obstruida": True, "hemorragia_severa": False,
     "pulso_radial": False, "relleno_capilar": 4.0, "obedece_ordenes": False},

    {"nombre": "Mujer con crisis de ansiedad y taquicardia, pero camina y sigue instrucciones",
     "consciente": True, "camina": True, "respira": True, "frecuencia_resp": 22,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.0, "obedece_ordenes": True},

    {"nombre": "Hombre con múltiples heridas leves por esquirlas, estable, no se mueve por temor",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 20,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": True},
]


def clasificar_start(v):
    if v["hemorragia_severa"]:
        return "rojo", "Hemorragia severa que requiere control inmediato (X)"
    if v["consciente"] and v["camina"]:
        return "verde", "Camina por sus propios medios"
    if not v["respira"]:
        return "negro", "No respira, incluso tras despejar la vía aérea (A)"
    if v["frecuencia_resp"] > 30 or v["frecuencia_resp"] < 10:
        return "rojo", "Frecuencia respiratoria fuera de rango normal (R)"
    if not v["pulso_radial"] or v["relleno_capilar"] > 2:
        return "rojo", "Perfusión inadecuada: sin pulso radial o relleno capilar > 2s (P)"
    if not v["obedece_ordenes"]:
        return "rojo", "No obedece órdenes simples (M)"
    return "amarillo", "Estable, no camina, pero cumple R-P-M"


def generar_acciones(v, es_consciente):
    if es_consciente:
        return [
            ("¿Puede caminar?", lambda v: f"¿Puede caminar? → {'Sí' if v['camina'] else 'No'}"),
            ("¿Presenta hemorragia?", lambda v: f"Revisión de hemorragia → {'Sí, severa (X)' if v['hemorragia_severa'] else 'No se observa'}"),
            ("¿Cómo respira?", lambda v: f"Respiración (R) → {v['frecuencia_resp']} resp/min" if v["respira"] else "Respiración (R) → No respira"),
            ("¿Tiene pulso radial?", lambda v: f"Perfusión (P) → Pulso: {'Presente' if v['pulso_radial'] else 'Ausente'}, Relleno capilar: {v['relleno_capilar']}s"),
            ("¿Responde a órdenes?", lambda v: f"Estado mental (M) → {'Obedece' if v['obedece_ordenes'] else 'No obedece'}"),
        ]
    else:
        return [
            ("Controlar hemorragia (X)", lambda v: f"Hemorragia (X) → {'Severa, se controla' if v['hemorragia_severa'] else 'No se observa'}"),
            ("Despejar vía aérea (A)", lambda v: f"Vía aérea (A) → {'Obstruida, se despeja' if v['via_aerea_obstruida'] else 'Permeable'}"),
            ("Evaluar respiración (R)", lambda v: f"Respiración (R) → {v['frecuencia_resp']} resp/min" if v["respira"] else "Respiración (R) → No respira"),
            ("Evaluar perfusión (P)", lambda v: f"Perfusión (P) → Pulso: {'Presente' if v['pulso_radial'] else 'Ausente'}, Relleno capilar: {v['relleno_capilar']}s"),
            ("Evaluar estado mental (M)", lambda v: f"Estado mental (M) → {'Obedece' if v['obedece_ordenes'] else 'No obedece'}"),
        ]


def nueva_ronda():
    st.session_state.v = dict(random.choice(CASOS))
    st.session_state.es_consciente = st.session_state.v["consciente"]
    st.session_state.findings = []
    st.session_state.resultado = None


def registrar_hallazgo(funcion):
    texto = funcion(st.session_state.v)
    st.session_state.findings.append(texto)


def elegir_color(color_elegido):
    color_correcto, motivo = clasificar_start(st.session_state.v)
    acierto = color_elegido == color_correcto
    st.session_state.resultado = {
        "acierto": acierto,
        "color_elegido": color_elegido,
        "color_correcto": color_correcto,
        "motivo": motivo,
    }
    if "puntaje" not in st.session_state:
        st.session_state.puntaje = {"aciertos": 0, "total": 0}
    st.session_state.puntaje["total"] += 1
    if acierto:
        st.session_state.puntaje["aciertos"] += 1


# --- Inicialización de estado ---
if "iniciado" not in st.session_state:
    st.session_state.iniciado = False
if "sonido_random" not in st.session_state:
    st.session_state.sonido_random = random.choice(SONIDOS_DISPONIBLES)
if "puntaje" not in st.session_state:
    st.session_state.puntaje = {"aciertos": 0, "total": 0}

# --- Pantalla de inicio (necesaria para desbloquear el audio) ---
if not st.session_state.iniciado:
    st.title("🚑 Simulador de Triaje STAR")
    st.write("Evalúa a la víctima, registra hallazgos y asigna el color correcto según el protocolo X-A-R-P-M.")
    st.info("El sonido ambiente comienza al iniciar (los navegadores no permiten audio automático sin un clic previo).")
    if st.button("▶ Comenzar simulación", use_container_width=True):
        st.session_state.iniciado = True
        nueva_ronda()
        st.rerun()
    st.stop()

# --- UI del juego ---
reproducir_audio_loop(st.session_state.sonido_random)

st.title("🚑 Simulador de Triaje STAR")
st.caption("Evalúa a la víctima, registra hallazgos y asigna el color correcto según el protocolo X-A-R-P-M")

puntaje = st.session_state.puntaje
st.metric("Puntaje", f"{puntaje['aciertos']} / {puntaje['total']}")

v = st.session_state.v
es_consciente = st.session_state.es_consciente

st.subheader(v["nombre"])
st.write(f"**Estado:** {'Consciente' if es_consciente else 'Inconsciente'}")

if st.session_state.resultado is None:
    st.markdown("### Preguntas / Acciones disponibles")
    acciones = generar_acciones(v, es_consciente)

    cols = st.columns(2)
    for i, (texto, funcion) in enumerate(acciones):
        with cols[i % 2]:
            if st.button(texto, key=f"accion_{i}", use_container_width=True):
                registrar_hallazgo(funcion)
                st.rerun()

    if st.session_state.findings:
        st.markdown("### Hallazgos registrados")
        for f in st.session_state.findings:
            st.write(f"🔎 {f}")

    st.markdown("### Asignar color de triaje")
    color_cols = st.columns(4)
    colores = ["verde", "amarillo", "rojo", "negro"]
    for i, c in enumerate(colores):
        with color_cols[i]:
            if st.button(c.upper(), key=f"color_{c}", use_container_width=True):
                elegir_color(c)
                st.rerun()

else:
    r = st.session_state.resultado
    if r["acierto"]:
        st.success("✅ ¡Correcto!")
    else:
        st.error("❌ Incorrecto")

    st.write(f"**Tu elección:** {r['color_elegido'].upper()}")
    st.markdown(
        f"**Color correcto:** <span style='color:{COLORES_HEX[r['color_correcto']]}; font-weight:bold'>{r['color_correcto'].upper()}</span>",
        unsafe_allow_html=True,
    )
    st.write(f"**Motivo:** {r['motivo']}")

    if st.button("Siguiente víctima ▶", use_container_width=True):
        nueva_ronda()
        st.rerun()
