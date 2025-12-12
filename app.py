import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import StringIO

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="KAI JourneySense Dashboard",
    page_icon="🚆",
    layout="wide"
)

# -------------------------------------------------
# Styling (simple, clean)
# -------------------------------------------------
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
      div[data-testid="stMetricValue"] { font-size: 1.6rem; }
      div[data-testid="stMetricLabel"] { font-size: 0.9rem; }
      .small-note { color: #6B7280; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# Data utilities
# -------------------------------------------------
EXPECTED_COLS = [
    "date", "country", "language", "route", "purpose",
    "ticket_class", "touchpoint", "satisfaction",
    "positive_feedback", "pain_point"
]

def make_dummy_data(n: int = 800) -> pd.DataFrame:
    import random

    countries = [
        "Australia", "Singapore", "Malaysia", "Japan", "South Korea",
        "China", "India", "USA", "UK", "Germany", "France", "Netherlands"
    ]
    languages = {
        "Australia": "English", "Singapore": "English", "Malaysia": "English",
        "Japan": "Japanese", "South Korea": "Korean", "China": "Chinese",
        "India": "English", "USA": "English", "UK": "English",
        "Germany": "German", "France": "French", "Netherlands": "English"
    }
    routes = [
        "Jakarta–Bandung",
        "Jakarta–Yogyakarta",
        "Jakarta–Surabaya",
        "Bandung–Yogyakarta",
        "Yogyakarta–Surabaya",
        "Surabaya–Malang"
    ]
    travel_purpose = ["Leisure", "Business", "Family", "Backpacking"]
    ticket_class = ["Economy", "Executive", "Luxury/Pariwisata"]
    touchpoints = ["Website/App", "Station", "On-train", "Customer Service"]
    pain_points = [
        "Language barrier at station",
        "Ticketing confusion",
        "Wayfinding signage",
        "Payment method limitations",
        "Seat comfort",
        "Schedule clarity"
    ]
    positives = [
        "On-time departure",
        "Comfortable seating",
        "Easy booking",
        "Clean station",
        "Friendly staff",
        "Scenic route experience"
    ]

    rows = []
    for _ in range(n):
        c = random.choice(countries)
        lang = languages.get(c, "English")
        r = random.choice(routes)
        p = random.choice(travel_purpose)
        cls = random.choice(ticket_class)
        tp = random.choice(touchpoints)

        base = 4.05 if cls == "Economy" else (4.35 if cls == "Executive" else 4.55)
        sat = max(1.0, min(5.0, random.gauss(base, 0.35)))

        pos = random.choice(positives)
        neg = random.choice(pain_points)

        # pseudo dates within a year
        year = 2025
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date = datetime(year, month, day).date().isoformat()

        rows.append({
            "date": date,
            "country": c,
            "language": lang,
            "route": r,
            "purpose": p,
            "ticket_class": cls,
            "touchpoint": tp,
            "satisfaction": round(sat, 2),
            "positive_feedback": pos,
            "pain_point": neg
        })

    return pd.DataFrame(rows)

def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")

    # Clean
    df = df.copy()
    df["satisfaction"] = pd.to_numeric(df["satisfaction"], errors="coerce")
    df = df.dropna(subset=["satisfaction"])
    df["satisfaction"] = df["satisfaction"].clip(1, 5)

    # Normalize text cols
    for c in ["country","language","route","purpose","ticket_class","touchpoint","positive_feedback","pain_point"]:
        df[c] = df[c].astype(str).str.strip()

    # Parse date best-effort
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["date"] = df["date"].dt.date

    return df

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
st.sidebar.title("⚙️ Settings")
st.sidebar.caption("Data source & filters")

data_mode = st.sidebar.radio(
    "Data source",
    ["Use dummy data (recommended for proposal)", "Upload CSV"],
    index=0
)

uploaded = None
if data_mode == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
    st.sidebar.markdown(
        "<div class='small-note'>CSV must include columns: "
        + ", ".join(EXPECTED_COLS) + "</div>",
        unsafe_allow_html=True
    )

lang_mode = st.sidebar.selectbox("Language", ["English", "Bilingual (EN/ID)"], index=0)

# Load data
if data_mode == "Use dummy data (recommended for proposal)":
    df = make_dummy_data(900)
    df = validate_and_clean(df)
else:
    if uploaded is None:
        st.warning("Please upload a CSV file, or switch to dummy data.")
        st.stop()
    try:
        df_raw = pd.read_csv(uploaded)
        df = validate_and_clean(df_raw)
    except Exception as e:
        st.error(f"Failed to read/validate CSV: {e}")
        st.stop()

# Filters
st.sidebar.subheader("Filters")
countries = sorted(df["country"].unique())
routes = sorted(df["route"].unique())
classes = sorted(df["ticket_class"].unique())
purposes = sorted(df["purpose"].unique())

sel_country = st.sidebar.multiselect("Country", countries, default=countries)
sel_route = st.sidebar.multiselect("Route", routes, default=routes)
sel_class = st.sidebar.multiselect("Ticket Class", classes, default=classes)
sel_purpose = st.sidebar.multiselect("Purpose", purposes, default=purposes)

min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    df["country"].isin(sel_country)
    & df["route"].isin(sel_route)
    & df["ticket_class"].isin(sel_class)
    & df["purpose"].isin(sel_purpose)
    & (df["date"] >= start_date)
    & (df["date"] <= end_date)
].copy()

