
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
st.caption("Calzado masculino elegante · Lujo · Sastrería · Personalización · Retail premium · Inspiración estratégica")

BLOQUES = {
    "Calzado masculino formal": {
        "descripcion": "Noticias y tendencias sobre Oxford, Derby, mocasines, botas elegantes y calzado de vestir masculino.",
        "queries": [
            "men formal shoes market trends",
            "men dress shoes luxury market",
            "classic mens shoes oxford derby loafer trends"
        ],
        "kpis": ["Demanda formal", "Precio medio", "Mix casual/formal", "Rotación por modelo", "Ticket medio"]
    },
    "Lujo y premium": {
        "descripcion": "Evolución de marcas premium y lujo, posicionamiento, precios, márgenes y cliente de alto valor.",
        "queries": [
            "luxury mens shoes market",
            "premium footwear men market trends",
            "luxury leather shoes men retail"
        ],
        "kpis": ["ASP", "Margen bruto", "Cliente internacional", "Repetición", "Venta asistida"]
    },
    "Sastrería y ceremonia": {
        "descripcion": "Relación entre calzado formal, tailoring, ceremonia, eventos, bodas y vestir elegante masculino.",
        "queries": [
            "men tailoring formal shoes trends",
            "wedding shoes men formal trends",
            "menswear tailoring luxury retail"
        ],
        "kpis": ["Ventas ceremonia", "Conversión por evento", "Ticket total look", "Cross-selling", "Anticipación pedido"]
    },
    "Personalización y MTM": {
        "descripcion": "Made to Measure, bespoke, escáner 3D, fitting, hormas y personalización estética/funcional.",
        "queries": [
            "bespoke men shoes market",
            "made to measure footwear men",
            "3D foot scanning custom shoes"
        ],
        "kpis": ["Mix MTM", "Tasa de repetición", "Tiempo entrega", "Satisfacción fit", "Margen MTM"]
    },
    "Piel, fabricación y artesanía": {
        "descripcion": "Materiales, pieles, suelas, construcción Goodyear, Blake, artesanía, costes y supply chain.",
        "queries": [
            "luxury leather footwear manufacturing",
            "Goodyear welted shoes market",
            "leather prices footwear industry"
        ],
        "kpis": ["Coste materiales", "Plazo fabricación", "Defectos/calidad", "Margen por construcción", "Capacidad taller"]
    },
    "Retail premium y experiencia": {
        "descripcion": "Experiencia en tienda, visual merchandising, venta asistida, servicio experto y tráfico premium.",
        "queries": [
            "luxury retail experience menswear",
            "premium footwear retail experience",
            "men luxury store experience"
        ],
        "kpis": ["Conversión tienda", "Tiempo atención", "NPS", "Ventas por m²", "Ratio prueba/compra"]
    },
    "Competidores y marcas referencia": {
        "descripcion": "Seguimiento de Crockett & Jones, Church's, Carmina, Santoni, Berluti, John Lobb, Magnanni, Mezlan, Edward Green.",
        "queries": [
            "Crockett Jones Church's Carmina shoes news",
            "Santoni Berluti John Lobb mens shoes news",
            "Magnanni Mezlan mens shoes market"
        ],
        "kpis": ["Precio referencia", "Nuevas aperturas", "Lanzamientos", "Promociones", "Estrategia canal"]
    }
}

