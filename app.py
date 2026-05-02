import streamlit as st
import pandas as pd
import feedparser
import requests
import re
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt

st.set_page_config(page_title="Formal Menswear Footwear Intelligence", layout="wide")
st.title("👞 Formal Menswear Footwear Intelligence")
st.caption("Calzado masculino elegante · Lujo · Sastrería · MTM · Retail premium · Competencia")

BLOQUES = {
    "Calzado masculino formal": {
        "descripcion": "Oxford, Derby, mocasines, Monkstrap, botas elegantes y calzado de vestir masculino.",
        "queries": ["men formal shoes market trends", "men dress shoes luxury market", "classic mens shoes oxford derby loafer trends"],
        "kpis": ["Demanda formal", "Precio medio", "Mix casual/formal", "Rotación por modelo", "Ticket medio"]
    },
    "Lujo y premium": {
        "descripcion": "Marcas premium y lujo, precios, márgenes, cliente internacional y valor percibido.",
        "queries": ["luxury mens shoes market", "premium footwear men market trends", "luxury leather shoes men retail"],
        "kpis": ["ASP", "Margen bruto", "Cliente internacional", "Repetición", "Venta asistida"]
    },
    "Sastrería y ceremonia": {
        "descripcion": "Relación entre calzado formal, tailoring, ceremonia, bodas y vestir elegante masculino.",
        "queries": ["men tailoring formal shoes trends", "wedding shoes men formal trends", "menswear tailoring luxury retail"],
        "kpis": ["Ventas ceremonia", "Conversión por evento", "Ticket total look", "Cross-selling", "Anticipación pedido"]
    },
    "Personalización y MTM": {
        "descripcion": "Made to Measure, bespoke, escáner 3D, fitting, hormas y personalización.",
        "queries": ["bespoke men shoes market", "made to measure footwear men", "3D foot scanning custom shoes"],
        "kpis": ["Mix MTM", "Tasa de repetición", "Tiempo entrega", "Satisfacción fit", "Margen MTM"]
    },
    "Piel, fabricación y artesanía": {
        "descripcion": "Materiales, pieles, suelas, Goodyear, Blake, artesanía, costes y supply chain.",
        "queries": ["luxury leather footwear manufacturing", "Goodyear welted shoes market", "leather prices footwear industry"],
        "kpis": ["Coste materiales", "Plazo fabricación", "Defectos/calidad", "Margen por construcción", "Capacidad taller"]
    },
    "Retail premium y experiencia": {
        "descripcion": "Tienda premium, venta asistida, visual merchandising, servicio experto y experiencia.",
        "queries": ["luxury retail experience menswear", "premium footwear retail experience", "men luxury store experience"],
        "kpis": ["Conversión tienda", "Tiempo atención", "NPS", "Ventas por m²", "Ratio prueba/compra"]
    },
    "Competidores y marcas referencia": {
        "descripcion": "Crockett & Jones, Church's, Carmina, Santoni, Berluti, John Lobb, Magnanni, Mezlan, Edward Green.",
        "queries": ["Crockett Jones Church's Carmina shoes news", "Santoni Berluti John Lobb mens shoes news", "Magnanni Mezlan mens shoes market"],
        "kpis": ["Precio referencia", "Nuevas aperturas", "Lanzamientos", "Promociones", "Estrategia canal"]
    }
}

