from pathlib import Path
import csv
import subprocess

import pandas as pd
import streamlit as st


# ============================================================
# TRADICION CHILANGA
# DASHBOARD PEATONAL
# COMPATIBLE CSV ANTIGUO + NUEVO
# ============================================================

st.set_page_config(
    page_title="Tradición Chilanga · Peatones",
    page_icon="🌮",
    layout="wide",
    initial_sidebar_state="expanded",
)

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=6_000, key="actualizacion_peatones")



# ============================================================
# ARCHIVOS
# ============================================================

BASE = Path(r"C:\TradicionIA")

CSV_EVENTOS = (
    BASE
    / "datos"
    / "eventos_peatones.csv"
)


# ============================================================
# PERIODOS DE DATOS
# ============================================================

FECHA_INICIO_VALIDADA = pd.Timestamp(
    "2026-09-25 00:00:00"
)

EXCLUSION_INICIO = pd.Timestamp(
    "2026-09-25 10:00:00"
)

EXCLUSION_FIN = pd.Timestamp(
    "2026-09-26 03:22:20"
)

INICIO_V245 = pd.Timestamp(
    "2026-09-26 03:22:20"
)


# ============================================================
# ESTILO
# ============================================================

st.markdown('<style>\n.stApp {background:#0b1220;color:#f1f5f9;color-scheme:dark;}\nsection[data-testid="stSidebar"] {background:#111c2e;border-right:1px solid #334155;}\n.block-container {padding-top:2rem;padding-bottom:3rem;max-width:1440px;}\n.titulo {color:#f8fafc;font-size:clamp(1.7rem,3vw,2.4rem);font-weight:800;line-height:1.2;margin-bottom:8px;}\n.subtitulo {color:#cbd5e1;font-size:1rem;margin-bottom:1.5rem;}\n.tarjeta {background:#162338;border:1px solid #40536d;border-top:3px solid #5eead4;border-radius:16px;padding:22px;min-height:160px;height:100%;box-sizing:border-box;}\n.tarjeta-titulo {color:#dbe7f5;font-size:1rem;font-weight:600;line-height:1.4;}\n.tarjeta-valor {color:#ffffff!important;font-size:clamp(2rem,3.3vw,3rem);font-weight:800;line-height:1.2;margin-top:12px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere;}\n.tarjeta-nota {color:#cbd5e1;font-size:.9rem;line-height:1.5;margin-top:12px;}\n.tarjeta-estado {font-size:1.35rem;line-height:1.4;}\ndiv[data-testid="stMetric"] {background:#162338;border:1px solid #40536d;border-radius:16px;padding:20px;min-height:140px;}\n[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {color:#dbe7f5!important;font-size:1rem!important;}\n[data-testid="stMetricValue"], [data-testid="stMetricValue"] div {color:#ffffff!important;font-size:2.5rem!important;font-weight:800!important;font-variant-numeric:tabular-nums;}\n[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {color:#cbd5e1!important;}\nh1,h2,h3,h4 {color:#f8fafc!important;}\n[data-testid="stHeader"] {background:#0b1220;}\n[data-testid="stSidebar"] label {color:#e2e8f0!important;}\n@media(max-width:850px){\n[data-testid="stHorizontalBlock"] {flex-wrap:wrap!important;gap:1rem!important;}\n[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] {min-width:calc(50% - 1rem)!important;flex:1 1 calc(50% - 1rem)!important;}\n.tarjeta {padding:18px;min-height:150px;}\n}\n@media(max-width:520px){\n.block-container {padding:1.25rem 1rem 2rem;}\n[data-testid="stHorizontalBlock"]>[data-testid="stColumn"] {min-width:100%!important;flex-basis:100%!important;}\n.tarjeta-valor {font-size:2.7rem;}\n.tarjeta-estado {font-size:1.3rem;}\n}\n</style>', unsafe_allow_html=True)


# ============================================================
# TARJETAS
# ============================================================

