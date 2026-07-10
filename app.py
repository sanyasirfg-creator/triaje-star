import random
import streamlit as st

st.set_page_config(page_title="Simulador de Triaje STAR", page_icon="🚑", layout="centered")

COLORES_HEX = {"verde": "#2ecc71", "amarillo": "#f1c40f", "rojo": "#e74c3c", "negro": "#2c3e50"}

CASOS = [
    {"nombre": "Hombre joven con herida superficial en brazo",
     "consciente": True, "camina": True, "respira": True, "frecuencia_resp": 18,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": True},

    {"nombre": "Mujer con fractura de tobillo, no puede caminar",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 20,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.8, "obedece_ordenes": True},

    {"nombre": "Hombre pálido y sudoroso, no puede caminar",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 24,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": False, "relleno_capilar": 3.0, "obedece_ordenes": True},

    {"nombre": "Mujer confusa, no responde órdenes claras",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 22,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 1.5, "obedece_ordenes": False},

    {"nombre": "Hombre con sangrado abundante en el muslo",
     "consciente": True, "camina": False, "respira": True, "frecuencia_resp": 26,
     "via_aerea_obstruida": False, "hemorragia_severa": True,
     "pulso_radial": True, "relleno_capilar": 2.0, "obedece_ordenes": True},

    {"nombre": "Hombre inconsciente que no respiraba y mejora al abrir vía aérea",
     "consciente": False, "camina": False, "respira": True, "frecuencia_resp": 32,
     "via_aerea_obstruida": True, "hemorragia_severa": False,
     "pulso_radial": True, "relleno_capilar": 2.0, "obedece_ordenes": False},

    {"nombre": "Mujer inconsciente sin respiración tras despejar vía aérea",
     "consciente": False, "camina": False, "respira": False, "frecuencia_resp": 0,
     "via_aerea_obstruida": True, "hemorragia_severa": False,
     "pulso_radial": False, "relleno_capilar": 4.0, "obedece_ordenes": False},

    {"nombre": "Hombre inconsciente, respira normal pero sin pulso radial",
     "consciente": False, "camina": False, "respira": True, "frecuencia_resp": 20,
     "via_aerea_obstruida": False, "hemorragia_severa": False,
     "pulso_radial": False, "relleno_capilar": 3.5, "obedece_ordenes": False},

    {"nombre": "Hombre inconsciente con hemorragia severa en la pierna",
     "consciente": False, "camina": False, "respira": True, "frecuencia_resp": 22,
     "via_aerea_obstruida": False, "hemorragia_severa": True,
     "pulso_radial": True, "relleno_capilar": 2.0, "obedece_ordenes": False},
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
if "v" not in st.session_state:
    nueva_ronda()
if "puntaje" not in st.session_state:
    st.session_state.puntaje = {"aciertos": 0, "total": 0}

# --- UI ---
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
