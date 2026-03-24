"""
╔══════════════════════════════════════════════════════════╗
║          🏆  LA PEÑA DE LA QUINIELA  🏆                  ║
║    Votación integrada · Resultados · Rankings            ║
╚══════════════════════════════════════════════════════════╝

INSTALACIÓN:
    pip install streamlit pandas plotly

EJECUTAR:
    streamlit run app.py

PUBLICAR ONLINE (para que tus amigos voten desde su móvil):
    1. Crea cuenta gratuita en https://share.streamlit.io
    2. Sube app.py a GitHub (también votos.json e historico.json vacíos)
    3. Despliega con un clic — te dan una URL pública
"""

import streamlit as st
import pandas as pd
import json
import os
import re
from datetime import datetime
from collections import Counter

try:
    import plotly.express as px
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

# ══════════════════════════════════════════════════════════════════════════════
#  ARCHIVOS DE DATOS
# ══════════════════════════════════════════════════════════════════════════════
VOTOS_PATH     = "votos.json"       # Votos de la jornada actual
HISTORICO_PATH = "historico.json"   # Acumulado de la temporada
PARTIDOS_PATH  = "partidos.json"    # Nombres de los partidos de la jornada

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE STREAMLIT
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="⚽ La Peña de la Quiniela",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Bebas Neue', cursive !important; letter-spacing: 1.5px; }