def tarjeta(titulo, valor, nota=""):
    clase_valor = "tarjeta-valor tarjeta-estado" if any(c.isalpha() for c in str(valor)) else "tarjeta-valor"

    html = (
        f'<div class="tarjeta">'
        f'<div class="tarjeta-titulo">{titulo}</div>'
        f'<div class="{clase_valor}">{valor}</div>'
        f'<div class="tarjeta-nota">{nota}</div>'
        f'</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ============================================================
# LECTOR CSV ROBUSTO
# ============================================================

@st.cache_data(ttl=5)
def cargar_csv_mixto():

    columnas = [
        "fecha",
        "hora",
        "timestamp",
        "logical_id",
        "bot_id",
        "direccion",
        "confianza",
    ]

    if not CSV_EVENTOS.exists():

        return pd.DataFrame(
            columns=columnas
        )

    registros = []

    with open(
        CSV_EVENTOS,
        "r",
        encoding="utf-8",
        newline=""
    ) as archivo:

        lector = csv.reader(
            archivo
        )

        for numero_linea, fila in enumerate(
            lector,
            start=1
        ):

            if not fila:

                continue

            # Ignorar encabezados antiguos o nuevos
            if (
                fila[0].strip().lower()
                ==
                "fecha"
            ):

                continue

            # --------------------------------------------
            # FORMATO NUEVO: 7 columnas
            #
            # fecha,hora,timestamp,
            # logical_id,bot_id,direccion,confianza
            # --------------------------------------------

            if len(fila) == 7:

                registros.append(
                    {
                        "fecha": fila[0],
                        "hora": fila[1],
                        "timestamp": fila[2],
                        "logical_id": fila[3],
                        "bot_id": fila[4],
                        "direccion": fila[5],
                        "confianza": fila[6],
                    }
                )

            # --------------------------------------------
            # FORMATO ANTIGUO: 6 columnas
            #
            # fecha,hora,timestamp,
            # bot_id,direccion,confianza
            #
            # logical_id todavía no existía.
            # --------------------------------------------

            elif len(fila) == 6:

                registros.append(
                    {
                        "fecha": fila[0],
                        "hora": fila[1],
                        "timestamp": fila[2],
                        "logical_id": None,
                        "bot_id": fila[3],
                        "direccion": fila[4],
                        "confianza": fila[5],
                    }
                )

            else:

                # No destruimos ni modificamos el CSV.
                # Simplemente ignoramos una línea con
                # estructura desconocida.
                continue

    df = pd.DataFrame(
        registros,
        columns=columnas
    )

    if df.empty:

        return df

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["logical_id"] = pd.to_numeric(
        df["logical_id"],
        errors="coerce"
    )

    df["bot_id"] = pd.to_numeric(
        df["bot_id"],
        errors="coerce"
    )

    df["confianza"] = pd.to_numeric(
        df["confianza"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["timestamp"]
    ).copy()

    return df


# ============================================================
# PREPARAR DATASETS
# ============================================================

def preparar_datos():

    df_raw = cargar_csv_mixto()

    if df_raw.empty:

        vacio = df_raw.copy()

        return (
            df_raw,
            vacio,
            vacio,
            vacio
        )

    df_validado = df_raw[
        df_raw["timestamp"]
        >=
        FECHA_INICIO_VALIDADA
    ].copy()

    mascara_anomalia = (
        (
            df_validado["timestamp"]
            >=
            EXCLUSION_INICIO
        )
        &
        (
            df_validado["timestamp"]
            <
            EXCLUSION_FIN
        )
    )

    df_anomalia = df_validado[
        mascara_anomalia
    ].copy()

    df_validado = df_validado[
        ~mascara_anomalia
    ].copy()

    df_v245 = df_validado[
        df_validado["timestamp"]
        >=
        INICIO_V245
    ].copy()

    return (
        df_raw,
        df_validado,
        df_anomalia,
        df_v245
    )


def contar_direcciones(df):

    if (
        df.empty
        or
        "direccion" not in df.columns
    ):

        return 0, 0

    izq_der = int(
        (
            df["direccion"]
            ==
            "IZQUIERDA_DERECHA"
        ).sum()
    )

    der_izq = int(
        (
            df["direccion"]
            ==
            "DERECHA_IZQUIERDA"
        ).sum()
    )

    return (
        izq_der,
        der_izq
    )


def proceso_activo(nombre):

    try:

        comando = (
            "Get-CimInstance Win32_Process | "
            "Select-Object -ExpandProperty CommandLine"
        )

        resultado = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                comando,
            ],
            capture_output=True,
            text=True,
            timeout=4,
        )

        return (
            nombre.lower()
            in
            resultado.stdout.lower()
        )

    except Exception:

        return False