FORMACION = {
    "Calzado masculino formal": {
        "concepto": "Categoría centrada en zapato de vestir y elegante: Oxford, Derby, Monkstrap, Loafer, botas dress y modelos smart casual.",
        "preguntas": ["¿Qué modelos son estructurales?", "¿El cliente compra por necesidad, estatus, ceremonia o placer?", "¿Qué modelos son puerta de entrada a la marca?"],
        "acciones": ["Separar ventas por tipología.", "Medir formal puro frente a smart casual.", "Detectar modelos permanentes y modelos de campaña."]
    },
    "Lujo y premium": {
        "concepto": "Posicionamiento basado en valor percibido, calidad, escasez, servicio, origen, artesanía y confianza.",
        "preguntas": ["¿El precio comunica valor o frena conversión?", "¿Qué argumentos justifican el diferencial premium?", "¿El cliente percibe lujo por producto, servicio o relato?"],
        "acciones": ["Crear benchmark de PVP.", "Medir conversión por rangos de precio.", "Reforzar relato de origen y servicio experto."]
    },
    "Sastrería y ceremonia": {
        "concepto": "El calzado formal como complemento estratégico del traje, ceremonia y vestuario masculino de ocasión.",
        "preguntas": ["¿Qué peso tienen bodas y eventos?", "¿Existe venta cruzada con sastrería?", "¿Qué modelos funcionan mejor en ceremonia?"],
        "acciones": ["Crear cápsula ceremonia.", "Medir pedidos por fecha de evento.", "Activar alianzas con sastrerías."]
    },
    "Personalización y MTM": {
        "concepto": "Propuesta de valor basada en ajuste, horma, pie, estética, comodidad y singularidad.",
        "preguntas": ["¿Qué porcentaje necesita ajuste específico?", "¿Qué parte es estética y qué parte funcional?", "¿Cómo se reduce el riesgo de error en fitting?"],
        "acciones": ["Medir mix RTW/MTM.", "Registrar incidencias de fit.", "Crear argumento comercial para escáner y horma."]
    },
    "Piel, fabricación y artesanía": {
        "concepto": "Base tangible de calidad: piel, construcción, acabado, comodidad, durabilidad y reparabilidad.",
        "preguntas": ["¿Qué pieles elevan percepción sin destruir margen?", "¿Qué construcción valora el cliente?", "¿Qué elementos productivos son diferenciales?"],
        "acciones": ["Formar al equipo en pieles y construcción.", "Traducir tecnicismos a beneficios.", "Medir incidencias por proveedor."]
    },
    "Retail premium y experiencia": {
        "concepto": "La tienda como espacio de confianza, asesoramiento experto, prueba, relación y conversión premium.",
        "preguntas": ["¿La experiencia justifica desplazamiento y precio?", "¿El vendedor asesora o despacha?", "¿Dónde nace la confianza?"],
        "acciones": ["Diseñar ritual de prueba.", "Medir ratio prueba/compra.", "Crear guion de venta consultiva."]
    },
    "Competidores y marcas referencia": {
        "concepto": "Seguimiento de marcas comparables para entender precios, productos, canales y mensajes.",
        "preguntas": ["¿Quién marca el precio psicológico?", "¿Qué competidor educa mejor al cliente?", "¿Dónde hay hueco de posicionamiento?"],
        "acciones": ["Actualizar benchmark trimestral.", "Seguir lanzamientos y aperturas.", "Comparar propuesta de valor, no solo precio."]
    }
}

LANGUAGES = {"Español": "es", "Inglés": "en"}
COUNTRIES = {"España": "ES", "Estados Unidos": "US", "Reino Unido": "GB", "Francia": "FR", "Italia": "IT"}

KEYWORDS_POSITIVE = ["growth", "crecimiento", "crece", "increase", "ventas", "sales", "profit", "beneficio", "premium", "luxury", "lujo", "bespoke", "made to measure", "craftsmanship", "artesanía", "expansion", "apertura", "heritage", "margen"]
KEYWORDS_NEGATIVE = ["fall", "decline", "cae", "descenso", "crisis", "loss", "pérdida", "closure", "cierre", "weak", "débil", "discount", "descuento", "pressure", "presión", "bankruptcy", "quiebra"]
KEYWORDS_RISK = ["cost", "costes", "leather prices", "piel", "raw materials", "materias primas", "supply chain", "logística", "tariff", "arancel", "inflation", "inflación", "counterfeit", "falsificación", "competition", "competencia", "margin pressure", "China"]
KEYWORDS_TREND = ["bespoke", "made to measure", "custom", "personalization", "personalización", "3D", "foot scanning", "smart casual", "quiet luxury", "heritage", "craftsmanship", "Goodyear", "loafer", "oxford", "derby", "comfort", "wedding", "ceremony", "ceremonia"]