FORMACION = {
    "Calzado masculino formal": {
        "concepto": "Categoría centrada en zapato de vestir y elegante: Oxford, Derby, Monkstrap, Loafer, botas dress y modelos híbridos smart casual.",
        "preguntas": [
            "¿Qué modelos siguen siendo estructurales y cuáles son moda pasajera?",
            "¿El cliente compra formal por necesidad, estatus, ceremonia o placer?",
            "¿Qué modelos actúan como puerta de entrada a la marca?"
        ],
        "acciones": [
            "Separar ventas por Oxford, Derby, Loafer, Monk y Bota.",
            "Medir formal puro frente a smart casual.",
            "Detectar modelos permanentes y modelos de campaña."
        ]
    },
    "Lujo y premium": {
        "concepto": "Posicionamiento basado en valor percibido, calidad, escasez, servicio, origen, artesanía y confianza.",
        "preguntas": [
            "¿El precio comunica valor o frena conversión?",
            "¿Qué argumentos justifican el diferencial premium?",
            "¿El cliente percibe lujo por producto, servicio o relato?"
        ],
        "acciones": [
            "Crear benchmark de PVP por competidor.",
            "Medir conversión por rangos de precio.",
            "Reforzar relato de origen, fabricación y servicio experto."
        ]
    },
    "Sastrería y ceremonia": {
        "concepto": "El calzado formal funciona como complemento estratégico del traje, la ceremonia y el vestuario masculino de ocasión.",
        "preguntas": [
            "¿Qué peso tienen bodas, eventos y business formal?",
            "¿Existe venta cruzada con sastrería o total look?",
            "¿Qué modelos funcionan mejor en ceremonia?"
        ],
        "acciones": [
            "Crear cápsula ceremonia.",
            "Medir pedidos por fecha de evento.",
            "Activar alianzas con sastrerías y asesores de imagen."
        ]
    },
    "Personalización y MTM": {
        "concepto": "Propuesta de valor basada en ajuste, horma, pie, estética, comodidad y singularidad.",
        "preguntas": [
            "¿Qué porcentaje de clientes necesita realmente ajuste específico?",
            "¿Qué parte de la personalización es estética y qué parte funcional?",
            "¿Cómo se reduce el riesgo de error en fitting?"
        ],
        "acciones": [
            "Medir mix RTW/MTM.",
            "Registrar incidencias de fit.",
            "Crear argumento comercial claro para escáner, horma y recomendación."
        ]
    },
    "Piel, fabricación y artesanía": {
        "concepto": "Base tangible de calidad: selección de piel, construcción, acabado, comodidad, durabilidad y reparabilidad.",
        "preguntas": [
            "¿Qué pieles elevan percepción sin destruir margen?",
            "¿Qué construcción entiende y valora el cliente?",
            "¿Qué elementos productivos son realmente diferenciales?"
        ],
        "acciones": [
            "Formar al equipo en pieles y construcción.",
            "Traducir tecnicismos a beneficios para cliente.",
            "Medir devoluciones, arreglos e incidencias por proveedor."
        ]
    },
    "Retail premium y experiencia": {
        "concepto": "La tienda como espacio de confianza, asesoramiento experto, prueba, relación y conversión premium.",
        "preguntas": [
            "¿La experiencia justifica desplazamiento y precio?",
            "¿El vendedor actúa como asesor o como despachador?",
            "¿Dónde se produce el momento de confianza?"
        ],
        "acciones": [
            "Diseñar ritual de prueba.",
            "Medir ratio prueba/compra.",
            "Crear guion de venta consultiva y diagnóstico."
        ]
    },
    "Competidores y marcas referencia": {
        "concepto": "Seguimiento de marcas aspiracionales o comparables para entender precios, productos, canales y mensajes.",
        "preguntas": [
            "¿Quién marca el precio psicológico del segmento?",
            "¿Qué competidor educa mejor al cliente?",
            "¿Dónde existe hueco de posicionamiento?"
        ],
        "acciones": [
            "Actualizar benchmark trimestral.",
            "Seguir lanzamientos y aperturas.",
            "Comparar propuesta de valor, no solo precio."
        ]
    }
}