# ============================================================
# DATOS
# ============================================================

(
    df_raw,
    df_validado,
    df_anomalia,
    df_v245
) = preparar_datos()


ahora = pd.Timestamp.now()

inicio_hoy = ahora.normalize()

hace_15 = (
    ahora
    -
    pd.Timedelta(
        minutes=15
    )
)

hace_30 = (
    ahora
    -
    pd.Timedelta(
        minutes=30
    )
)


if df_validado.empty:

    df_hoy = df_validado.copy()

    df_15 = df_validado.copy()

    df_30 = df_validado.copy()

else:

    df_hoy = df_validado[
        df_validado["timestamp"]
        >=
        inicio_hoy
    ].copy()

    df_15 = df_validado[
        df_validado["timestamp"]
        >=
        hace_15
    ].copy()

    df_30 = df_validado[
        df_validado["timestamp"]
        >=
        hace_30
    ].copy()


(
    izquierda_derecha,
    derecha_izquierda
) = contar_direcciones(
    df_validado
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "## Tradición Chilanga"
)

st.sidebar.caption(
    "Analítica peatonal"
)

seccion = st.sidebar.radio(
    "Navegación",
    [
        "Resumen",
        "Análisis",
        "Cámara",
        "Registros",
        "Sistema",
    ],
)

st.sidebar.markdown("---")

st.sidebar.caption(
    "Versión actual"
)

st.sidebar.write(
    "**V2.4.5 · EN VALIDACIÓN**"
)

st.sidebar.caption(
    f"Desde "
    f"{INICIO_V245:%d/%m/%Y %H:%M:%S}"
)


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    '<div class="titulo">'
    'Tradición Chilanga'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitulo">'
    'Conteo y análisis de flujo peatonal'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# RESUMEN
# ============================================================

