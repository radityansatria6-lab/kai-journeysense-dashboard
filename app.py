import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Optional

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="KAI JourneySense Dashboard",
    page_icon="🚆",
    layout="wide"
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
      div[data-testid="stMetricValue"] { font-size: 1.55rem; }
      div[data-testid="stMetricLabel"] { font-size: 0.9rem; }
      .small-note { color: #6B7280; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True
)

EXPECTED_COLS = [
    "date", "country", "language", "route", "purpose",
    "ticket_class", "touchpoint", "satisfaction",
    "positive_feedback", "pain_point"
]

# =========================================================
# KAI STAR (Conceptual) - Tourism Recommendation Data
# =========================================================
KAI_STAR_SCALE = {
    3: "★★★ KAI Star – Wajib Dikunjungi",
    2: "★★ KAI Star – Sangat Direkomendasikan",
    1: "★ KAI Star – Direkomendasikan",
}

ROUTE_TO_DEST = {
    "Jakarta–Bandung": "Bandung",
    "Jakarta–Yogyakarta": "Yogyakarta",
    "Jakarta–Surabaya": "Surabaya",
    "Bandung–Yogyakarta": "Yogyakarta",
    "Yogyakarta–Surabaya": "Surabaya",
    "Surabaya–Malang": "Malang",
}

# Konseptual: rating internal KAI (bukan rating publik resmi)
KAI_TOURISM_RECS = {
    "Bandung": [
        {"place": "Kawah Putih Ciwidey", "kai_star": 3, "category": "Nature",
         "why": "Pengalaman alam unik, visual kuat, cocok wisatawan internasional."},
        {"place": "Jalan Braga", "kai_star": 2, "category": "Heritage & City Walk",
         "why": "Ikonik, mudah diakses, city vibe & foto."},
        {"place": "Gedung Sate", "kai_star": 2, "category": "Landmark",
         "why": "Landmark kota, pengalaman singkat namun memorable."},
    ],
    "Yogyakarta": [
        {"place": "Candi Prambanan", "kai_star": 3, "category": "UNESCO Heritage",
         "why": "Destinasi kelas dunia, nilai budaya tinggi."},
        {"place": "Keraton Yogyakarta", "kai_star": 3, "category": "Culture",
         "why": "Pengalaman budaya autentik dan edukatif."},
        {"place": "Malioboro", "kai_star": 2, "category": "City Experience",
         "why": "Pusat pengalaman kota, kuliner, dan belanja."},
    ],
    "Surabaya": [
        {"place": "Tugu Pahlawan", "kai_star": 2, "category": "History",
         "why": "Ikon sejarah nasional, mudah dijangkau."},
        {"place": "Kota Tua Surabaya (Kembang Jepun)", "kai_star": 2, "category": "Heritage",
         "why": "Area heritage cocok untuk city photography."},
        {"place": "House of Sampoerna", "kai_star": 1, "category": "Museum",
         "why": "Museum populer dengan pengalaman tur singkat."},
    ],
    "Malang": [
        {"place": "Bromo (akses via Malang)", "kai_star": 3, "category": "Nature",
         "why": "Destinasi internasional, pengalaman sunrise ikonik."},
        {"place": "Kampung Warna-Warni Jodipan", "kai_star": 2, "category": "City Spot",
         "why": "Visual kuat, cocok untuk wisata singkat."},
        {"place": "Alun-Alun Malang", "kai_star": 1, "category": "City Experience",
         "why": "Ruang publik nyaman untuk wisata santai."},
    ],
}

def get_destination_city(route: str) -> Optional[str]:
    return ROUTE_TO_DEST.get(route)

def build_kai_star_table(city: str) -> pd.DataFrame:
    items = KAI_TOURISM_RECS.get(city, [])
    if not items:
        return pd.DataFrame(columns=["KAI Star", "Tempat", "Kategori", "Alasan singkat"])
    df_rec = pd.DataFrame(items)
    df_rec["KAI Star"] = df_rec["kai_star"].map(KAI_STAR_SCALE)
    df_rec = df_rec.rename(columns={"place": "Tempat", "category": "Kategori", "why": "Alasan singkat"})
    df_rec = df_rec[["KAI Star", "Tempat", "Kategori", "Alasan singkat", "kai_star"]]
    df_rec = df_rec.sort_values(["kai_star", "Tempat"], ascending=[False, True]).drop(columns=["kai_star"])
    return df_rec

# =========================================================
# DATA: Dummy + Validation
# =========================================================
def make_dummy_data(n: int = 900) -> pd.DataFrame:
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
    routes = list(ROUTE_TO_DEST.keys())
    purposes = ["Leisure", "Business", "Family", "Backpacking"]
    classes = ["Economy", "Executive", "Luxury/Pariwisata"]
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
        p = random.choice(purposes)
        cls = random.choice(classes)
        tp = random.choice(touchpoints)

        # satisfaction slightly higher for Executive/Luxury
        base = 4.05 if cls == "Economy" else (4.35 if cls == "Executive" else 4.55)
        sat = max(1.0, min(5.0, random.gauss(base, 0.35)))

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
            "positive_feedback": random.choice(positives),
            "pain_point": random.choice(pain_points)
        })

    return pd.DataFrame(rows)

