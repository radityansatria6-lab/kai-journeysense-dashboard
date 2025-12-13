import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Optional

# =========================
# CSS Loader
# =========================
def load_css(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {path}. Make sure it exists in your repo.")

def hero(title: str, subtitle: str, kicker: str, badges: list[str]):
    badges_html = "".join([f'<div class="kai-badge">{b}</div>' for b in badges])
    st.markdown(
        f"""
        <div class="kai-hero">
          <div class="kai-kicker">{kicker}</div>
          <div class="kai-title">{title}</div>
          <div class="kai-subtitle">{subtitle}</div>
          <div class="kai-badges">{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def section(title: str, chip: str = ""):
    st.markdown(
        f"""
        <div class="kai-section">
          <div class="label">{title}</div>
          {f'<div class="kai-chip">{chip}</div>' if chip else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

def kpi_card(title: str, value: str, hint: str = ""):
    st.markdown(
        f"""
        <div class="kai-kpi">
          <div class="label">{title}</div>
          <div class="value">{value}</div>
          {f'<div class="hint">{hint}</div>' if hint else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================
# Page Config
# =========================
st.set_page_config(page_title="KAI JourneySense Dashboard", page_icon="🚆", layout="wide")
load_css("styles/main.css")

# =========================
# Constants & Concept Data
# =========================
EXPECTED_COLS = [
    "date", "country", "language", "route", "purpose",
    "ticket_class", "touchpoint", "satisfaction",
    "positive_feedback", "pain_point"
]

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

KAI_TOURISM_RECS = {
    "Bandung": [
        {"place": "Kawah Putih Ciwidey", "kai_star": 3, "category": "Nature",
         "why": "Pengalaman alam unik dan sangat memorable."},
        {"place": "Jalan Braga", "kai_star": 2, "category": "Heritage",
         "why": "Ikonik, mudah dijangkau, cocok untuk first-timer."},
        {"place": "Gedung Sate", "kai_star": 2, "category": "Landmark",
         "why": "Landmark kota dengan nilai sejarah."},
    ],
    "Yogyakarta": [
        {"place": "Candi Prambanan", "kai_star": 3, "category": "UNESCO Heritage",
         "why": "Destinasi kelas dunia bernilai budaya tinggi."},
        {"place": "Keraton Yogyakarta", "kai_star": 3, "category": "Culture",
         "why": "Pengalaman budaya autentik dan edukatif."},
        {"place": "Malioboro", "kai_star": 2, "category": "City Experience",
         "why": "Pusat aktivitas wisata kota & belanja."},
    ],
    "Surabaya": [
        {"place": "Tugu Pahlawan", "kai_star": 2, "category": "History",
         "why": "Ikon sejarah nasional, mudah diakses."},
        {"place": "Kota Tua (Kembang Jepun)", "kai_star": 2, "category": "Heritage",
         "why": "Area heritage untuk city walk & foto."},
        {"place": "House of Sampoerna", "kai_star": 1, "category": "Museum",
         "why": "Museum populer untuk kunjungan singkat."},
    ],
    "Malang": [
        {"place": "Bromo (akses via Malang)", "kai_star": 3, "category": "Nature",
         "why": "Ikonik, pengalaman yang dicari wisatawan internasional."},
        {"place": "Kampung Warna-Warni Jodipan", "kai_star": 2, "category": "City Spot",
         "why": "Spot visual menarik untuk social sharing."},
        {"place": "Alun-Alun Malang", "kai_star": 1, "category": "City Experience",
         "why": "Ruang publik nyaman untuk wisata santai."},
    ],
}

CITY_COORDS = {
    "Bandung": {"lat": -6.9175, "lon": 107.6191},
    "Yogyakarta": {"lat": -7.7956, "lon": 110.3695},
    "Surabaya": {"lat": -7.2575, "lon": 112.7521},
    "Malang": {"lat": -7.9666, "lon": 112.6326},
}

KAI_DAY_ITINERARY = {
    "Bandung": [
        {"Time": "08:00", "Activity": "Sarapan & coffee stop"},
        {"Time": "09:30", "Activity": "Gedung Sate"},
        {"Time": "11:30", "Activity": "Jalan Braga (city walk)"},
        {"Time": "13:00", "Activity": "Makan siang"},
        {"Time": "15:00", "Activity": "Kawah Putih Ciwidey"},
        {"Time": "19:00", "Activity": "Makan malam"},
    ],
    "Yogyakarta": [
        {"Time": "08:00", "Activity": "Sarapan"},
        {"Time": "09:00", "Activity": "Keraton Yogyakarta"},
        {"Time": "12:00", "Activity": "Makan siang"},
        {"Time": "14:00", "Activity": "Candi Prambanan"},
        {"Time": "19:00", "Activity": "Malioboro"},
    ],
    "Surabaya": [
        {"Time": "08:00", "Activity": "Sarapan"},
        {"Time": "09:30", "Activity": "Tugu Pahlawan"},
        {"Time": "12:00", "Activity": "Makan siang"},
        {"Time": "14:00", "Activity": "Kota Tua (Kembang Jepun)"},
        {"Time": "16:30", "Activity": "House of Sampoerna"},
    ],
    "Malang": [
        {"Time": "08:00", "Activity": "Sarapan"},
        {"Time": "09:30", "Activity": "Alun-Alun Malang"},
        {"Time": "11:00", "Activity": "Kampung Warna-Warni Jodipan"},
        {"Time": "13:00", "Activity": "Makan siang"},
        {"Time": "15:00", "Activity": "Persiapan trip Bromo (opsional)"},
    ],
}

# =========================
# Helpers (data)
# =========================
def make_dummy_data(n: int = 1100) -> pd.DataFrame:
    import random
    countries = ["Japan", "Australia", "Germany", "France", "Singapore", "Malaysia", "USA"]
    languages = {
        "Japan": "Japanese", "Australia": "English", "Germany": "German",
        "France": "French", "Singapore": "English", "Malaysia": "English", "USA": "English"
    }
    routes = list(ROUTE_TO_DEST.keys())
    purposes = ["Leisure", "Business", "Family", "Backpacking"]
    classes = ["Economy", "Executive", "Luxury/Pariwisata"]
    touchpoints = ["Website/App", "Station", "On-train", "Customer Service"]
    pains = [
        "Language barrier at station",
        "Wayfinding signage",
        "Ticketing confusion",
        "Payment limitations",
        "Schedule clarity"
    ]
    positives = [
        "On-time departure",
        "Comfortable seating",
        "Easy booking",
        "Clean station",
        "Friendly staff",
        "Scenic route"
    ]

    rows = []
    for _ in range(n):
        c = random.choice(countries)
        r = random.choice(routes)
        cls = random.choice(classes)
        base = 4.05 if cls == "Economy" else (4.35 if cls == "Executive" else 4.55)
        sat = max(1, min(5, random.gauss(base, 0.35)))

        rows.append({
            "date": datetime(2025, random.randint(1, 12), random.randint(1, 28)).date().isoformat(),
            "country": c,
            "language": languages.get(c, "English"),
            "route": r,
            "purpose": random.choice(purposes),
            "ticket_class": cls,
            "touchpoint": random.choice(touchpoints),
            "satisfaction": round(sat, 2),
            "positive_feedback": random.choice(positives),
            "pain_point": random.choice(pains),
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

    for c in ["country","language","route","purpose","ticket_class","touchpoint","positive_feedback","pain_point"]:
        df[c] = df[c].astype(str).str.strip()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["date"] = df["date"].dt.date
    return df

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def get_destination_city(route: str) -> Optional[str]:
    return ROUTE_TO_DEST.get(route)

def build_kai_star_table(city: str) -> pd.DataFrame:
    items = KAI_TOURISM_RECS.get(city, [])
    if not items:
        return pd.DataFrame(columns=["KAI Star", "Tempat", "Kategori", "Alasan singkat"])
    d = pd.DataFrame(items)
    d["KAI Star"] = d["kai_star"].map(KAI_STAR_SCALE)
    d = d.rename(columns={"place":"Tempat", "category":"Kategori", "why":"Alasan singkat"})
    d = d[["KAI Star","Tempat","Kategori","Alasan singkat","kai_star"]]
    d = d.sort_values(["kai_star","Tempat"], ascending=[False,True]).drop(columns=["kai_star"])
    return d

def build_city_map_df(city: str) -> pd.DataFrame:
    c = CITY_COORDS.get(city)
    if not c:
        return pd.DataFrame(columns=["city","lat","lon"])
    return pd.DataFrame([{"city": city, "lat": c["lat"], "lon": c["lon"]}])

def build_itinerary_df(city: str) -> pd.DataFrame:
    items = KAI_DAY_ITINERARY.get(city, [])
    return pd.DataFrame(items) if items else pd.DataFrame(columns=["Time","Activity"])

# =========================
# Sidebar (Page + Data Source + Filters)
# =========================
st.sidebar.markdown("### 🚆 JourneySense")
page = st.sidebar.radio("Menu", ["Page 1 — Overview", "Page 2 — Analytics"], index=0)

data_mode = st.sidebar.radio("Data source", ["Use dummy data (recommended)", "Upload CSV"], index=0)
uploaded = None
if data_mode == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    st.sidebar.caption("Required columns: " + ", ".join(EXPECTED_COLS))

# Load data
if data_mode == "Use dummy data (recommended)":
    df = validate_and_clean(make_dummy_data())
else:
    if uploaded is None:
        st.info("Upload CSV dulu, atau pilih dummy data.")
        st.stop()
    df = validate_and_clean(pd.read_csv(uploaded))

# Filters
st.sidebar.markdown("---")
st.sidebar.markdown("#### Filters")

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
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

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

# Metrics
total = len(filtered)
avg_sat = float(filtered["satisfaction"].mean()) if total else 0.0
top_country = filtered["country"].value_counts().index[0] if total else "-"
top_route = filtered["route"].value_counts().index[0] if total else "-"
low_sat_share = (filtered["satisfaction"] < 4.0).mean() * 100 if total else 0.0

# =========================
# PAGE 1 — OVERVIEW
# =========================
if page == "Page 1 — Overview":
    hero(
        title="KAI JourneySense Dashboard",
        subtitle="Data-driven journey experience & tourism recommendations for international travelers (conceptual prototype).",
        kicker="KAI Ideation Challenge 2025 • Global Branding, Local Hearts",
        badges=["🚆 Experience", "📊 Insights", "🌏 Tourism", "✨ KAI Star"]
    )

    st.markdown("""
    <div class="kai-note">
      <b>Catatan:</b> Dashboard ini adalah prototipe konseptual untuk kebutuhan proposal (bukan data operasional resmi).
    </div>
    """, unsafe_allow_html=True)

    # KPI cards
    section("Key Performance Indicators", chip="Overview")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi_card("Trips (records)", f"{total:,}", "Filtered view")
    with c2: kpi_card("Avg satisfaction", f"{avg_sat:.2f} / 5", "Experience quality")
    with c3: kpi_card("Top origin", top_country, "Highest share")
    with c4: kpi_card("Top route", top_route, "Most selected")
    with c5: kpi_card("Below 4.0 share", f"{low_sat_share:.1f}%", "Attention needed")

    st.divider()

    # Customer recommendations
    section("Customer Recommendations", chip="Actionable")
    if total == 0:
        st.info("Tidak ada data setelah filter.")
    else:
        worst_touch = filtered.groupby("touchpoint")["satisfaction"].mean().sort_values().index[0]
        worst_route = filtered.groupby("route")["satisfaction"].mean().sort_values().index[0]
        top_pain = filtered["pain_point"].value_counts().index[0]

        recs = [
            f"Gunakan aplikasi/website KAI untuk info rute terpandu pada: {worst_route}.",
            "Datang lebih awal ke stasiun untuk memudahkan navigasi (terutama jam ramai).",
            f"Kendala umum yang perlu diantisipasi: {top_pain}. Siapkan alternatif (bahasa/pembayaran/jadwal).",
            f"Jika ragu, manfaatkan petugas/Customer Service—terutama pada: {worst_touch}.",
        ]
        for r in recs:
            st.write("• " + r)

    st.divider()

    # Tourism recommendations
    section("KAI Star Tourism Recommendations", chip="Conceptual")
    if total == 0:
        st.info("Tidak ada data setelah filter.")
    else:
        primary_route = filtered["route"].value_counts().index[0]
        dest_city = get_destination_city(primary_route)

        leftA, midA, rightA = st.columns([1, 1.1, 1.9])

        with leftA:
            st.markdown("**Primary tourist route**")
            st.write(primary_route)
            st.markdown("**Destination city**")
            st.write(dest_city if dest_city else "-")
            st.caption("KAI Star = penilaian internal konseptual (mirip konsep Michelin, namun untuk destinasi).")
            min_star = st.selectbox("Minimum KAI Star", [1, 2, 3], index=0)

        with midA:
            st.markdown("**Destination map**")
            if not dest_city or dest_city not in CITY_COORDS:
                st.info("Peta belum tersedia untuk destinasi ini.")
            else:
                st.map(build_city_map_df(dest_city), latitude="lat", longitude="lon", size=70)
                st.caption("Penanda kota (perkiraan, konseptual).")

        with rightA:
            if not dest_city:
                st.warning("Mapping kota tujuan belum tersedia.")
            else:
                rec_df = build_kai_star_table(dest_city)
                if rec_df.empty:
                    st.info("Belum ada rekomendasi untuk kota ini.")
                else:
                    rec_df["_stars"] = rec_df["KAI Star"].apply(lambda s: s.count("★"))
                    rec_df = rec_df[rec_df["_stars"] >= min_star].drop(columns=["_stars"])
                    st.dataframe(rec_df, use_container_width=True, hide_index=True)

                    st.markdown("#### Itinerary 1 Hari (Konseptual)")
                    iti_df = build_itinerary_df(dest_city)
                    st.dataframe(iti_df, use_container_width=True, hide_index=True)
                    st.caption("Itinerary dapat disesuaikan dengan jadwal kereta & profil wisatawan.")

    st.divider()

    # Export
    section("Export (for Appendix)", chip="CSV")
    insight_df = pd.DataFrame([
        {"metric": "Trips", "value": total},
        {"metric": "Avg satisfaction", "value": round(avg_sat, 2)},
        {"metric": "Top origin", "value": top_country},
        {"metric": "Top route", "value": top_route},
    ])

    colA, colB = st.columns([1, 2])
    with colA:
        st.download_button("Download filtered data (CSV)", df_to_csv_bytes(filtered),
                           file_name="journeysense_filtered_data.csv", mime="text/csv")
        st.download_button("Download executive insights (CSV)", df_to_csv_bytes(insight_df),
                           file_name="journeysense_executive_insights.csv", mime="text/csv")
    with colB:
        st.dataframe(insight_df, use_container_width=True, hide_index=True)

    with st.expander("Preview filtered data"):
        st.dataframe(filtered, use_container_width=True)

    st.caption("© KAI JourneySense – conceptual dashboard prototype (proposal use).")

# =========================
# PAGE 2 — ANALYTICS
# =========================
else:
    hero(
        title="JourneySense Analytics",
        subtitle="Deeper statistics by origin, route, class, touchpoint, and satisfaction trend (conceptual prototype).",
        kicker="Insights • Performance • Continuous Improvement",
        badges=["📈 Trend", "🧭 Segmentation", "🧩 Pain Points"]
    )

    section("KPI Snapshot", chip="Analytics")
    a1, a2, a3, a4 = st.columns(4)
    with a1: kpi_card("Trips", f"{total:,}")
    with a2: kpi_card("Avg satisfaction", f"{avg_sat:.2f}")
    with a3: kpi_card("Top origin", top_country)
    with a4: kpi_card("Top route", top_route)

    st.divider()

    if total == 0:
        st.info("Tidak ada data setelah filter. Silakan ubah filter.")
        st.stop()

    section("Demand & Profile", chip="Charts")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Origin Country Distribution")
        cc = filtered["country"].value_counts().reset_index()
        cc.columns = ["country", "count"]
        st.plotly_chart(px.bar(cc, x="country", y="count"), use_container_width=True)

    with c2:
        st.subheader("Purpose Distribution")
        pc = filtered["purpose"].value_counts().reset_index()
        pc.columns = ["purpose", "count"]
        st.plotly_chart(px.pie(pc, names="purpose", values="count"), use_container_width=True)

    st.divider()

    section("Route & Class Mix", chip="Breakdown")
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Top Routes")
        rc = filtered["route"].value_counts().reset_index()
        rc.columns = ["route", "count"]
        st.plotly_chart(px.bar(rc, x="route", y="count"), use_container_width=True)

    with c4:
        st.subheader("Ticket Class Mix")
        tc = filtered["ticket_class"].value_counts().reset_index()
        tc.columns = ["ticket_class", "count"]
        st.plotly_chart(px.pie(tc, names="ticket_class", values="count"), use_container_width=True)

    st.divider()

    section("Experience Quality", chip="Satisfaction")
    c5, c6 = st.columns(2)
    with c5:
        st.subheader("Satisfaction by Ticket Class")
        st.plotly_chart(px.box(filtered, x="ticket_class", y="satisfaction"), use_container_width=True)

    with c6:
        st.subheader("Satisfaction by Touchpoint")
        st.plotly_chart(px.box(filtered, x="touchpoint", y="satisfaction"), use_container_width=True)

    st.divider()

    section("Voice of Tourist", chip="Top issues")
    c7, c8 = st.columns(2)
    with c7:
        st.subheader("Top Pain Points")
        pp = filtered["pain_point"].value_counts().reset_index()
        pp.columns = ["pain_point", "count"]
        st.plotly_chart(px.bar(pp.head(10), x="pain_point", y="count"), use_container_width=True)

    with c8:
        st.subheader("Top Positive Feedback")
        pf = filtered["positive_feedback"].value_counts().reset_index()
        pf.columns = ["positive_feedback", "count"]
        st.plotly_chart(px.bar(pf.head(10), x="positive_feedback", y="count"), use_container_width=True)

    st.divider()

    section("Trend", chip="Time series")
    st.subheader("Satisfaction Trend Over Time")
    trend = filtered.groupby("date", as_index=False)["satisfaction"].mean().sort_values("date")
    st.plotly_chart(px.line(trend, x="date", y="satisfaction"), use_container_width=True)

    with st.expander("Preview filtered data"):
        st.dataframe(filtered, use_container_width=True)

    st.caption("© KAI JourneySense – conceptual dashboard prototype (proposal use).")