section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d2137 0%, #1565c0 100%) !important;
}
section[data-testid="stSidebar"] * { color: #e3f2fd !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

.aviso-banner {
    background: linear-gradient(90deg, #1565c0, #0d47a1);
    color: white !important;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  FUNCIONES DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def cargar_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cargar_votos():
    return cargar_json(VOTOS_PATH, {"jornada": 1, "votos": []})

def guardar_votos(data):
    guardar_json(VOTOS_PATH, data)

def cargar_partidos():
    default = [f"Partido {i}" for i in range(1, 16)]
    return cargar_json(PARTIDOS_PATH, default)

def guardar_partidos(lista):
    guardar_json(PARTIDOS_PATH, lista)

def cargar_historico():
    return cargar_json(HISTORICO_PATH, {"jornadas": []})

def guardar_historico(data):
    guardar_json(HISTORICO_PATH, data)

# ══════════════════════════════════════════════════════════════════════════════
#  FUNCIONES DE LÓGICA
# ══════════════════════════════════════════════════════════════════════════════

def signo_mas_votado(votos):
    limpio = [str(v).strip().upper() for v in votos if str(v).strip() not in ("", "?")]
    if not limpio:
        return "?"
    c = Counter(limpio)
    orden = ["1", "X", "2"]
    return max(c, key=lambda k: (c[k], -orden.index(k) if k in orden else -99))

def resultado_a_signo(val):
    val = str(val).strip()
    m = re.match(r"(\d+)\s*[-–]\s*(\d+)", val)
    if m:
        l, v = int(m.group(1)), int(m.group(2))
        return "1" if l > v else ("X" if l == v else "2")
    return val.upper()

def normalizar(val):
    return str(val).strip().upper()

def calcular_aciertos(signos_persona, resultados):
    total = 0
    for i in range(min(len(signos_persona), len(resultados))):
        r = normalizar(resultados[i])
        s = normalizar(signos_persona[i])
        if r not in ("", "?") and r == s:
            total += 1
    return total

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — NAVEGACIÓN
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚽ LA PEÑA")
    st.markdown("---")
    seccion = st.radio(
        "Sección:",
        ["✍️ Votar", "🗓️ Gestión de Jornada", "📊 Resultados & Aciertos", "🏆 Ranking Histórico"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    datos_votos_sb = cargar_votos()
    st.markdown(f"**Jornada activa:** {datos_votos_sb.get('jornada', 1)}")
    st.markdown(f"**Votos recibidos:** {len(datos_votos_sb.get('votos', []))} 🗳️")
    st.markdown("---")
    st.caption("Hecho con ❤️ y Streamlit")

# ══════════════════════════════════════════════════════════════════════════════
#  CABECERA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<h1 style='text-align:center; font-size:2.8rem; margin-bottom:0;'>
    🏆 LA PEÑA DE LA QUINIELA
</h1>
<p style='text-align:center; color:#888; margin-top:0;'>
    Vota · Compara · Compite
</p>
<hr style='margin-bottom:1.5rem;'>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 1 — FORMULARIO DE VOTO
# ══════════════════════════════════════════════════════════════════════════════
if seccion == "✍️ Votar":

    datos_votos = cargar_votos()
    partidos    = cargar_partidos()
    jornada     = datos_votos.get("jornada", 1)

    st.header(f"✍️ Formulario de Voto — Jornada {jornada}")
    st.markdown(
        "<div class='aviso-banner'>📱 Comparte la URL de esta app con tus amigos "
        "para que voten desde su móvil o PC.</div>",
        unsafe_allow_html=True,
    )

    # ── Nombre ──────────────────────────────────────────────────────────────
    nombre = st.text_input(
        "👤 Tu nombre *",
        placeholder="Escribe tu nombre aquí...",
        key="input_nombre",
    )

    st.markdown("---")
    st.subheader("⚽ Elige tu pronóstico para cada partido")
    st.caption(
        "Partidos 1–14: elige **1** (gana local), **X** (empate) o **2** (gana visitante).  \n"
        "Partido 15: escribe el marcador exacto (ej: **2-1**) o un signo (1/X/2)."
    )

    signos = []

    # ── Partidos 1–14 ────────────────────────────────────────────────────────
    for i in range(14):
        nombre_partido = partidos[i] if i < len(partidos) else f"Partido {i+1}"
        col_num, col_partido, col_voto = st.columns([0.5, 3.5, 3])
        with col_num:
            st.markdown(
                f"<div style='background:#1565c0;color:white;border-radius:50%;"
                f"width:32px;height:32px;display:flex;align-items:center;"
                f"justify-content:center;font-weight:700;font-size:.9rem;"
                f"margin-top:8px;'>{i+1}</div>",
                unsafe_allow_html=True,
            )
        with col_partido:
            st.markdown(
                f"<div style='padding-top:10px;font-weight:600;'>{nombre_partido}</div>",
                unsafe_allow_html=True,
            )
        with col_voto:
            signo = st.radio(
                f"p{i+1}",
                options=["1", "X", "2"],
                horizontal=True,
                index=None,
                label_visibility="collapsed",
                key=f"voto_{i}",
            )
        signos.append(signo)

    # ── Partido 15 ───────────────────────────────────────────────────────────
    st.markdown("---")
    nombre_p15 = partidos[14] if len(partidos) >= 15 else "Partido 15"
    col_num15, col_p15, col_v15 = st.columns([0.5, 3.5, 3])
    with col_num15:
        st.markdown(
            "<div style='background:#ffd600;color:#1a1a1a;border-radius:50%;"
            "width:32px;height:32px;display:flex;align-items:center;"
            "justify-content:center;font-weight:700;font-size:.85rem;"
            "margin-top:8px;'>15</div>",
            unsafe_allow_html=True,
        )
    with col_p15:
        st.markdown(
            f"<div style='padding-top:10px;font-weight:600;'>⭐ {nombre_p15} "
            f"<span style='color:#888;font-size:.8rem;'>(Pleno al 15)</span></div>",
            unsafe_allow_html=True,
        )
    with col_v15:
        signo_p15 = st.text_input(
            "p15",
            placeholder="Ej: 2-1  ó  1  ó  X",
            label_visibility="collapsed",
            key="voto_14",
        )
    signos.append(signo_p15.strip() if signo_p15 else None)

    # ── Botón enviar ─────────────────────────────────────────────────────────
    st.markdown("---")
    enviar = st.button("🗳️ Enviar mi voto", use_container_width=True, type="primary")

    if enviar:
        errores = []
        if not nombre.strip():
            errores.append("⚠️ Debes escribir tu nombre.")
        vacios_14 = [i + 1 for i, s in enumerate(signos[:14]) if s is None]
        if vacios_14:
            errores.append(f"⚠️ Falta tu pronóstico en los partidos: {', '.join(map(str, vacios_14))}")
        if not signos[14]:
            errores.append("⚠️ Falta el resultado del Partido 15 (Pleno al 15).")

        if errores:
            for e in errores:
                st.error(e)
        else:
            datos_votos = cargar_votos()
            votos_actuales = datos_votos.get("votos", [])

            signos_norm = [normalizar(s) if s else "?" for s in signos[:14]]
            signos_norm.append(signos[14].strip() if signos[14] else "?")

            idx_existente = next(
                (i for i, v in enumerate(votos_actuales)
                 if v["nombre"].strip().lower() == nombre.strip().lower()),
                None,
            )
            entrada = {
                "nombre": nombre.strip(),
                "signos": signos_norm,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            if idx_existente is not None:
                votos_actuales[idx_existente] = entrada
                st.success(f"✅ Voto de **{nombre}** actualizado correctamente.")
            else:
                votos_actuales.append(entrada)
                st.success(
                    f"✅ ¡Voto de **{nombre}** registrado! "
                    f"Ya han votado {len(votos_actuales)} personas."
                )

            datos_votos["votos"] = votos_actuales
            guardar_votos(datos_votos)
            st.balloons()

    # ── Quién ha votado ya ───────────────────────────────────────────────────
    datos_votos = cargar_votos()
    votantes = [v["nombre"] for v in datos_votos.get("votos", [])]
    if votantes:
        st.info(f"🗳️ Han votado **{len(votantes)}** persona(s): {', '.join(votantes)}")


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 2 — GESTIÓN DE JORNADA
# ══════════════════════════════════════════════════════════════════════════════
elif seccion == "🗓️ Gestión de Jornada":
    st.header("🗓️ Gestión de Jornada")
    st.info("⚙️ Esta sección es para el administrador de la peña.")

    datos_votos = cargar_votos()
    partidos    = cargar_partidos()

    # ── Número de jornada ────────────────────────────────────────────────────
    st.subheader("1️⃣ Jornada activa")
    col_j1, col_j2 = st.columns([2, 1])
    with col_j1:
        nueva_jornada = st.number_input(
            "Número de jornada",
            min_value=1, max_value=42,
            value=datos_votos.get("jornada", 1),
            step=1,
        )
    with col_j2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Actualizar jornada", use_container_width=True):
            datos_votos["jornada"] = int(nueva_jornada)
            guardar_votos(datos_votos)
            st.success(f"✅ Jornada actualizada a {nueva_jornada}.")

    st.warning(
        "⚠️ **Antes de iniciar una nueva jornada:** guarda los resultados "
        "en el Histórico (sección 'Resultados & Aciertos') y luego usa "
        "'🗑️ Limpiar votos' aquí abajo."
    )

    # ── Nombres de partidos ──────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("2️⃣ Nombres de los 15 partidos")
    st.caption(
        "Escribe el nombre de cada enfrentamiento. "
        "Aparecerán en el formulario de voto de tus amigos."
    )

    nuevos_partidos = []
    # Mostramos en dos columnas para no ocupar tanto espacio
    col_izq, col_der = st.columns(2)
    for i in range(15):
        val_actual = partidos[i] if i < len(partidos) else f"Partido {i+1}"
        emoji = "⭐" if i == 14 else f"{i+1}."
        with col_izq if i % 2 == 0 else col_der:
            nuevo = st.text_input(
                f"{emoji} Partido {i+1}",
                value=val_actual,
                key=f"nombre_p_{i}",
            )
        nuevos_partidos.append(nuevo.strip() if nuevo.strip() else val_actual)

    if st.button("💾 Guardar nombres de partidos", use_container_width=True, type="primary"):
        guardar_partidos(nuevos_partidos)
        st.success("✅ Guardado. Los partidos ya aparecen actualizados en el formulario de voto.")

    # ── Limpiar votos ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("3️⃣ Nueva jornada — Limpiar votos")
    n_votos = len(datos_votos.get("votos", []))
    st.markdown(f"Votos actuales en memoria: **{n_votos}**")

    confirmar = st.checkbox("✅ Confirmo que quiero borrar todos los votos de la jornada actual")
    if st.button("🗑️ Limpiar votos para nueva jornada", use_container_width=True, disabled=not confirmar):
        datos_votos["votos"] = []
        guardar_votos(datos_votos)
        st.success("✅ Votos eliminados. La peña puede empezar a votar la nueva jornada.")

    # ── Ver votos actuales ───────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("4️⃣ Votos recibidos hasta ahora")
    votos = datos_votos.get("votos", [])
    if not votos:
        st.info("Aún no hay votos para esta jornada.")
    else:
        filas = []
        for v in votos:
            fila = {"Nombre": v["nombre"], "Fecha": v.get("fecha", "")}
            for i, s in enumerate(v.get("signos", [])):
                clave = partidos[i] if i < len(partidos) else f"P{i+1}"
                fila[clave] = s
            filas.append(fila)
        st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 3 — RESULTADOS & ACIERTOS
# ══════════════════════════════════════════════════════════════════════════════
elif seccion == "📊 Resultados & Aciertos":

    datos_votos = cargar_votos()
    partidos    = cargar_partidos()
    jornada     = datos_votos.get("jornada", 1)
    votos       = datos_votos.get("votos", [])

    st.header(f"📊 Resultados & Aciertos — Jornada {jornada}")

    if not votos:
        st.warning("⚠️ Aún no hay votos registrados para esta jornada.")
        st.stop()

    # ── Introducir resultados reales ─────────────────────────────────────────
    st.subheader("1️⃣ Introduce los resultados reales")
    st.caption(
        "Partidos 1–14: escribe **1**, **X** o **2**.  \n"
        "Partido 15: escribe el marcador (ej: **2-1**) o directamente 1/X/2."
    )

    if "resultados_reales" not in st.session_state:
        st.session_state["resultados_reales"] = [""] * 15

    cols_res = st.columns(5)
    resultados_introducidos = []
    for i in range(15):
        col = cols_res[i % 5]
        nombre_p = partidos[i] if i < len(partidos) else f"Partido {i+1}"
        partes = nombre_p.split(" - ")
        etiqueta = f"P{i+1}: {partes[0][:9]}" if partes else f"P{i+1}"
        with col:
            r = st.text_input(
                etiqueta,
                value=st.session_state["resultados_reales"][i],
                key=f"res_{i}",
                placeholder="1/X/2" if i < 14 else "2-1",
            )
        resultados_introducidos.append(r.strip().upper() if r.strip() else "")

    st.session_state["resultados_reales"] = resultados_introducidos
    completados = sum(1 for r in resultados_introducidos if r)
    st.info(f"📌 Resultados introducidos: **{completados} / 15**")

    if completados == 0:
        st.info("👆 Introduce al menos un resultado para ver los aciertos.")
        st.stop()

    # Normalizar resultados
    resultados_norm = []
    for i, r in enumerate(resultados_introducidos):
        if i == 14:
            resultados_norm.append(resultado_a_signo(r) if r else "")
        else:
            resultados_norm.append(r)

    # ── Quiniela de la Peña ──────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🤝 Quiniela de la Peña (voto mayoritario)")

    quiniela_peña = []
    for i in range(15):
        todos_signos = [
            normalizar(v["signos"][i]) if i < len(v.get("signos", [])) else "?"
            for v in votos
        ]
        quiniela_peña.append(signo_mas_votado(todos_signos))

    filas_peña = []
    for i in range(15):
        vp = quiniela_peña[i]
        rr = resultados_norm[i]
        if rr and rr != "?":
            estado = "✅ Acierto" if vp == rr else "❌ Fallo"
        else:
            estado = "⏳ Pendiente"
        filas_peña.append({
            "Nº": i + 1,
            "Partido": partidos[i] if i < len(partidos) else f"Partido {i+1}",
            "Voto Peña": vp,
            "Resultado Real": rr if rr else "—",
            "Estado": estado,
        })

    df_peña = pd.DataFrame(filas_peña)
    aciertos_peña = sum(1 for r in filas_peña if "Acierto" in r["Estado"])
    st.dataframe(df_peña, hide_index=True, use_container_width=True)
    st.metric("🤝 Aciertos de la Peña", f"{aciertos_peña} / {completados}")

    # ── Tabla individual ──────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Aciertos individuales")

    filas_ind = []
    for v in votos:
        signos_v = [
            normalizar(v["signos"][i]) if i < len(v.get("signos", [])) else "?"
            for i in range(15)
        ]
        aciertos = calcular_aciertos(signos_v, resultados_norm)
        fila = {"Nombre": v["nombre"], "Aciertos": aciertos}
        for i in range(15):
            fila[f"P{i+1}"] = signos_v[i]
        filas_ind.append(fila)

    df_ind = pd.DataFrame(filas_ind).sort_values("Aciertos", ascending=False)

    def color_celda(val, col_name):
        m = re.match(r"P(\d+)$", col_name)
        if not m:
            return ""
        idx = int(m.group(1)) - 1
        if idx >= len(resultados_norm):
            return ""
        ref = resultados_norm[idx]
        if not ref or ref == "?":
            return "background-color:#fff8e1"
        return (
            "background-color:#e8f5e9;color:#1b5e20;font-weight:600"
            if val == ref
            else "background-color:#ffebee;color:#c62828"
        )

    styler = df_ind.style.background_gradient(subset=["Aciertos"], cmap="YlGn")
    for col in df_ind.columns:
        if re.match(r"P\d+", col):
            styler = styler.apply(
                lambda s, c=col: [color_celda(v, c) for v in s], subset=[col]
            )

    st.dataframe(styler, hide_index=True, use_container_width=True)

    # ── Métricas rápidas ──────────────────────────────────────────────────────
    if filas_ind:
        max_ac = df_ind["Aciertos"].max()
        lider  = ", ".join(df_ind[df_ind["Aciertos"] == max_ac]["Nombre"].tolist())
        m1, m2, m3 = st.columns(3)
        m1.metric("🥇 Mejor de la jornada", lider)
        m2.metric("🎯 Sus aciertos", f"{max_ac} / {completados}")
        m3.metric("👥 Participantes", len(filas_ind))

    # ── Gráfico ───────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📊 Gráfico de aciertos")
    df_graf = df_ind[["Nombre", "Aciertos"]].sort_values("Aciertos", ascending=False)

    if PLOTLY_OK:
        fig = px.bar(
            df_graf,
            x="Nombre", y="Aciertos",
            color="Aciertos",
            color_continuous_scale=["#ef5350", "#ffd600", "#66bb6a"],
            text="Aciertos",
            title=f"Aciertos — Jornada {jornada}",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="white",
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title="",
            yaxis_title="Aciertos",
            title_font_size=17,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(df_graf.set_index("Nombre"))

    # ── Guardar en histórico ──────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("💾 Cerrar jornada y guardar en el Histórico")
    st.caption("Hazlo cuando todos hayan votado y los resultados estén completos.")

    if st.button("💾 Guardar Jornada en el Histórico", type="primary", use_container_width=True):
        historico = cargar_historico()
        historico["jornadas"] = [
            j for j in historico["jornadas"] if j.get("jornada") != jornada
        ]
        historico["jornadas"].append({
            "jornada": jornada,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "partidos": partidos[:15],
            "resultados": resultados_norm,
            "quiniela_peña": quiniela_peña,
            "aciertos_peña": aciertos_peña,
            "participantes": [
                {"nombre": f["Nombre"], "aciertos": f["Aciertos"]}
                for f in filas_ind
            ],
        })
        guardar_historico(historico)
        st.success(f"✅ Jornada {jornada} guardada en `historico.json`.")


# ══════════════════════════════════════════════════════════════════════════════
#  SECCIÓN 4 — RANKING HISTÓRICO
# ══════════════════════════════════════════════════════════════════════════════
elif seccion == "🏆 Ranking Histórico":
    st.header("🏆 Ranking Histórico de la Temporada")

    historico = cargar_historico()
    jornadas  = sorted(historico.get("jornadas", []), key=lambda j: j["jornada"])

    if not jornadas:
        st.info("📭 Aún no hay jornadas guardadas. Ve a 'Resultados & Aciertos' y guarda una jornada primero.")
        st.stop()

    # ── Última jornada ────────────────────────────────────────────────────────
    ultima = jornadas[-1]
    st.subheader(f"🌟 Última jornada guardada: Jornada {ultima['jornada']} ({ultima['fecha']})")

    part_ult  = sorted(ultima["participantes"], key=lambda p: p["aciertos"], reverse=True)
    lider_ult = part_ult[0] if part_ult else None

    c1, c2, c3 = st.columns(3)
    c1.metric("🥇 Ganador de la jornada", lider_ult["nombre"] if lider_ult else "—")
    c2.metric("🎯 Aciertos", lider_ult["aciertos"] if lider_ult else 0)
    c3.metric("🤝 Aciertos de la Peña", ultima.get("aciertos_peña", 0))

    df_ult = pd.DataFrame(part_ult).rename(columns={"nombre": "Nombre", "aciertos": "Aciertos"})
    df_ult.insert(0, "Pos", range(1, len(df_ult) + 1))
    st.dataframe(df_ult.set_index("Pos"), use_container_width=True)

    # ── Clasificación general ─────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📊 Clasificación General de la Temporada")

    totales   = {}
    victorias = {}
    jugadas   = {}

    for j in jornadas:
        if not j["participantes"]:
            continue
        max_j = max(p["aciertos"] for p in j["participantes"])
        ganadores_j = {p["nombre"] for p in j["participantes"] if p["aciertos"] == max_j}
        for p in j["participantes"]:
            n = p["nombre"]
            totales[n]   = totales.get(n, 0)   + p["aciertos"]
            victorias[n] = victorias.get(n, 0) + (1 if n in ganadores_j else 0)
            jugadas[n]   = jugadas.get(n, 0)   + 1

    ranking = sorted(
        totales.items(),
        key=lambda x: (x[1], victorias.get(x[0], 0)),
        reverse=True,
    )
    medallas = {1: "🥇", 2: "🥈", 3: "🥉"}

    df_rank = pd.DataFrame([
        {
            "Pos": f"{medallas.get(i+1, '')} {i+1}",
            "Nombre": nombre,
            "Total Aciertos": total,
            "Victorias": victorias.get(nombre, 0),
            "Jornadas": jugadas.get(nombre, 0),
            "Media": round(total / jugadas.get(nombre, 1), 1),
        }
        for i, (nombre, total) in enumerate(ranking)
    ]).set_index("Pos")

    st.dataframe(
        df_rank.style.background_gradient(subset=["Total Aciertos"], cmap="YlGn"),
        use_container_width=True,
    )

    # ── Gráfico evolución ─────────────────────────────────────────────────────
    if len(jornadas) > 1 and PLOTLY_OK:
        st.markdown("---")
        st.subheader("📈 Evolución por jornada")

        todos = list(totales.keys())
        evol  = {n: [] for n in todos}
        nums  = []
        for j in jornadas:
            nums.append(j["jornada"])
            dic = {p["nombre"]: p["aciertos"] for p in j["participantes"]}
            for n in todos:
                evol[n].append(dic.get(n, 0))

        df_ev = pd.DataFrame(evol, index=nums)
        df_ev.index.name = "Jornada"

        fig2 = px.line(
            df_ev.reset_index().melt("Jornada", var_name="Jugador", value_name="Aciertos"),
            x="Jornada", y="Aciertos", color="Jugador",
            markers=True, title="Aciertos por jornada",
        )
        fig2.update_layout(plot_bgcolor="white", title_font_size=17)
        st.plotly_chart(fig2, use_container_width=True)

    # ── Gestión del histórico ─────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🗃️ Gestión del Histórico")

    col_dl, col_del = st.columns(2)
    with col_dl:
        st.download_button(
            "⬇️ Descargar historico.json",
            data=json.dumps(historico, ensure_ascii=False, indent=2),
            file_name="historico.json",
            mime="application/json",
            use_container_width=True,
        )
    with col_del:
        confirmar_borrado = st.checkbox("Confirmo que quiero borrar el histórico completo")
        if st.button("🗑️ Borrar histórico", use_container_width=True, disabled=not confirmar_borrado):
            guardar_historico({"jornadas": []})
            st.success("✅ Histórico borrado.")
            st.rerun()

    with st.expander("🗂️ Ver / eliminar jornadas guardadas"):
        for j in jornadas:
            c_j1, c_j2 = st.columns([5, 1])
            with c_j1:
                lider_j = max(
                    j["participantes"],
                    key=lambda p: p["aciertos"],
                    default={"nombre": "—"},
                )
                st.markdown(
                    f"**Jornada {j['jornada']}** · {j['fecha']} · 🥇 {lider_j['nombre']}"
                )
            with c_j2:
                if st.button("🗑️", key=f"del_{j['jornada']}"):
                    historico["jornadas"] = [
                        x for x in historico["jornadas"] if x["jornada"] != j["jornada"]
                    ]
                    guardar_historico(historico)
                    st.rerun()

# ── Pie ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#bbb;font-size:.8rem;'>"
    "🏆 La Peña de la Quiniela · Hecho con ❤️ y Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