def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")

    df = df.copy()

    df["satisfaction"] = pd.to_numeric(df["satisfaction"], errors="coerce")
    df = df.dropna(subset=["satisfaction"])
    df["satisfaction"] = df["satisfaction"].clip(1, 5)

    # Normalize text columns
    for c in ["country", "language", "route", "purpose", "ticket_class", "touchpoint", "positive_feedback", "pain_point"]:
        df[c] = df[c].astype(str).str.strip()

    # Parse date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["date"] = df["date"].dt.date

    return df

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Settings")

lang_mode = st.sidebar.selectbox("Language", ["English", "Bilingual (EN/ID)"], index=1)

def t(en: str, idn: str) -> str:
    return en if lang_mode == "English" else f"{en}\n{idn}"

data_mode = st.sidebar.radio(
    t("Data source", "Sumber data"),
    [t("Use dummy data (recommended for proposal)", "Gunakan dummy data (disarankan untuk proposal)"),
     t("Upload CSV", "Unggah CSV")],
    index=0
)

uploaded = None
if "Upload CSV" in data_mode:
    uploaded = st.sidebar.file_uploader(t("Upload CSV file", "Unggah file CSV"), type=["csv"])
    st.sidebar.markdown(
        "<div class='small-note'>CSV columns: " + ", ".join(EXPECTED_COLS) + "</div>",
        unsafe_allow_html=True
    )

# Load data
if "dummy" in data_mode.lower():
    df = validate_and_clean(make_dummy_data(1000))
else:
    if uploaded is None:
        st.warning(t("Please upload a CSV file, or switch to dummy data.",
                     "Silakan unggah CSV, atau gunakan dummy data."))
        st.stop()
    try:
        df_raw = pd.read_csv(uploaded)
        df = validate_and_clean(df_raw)
    except Exception as e:
        st.error(f"{t('Failed to read/validate CSV', 'Gagal membaca/memvalidasi CSV')}: {e}")
        st.stop()

# Filters
st.sidebar.subheader(t("Filters", "Filter"))
countries = sorted(df["country"].unique())
routes = sorted(df["route"].unique())
classes = sorted(df["ticket_class"].unique())
purposes = sorted(df["purpose"].unique())

sel_country = st.sidebar.multiselect(t("Country", "Negara"), countries, default=countries)
sel_route = st.sidebar.multiselect(t("Route", "Rute"), routes, default=routes)
sel_class = st.sidebar.multiselect(t("Ticket Class", "Kelas"), classes, default=classes)
sel_purpose = st.sidebar.multiselect(t("Purpose", "Tujuan perjalanan"), purposes, default=purposes)