if seccion == "Resumen":
    st.subheader("Flujo peatonal")
    st.caption(f"Actualizado: {ahora:%d/%m/%Y %H:%M:%S} · Recarga cada 6 segundos")
    esta_hora = df_hoy[df_hoy["timestamp"] >= ahora.floor("h")] if not df_hoy.empty else df_hoy
    columnas = st.columns(4)
    for columna, titulo, valor, nota in zip(columnas,
        ["Peatones hoy", "Últimos 15 min", "Últimos 30 min", "Esta hora"],
        [len(df_hoy), len(df_15), len(df_30), len(esta_hora)],
        ["Eventos válidos de hoy", "Ventana móvil de 15 minutos", "Ventana móvil de 30 minutos", f"Desde las {ahora:%H}:00"]):
        with columna:
            tarjeta(titulo, f"{valor:,}", nota)
    st.markdown("### Dirección del flujo · hoy")
    id_hoy, di_hoy = contar_direcciones(df_hoy)
    d1, d2 = st.columns(2)
    with d1:
        st.metric("Izquierda → Derecha", f"{id_hoy:,}")
    with d2:
        st.metric("Derecha → Izquierda", f"{di_hoy:,}")


    st.markdown("### Dirección del flujo por hora · hoy")

    hora_elegida = st.selectbox(
        "Selecciona una hora de hoy",
        options=list(range(ahora.hour + 1)),
        index=ahora.hour,
        format_func=lambda h: f"{h:02d}:00–{h:02d}:59",
        key="hora_direccion_flujo",
    )

    datos_hora = df_hoy[
        df_hoy["timestamp"].dt.hour == hora_elegida
    ].copy() if not df_hoy.empty else df_hoy

    izq_der_hora, der_izq_hora = contar_direcciones(datos_hora)
    columna_izq, columna_der = st.columns(2)

    with columna_izq:
        st.metric("Izquierda → Derecha", f"{izq_der_hora:,}")
    with columna_der:
        st.metric("Derecha → Izquierda", f"{der_izq_hora:,}")

    st.caption(
        f"Total registrado en esta hora: {len(datos_hora):,}"
        + (
            " · Hora en curso."
            if hora_elegida == ahora.hour
            else " · Hora terminada."
        )
    )
    if datos_hora.empty:
        st.caption(
            "Sin registros en esta hora; "
            "esto no confirma que la cámara estuvo activa."
        )

    st.markdown("### Actividad actual")
    if df_validado.empty:
        st.info("Todavía no hay eventos válidos.")
    else:
        ultimo = df_validado["timestamp"].max()
        st.caption(f"Último peatón detectado: {ultimo:%d/%m/%Y %H:%M:%S}. La ausencia de eventos no indica una falla de cámara.")
    st.markdown("### Flujo por hora · hoy y ayer")
    horas = pd.DataFrame(index=range(24))
    horas.index.name = "Hora"
    horas["Hoy"] = df_hoy.groupby(df_hoy["timestamp"].dt.hour).size().reindex(range(24), fill_value=0) if not df_hoy.empty else 0
    ayer_inicio = inicio_hoy - pd.Timedelta(days=1)
    ayer = df_validado[(df_validado["timestamp"] >= ayer_inicio) & (df_validado["timestamp"] < inicio_hoy)] if not df_validado.empty else df_validado
    horas["Ayer"] = ayer.groupby(ayer["timestamp"].dt.hour).size().reindex(range(24), fill_value=0) if not ayer.empty else 0
    st.bar_chart(horas, color=["#5eead4", "#93c5fd"])
    st.caption("Conteos por hora. La hora actual puede estar incompleta; cero también puede significar ausencia de datos.")

    st.markdown("### Contexto del día")
    st.caption(
        "Las 3 horas de mayor y menor flujo registrado hoy. "
        "Se comparan horas terminadas con registros."
    )
    horas_terminadas = df_hoy[
        df_hoy["timestamp"] < ahora.floor("h")
    ].copy()

    if horas_terminadas.empty:
        st.info(
            "El ranking aparecerá cuando haya "
            "registros de una hora terminada."
        )
    else:
        ranking_horas = (
            horas_terminadas
            .groupby(horas_terminadas["timestamp"].dt.hour)
            .size()
            .rename("Cruces")
            .rename_axis("Hora")
            .reset_index()
        )
        mayores = ranking_horas.sort_values(
            ["Cruces", "Hora"], ascending=[False, True]
        ).head(3).copy()
        menores = ranking_horas.sort_values(
            ["Cruces", "Hora"], ascending=[True, True]
        ).head(3).copy()

        for tabla in [mayores, menores]:
            tabla["Hora"] = tabla["Hora"].map(
                lambda h: f"{int(h):02d}:00–{int(h):02d}:59"
            )
            tabla.insert(0, "Puesto", range(1, len(tabla) + 1))

        mayor_col, menor_col = st.columns(2)
        with mayor_col:
            st.markdown("#### Mayor flujo observado")
            st.dataframe(
                mayores, hide_index=True, use_container_width=True
            )
        with menor_col:
            st.markdown("#### Menor flujo observado")
            st.dataframe(
                menores, hide_index=True, use_container_width=True
            )

        st.caption(
            "Se muestran hasta 3 resultados disponibles. "
            "En empates se ordena por hora. "
            "No se incluyen horas sin registros."
        )

    st.markdown("### Días recientes")
    if not df_validado.empty:
        dias = df_validado.groupby(df_validado["timestamp"].dt.normalize()).size().rename("Peatones")
        st.bar_chart(dias.tail(7), color="#5eead4")
    st.markdown("### Últimos peatones detectados")
    st.dataframe(df_validado.sort_values("timestamp", ascending=False).head(10)[["timestamp", "direccion", "confianza"]], hide_index=True, use_container_width=True)