INSPIRACION = {
    "Producto": {
        "keywords": ["oxford", "derby", "loafer", "monk", "boot", "horma", "last", "silhouette", "design", "material", "leather", "piel", "suede", "cordovan", "sole", "Goodyear"],
        "preguntas": [
            "¿Qué marcas están redefiniendo el zapato formal en materiales, hormas o construcción?",
            "¿Dónde se produce la hibridación entre formal y casual?",
            "¿Qué detalles elevan la percepción de lujo?",
            "¿Qué modelos se están convirtiendo en iconos contemporáneos?"
        ]
    },
    "Experiencia de cliente": {
        "keywords": ["store experience", "retail experience", "clienteling", "service", "customer journey", "in-store", "boutique", "appointment", "asesoramiento", "experience"],
        "preguntas": [
            "¿Qué marcas crean experiencias memorables en tienda?",
            "¿Dónde el proceso de prueba se convierte en parte del valor?",
            "¿Qué ejemplos existen de venta consultiva real?",
            "¿Qué retailers convierten la tienda en destino?"
        ]
    },
    "Personalización": {
        "keywords": ["bespoke", "made to measure", "custom", "personalization", "personalización", "3D", "foot scanning", "fit", "fitting", "last", "horma"],
        "preguntas": [
            "¿Quién lidera el Made to Measure o bespoke a nivel global?",
            "¿Cómo se comunica la personalización sin complejidad?",
            "¿Qué tecnologías mejoran el fitting?",
            "¿Qué parte de la personalización es emocional y qué parte funcional?"
        ]
    },
    "Marca y posicionamiento": {
        "keywords": ["brand", "heritage", "quiet luxury", "luxury", "premium", "craftsmanship", "storytelling", "made in", "artesanía", "lujo", "positioning"],
        "preguntas": [
            "¿Qué marcas construyen relato sin depender del descuento?",
            "¿Cómo se comunica hoy la artesanía de forma contemporánea?",
            "¿Quién gana en quiet luxury dentro del calzado?",
            "¿Qué marcas captan mejor al cliente internacional?"
        ]
    },
    "Canal y distribución": {
        "keywords": ["retail", "wholesale", "department store", "corner", "pop-up", "trunk show", "multibrand", "boutique", "distribution", "channel", "store opening"],
        "preguntas": [
            "¿Dónde venden mejor las marcas premium: tienda propia, multimarca o department store?",
            "¿Qué espacios generan tráfico cualificado?",
            "¿Qué colaboraciones generan autoridad y venta?",
            "¿Qué retailers actúan como curadores de producto?"
        ]
    },
    "Pricing y valor": {
        "keywords": ["price", "pricing", "premium price", "discount", "margin", "ASP", "value", "luxury price", "margen", "precio"],
        "preguntas": [
            "¿Qué marcas suben precio sin perder demanda?",
            "¿Cómo justifican el precio: producto, servicio, marca o escasez?",
            "¿Dónde está el límite psicológico del cliente?",
            "¿Qué estrategias evitan la erosión por descuento?"
        ]
    },
    "Inspiración fuera del sector": {
        "keywords": ["watch", "watches", "hospitality", "hotel", "automotive", "tailoring", "sartorial", "jewelry", "clinic", "concierge", "private club"],
        "preguntas": [
            "¿Qué puede aprender el calzado de relojería, sastrería, automoción u hospitality?",
            "¿Qué rituales de servicio premium pueden trasladarse a tienda?",
            "¿Qué sectores educan mejor al cliente en valor y precio?",
            "¿Qué experiencias externas podrían convertirse en ventaja competitiva?"
        ]
    }
}

LANGUAGES = {"Español": "es", "Inglés": "en"}
COUNTRIES = {"España": "ES", "Estados Unidos": "US", "Reino Unido": "GB", "Francia": "FR", "Italia": "IT"}

KEYWORDS_POSITIVE = [
    "growth", "crecimiento", "crece", "increase", "aumenta", "ventas", "sales",
    "profit", "beneficio", "premium", "luxury", "lujo", "bespoke", "made to measure",
    "craftsmanship", "artesanía", "expansion", "apertura", "heritage", "margen"
]
KEYWORDS_NEGATIVE = [
    "fall", "decline", "cae", "descenso", "crisis", "loss", "pérdida", "closure",
    "cierre", "weak", "débil", "discount", "descuento", "pressure", "presión",
    "bankruptcy", "quiebra", "layoffs", "despidos"
]
KEYWORDS_RISK = [
    "cost", "costes", "leather prices", "piel", "raw materials", "materias primas",
    "supply chain", "logística", "tariff", "arancel", "inflation", "inflación",
    "counterfeit", "falsificación", "competition", "competencia", "margin pressure",
    "China", "labour", "huelga"
]
KEYWORDS_TREND = [
    "bespoke", "made to measure", "custom", "personalization", "personalización",
    "3D", "foot scanning", "smart casual", "quiet luxury", "heritage", "craftsmanship",
    "Goodyear", "loafer", "oxford", "derby", "sneakerization", "comfort", "wellness",
    "wedding", "ceremony", "ceremonia"
]

def limpiar_html(texto):
    if not texto:
        return ""
    texto = re.sub("<.*?>", "", texto)
    texto = texto.replace("&nbsp;", " ").replace("&amp;", "&")
    return texto.strip()

def construir_google_news_rss(query, lang="es", country="ES"):
    query_encoded = requests.utils.quote(query)
    return f"https://news.google.com/rss/search?q={query_encoded}&hl={lang}&gl={country}&ceid={country}:{lang}"