min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input(
    t("Date range", "Rentang tanggal"),
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

# =========================================================
# HEADER
# =========================================================
st.title("🚆 KAI JourneySense – International Tourism Insight Dashboard")
st.caption(
    t(
        "Conceptual dashboard to support data-driven branding and journey experience for international tourists.",
        "Dashboard konseptual untuk mendukung branding berbasis data dan pengalaman perjalanan wisatawan internasional."
    )
)

# =========================================================
# KPI
# =========================================================
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

# =========================================================
# EXEC SUMMARY
# =========================================================
st.subheader(t("Executive Summary", "Ringkasan Eksekutif"))
if total == 0:
    st.info(t("No data after filters. Please adjust filters.",
              "Tidak ada data setelah filter. Silakan ubah filter."))
else:
    worst_touch = filtered.groupby("touchpoint")["satisfaction"].mean().sort_values().index[0]
    worst_route = filtered.groupby("route")["satisfaction"].mean().sort_values().index[0]
    top_pain = filtered["pain_point"].value_counts().index[0]
    top_pos = filtered["positive_feedback"].value_counts().index[0]

    bullets = [
        t(f"Priority touchpoint to improve: {worst_touch}.",
          f"Touchpoint prioritas untuk ditingkatkan: {worst_touch}."),
        t(f"Route needing attention: {worst_route}.",
          f"Rute yang perlu perhatian: {worst_route}."),
        t(f"Most frequent pain point: {top_pain}.",
          f"Pain point paling sering: {top_pain}."),
        t(f"Brand strength to amplify: {top_pos}.",
          f"Kekuatan layanan untuk diperkuat: {top_pos}."),
    ]
    for b in bullets:
        st.write("• " + b)

st.divider()

# =========================================================
# CHARTS
# =========================================================
c1, c2 = st.columns(2)

with c1:
    st.subheader(t("Origin Country Distribution", "Distribusi Negara Asal"))
    country_counts = filtered["country"].value_counts().reset_index()
    country_counts.columns = ["country", "count"]
    st.plotly_chart(px.bar(country_counts, x="country", y="count"), use_container_width=True)

with c2:
    st.subheader(t("Top Routes", "Rute Teratas"))
    route_counts = filtered["route"].value_counts().reset_index()
    route_counts.columns = ["route", "count"]
    st.plotly_chart(px.bar(route_counts, x="route", y="count"), use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader(t("Satisfaction by Ticket Class", "Kepuasan per Kelas"))
    st.plotly_chart(px.box(filtered, x="ticket_class", y="satisfaction"), use_container_width=True)

with c4:
    st.subheader(t("Satisfaction by Touchpoint", "Kepuasan per Touchpoint"))
    st.plotly_chart(px.box(filtered, x="touchpoint", y="satisfaction"), use_container_width=True)

st.divider()

# =========================================================
# PAIN POINTS & POSITIVES
# =========================================================
p1, p2 = st.columns(2)

with p1:
    st.subheader(t("Top Pain Points", "Pain Point Teratas"))
    pp = filtered["pain_point"].value_counts().reset_index()
    pp.columns = ["pain_point", "count"]
    st.plotly_chart(px.bar(pp.head(10), x="pain_point", y="count"), use_container_width=True)

with p2:
    st.subheader(t("Top Positive Feedback", "Feedback Positif Teratas"))
    pf = filtered["positive_feedback"].value_counts().reset_index()
    pf.columns = ["positive_feedback", "count"]
    st.plotly_chart(px.bar(pf.head(10), x="positive_feedback", y="count"), use_container_width=True)

st.divider()

# =========================================================
# RECOMMENDED ACTIONS (conceptual)
# =========================================================
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
        t("Standardize global-friendly communication tone across key touchpoints (English-first).",
          "Standarisasi tone komunikasi ramah global pada touchpoint utama (English-first)."),
        t("Embed lightweight local cultural storytelling on high-tourist routes.",
          "Integrasikan storytelling budaya lokal yang ringan pada rute wisata."),
    ]
    for r in recs:
        st.write("• " + r)

st.divider()

# =========================================================
# KAI STAR TOURISM RECOMMENDATIONS (Michelin-like, conceptual)
# =========================================================
st.subheader(t("Tourism Recommendations (KAI Star – Conceptual)", "Rekomendasi Pariwisata (KAI Star – Konseptual)"))

if total == 0:
    st.info(t("No data after filters.", "Tidak ada data setelah filter."))
else:
    # Pilih rute dominan dari data terfilter
    primary_route = filtered["route"].value_counts().index[0]
    dest_city = get_destination_city(primary_route)

    leftA, rightA = st.columns([1, 2])

    with leftA:
        st.markdown("**" + t("Primary tourist route", "Rute utama wisatawan") + "**")
        st.write(primary_route)

        st.markdown("**" + t("Destination city", "Kota tujuan") + "**")
        st.write(dest_city if dest_city else "-")

        st.caption(
            t(
                "KAI Star is an internal conceptual rating (not a public official rating).",
                "KAI Star adalah penilaian internal konseptual (bukan rating publik resmi)."
            )
        )

        min_star = st.selectbox(
            t("Minimum KAI Star", "Minimal KAI Star"),
            options=[1, 2, 3],
            index=0
        )

    with rightA:
        if not dest_city:
            st.warning(t(
                "Destination city mapping not available for this route yet.",
                "Mapping kota tujuan belum tersedia untuk rute ini."
            ))
        else:
            rec_df = build_kai_star_table(dest_city)
            if rec_df.empty:
                st.info(t(
                    "No recommendations available for this city yet.",
                    "Belum ada rekomendasi untuk kota ini."
                ))
            else:
                # filter by minimum star
                def star_count(label: str) -> int:
                    return label.count("★")

                rec_df["_stars"] = rec_df["KAI Star"].apply(star_count)
                rec_df = rec_df[rec_df["_stars"] >= min_star].drop(columns=["_stars"])

                st.dataframe(rec_df, use_container_width=True, hide_index=True)
                st.caption(
                    t(
                        "Conceptual criteria example: accessibility from station, safety, experience quality, memorability.",
                        "Contoh kriteria konseptual: akses dari stasiun, keamanan, kualitas pengalaman, tingkat memorable."
                    )
                )

st.divider()

# =========================================================
# EXPORT
# =========================================================
st.subheader(t("Export (for proposal appendix)", "Ekspor (untuk lampiran proposal)"))

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

colA, colB = st.columns([1, 2])

with colA:
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
    st.dataframe(insight_df, use_container_width=True, hide_index=True)
    st.markdown(
        "<div class='small-note'>"
        + t(
            "Use exports as appendix evidence (conceptual prototype).",
            "Gunakan hasil ekspor sebagai bukti lampiran (prototype konseptual)."
        )
        + "</div>",
        unsafe_allow_html=True
    )

with st.expander(t("Preview filtered data", "Lihat data terfilter")):
    st.dataframe(filtered, use_container_width=True)

st.caption("© KAI JourneySense – conceptual dashboard prototype (for proposal use).")
