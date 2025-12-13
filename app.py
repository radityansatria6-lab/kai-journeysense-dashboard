import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Optional

# =========================================================
# PAGE CONFIG + STYLE
# =========================================================
st.set_page_config(page_title="KAI JourneySense Dashboard", page_icon="🚆", layout="wide")
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.1rem; padding-bottom: 1.2rem; }
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
# KAI STAR (Conceptual) - Tourism Recs, Map, Itinerary
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

KAI_TOURISM_RECS = {
    "Bandung": [
        {"place": "Kawah Putih Ciwidey", "kai_star": 3, "category": "Nature",
         "why": "Pengalaman alam unik dan sangat memorable."},
        {"place": "Jalan Braga", "kai_star": 2, "category": "Heritage",
         "why": "Ikonik dan mudah dijangkau wisatawan."},
        {"place": "Gedung Sate", "kai_star": 2, "category": "Landmark",
         "why": "Landmark kota dengan nilai sejarah."},
    ],
    "Yogyakarta": [
        {"place": "Candi Prambanan", "kai_star": 3, "category": "UNESCO Heritage",
         "why": "Destinasi kelas dunia dan bernilai budaya tinggi."},
        {"place": "Keraton Yogyakarta", "kai_star": 3, "category": "Culture",
         "why": "Pengalaman budaya autentik."},
        {"place": "Malioboro", "kai_star": 2, "category": "City Experience",
         "why": "Pusat aktivitas wisata kota."},
    ],
    "Surabaya": [
        {"place": "Tugu Pahlawan", "kai_star": 2, "category": "History",
         "why": "Ikon sejarah nasional."},
        {"place": "Kota Tua (Kembang Jepun)", "kai_star": 2, "category": "Heritage",
         "why": "Area heritage yang mudah dijelajahi."},
        {"place": "House of Sampoerna", "kai_star": 1, "category": "Museum",
         "why": "Museum populer untuk kunjungan singkat."},
    ],
    "Malang": [
        {"place": "Bromo (akses via Malang)", "kai_star": 3, "category": "Nature",
         "why": "Destinasi internasional dengan pengalaman ikonik."},
        {"place": "Kampung Warna-Warni Jodipan", "kai_star": 2, "category": "City Spot",
         "why": "Spot visual yang menarik wisatawan."},
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

def get_destination_city(route: str) -> Optional[str]:
    return ROUTE_TO_DEST.get(route)

def build_kai_star_table(city: str) -> pd.DataFrame:
    items = KAI_TOURISM_RECS.get(city, [])
    if not items:
        return pd.DataFrame(columns=["KAI Star", "Tempat", "Kategori", "Alasan singkat"])
    df = pd.DataFrame(items)
    df["KAI Star"] = df["kai_star"].map(KAI_STAR_SCALE)
    df = df.rename(columns={"place": "Tempat", "category": "Kategori", "why": "Alasan singkat"})
    df = df[["KAI Star", "Tempat", "Kategori", "Alasan singkat", "kai_star"]]
    df = df.sort_values(["kai_star", "Tempat"], ascending=[False, True]).drop(columns=["kai_star"])
    return df

def build_city_map_df(city: str) -> pd.DataFrame:
    c = CITY_COORDS.get(city)
    if not c:
        return pd.DataFrame(columns=["city", "lat", "lon"])
    return pd.DataFrame([{"city": city, "lat": c["lat"], "lon": c["lon"]}])

def build_itinerary_df(city: str) -> pd.DataFrame:
    items = KAI_DAY_ITINERARY.get(city, [])
    return pd.DataFrame(items) if items else pd.DataFrame(columns=["Time", "Activity"])

# =========================================================
# DATA (Dummy / Upload) + Cleaning
# =========================================================
def make_dummy_data(n: int = 1000) -> pd.DataFrame:
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
    pains = ["Language barrier at station", "Wayfinding signage", "Ticketing confusion", "Payment limitations", "Schedule clarity"]
    positives = ["On-time departure", "Comfortable seating", "Easy booking", "Clean station", "Friendly staff", "Scenic route"]

    rows = []
    for _ in range(n):
        c = random.choice(countries)
        r = random.choice(routes)
        cls = random.choice(classes)
        base = 4.05 if cls == "Economy" else (4.35 if cls == "Executive" else 4.55)

        rows.append({
            "date": datetime(2025, random.randint(1, 12), random.randint(1, 28)).date().isoformat(),
            "country": c,
            "language": languages.get(c, "English"),
            "route": r,
            "purpose": random.choice(purposes),
            "ticket_class": cls,
            "touchpoint": random.choice(touchpoints),
            "satisfaction": round(max(1, min(5, random.gauss(base, 0.35))), 2),
            "positive_feedback": random.choice(positives),
            "pain_point": random.choice(pains)
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

# =========================================================
# SIDEBAR (Page switch + options)
# =========================================================
st.sidebar.title("🚆 JourneySense")
page = st.sidebar.radio("Menu", ["Page 1 — Overview", "Page 2 — Analytics"], index=0)

lang_mode = st.sidebar.selectbox("Language", ["English", "Bilingual (EN/ID)"], index=1)
def t(en: str, idn: str) -> str:
    return en if lang_mode == "English" else f"{en}\n{idn}"

data_mode = st.sidebar.radio(
    t("Data source", "Sumber data"),
    [t("Use dummy data (recommended)", "Gunakan dummy data (disarankan)"),
     t("Upload CSV", "Unggah CSV")],
    index=0
)

uploaded = None
if "Upload CSV" in data_mode:
    uploaded = st.sidebar.file_uploader(t("Upload CSV file", "Unggah file CSV"), type=["csv"])
    st.sidebar.markdown("<div class='small-note'>CSV columns: " + ", ".join(EXPECTED_COLS) + "</div>",
                        unsafe_allow_html=True)

# Load data
if "dummy" in data_mode.lower():
    df = validate_and_clean(make_dummy_data(1100))
else:
    if uploaded is None:
        st.warning(t("Please upload a CSV file, or switch to dummy data.",
                     "Silakan unggah CSV, atau gunakan dummy data."))
        st.stop()
    df = validate_and_clean(pd.read_csv(uploaded))

# Filters (shared across both pages)
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

# Common metrics
total = len(filtered)
avg_sat = float(filtered["satisfaction"].mean()) if total else 0.0
top_country = filtered["country"].value_counts().index[0] if total else "-"
top_route = filtered["route"].value_counts().index[0] if total else "-"
low_sat_share = (filtered["satisfaction"] < 4.0).mean() * 100 if total else 0.0

# =========================================================
# PAGE 1 — OVERVIEW (KPI + Recommendations)
# =========================================================
if page == "Page 1 — Overview":
    st.title("🚆 KAI JourneySense – Overview")
    st.caption(t(
        "Page 1 focuses on KPI cards and customer-facing recommendations (conceptual).",
        "Halaman 1 berisi KPI dan rekomendasi untuk pelanggan (konseptual)."
    ))

    # KPI cards
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric(t("Trips (records)", "Perjalanan (record)"), f"{total:,}")
    k2.metric(t("Avg satisfaction", "Rata-rata kepuasan"), f"{avg_sat:.2f} / 5")
    k3.metric(t("Top origin", "Asal terbanyak"), top_country)
    k4.metric(t("Top route", "Rute favorit"), top_route)
    k5.metric(t("Below 4.0 share", "Proporsi < 4.0"), f"{low_sat_share:.1f}%")

    st.divider()

    st.subheader(t("Customer Recommendations (Conceptual)", "Rekomendasi untuk Pelanggan (Konseptual)"))
    if total == 0:
        st.info(t("No data after filters.", "Tidak ada data setelah filter."))
    else:
        worst_touch = filtered.groupby("touchpoint")["satisfaction"].mean().sort_values().index[0]
        worst_route = filtered.groupby("route")["satisfaction"].mean().sort_values().index[0]
        top_pain = filtered["pain_point"].value_counts().index[0]

        # Customer-facing recs (simple & friendly)
        recs = [
            t(f"If you are new to the system, start from the KAI app/website and follow the guided route info for: {worst_route}.",
              f"Jika baru pertama kali, mulai dari aplikasi/website KAI dan ikuti info rute terpandu untuk: {worst_route}."),
            t("Arrive earlier at the station for smoother wayfinding, especially during peak hours.",
              "Datang lebih awal ke stasiun untuk memudahkan navigasi, terutama saat jam ramai."),
            t(f"Common friction to anticipate: {top_pain}. Prepare alternatives (language help / payment method / schedule check).",
              f"Hal yang sering jadi kendala: {top_pain}. Siapkan alternatif (bantuan bahasa / metode bayar / cek jadwal)."),
            t(f"Touchpoint to watch: {worst_touch}. Use official staff/customer service when in doubt.",
              f"Touchpoint yang perlu perhatian: {worst_touch}. Manfaatkan petugas/CS resmi jika ragu."),
        ]
        for r in recs:
            st.write("• " + r)

    st.divider()

    st.subheader(t("Tourism Recommendations (KAI Star – Conceptual)", "Rekomendasi Pariwisata (KAI Star – Konseptual)"))
    if total == 0:
        st.info(t("No data after filters.", "Tidak ada data setelah filter."))
    else:
        primary_route = filtered["route"].value_counts().index[0]
        dest_city = get_destination_city(primary_route)

        leftA, midA, rightA = st.columns([1, 1.1, 1.9])

        with leftA:
            st.markdown("**" + t("Primary tourist route", "Rute utama wisatawan") + "**")
            st.write(primary_route)
            st.markdown("**" + t("Destination city", "Kota tujuan") + "**")
            st.write(dest_city if dest_city else "-")
            st.caption(t(
                "KAI Star is an internal conceptual rating (not a public official rating).",
                "KAI Star adalah penilaian internal konseptual (bukan rating publik resmi)."
            ))
            min_star = st.selectbox(t("Minimum KAI Star", "Minimal KAI Star"), [1, 2, 3], index=0)

        with midA:
            st.markdown("**" + t("Destination map", "Peta destinasi") + "**")
            if not dest_city or dest_city not in CITY_COORDS:
                st.info(t("Map not available for this destination yet.", "Peta belum tersedia untuk destinasi ini."))
            else:
                st.map(build_city_map_df(dest_city), latitude="lat", longitude="lon", size=60)
                st.caption(t("Conceptual city marker (approx.).", "Penanda kota (perkiraan, konseptual)."))

        with rightA:
            if not dest_city:
                st.warning(t("Destination city mapping not available.", "Mapping kota tujuan belum tersedia."))
            else:
                rec_df = build_kai_star_table(dest_city)
                if rec_df.empty:
                    st.info(t("No recommendations for this city yet.", "Belum ada rekomendasi untuk kota ini."))
                else:
                    # filter by minimum star
                    rec_df["_stars"] = rec_df["KAI Star"].apply(lambda s: s.count("★"))
                    rec_df = rec_df[rec_df["_stars"] >= min_star].drop(columns=["_stars"])

                    st.dataframe(rec_df, use_container_width=True, hide_index=True)

                    st.markdown("### " + t("1-Day Itinerary (Conceptual)", "Itinerary 1 Hari (Konseptual)"))
                    iti_df = build_itinerary_df(dest_city)
                    if iti_df.empty:
                        st.info(t("No itinerary available for this city yet.", "Belum ada itinerary untuk kota ini."))
                    else:
                        st.dataframe(iti_df, use_container_width=True, hide_index=True)

                    st.caption(t(
                        "Itinerary is a proposal concept and can be adjusted to train schedule and tourist profile.",
                        "Itinerary bersifat konsep proposal dan dapat disesuaikan dengan jadwal kereta serta profil wisatawan."
                    ))

    st.divider()

    st.subheader(t("Export (for appendix)", "Ekspor (untuk lampiran)"))
    if total == 0:
        insight_df = pd.DataFrame([{"note": "No data"}])
    else:
        worst_touch = filtered.groupby("touchpoint")["satisfaction"].mean().sort_values().index[0]
        worst_route = filtered.groupby("route")["satisfaction"].mean().sort_values().index[0]
        top_pain = filtered["pain_point"].value_counts().index[0]
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

    with st.expander(t("Preview filtered data", "Lihat data terfilter")):
        st.dataframe(filtered, use_container_width=True)

    st.caption("© KAI JourneySense – conceptual dashboard prototype (proposal use).")

# =========================================================
# PAGE 2 — ANALYTICS (Detailed charts)
# =========================================================
else:
    st.title("📊 KAI JourneySense – Analytics")
    st.caption(t(
        "Page 2 focuses on detailed statistics and deeper charts (conceptual).",
        "Halaman 2 berisi statistik dan chart yang lebih detail (konseptual)."
    ))

    # KPI summary (small)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(t("Trips", "Perjalanan"), f"{total:,}")
    k2.metric(t("Avg satisfaction", "Rata-rata kepuasan"), f"{avg_sat:.2f}")
    k3.metric(t("Top origin", "Asal terbanyak"), top_country)
    k4.metric(t("Top route", "Rute favorit"), top_route)

    st.divider()

    if total == 0:
        st.info(t("No data after filters. Please adjust filters.", "Tidak ada data setelah filter. Silakan ubah filter."))
        st.stop()

    # --- More detailed charts ---
    c1, c2 = st.columns(2)
    with c1:
        st.subheader(t("Origin Country Distribution", "Distribusi Negara Asal"))
        cc = filtered["country"].value_counts().reset_index()
        cc.columns = ["country", "count"]
        st.plotly_chart(px.bar(cc, x="country", y="count"), use_container_width=True)

    with c2:
        st.subheader(t("Purpose Distribution", "Distribusi Tujuan Perjalanan"))
        pc = filtered["purpose"].value_counts().reset_index()
        pc.columns = ["purpose", "count"]
        st.plotly_chart(px.pie(pc, names="purpose", values="count"), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader(t("Top Routes", "Rute Teratas"))
        rc = filtered["route"].value_counts().reset_index()
        rc.columns = ["route", "count"]
        st.plotly_chart(px.bar(rc, x="route", y="count"), use_container_width=True)

    with c4:
        st.subheader(t("Ticket Class Mix", "Komposisi Kelas"))
        tc = filtered["ticket_class"].value_counts().reset_index()
        tc.columns = ["ticket_class", "count"]
        st.plotly_chart(px.pie(tc, names="ticket_class", values="count"), use_container_width=True)

    st.divider()

    c5, c6 = st.columns(2)
    with c5:
        st.subheader(t("Satisfaction by Ticket Class", "Kepuasan per Kelas"))
        st.plotly_chart(px.box(filtered, x="ticket_class", y="satisfaction"), use_container_width=True)

    with c6:
        st.subheader(t("Satisfaction by Touchpoint", "Kepuasan per Touchpoint"))
        st.plotly_chart(px.box(filtered, x="touchpoint", y="satisfaction"), use_container_width=True)

    st.divider()

    c7, c8 = st.columns(2)
    with c7:
        st.subheader(t("Top Pain Points", "Pain Point Teratas"))
        pp = filtered["pain_point"].value_counts().reset_index()
        pp.columns = ["pain_point", "count"]
        st.plotly_chart(px.bar(pp.head(10), x="pain_point", y="count"), use_container_width=True)

    with c8:
        st.subheader(t("Top Positive Feedback", "Feedback Positif Teratas"))
        pf = filtered["positive_feedback"].value_counts().reset_index()
        pf.columns = ["positive_feedback", "count"]
        st.plotly_chart(px.bar(pf.head(10), x="positive_feedback", y="count"), use_container_width=True)

    st.divider()

    st.subheader(t("Satisfaction Trend Over Time", "Tren Kepuasan dari Waktu ke Waktu"))
    # daily average satisfaction
    trend = filtered.groupby("date", as_index=False)["satisfaction"].mean().sort_values("date")
    st.plotly_chart(px.line(trend, x="date", y="satisfaction"), use_container_width=True)

    with st.expander(t("Preview filtered data", "Lihat data terfilter")):
        st.dataframe(filtered, use_container_width=True)

    st.caption("© KAI JourneySense – conceptual dashboard prototype (proposal use).")