@st.cache_data(ttl=1800, show_spinner=False)
def obtener_noticias(query, lang="es", country="ES", max_items=8):
    url = construir_google_news_rss(query, lang, country)
    feed = feedparser.parse(url)
    noticias = []

    for entry in feed.entries[:max_items]:
        fuente = ""
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
    relevancia = score_pos + score_neg + score_risk + score_trend

    return impacto, riesgo, tendencia, relevancia

def detectar_inspiracion(titulo, resumen):
    texto = f"{titulo} {resumen}".lower()
    scores = {}

    for area, data in INSPIRACION.items():
        scores[area] = sum(1 for kw in data["keywords"] if kw.lower() in texto)

    area_principal = max(scores, key=scores.get)
    score_principal = scores[area_principal]

    if score_principal == 0:
        return "General", 0

    return area_principal, score_principal

@st.cache_data(ttl=1800, show_spinner=False)
def cargar_noticias(bloques_activos, lang, country, max_items):
    registros = []

    for bloque in bloques_activos:
        for query in BLOQUES[bloque]["queries"]:
            noticias = obtener_noticias(query, lang, country, max_items)
            for n in noticias:
                impacto, riesgo, tendencia, relevancia = clasificar_texto(n["Titular"], n["Resumen"])
                inspiracion_area, inspiracion_score = detectar_inspiracion(n["Titular"], n["Resumen"])

                n["Bloque"] = bloque
                n["Impacto"] = impacto
                n["Riesgo"] = riesgo
                n["Tendencia"] = tendencia
                n["Relevancia"] = relevancia
                n["Inspiración"] = inspiracion_area
                n["Score inspiración"] = inspiracion_score
                registros.append(n)

    df = pd.DataFrame(registros)

    if df.empty:
        return df

    return df.drop_duplicates(subset=["Titular"]).sort_values(
        ["Relevancia", "Score inspiración"], ascending=False
    )

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

def construir_df_inspiracion():
    rows = []
    for area, data in INSPIRACION.items():
        rows.append({
            "Área de inspiración": area,
            "Preguntas clave": " | ".join(data["preguntas"]),
            "Palabras clave": " | ".join(data["keywords"])
        })
    return pd.DataFrame(rows)

def preparar_excel(df_news, df_formacion, df_inspiracion):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_news.to_excel(writer, index=False, sheet_name="Noticias")
        df_formacion.to_excel(writer, index=False, sheet_name="Formacion")
        df_inspiracion.to_excel(writer, index=False, sheet_name="Inspiracion")

        workbook = writer.book
        header_format = workbook.add_format({"bold": True, "bg_color": "#D9EAF7", "border": 1})

        for sheet_name, df_temp in [("Noticias", df_news), ("Formacion", df_formacion), ("Inspiracion", df_inspiracion)]:
            worksheet = writer.sheets[sheet_name]
            for col_num, value in enumerate(df_temp.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 28)

    return output.getvalue()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Configuración")

idioma_label = st.sidebar.selectbox("Idioma noticias", list(LANGUAGES.keys()), index=0)
pais_label = st.sidebar.selectbox("País base", list(COUNTRIES.keys()), index=0)
max_items = st.sidebar.slider("Noticias por búsqueda", 3, 20, 8)

bloques_activos = st.sidebar.multiselect(
    "Bloques activos",
    list(BLOQUES.keys()),
    default=list(BLOQUES.keys())
)

lang = LANGUAGES[idioma_label]
country = COUNTRIES[pais_label]

with st.spinner("Cargando inteligencia sectorial..."):
    df_news = cargar_noticias(bloques_activos, lang, country, max_items)

df_formacion = construir_df_formacion()
df_inspiracion = construir_df_inspiracion()

tab_dashboard, tab_news, tab_strategy, tab_inspiration, tab_training, tab_kpis, tab_export = st.tabs([
    "📊 Dashboard",
    "📰 Noticias",
    "🧠 Lectura estratégica",
    "💡 Inspiración",
    "🎓 Formación",
    "📈 KPIs",
    "📥 Exportación"
])

# ============================================================
# DASHBOARD
# ============================================================

with tab_dashboard:
    st.subheader("📊 Panel ejecutivo")

    if df_news.empty:
        st.warning("No se han encontrado noticias. Prueba con otro idioma, país o bloque.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Noticias", len(df_news))
        col2.metric("Impacto positivo", len(df_news[df_news["Impacto"] == "Positivo"]))
        col3.metric("Riesgo alto", len(df_news[df_news["Riesgo"] == "Alto"]))
        col4.metric("Tendencia alta", len(df_news[df_news["Tendencia"] == "Alta"]))
        col5.metric("Inspiración detectada", len(df_news[df_news["Inspiración"] != "General"]))

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
        st.dataframe(
            df_news.head(12)[["Bloque", "Inspiración", "Titular", "Fuente", "Impacto", "Riesgo", "Tendencia", "Relevancia", "Link"]],
            use_container_width=True
        )