# -------------------------------------------------
# Copy text helpers
# -------------------------------------------------
def t(en: str, idn: str) -> str:
    return en if lang_mode == "English" else f"{en}\n{idn}"

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("🚆 KAI JourneySense – International Tourism Insight Dashboard")
st.caption(
    t(
        "Conceptual dashboard to support data-driven branding and personalized journey experience.",
        "Dashboard konseptual untuk mendukung branding berbasis data dan pengalaman perjalanan yang lebih personal."
    )
)

# -------------------------------------------------
# KPIs
# -------------------------------------------------
total = len(filtered)
avg_sat = float(filtered["satisfaction"].mean()) if total else 0.0
top_country = filtered["country"].value_counts().index[0] if total else "-"
top_route = filtered["route"].value_counts().index[0] if total else "-"
low_sat_share = (filtered["satisfaction"] < 4.0).mean() * 100 if total else 0.0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(t("Trips (records)", "Perjalanan (record)"), f"{total:,}")
k2.metric(t("Avg satisfaction", "Rata-rata kepuasan"), f"{avg_sat:.2f} / 5")
k3.metric(t("Top origin", "Asal terbanyak"), top_country)
k4.metric(t("Top route", "Rute favorit"), top_route)
k5.metric(t("Below 4.0 share", "Proporsi < 4.0"), f"{low_sat_share:.1f}%")

st.divider()

# -------------------------------------------------
# Executive Summary (juri-friendly)
# -------------------------------------------------
st.subheader(t("Executive Summary", "Ringkasan Eksekutif"))

if total == 0:
    st.info(t("No data after filters. Please adjust filters.", "Tidak ada data setelah filter. Silakan ubah filter."))
else:
    worst_touch = filtered.groupby("touchpoint")["satisfaction"].mean().sort_values().index[0]
    worst_route = filtered.groupby("route")["satisfaction"].mean().sort_values().index[0]
    top_pain = filtered["pain_point"].value_counts().index[0]
    top_pos = filtered["positive_feedback"].value_counts().index[0]

    summary = [
        t(f"Priority touchpoint to improve: {worst_touch}.",
          f"Touchpoint prioritas untuk ditingkatkan: {worst_touch}."),
        t(f"Route needing attention: {worst_route}.",
          f"Rute yang perlu perhatian: {worst_route}."),
        t(f"Most frequent pain point: {top_pain}.",
          f"Pain point paling sering: {top_pain}."),
        t(f"Brand strength to amplify: {top_pos}.",
          f"Kekuatan layanan untuk diperkuat: {top_pos}."),
    ]
    for s in summary:
        st.write("• " + s)

st.divider()

# -------------------------------------------------
# Charts
# -------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader(t("Origin Country Distribution", "Distribusi Negara Asal"))
    country_counts = filtered["country"].value_counts().reset_index()
    country_counts.columns = ["country", "count"]
    fig_country = px.bar(country_counts, x="country", y="count")
    st.plotly_chart(fig_country, use_container_width=True)