def limpiar_html(texto):
    if not texto:
        return ""
    texto = re.sub("<.*?>", "", texto)
    return texto.replace("&nbsp;", " ").replace("&amp;", "&").strip()


def construir_google_news_rss(query, lang="es", country="ES"):
    query_encoded = requests.utils.quote(query)
    return f"https://news.google.com/rss/search?q={query_encoded}&hl={lang}&gl={country}&ceid={country}:{lang}"


@st.cache_data(ttl=1800, show_spinner=False)
def obtener_noticias(query, lang="es", country="ES", max_items=8):
    feed = feedparser.parse(construir_google_news_rss(query, lang, country))
    noticias = []
    for entry in feed.entries[:max_items]:
        try:
            fuente = entry.get("source", {}).get("title", "")
        except Exception:
            fuente = ""
        noticias.append({
            "Fecha": entry.get("published", ""),
            "Fuente": fuente,
            "Titular": limpiar_html(entry.get("title", "")),
            "Resumen": limpiar_html(entry.get("summary", "")),
            "Link": entry.get("link", ""),
            "Query": query
        })
    return noticias


def clasificar_texto(titulo, resumen):
    texto = f"{titulo} {resumen}".lower()
    score_pos = sum(1 for kw in KEYWORDS_POSITIVE if kw.lower() in texto)
    score_neg = sum(1 for kw in KEYWORDS_NEGATIVE if kw.lower() in texto)
    score_risk = sum(1 for kw in KEYWORDS_RISK if kw.lower() in texto)
    score_trend = sum(1 for kw in KEYWORDS_TREND if kw.lower() in texto)
    impacto = "Positivo" if score_pos > score_neg else "Negativo" if score_neg > score_pos else "Neutro"
    riesgo = "Alto" if score_risk >= 2 else "Medio" if score_risk == 1 else "Bajo"
    tendencia = "Alta" if score_trend >= 2 else "Media" if score_trend == 1 else "Baja"
    return impacto, riesgo, tendencia, score_pos + score_neg + score_risk + score_trend


@st.cache_data(ttl=1800, show_spinner=False)
def cargar_noticias(bloques_activos, lang, country, max_items):
    registros = []
    for bloque in bloques_activos:
        for query in BLOQUES[bloque]["queries"]:
            for n in obtener_noticias(query, lang, country, max_items):
                impacto, riesgo, tendencia, relevancia = clasificar_texto(n["Titular"], n["Resumen"])
                n.update({"Bloque": bloque, "Impacto": impacto, "Riesgo": riesgo, "Tendencia": tendencia, "Relevancia": relevancia})
                registros.append(n)
    df = pd.DataFrame(registros)
    if df.empty:
        return df
    return df.drop_duplicates(subset=["Titular"]).sort_values("Relevancia", ascending=False)


def construir_df_formacion():
    rows = []
    for bloque, data in FORMACION.items():
        rows.append({
            "Bloque": bloque,
            "Concepto": data["concepto"],
            "Preguntas clave": " | ".join(data["preguntas"]),
            "Acciones recomendadas": " | ".join(data["acciones"]),
            "KPIs": " | ".join(BLOQUES[bloque]["kpis"])
        })
    return pd.DataFrame(rows)


def preparar_excel(df_news, df_formacion):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_news.to_excel(writer, index=False, sheet_name="Noticias")
        df_formacion.to_excel(writer, index=False, sheet_name="Formacion")
        workbook = writer.book
        header_format = workbook.add_format({"bold": True, "bg_color": "#D9EAF7", "border": 1})
        for sheet_name, df_temp in [("Noticias", df_news), ("Formacion", df_formacion)]:
            worksheet = writer.sheets[sheet_name]
            for col_num, value in enumerate(df_temp.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 26)
    return output.getvalue()