# ============================================================
# NOTICIAS
# ============================================================

with tab_news:
    st.subheader("📰 Noticias clasificadas")

    if df_news.empty:
        st.warning("No hay noticias disponibles.")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        filtro_bloque = c1.selectbox("Bloque", ["Todos"] + sorted(df_news["Bloque"].unique()))
        filtro_impacto = c2.selectbox("Impacto", ["Todos"] + sorted(df_news["Impacto"].unique()))
        filtro_riesgo = c3.selectbox("Riesgo", ["Todos"] + sorted(df_news["Riesgo"].unique()))
        filtro_tendencia = c4.selectbox("Tendencia", ["Todos"] + sorted(df_news["Tendencia"].unique()))
        filtro_inspiracion = c5.selectbox("Inspiración", ["Todos"] + sorted(df_news["Inspiración"].unique()))

        df_view = df_news.copy()

        if filtro_bloque != "Todos":
            df_view = df_view[df_view["Bloque"] == filtro_bloque]
        if filtro_impacto != "Todos":
            df_view = df_view[df_view["Impacto"] == filtro_impacto]
        if filtro_riesgo != "Todos":
            df_view = df_view[df_view["Riesgo"] == filtro_riesgo]
        if filtro_tendencia != "Todos":
            df_view = df_view[df_view["Tendencia"] == filtro_tendencia]
        if filtro_inspiracion != "Todos":
            df_view = df_view[df_view["Inspiración"] == filtro_inspiracion]

        for _, row in df_view.head(80).iterrows():
            with st.container(border=True):
                st.markdown(f"### [{row['Titular']}]({row['Link']})")
                st.write(f"**Bloque:** {row['Bloque']} | **Fuente:** {row['Fuente']}")
                st.write(f"**Impacto:** {row['Impacto']} · **Riesgo:** {row['Riesgo']} · **Tendencia:** {row['Tendencia']} · **Inspiración:** {row['Inspiración']}")
                if row["Resumen"]:
                    st.caption(row["Resumen"][:420])

# ============================================================
# ESTRATEGIA
# ============================================================

with tab_strategy:
    st.subheader("🧠 Lectura estratégica")

    if df_news.empty:
        st.warning("No hay datos suficientes para elaborar lectura estratégica.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### ⚠️ Riesgos a vigilar")
            riesgos = df_news[df_news["Riesgo"] == "Alto"].head(10)
            if riesgos.empty:
                st.write("No se detectan riesgos altos.")
            else:
                for _, row in riesgos.iterrows():
                    st.write(f"- **{row['Bloque']}** · [{row['Titular']}]({row['Link']})")

            st.markdown("### 📉 Señales negativas")
            negativas = df_news[df_news["Impacto"] == "Negativo"].head(10)
            if negativas.empty:
                st.write("No se detectan señales negativas destacadas.")
            else:
                for _, row in negativas.iterrows():
                    st.write(f"- **{row['Bloque']}** · [{row['Titular']}]({row['Link']})")

        with col2:
            st.markdown("### 🚀 Tendencias emergentes")
            tendencias = df_news[df_news["Tendencia"] == "Alta"].head(10)
            if tendencias.empty:
                st.write("No se detectan tendencias altas.")
            else:
                for _, row in tendencias.iterrows():
                    st.write(f"- **{row['Bloque']}** · [{row['Titular']}]({row['Link']})")

            st.markdown("### 📈 Señales positivas")
            positivas = df_news[df_news["Impacto"] == "Positivo"].head(10)
            if positivas.empty:
                st.write("No se detectan señales positivas destacadas.")
            else:
                for _, row in positivas.iterrows():
                    st.write(f"- **{row['Bloque']}** · [{row['Titular']}]({row['Link']})")

        bloque_mas_activo = df_news["Bloque"].value_counts().idxmax()
        st.info(
            f"El bloque con mayor actividad informativa es **{bloque_mas_activo}**. "
            "Conviene analizar si las señales apuntan a recuperación del formal, expansión del premium, presión de costes, avance de la personalización o nuevas fuentes de inspiración."
        )

        st.markdown("## 💡 Preguntas de inspiración estratégica")
        st.write("Utiliza estas preguntas como filtro directivo para convertir noticias en ideas accionables.")

        for area, data in INSPIRACION.items():
            with st.expander(area):
                for pregunta in data["preguntas"]:
                    st.write(f"- {pregunta}")