with c2:
    st.subheader(t("Top Routes", "Rute Teratas"))
    route_counts = filtered["route"].value_counts().reset_index()
    route_counts.columns = ["route", "count"]
    fig_route = px.bar(route_counts, x="route", y="count")
    st.plotly_chart(fig_route, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader(t("Satisfaction by Ticket Class", "Kepuasan per Kelas"))
    fig_class = px.box(filtered, x="ticket_class", y="satisfaction")
    st.plotly_chart(fig_class, use_container_width=True)

with c4:
    st.subheader(t("Satisfaction by Touchpoint", "Kepuasan per Touchpoint"))
    fig_touch = px.box(filtered, x="touchpoint", y="satisfaction")
    st.plotly_chart(fig_touch, use_container_width=True)

st.divider()

# -------------------------------------------------
# Pain points & Positives
# -------------------------------------------------
p1, p2 = st.columns(2)

with p1:
    st.subheader(t("Top Pain Points", "Pain Point Teratas"))
    pp = filtered["pain_point"].value_counts().reset_index()
    pp.columns = ["pain_point", "count"]
    fig_pp = px.bar(pp.head(10), x="pain_point", y="count")
    st.plotly_chart(fig_pp, use_container_width=True)

with p2:
    st.subheader(t("Top Positive Feedback", "Feedback Positif Teratas"))
    pf = filtered["positive_feedback"].value_counts().reset_index()
    pf.columns = ["positive_feedback", "count"]
    fig_pf = px.bar(pf.head(10), x="positive_feedback", y="count")
    st.plotly_chart(fig_pf, use_container_width=True)

st.divider()

# -------------------------------------------------
# Recommendation panel (rule-based, conceptual)
# -------------------------------------------------
st.subheader(t("Recommended Actions (Conceptual)", "Rekomendasi Aksi (Konseptual)"))

if total == 0:
    st.info(t("No data after filters.", "Tidak ada data setelah filter."))
else:
    worst_touch = filtered.groupby("touchpoint")["satisfaction"].mean().sort_values().index[0]
    worst_route = filtered.groupby("route")["satisfaction"].mean().sort_values().index[0]
    top_pain = filtered["pain_point"].value_counts().index[0]

    recs = [
        t(f"Improve multilingual wayfinding and service clarity at: {worst_touch}.",
          f"Tingkatkan wayfinding multibahasa dan kejelasan layanan pada: {worst_touch}."),
        t(f"Pilot JourneySense enhancements on route: {worst_route}.",
          f"Uji coba peningkatan JourneySense pada rute: {worst_route}."),
        t(f"Fix the top friction: {top_pain}.",
          f"Prioritaskan perbaikan pain point utama: {top_pain}."),
        t("Standardize a global-friendly tone (English-first) across key touchpoints.",
          "Standarisasi tone komunikasi ramah global (English-first) pada touchpoint utama."),
        t("Embed local cultural storytelling on high-tourist routes (lightweight, non-intrusive).",
          "Integrasikan storytelling budaya lokal pada rute wisata (ringan dan tidak mengganggu).")
    ]
    for r in recs:
        st.write("• " + r)

st.divider()

# -------------------------------------------------
# Export (for proposal evidence)
# -------------------------------------------------
st.subheader(t("Export (for proposal appendix)", "Ekspor (untuk lampiran proposal)"))

colA, colB = st.columns([1, 2])

with colA:
    # Build a small insights table
    if total == 0:
        insight_df = pd.DataFrame([{"note": "No data"}])
    else:
        insight_df = pd.DataFrame([
            {"metric": "Trips (records)", "value": total},
            {"metric": "Avg satisfaction", "value": round(avg_sat, 2)},
            {"metric": "Top origin", "value": top_country},
            {"metric": "Top route", "value": top_route},
            {"metric": "Worst touchpoint", "value": worst_touch},
            {"metric": "Worst route", "value": worst_route},
            {"metric": "Top pain point", "value": top_pain},
        ])

    st.download_button(
        label=t("Download filtered data (CSV)", "Unduh data terfilter (CSV)"),
        data=df_to_csv_bytes(filtered),
        file_name="journeysense_filtered_data.csv",
        mime="text/csv"
    )

    st.download_button(
        label=t("Download executive insights (CSV)", "Unduh ringkasan insight (CSV)"),
        data=df_to_csv_bytes(insight_df),
        file_name="journeysense_executive_insights.csv",
        mime="text/csv"
    )

with colB:
    st.markdown(
        t(
            "Use exported CSV as evidence for the appendix (conceptual prototype).",
            "Gunakan CSV hasil ekspor sebagai bukti lampiran (prototype konseptual)."
        )
    )
    st.dataframe(insight_df, use_container_width=True)

# -------------------------------------------------
# Data preview (optional)
# -------------------------------------------------
with st.expander(t("Preview filtered data", "Lihat data terfilter")):
    st.dataframe(filtered, use_container_width=True)

st.caption("© KAI JourneySense – conceptual dashboard prototype (proposal use).")