st.sidebar.header("Configuración")
idioma_label = st.sidebar.selectbox("Idioma noticias", list(LANGUAGES.keys()), index=0)
pais_label = st.sidebar.selectbox("País base", list(COUNTRIES.keys()), index=0)
max_items = st.sidebar.slider("Noticias por búsqueda", 3, 20, 8)
bloques_activos = st.sidebar.multiselect("Bloques activos", list(BLOQUES.keys()), default=list(BLOQUES.keys()))

lang = LANGUAGES[idioma_label]
country = COUNTRIES[pais_label]

with st.spinner("Cargando inteligencia sectorial..."):
    df_news = cargar_noticias(bloques_activos, lang, country, max_items)

df_formacion = construir_df_formacion()

tab_dashboard, tab_news, tab_strategy, tab_training, tab_kpis, tab_export = st.tabs(["📊 Dashboard", "📰 Noticias", "🧠 Lectura estratégica", "🎓 Formación", "📈 KPIs", "📥 Exportación"])

with tab_dashboard:
    st.subheader("📊 Panel ejecutivo")
    if df_news.empty:
        st.warning("No se han encontrado noticias. Prueba con otro idioma, país o bloque.")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Noticias analizadas", len(df_news))
        col2.metric("Impacto positivo", len(df_news[df_news["Impacto"] == "Positivo"]))
        col3.metric("Riesgo alto", len(df_news[df_news["Riesgo"] == "Alto"]))
        col4.metric("Tendencia alta", len(df_news[df_news["Tendencia"] == "Alta"]))
        st.markdown("### Distribución por bloque")
        bloque_counts = df_news["Bloque"].value_counts().reset_index()
        bloque_counts.columns = ["Bloque", "Noticias"]
        st.dataframe(bloque_counts, use_container_width=True)
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.bar(bloque_counts["Bloque"], bloque_counts["Noticias"])
        ax.set_ylabel("Número de noticias")
        ax.set_title("Noticias por bloque estratégico")
        ax.tick_params(axis="x", rotation=35)
        st.pyplot(fig)
        st.markdown("### Top señales relevantes")
        st.dataframe(df_news.head(12)[["Bloque", "Titular", "Fuente", "Impacto", "Riesgo", "Tendencia", "Relevancia", "Link"]], use_container_width=True)