# ============================================================
# INSPIRACIÓN
# ============================================================

with tab_inspiration:
    st.subheader("💡 Radar de inspiración")

    st.write(
        "Este apartado detecta si una noticia puede inspirar decisiones de producto, experiencia, personalización, marca, canal, pricing o referencias fuera del sector."
    )

    st.markdown("### Mapa de inspiración")
    st.dataframe(df_inspiracion[["Área de inspiración", "Preguntas clave"]], use_container_width=True)

    if df_news.empty:
        st.warning("No hay noticias para analizar.")
    else:
        inspiracion_counts = df_news["Inspiración"].value_counts().reset_index()
        inspiracion_counts.columns = ["Área", "Noticias"]

        st.markdown("### Noticias por tipo de inspiración")
        st.dataframe(inspiracion_counts, use_container_width=True)

        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.bar(inspiracion_counts["Área"], inspiracion_counts["Noticias"])
        ax2.set_title("Distribución de inspiración detectada")
        ax2.tick_params(axis="x", rotation=35)
        st.pyplot(fig2)

        area_sel = st.selectbox(
            "Selecciona área de inspiración",
            ["Todas"] + sorted(df_news["Inspiración"].unique())
        )

        df_ins = df_news.copy()
        if area_sel != "Todas":
            df_ins = df_ins[df_ins["Inspiración"] == area_sel]

        st.markdown("### Noticias inspiradoras")
        for _, row in df_ins[df_ins["Inspiración"] != "General"].head(30).iterrows():
            with st.container(border=True):
                st.markdown(f"### [{row['Titular']}]({row['Link']})")
                st.write(f"**Inspiración:** {row['Inspiración']} | **Bloque:** {row['Bloque']} | **Fuente:** {row['Fuente']}")
                st.caption(row["Resumen"][:360] if row["Resumen"] else "")

# ============================================================
# FORMACIÓN
# ============================================================

with tab_training:
    st.subheader("🎓 Módulo formativo")

    bloque_formacion = st.selectbox("Selecciona bloque formativo", list(FORMACION.keys()))
    data = FORMACION[bloque_formacion]

    st.markdown(f"## {bloque_formacion}")
    st.write(data["concepto"])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Preguntas clave")
        for pregunta in data["preguntas"]:
            st.write(f"- {pregunta}")

    with col2:
        st.markdown("### Acciones recomendadas")
        for accion in data["acciones"]:
            st.write(f"- {accion}")

    st.markdown("### KPIs recomendados")
    st.write(", ".join(BLOQUES[bloque_formacion]["kpis"]))

    st.success(
        "La ventaja en calzado masculino formal no está solo en el producto: está en unir ajuste, relato, servicio experto, experiencia y consistencia comercial."
    )

# ============================================================
# KPIS
# ============================================================

with tab_kpis:
    st.subheader("📈 KPIs por bloque estratégico")

    rows = []
    for bloque, data in BLOQUES.items():
        for kpi in data["kpis"]:
            rows.append({
                "Bloque": bloque,
                "KPI": kpi,
                "Uso directivo": "Medir rendimiento, comparar tiendas/canales y priorizar acciones comerciales"
            })

    df_kpis = pd.DataFrame(rows)
    st.dataframe(df_kpis, use_container_width=True, height=520)

    st.markdown("### KPIs especialmente relevantes")
    st.write(
        "**Mix RTW/MTM, ticket medio, conversión, ventas por m², repetición, ratio prueba/compra, margen por modelo y plazo de entrega.**"
    )

# ============================================================
# EXPORTACIÓN
# ============================================================

with tab_export:
    st.subheader("📥 Exportación")

    excel = preparar_excel(df_news, df_formacion, df_inspiracion)

    st.download_button(
        "📥 Descargar informe Excel",
        data=excel,
        file_name=f"formal_menswear_footwear_intelligence_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("### Archivos necesarios")
    st.code("app.py\nrequirements.txt", language="text")

st.caption("Noticias vía Google News RSS. Clasificación automática por palabras clave estratégicas. Puede evolucionarse con IA generativa/API para análisis más profundo.")
