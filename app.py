import base64
import os
import random
import time
import streamlit as st

st.set_page_config(page_title="Simulador de Triaje STAR", page_icon="🚑", layout="centered")

CARPETA_SONIDOS = "assets/sonidos"
SONIDOS_DISPONIBLES = ["caos.mp3", "incendio.mp3", "explosiones.mp3"]

COLORES_HEX = {"verde": "#2ecc71", "amarillo": "#f1c40f", "rojo": "#e74c3c", "negro": "#2c3e50"}
RANGO_SEVERIDAD = {"verde": 0, "amarillo": 1, "rojo": 2, "negro": 3}

UMBRAL_TIEMPO_SEGUNDOS = 30
UMBRAL_APROBACION = 7  # sobre 12 casos (~58%, similar proporción a la versión anterior)


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


# Cada caso guarda el ESTADO REAL del paciente (ground truth) por separado de lo
# que el jugador puede "medir mal" si no hace las maniobras correctas primero.
CASOS = [
    {"nombre": "Hombre camina gritando y llorando en medio del humo de un incendio",
     "entorno": "🔥 Incendio activo: hay humo denso en el ambiente",
     "consciente": True, "camina": True, "histerico": True, "sangre_visible": False,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 22, "ambiente_frio": False, "relleno_capilar_real": 1.2,
     "pulso_radial_real": True, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": True, "barrera": None, "requiere_maniobra_critica": None},

    {"nombre": "Mujer con sangrado abundante en el cuero cabelludo, camina normalmente",
     "entorno": None,
     "consciente": True, "camina": True, "histerico": False, "sangre_visible": True,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 18, "ambiente_frio": False, "relleno_capilar_real": 1.0,
     "pulso_radial_real": True, "tipo_hemorragia": "leve",
     "obedece_ordenes_real": True, "barrera": None, "requiere_maniobra_critica": None},

    {"nombre": "Hombre inconsciente, encontrado boca arriba, sin heridas visibles",
     "entorno": None,
     "consciente": False, "camina": False, "histerico": False, "sangre_visible": False,
     "via_aerea_posicional": True, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 18, "ambiente_frio": False, "relleno_capilar_real": 1.5,
     "pulso_radial_real": True, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": False, "barrera": None, "requiere_maniobra_critica": "via_aerea"},

    {"nombre": "Mujer atrapada en el vehículo, sangre coagulada obstruye la boca, inconsciente",
     "entorno": "🚗 Vehículo accidentado",
     "consciente": False, "camina": False, "histerico": False, "sangre_visible": True,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": True,
     "frecuencia_resp_real": 28, "ambiente_frio": False, "relleno_capilar_real": 1.8,
     "pulso_radial_real": True, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": False, "barrera": None, "requiere_maniobra_critica": "via_aerea"},

    {"nombre": "Hombre no puede caminar tras la caída; hace mucho frío en el lugar",
     "entorno": "❄️ Ambiente muy frío",
     "consciente": True, "camina": False, "histerico": False, "sangre_visible": False,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 20, "ambiente_frio": True, "relleno_capilar_real": 1.6,
     "pulso_radial_real": True, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": True, "barrera": None, "requiere_maniobra_critica": None},

    {"nombre": "Mujer con hemorragia severa en el brazo, consciente, grita pidiendo ayuda",
     "entorno": None,
     "consciente": True, "camina": False, "histerico": True, "sangre_visible": True,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 24, "ambiente_frio": False, "relleno_capilar_real": 1.8,
     "pulso_radial_real": True, "tipo_hemorragia": "exanguinante",
     "obedece_ordenes_real": True, "barrera": None, "requiere_maniobra_critica": "hemorragia"},

    {"nombre": "Hombre no responde en español a las preguntas, parece confundido",
     "entorno": None,
     "consciente": True, "camina": False, "histerico": False, "sangre_visible": False,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 20, "ambiente_frio": False, "relleno_capilar_real": 1.3,
     "pulso_radial_real": True, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": True, "barrera": "idioma", "requiere_maniobra_critica": None},

    {"nombre": "Mujer no reacciona a los llamados verbales, posible pérdida auditiva",
     "entorno": None,
     "consciente": True, "camina": False, "histerico": False, "sangre_visible": False,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 19, "ambiente_frio": False, "relleno_capilar_real": 1.4,
     "pulso_radial_real": True, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": True, "barrera": "sordera", "requiere_maniobra_critica": None},

    {"nombre": "Mujer con respiración muy acelerada por inhalación de humo, no puede caminar",
     "entorno": "🔥 Incendio activo",
     "consciente": True, "camina": False, "histerico": False, "sangre_visible": False,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 38, "ambiente_frio": False, "relleno_capilar_real": 1.5,
     "pulso_radial_real": True, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": True, "barrera": None, "requiere_maniobra_critica": None},

    {"nombre": "Hombre en paro respiratorio, no reacciona",
     "entorno": None,
     "consciente": False, "camina": False, "histerico": False, "sangre_visible": False,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 0, "ambiente_frio": False, "relleno_capilar_real": 4.0,
     "pulso_radial_real": False, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": False, "barrera": None, "requiere_maniobra_critica": "via_aerea"},

    {"nombre": "Mujer con fractura cerrada de tobillo, no puede caminar, ambiente tranquilo",
     "entorno": None,
     "consciente": True, "camina": False, "histerico": False, "sangre_visible": False,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 18, "ambiente_frio": False, "relleno_capilar_real": 1.4,
     "pulso_radial_real": True, "tipo_hemorragia": "ninguna",
     "obedece_ordenes_real": True, "barrera": None, "requiere_maniobra_critica": None},

    {"nombre": "Hombre con amputación parcial de mano, mucha sangre, consciente y asustado",
     "entorno": None,
     "consciente": True, "camina": False, "histerico": True, "sangre_visible": True,
     "via_aerea_posicional": False, "via_aerea_cuerpo_extrano": False,
     "frecuencia_resp_real": 26, "ambiente_frio": False, "relleno_capilar_real": 1.6,
     "pulso_radial_real": True, "tipo_hemorragia": "exanguinante",
     "obedece_ordenes_real": True, "barrera": None, "requiere_maniobra_critica": "hemorragia"},
]

ACCIONES_HEMORRAGIA = [
    ("Aplicar torniquete / control agresivo", "exanguinante"),
    ("Cubrir con gasa y presión directa", "leve"),
    ("No requiere intervención", "ninguna"),
]


def clasificar_start(v):
    """Clasifica SIEMPRE según el estado real del paciente (ground truth)."""
    if v["tipo_hemorragia"] == "exanguinante":
        return "rojo", "Hemorragia exanguinante sin control (prioridad X)"
    if v["consciente"] and v["camina"]:
        return "verde", "Camina por sus propios medios"
    if v["frecuencia_resp_real"] == 0:
        return "negro", "No respira, incluso después de intentar despejar la vía aérea"
    if v["frecuencia_resp_real"] > 30 or v["frecuencia_resp_real"] < 10:
        return "rojo", "Frecuencia respiratoria real fuera de rango (R)"
    if not v["pulso_radial_real"] or v["relleno_capilar_real"] > 2:
        return "rojo", "Perfusión real inadecuada: sin pulso o relleno capilar > 2s (P)"
    if not v["obedece_ordenes_real"]:
        return "rojo", "No obedece órdenes según evaluación motora (M)"
    return "amarillo", "Estable, no camina, pero cumple R-P-M reales"


def leer_respiracion(v, maniobra_hecha):
    obstruccion = v["via_aerea_posicional"] or v["via_aerea_cuerpo_extrano"]
    if obstruccion and not maniobra_hecha:
        return 0, True
    return v["frecuencia_resp_real"], False


def leer_perfusion(v, calentado):
    if v["ambiente_frio"] and not calentado:
        return round(v["relleno_capilar_real"] + 1.6, 1)
    return v["relleno_capilar_real"]


def leer_mental_verbal(v):
    if v["barrera"] == "idioma":
        return "incoherente_idioma"
    if v["barrera"] == "sordera":
        return "sin_respuesta_sordera"
    return "coherente" if v["obedece_ordenes_real"] else "incoherente"


def generar_mensaje_sesgo(v, color_elegido, color_correcto_final):
    if color_elegido == color_correcto_final:
        return None
    if RANGO_SEVERIDAD[color_elegido] > RANGO_SEVERIDAD[color_correcto_final]:
        if v["histerico"] or v["sangre_visible"]:
            return "Sobre-triaje: parece que la dramatización de la escena (gritos, sangre visible) pesó más que los signos vitales reales."
        return "Sobre-triaje: clasificaste con más gravedad de la que indicaban los signos reales."
    else:
        if not v["consciente"] and not v["sangre_visible"]:
            return "Sub-triaje: la ausencia de heridas visibles no garantiza estabilidad, sobre todo en un paciente inconsciente."
        return "Sub-triaje: clasificaste con menos gravedad de la que indicaban los signos reales."


def agregar_hallazgo(texto):
    st.session_state.findings.append(texto)


def iniciar_juego():
    st.session_state.mazo = random.sample(CASOS, len(CASOS))
    st.session_state.puntaje = {"aciertos": 0, "total": 0}
    st.session_state.decisiones = {"aciertos": 0, "total": 0}
    st.session_state.terminado = False
    st.session_state.sonido_random = random.choice(SONIDOS_DISPONIBLES)
    nueva_ronda()


def nueva_ronda():
    if not st.session_state.mazo:
        st.session_state.terminado = True
        return
    st.session_state.v = st.session_state.mazo.pop()
    st.session_state.findings = []
    st.session_state.resultado = None
    st.session_state.maniobra_hecha = False
    st.session_state.calentado = False
    st.session_state.hemorragia_controlada = False
    st.session_state.decision_hemorragia = None
    st.session_state.camina_revelado = None
    st.session_state.tiempo_inicio = time.time()


def tomar_decision_hemorragia(valor_elegido):
    v = st.session_state.v
    correcta = v["tipo_hemorragia"]
    acierto = valor_elegido == correcta
    st.session_state.decision_hemorragia = {"acierto": acierto, "correcta": correcta}
    st.session_state.decisiones["total"] += 1
    if acierto:
        st.session_state.decisiones["aciertos"] += 1
    if valor_elegido == "exanguinante" and correcta == "exanguinante":
        st.session_state.hemorragia_controlada = True


def finalizar_ronda(color_elegido):
    v = st.session_state.v
    elapsed = time.time() - st.session_state.tiempo_inicio
    tardanza = elapsed > UMBRAL_TIEMPO_SEGUNDOS

    requiere = v["requiere_maniobra_critica"]
    if requiere == "via_aerea":
        completado = st.session_state.maniobra_hecha
    elif requiere == "hemorragia":
        completado = st.session_state.hemorragia_controlada
    else:
        completado = True

    deterioro = tardanza or not completado
    color_base, motivo_base = clasificar_start(v)
    color_final = color_base
    motivo_deterioro = None

    if deterioro and color_base == "amarillo":
        color_final = "rojo"
        motivo_deterioro = "tardanza en decidir" if tardanza else "no completaste la maniobra crítica requerida"
    elif deterioro and color_base == "rojo":
        color_final = "negro"
        motivo_deterioro = "tardanza en decidir" if tardanza else "no completaste la maniobra crítica requerida"

    acierto = color_elegido == color_final
    sesgo = generar_mensaje_sesgo(v, color_elegido, color_final)

    st.session_state.puntaje["total"] += 1
    if acierto:
        st.session_state.puntaje["aciertos"] += 1

    st.session_state.resultado = {
        "color_elegido": color_elegido, "color_base": color_base, "color_final": color_final,
        "motivo_base": motivo_base, "motivo_deterioro": motivo_deterioro,
        "acierto": acierto, "elapsed": elapsed, "tardanza": tardanza, "sesgo": sesgo,
    }


# --- Inicialización ---
if "iniciado" not in st.session_state:
    st.session_state.iniciado = False

if not st.session_state.iniciado:
    st.title("🚑 Simulador de Triaje STAR")
    st.write("Evalúa a cada víctima bajo presión: el tiempo corre, el entorno puede engañarte, y tus acciones (o tu inacción) afectan al paciente.")
    st.write(f"Vas a enfrentar **{len(CASOS)} casos**, cada uno una sola vez.")
    st.info("El sonido ambiente comienza al iniciar (los navegadores no permiten audio automático sin un clic previo).")
    if st.button("▶ Comenzar simulación", use_container_width=True):
        st.session_state.iniciado = True
        iniciar_juego()
        st.rerun()
    st.stop()

if st.session_state.terminado:
    aciertos = st.session_state.puntaje["aciertos"]
    total = st.session_state.puntaje["total"]
    decis = st.session_state.decisiones
    aprobado = aciertos >= UMBRAL_APROBACION
    color_nota = "#2ecc71" if aprobado else "#e74c3c"
    texto_nota = "APROBADO" if aprobado else "REPROBADO"

    st.title("🏁 Resultado final")
    st.markdown(
        f"""<div style='background-color:{color_nota}; padding:30px; border-radius:12px; text-align:center;'>
        <h1 style='color:white; margin:0;'>{aciertos} / {total}</h1>
        <h2 style='color:white; margin:0;'>{texto_nota}</h2></div>""",
        unsafe_allow_html=True,
    )
    st.write("")
    st.write(f"Umbral de aprobación: **{UMBRAL_APROBACION} o más aciertos**.")
    if decis["total"] > 0:
        st.write(f"Decisiones de hemorragia acertadas: **{decis['aciertos']} / {decis['total']}**.")
    if st.button("🔁 Jugar de nuevo", use_container_width=True):
        iniciar_juego()
        st.rerun()
    st.stop()

reproducir_audio_loop(st.session_state.sonido_random)

st.title("🚑 Simulador de Triaje STAR")
casos_restantes = len(st.session_state.mazo) + 1
st.caption(f"Caso {len(CASOS) - casos_restantes + 1} de {len(CASOS)}")

puntaje = st.session_state.puntaje
st.metric("Puntaje", f"{puntaje['aciertos']} / {puntaje['total']}")

v = st.session_state.v
st.subheader(v["nombre"])
if v["entorno"]:
    st.caption(v["entorno"])
st.write(f"**Estado:** {'Consciente' if v['consciente'] else 'Inconsciente'}")

if st.session_state.resultado is None:

    if v["consciente"]:
        st.markdown("### 🚶 Movilidad")
        if st.session_state.camina_revelado is None:
            if st.button("¿Puede moverse por sí mismo?"):
                st.session_state.camina_revelado = v["camina"]
                agregar_hallazgo(f"Movilidad → {'Se moviliza solo' if v['camina'] else 'No puede moverse solo'}")
                st.rerun()
        else:
            st.write(f"🔎 Movilidad → {'Se moviliza solo' if v['camina'] else 'No puede moverse solo'}")

    st.markdown("### 🫁 Vía aérea y respiración")
    col1, col2 = st.columns(2)
    with col1:
        etiqueta = "✅ Maniobra realizada" if st.session_state.maniobra_hecha else "Maniobra de apertura de vía aérea"
        if st.button(etiqueta, disabled=st.session_state.maniobra_hecha, key="btn_maniobra"):
            st.session_state.maniobra_hecha = True
            agregar_hallazgo("Se realizó maniobra de apertura / despeje de vía aérea")
            st.rerun()
    with col2:
        if st.button("Evaluar respiración (contar RPM)", key="btn_resp"):
            valor, _ = leer_respiracion(v, st.session_state.maniobra_hecha)
            if valor == 0:
                agregar_hallazgo("Respiración → No se percibe respiración")
            else:
                agregar_hallazgo(f"Respiración → {valor} resp/min")
            st.rerun()

    st.markdown("### 🩸 Perfusión")
    col3, col4 = st.columns(2)
    with col3:
        if v["ambiente_frio"]:
            etiqueta_ab = "✅ Paciente abrigado" if st.session_state.calentado else "Abrigar al paciente"
            if st.button(etiqueta_ab, disabled=st.session_state.calentado, key="btn_abrigar"):
                st.session_state.calentado = True
                agregar_hallazgo("Se abrigó al paciente")
                st.rerun()
    with col4:
        if st.button("Evaluar perfusión (pulso / relleno capilar)", key="btn_perf"):
            relleno = leer_perfusion(v, st.session_state.calentado)
            agregar_hallazgo(f"Perfusión → Pulso: {'Presente' if v['pulso_radial_real'] else 'Ausente'}, Relleno capilar: {relleno}s")
            st.rerun()

    st.markdown("### 🆘 El paciente sangra. ¿Qué acción sigues?")
    if st.session_state.decision_hemorragia is None:
        cols_h = st.columns(len(ACCIONES_HEMORRAGIA))
        for i, (texto, valor) in enumerate(ACCIONES_HEMORRAGIA):
            with cols_h[i]:
                if st.button(texto, key=f"hem_{i}", use_container_width=True):
                    tomar_decision_hemorragia(valor)
                    st.rerun()
    else:
        d = st.session_state.decision_hemorragia
        if d["acierto"]:
            st.success("✅ Decisión correcta")
        else:
            correcta_texto = next(t for t, val in ACCIONES_HEMORRAGIA if val == d["correcta"])
            st.error(f"❌ Decisión incorrecta. Lo adecuado era: '{correcta_texto}'")

    st.markdown("### 🧠 Estado mental")
    col5, col6 = st.columns(2)
    with col5:
        if st.button("Ordena: 'Aprieta mi mano'", key="btn_motor"):
            resultado_motor = v["obedece_ordenes_real"]
            agregar_hallazgo(f"Orden motora → {'Aprieta con fuerza' if resultado_motor else 'No responde al estímulo'}")
            st.rerun()
    with col6:
        if st.button("Pregunta: '¿Qué día es hoy?'", key="btn_verbal"):
            r = leer_mental_verbal(v)
            textos = {
                "coherente": "Responde correctamente y con coherencia",
                "incoherente": "No logra responder con coherencia",
                "incoherente_idioma": "Responde en otro idioma, no parece entender la pregunta",
                "sin_respuesta_sordera": "No reacciona al estímulo verbal",
            }
            agregar_hallazgo(f"Pregunta verbal → {textos[r]}")
            st.rerun()

    if st.session_state.findings:
        st.markdown("### 🔎 Hallazgos registrados")
        for f in st.session_state.findings:
            st.write(f"- {f}")

    st.markdown("### Asignar color de triaje")
    color_cols = st.columns(4)
    for i, c in enumerate(["verde", "amarillo", "rojo", "negro"]):
        with color_cols[i]:
            if st.button(c.upper(), key=f"color_{c}", use_container_width=True):
                finalizar_ronda(c)
                st.rerun()

else:
    r = st.session_state.resultado
    st.success("✅ ¡Correcto!") if r["acierto"] else st.error("❌ Incorrecto")

    st.write(f"**Tu elección:** {r['color_elegido'].upper()}")
    st.markdown(
        f"**Clasificación correcta en este momento:** <span style='color:{COLORES_HEX[r['color_final']]}; font-weight:bold'>{r['color_final'].upper()}</span>",
        unsafe_allow_html=True,
    )
    st.write(f"**Motivo base:** {r['motivo_base']}")

    if r["color_base"] != r["color_final"]:
        st.warning(f"⚠️ El paciente se agravó de {r['color_base'].upper()} a {r['color_final'].upper()} porque: {r['motivo_deterioro']}.")

    st.write(f"⏱️ Tiempo empleado: {r['elapsed']:.0f}s" + (" — superó el umbral de 30s" if r["tardanza"] else ""))

    if r["sesgo"]:
        st.warning(r["sesgo"])

    etiqueta_boton = "Siguiente víctima ▶" if st.session_state.mazo else "Ver resultado final 🏁"
    if st.button(etiqueta_boton, use_container_width=True):
        nueva_ronda()
        st.rerun()