elif seccion == "Análisis":

    st.subheader(
        "Análisis de afluencia"
    )

    if df_validado.empty:

        st.info(
            "Todavía no existen datos válidos para analizar."
        )

    else:

        trabajo = df_validado.copy()

        trabajo["hora_num"] = (
            trabajo["timestamp"].dt.hour
        )

        trabajo["minuto"] = (
            trabajo["timestamp"].dt.floor(
                "min"
            )
        )


        st.markdown(
            "#### Peatones por hora"
        )


        por_hora = (
            trabajo
            .groupby("hora_num")
            .size()
            .rename("peatones")
        )

        st.bar_chart(
            por_hora
        )


        st.markdown(
            "#### Actividad reciente"
        )


        reciente = trabajo[
            trabajo["timestamp"]
            >=
            ahora
            -
            pd.Timedelta(hours=6)
        ].copy()


        if reciente.empty:

            st.caption(
                "Sin eventos válidos en las últimas 6 horas."
            )

        else:

            por_minuto = (
                reciente
                .groupby("minuto")
                .size()
                .rename("peatones")
            )

            st.line_chart(
                por_minuto
            )


        a1, a2, a3 = st.columns(3)


        with a1:

            st.metric(
                "Últimos 30 min",
                len(df_30),
            )


        with a2:

            st.metric(
                "Eventos V2.4.5",
                len(df_v245),
            )


        with a3:

            st.metric(
                "Excluidos",
                len(df_anomalia),
            )


# ============================================================
# CAMARA
# ============================================================

elif seccion == "Cámara":

    st.subheader(
        "Cámara / Contador"
    )

    contador_activo = proceso_activo(
        "camara_tapo.py"
    )

    if contador_activo:

        st.success(
            "camara_tapo.py está ejecutándose."
        )

    else:

        st.warning(
            "No se detectó camara_tapo.py."
        )


    st.markdown(
        "### V2.4.5 adaptativa"
    )

    st.code(
        """0 personas  → 448
1 persona   → 512
2+ personas → 544""",
        language="text",
    )


# ============================================================
# REGISTROS
# ============================================================

elif seccion == "Registros":

    st.subheader(
        "Registros"
    )

    filtro = st.radio(
        "Mostrar",
        [
            "Válidos",
            "V2.4.5",
            "Periodo excluido",
            "RAW",
        ],
        horizontal=True,
    )


    if filtro == "Válidos":

        tabla = df_validado.copy()

    elif filtro == "V2.4.5":

        tabla = df_v245.copy()

    elif filtro == "Periodo excluido":

        tabla = df_anomalia.copy()

    else:

        tabla = df_raw.copy()


    if tabla.empty:

        st.info(
            "No hay registros para este filtro."
        )

    else:

        tabla = tabla.sort_values(
            "timestamp",
            ascending=False,
        )

        st.dataframe(
            tabla,
            use_container_width=True,
            hide_index=True,
        )


    st.caption(
        "El dashboard sólo filtra. "
        "No borra filas del CSV original."
    )


# ============================================================
# SISTEMA
# ============================================================

elif seccion == "Sistema":

    st.subheader("Estado del sistema")
    if proceso_activo("camara_tapo.py"):
        st.success("Contador activo")
    else:
        st.warning("Contador no detectado")
    st.caption(f"Consulta actualizada: {ahora:%d/%m/%Y %H:%M:%S}")