with tab_news:
    st.subheader("📰 Noticias clasificadas")
    if df_news.empty:
        st.warning("No hay noticias disponibles.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        filtro_bloque = c1.selectbox("Bloque", ["Todos"] + sorted(df_news["Bloque"].unique()))
        filtro_impacto = c2.selectbox("Impacto", ["Todos"] + sorted(df_news["Impacto"].unique()))
        filtro_riesgo = c3.selectbox("Riesgo", ["Todos"] + sorted(df_news["Riesgo"].unique()))
        filtro_tendencia = c4.selectbox("Tendencia", ["Todos"] + sorted(df_news["Tendencia"].unique()))
        df_view = df_news.copy()
        if filtro_bloque != "Todos": df_view = df_view[df_view["Bloque"] == filtro_bloque]
        if filtro_impacto != "Todos": df_view = df_view[df_view["Impacto"] == filtro_impacto]
        if filtro_riesgo != "Todos": df_view = df_view[df_view["Riesgo"] == filtro_riesgo]
        if filtro_tendencia != "Todos": df_view = df_view[df_view["Tendencia"] == filtro_tendencia]
        for _, row in df_view.head(80).iterrows():
            with st.container(border=True):
                st.markdown(f"### [{row['Titular']}]({row['Link']})")
                st.write(f"**Bloque:** {row['Bloque']} | **Fuente:** {row['Fuente']}")
                st.write(f"**Impacto:** {row['Impacto']} · **Riesgo:** {row['Riesgo']} · **Tendencia:** {row['Tendencia']} · **Relevancia:** {row['Relevancia']}")
                if row["Resumen"]: st.caption(row["Resumen"][:420])

with tab_strategy:
    st.subheader("🧠 Lectura estratégica")
    if df_news.empty:
        st.warning("No hay datos suficientes para elaborar lectura estratégica.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ⚠️ Riesgos a vigilar")
            riesgos = df_news[df_news["Riesgo"] == "Alto"].head(10)
            if riesgos.empty: st.write("No se detectan riesgos altos.")
            else:
                for _, row in riesgos.iterrows(): st.write(f"- **{row['Bloque']}** · [{row['Titular']}]({row['Link']})")
            st.markdown("### 📉 Señales negativas")
            negativas = df_news[df_news["Impacto"] == "Negativo"].head(10)
            if negativas.empty: st.write("No se detectan señales negativas destacadas.")
            else:
                for _, row in negativas.iterrows(): st.write(f"- **{row['Bloque']}** · [{row['Titular']}]({row['Link']})")
        with col2:
            st.markdown("### 🚀 Tendencias emergentes")
            tendencias = df_news[df_news["Tendencia"] == "Alta"].head(10)
            if tendencias.empty: st.write("No se detectan tendencias altas.")
            else:
                for _, row in tendencias.iterrows(): st.write(f"- **{row['Bloque']}** · [{row['Titular']}]({row['Link']})")
            st.markdown("### 📈 Señales positivas")
            positivas = df_news[df_news["Impacto"] == "Positivo"].head(10)
            if positivas.empty: st.write("No se detectan señales positivas destacadas.")
            else:
                for _, row in positivas.iterrows(): st.write(f"- **{row['Bloque']}** · [{row['Titular']}]({row['Link']})")
        bloque_mas_activo = df_news["Bloque"].value_counts().idxmax()
        st.info(f"El bloque con mayor actividad informativa es **{bloque_mas_activo}**. Conviene analizar si las señales apuntan a recuperación del formal, expansión del premium, presión de costes o avance de la personalización.")

with tab_training:
    st.subheader("🎓 Módulo formativo")
    bloque_formacion = st.selectbox("Selecciona bloque formativo", list(FORMACION.keys()))
    data = FORMACION[bloque_formacion]
    st.markdown(f"## {bloque_formacion}")
    st.write(data["concepto"])
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Preguntas clave")
        for pregunta in data["preguntas"]: st.write(f"- {pregunta}")
    with col2:
        st.markdown("### Acciones recomendadas")
        for accion in data["acciones"]: st.write(f"- {accion}")
    st.markdown("### KPIs recomendados")
    st.write(", ".join(BLOQUES[bloque_formacion]["kpis"]))
    st.success("La ventaja en calzado masculino formal no está solo en el producto: está en unir ajuste, relato, servicio experto, experiencia y consistencia comercial.")

with tab_kpis:
    st.subheader("📈 KPIs por bloque estratégico")
    rows = []
    for bloque, data in BLOQUES.items():
        for kpi in data["kpis"]: rows.append({"Bloque": bloque, "KPI": kpi, "Uso directivo": "Medir rendimiento, comparar tiendas/canales y priorizar acciones comerciales"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, height=520)
    st.markdown("### KPIs especialmente relevantes")
    st.write("**Mix RTW/MTM, ticket medio, conversión, ventas por m², repetición, ratio prueba/compra, margen por modelo y plazo de entrega.**")

with tab_export:
    st.subheader("📥 Exportación")
    excel = preparar_excel(df_news, df_formacion)
    st.download_button("📥 Descargar informe Excel", data=excel, file_name=f"formal_menswear_footwear_intelligence_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("### Archivos necesarios")
    st.code("app.py\nrequirements.txt", language="text")

st.caption("Noticias vía Google News RSS. Clasificación automática por palabras clave estratégicas. Puede evolucionarse con IA generativa/API para análisis más profundo.")
