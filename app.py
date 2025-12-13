import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Optional

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="KAI JourneySense Dashboard",
    page_icon="🚆",
    layout="wide"
)

st.markdown("""
<style>
.block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; }
.small-note { color: #6B7280; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONSTANTS
# =========================================================
EXPECTED_COLS = [
    "date", "country", "language", "route", "purpose",
    "ticket_class", "touchpoint", "satisfaction",
    "positive_feedback", "pain_point"
]

# =========================================================
# KAI STAR – TOURISM (CONCEPTUAL)
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
        {"place": "Kota Tua Kembang Jepun", "kai_star": 2, "category": "Heritage",
         "why": "Area heritage yang mudah dijelajahi."},
        {"place": "House of Sampoerna", "kai_star": 1, "category": "Museum",
         "why": "Museum populer untuk kunjungan singkat."},
    ],
    "Malang": [
        {"place": "Bromo (via Malang)", "kai_star": 3, "category": "Nature",
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
        {"Time": "11:30", "Activity": "Jalan Braga"},
        {"Time": "13:00", "Activity": "Makan siang"},
        {"Time": "15:00", "Activity": "Kawah Putih Ciwidey"},
        {"Time": "19:00", "Activity": "Makan malam"},
    ],
    "Yogyakarta": [
        {"Time": "08:00", "Activity": "Sarapan"},
        {"Time": "09:00", "Activity": "Keraton Yogyakarta"},
        {"Time": "12:00", "Activity": "Makan siang"},
        {"Time": "14:00", "Activity": "Candi Prambanan"},
        {"Time": "17:30", "Activity": "Sunset"},
        {"Time": "19:00", "Activity": "Malioboro"},
    ],
    "Surabaya": [
        {"Time": "08:00", "Activity": "Sarapan"},
        {"Time": "09:30", "Activity": "Tugu Pahlawan"},
        {"Time": "12:00", "Activity": "Makan siang"},
        {"Time": "14:00", "Activity": "Kota Tua Kembang Jepun"},
        {"Time": "16:30", "Activity": "House of Sampoerna"},
    ],
    "Malang": [
        {"Time": "08:00", "Activity": "Sarapan"},
        {"Time": "09:30", "Activity": "Alun-Alun Malang"},
        {"Time": "11:00", "Activity": "Kampung Warna-Warni Jodipan"},
        {"Time": "13:00", "Activity": "Makan siang"},
        {"Time": "15:00", "Activity": "Persiapan trip Bromo"},
    ],
}

# =========================================================
# FUNCTIONS
# =========================================================
def make_dummy_data(n=1000):
    import random
    countries = ["Japan", "Australia", "Germany", "France", "Singapore"]
    routes = list(ROUTE_TO_DEST.keys())
    classes = ["Economy", "Executive", "Luxury"]
    touchpoints = ["Website/App", "Station", "On-train"]
    pains = ["Language barrier", "Wayfinding", "Ticket clarity"]
    positives = ["On-time", "Comfort", "Friendly staff"]

    rows = []
    for _ in range(n):
        rows.append({
            "date": datetime(2025, random.randint(1, 12), random.randint(1, 28)).date(),
            "country": random.choice(countries),
            "language": "English",
            "route": random.choice(routes),
            "purpose": "Leisure",
            "ticket_class": random.choice(classes),
            "touchpoint": random.choice(touchpoints),
            "satisfaction": round(random.uniform(3.8, 4.8), 2),
            "positive_feedback": random.choice(positives),
            "pain_point": random.choice(pains)
        })
    return pd.DataFrame(rows)

def get_destination_city(route):
    return ROUTE_TO_DEST.get(route)

def build_kai_star_table(city):
    items = KAI_TOURISM_RECS.get(city, [])
    df = pd.DataFrame(items)
    if df.empty:
        return df
    df["KAI Star"] = df["kai_star"].map(KAI_STAR_SCALE)
    return df[["KAI Star", "place", "category", "why"]]

# =========================================================
# LOAD DATA
# =========================================================
df = make_dummy_data()

# =========================================================
# UI
# =========================================================
st.title("🚆 KAI JourneySense – International Tourism Dashboard")
st.caption("Conceptual dashboard for branding & journey experience (Ideation Challenge)")

# KPI
st.subheader("Key Metrics")
k1, k2, k3 = st.columns(3)
k1.metric("Total Trips", len(df))
k2.metric("Avg Satisfaction", f"{df['satisfaction'].mean():.2f} / 5")
k3.metric("Top Route", df["route"].value_counts().idxmax())

st.divider()

# Charts
st.subheader("Insights")
st.plotly_chart(px.bar(df["route"].value_counts().reset_index(),
                       x="index", y="route", labels={"index": "Route", "route": "Trips"}))

st.divider()

# =========================================================
# KAI STAR + MAP + ITINERARY
# =========================================================
st.subheader("🌏 KAI Star Tourism Recommendation (Conceptual)")

primary_route = df["route"].value_counts().idxmax()
city = get_destination_city(primary_route)

left, mid, right = st.columns([1, 1.2, 1.8])

with left:
    st.markdown("**Primary Route**")
    st.write(primary_route)
    st.markdown("**Destination City**")
    st.write(city)
    st.caption("KAI Star adalah penilaian internal konseptual.")

with mid:
    if city in CITY_COORDS:
        map_df = pd.DataFrame([CITY_COORDS[city]])
        st.map(map_df, latitude="lat", longitude="lon", size=60)
    else:
        st.info("Map not available")

with right:
    rec_df = build_kai_star_table(city)
    st.dataframe(rec_df, use_container_width=True, hide_index=True)

    st.markdown("### Itinerary 1 Hari")
    iti_df = pd.DataFrame(KAI_DAY_ITINERARY.get(city, []))
    st.dataframe(iti_df, use_container_width=True, hide_index=True)

st.caption("© KAI JourneySense – conceptual prototype")
