pip install streamlit pandas plotly
streamlit run app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="KAI JourneySense Dashboard",
    page_icon="🚆",
    layout="wide"
)

# -----------------------------
# Helpers
# -----------------------------
def make_dummy_data(n: int = 500) -> pd.DataFrame:
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

        # satisfaction: slightly higher for Executive/Luxury
        base = 4.1 if cls == "Economy" else (4.4 if cls == "Executive" else 4.6)
        sat = max(1.0, min(5.0, random.gauss(base, 0.35)))

        # choose feedback
        pos = random.choice(positives)
        neg = random.choice(pain_points)

        # pseudo dates in recent window
        day = random.randint(1, 28)
        month = random.randint(1, 12)
        year = 2025
        date = datetime(year, month, day)

        rows.append({
            "date": date.date().isoformat(),
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


def load_data(uploaded_file) -> pd.DataFrame:
    if uploaded_file is None:
        return make_dummy_data(800)

    df = pd.read_csv(uploaded_file)
    # Expected columns (you can rename in your CSV to match):
    # date,country,language,route,purpose,ticket_class,touchpoint,satisfaction,positive_feedback,pain_point
    required = [
        "date","country","language","route","purpose","ticket_class",
        "touchpoint","satisfaction","positive_feedback","pain_point"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"CSV missing columns: {missing}\n\nExpected: {required}")
        st.stop()

    # Clean types
    df["satisfaction"] = pd.to_numeric(df["satisfaction"], errors="coerce")
    df = df.dropna(subset=["satisfaction"])
    return df


# -----------------------------
# Sidebar: Data Source + Filters
# -----------------------------
st.sidebar.title("⚙️ Settings")
uploaded = st.sidebar.file_uploader("Upload CSV (optional)", type=["csv"])
df = load_data(uploaded)

st.sidebar.caption("Filters")
countries = sorted(df["country"].unique())
routes = sorted(df["route"].unique())
classes = sorted(df["ticket_class"].unique())
purposes = sorted(df["purpose"].unique())

sel_country = st.sidebar.multiselect("Country", countries, default=countries)
sel_route = st.sidebar.multiselect("Route", routes, default=routes)
sel_class = st.sidebar.multiselect("Ticket Class", classes, default=classes)
sel_purpose = st.sidebar.multiselect("Purpose", purposes, default=purposes)

filtered = df[
    df["country"].isin(sel_country)
    & df["route"].isin(sel_route)
    & df["ticket_class"].isin(sel_class)
    & df["purpose"].isin(sel_purpose)
].copy()

# -----------------------------
# Header
# -----------------------------
st.title("🚆 KAI JourneySense – International Tourism Insight Dashboard")
st.caption(
    "Conceptual dashboard to support data-driven branding and personalized journey experience."
)

# -----------------------------
# KPI Row
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

total_travelers = len(filtered)
avg_sat = filtered["satisfaction"].mean() if total_travelers else 0
top_country = filtered["country"].value_counts().index[0] if total_travelers else "-"
top_route = filtered["route"].value_counts().index[0] if total_travelers else "-"

col1.metric("Total Records (Tourist Trips)", f"{total_travelers:,}")
col2.metric("Avg Satisfaction", f"{avg_sat:.2f} / 5")
col3.metric("Top Origin Country", top_country)
col4.metric("Top Route", top_route)

st.divider()

# -----------------------------
# Charts
# -----------------------------
left, right = st.columns(2)

with left:
    st.subheader("Origin Country Distribution")
    country_counts = filtered["country"].value_counts().reset_index()
    country_counts.columns = ["country", "count"]
    fig_country = px.bar(country_counts, x="country", y="count")
    st.plotly_chart(fig_country, use_container_width=True)

with right:
    st.subheader("Top Routes Used by International Tourists")
    route_counts = filtered["route"].value_counts().reset_index()
    route_counts.columns = ["route", "count"]
    fig_route = px.bar(route_counts, x="route", y="count")
    st.plotly_chart(fig_route, use_container_width=True)

mid1, mid2 = st.columns(2)

with mid1:
    st.subheader("Satisfaction by Ticket Class")
    fig_class = px.box(filtered, x="ticket_class", y="satisfaction")
    st.plotly_chart(fig_class, use_container_width=True)

with mid2:
    st.subheader("Satisfaction by Touchpoint")
    fig_touch = px.box(filtered, x="touchpoint", y="satisfaction")
    st.plotly_chart(fig_touch, use_container_width=True)

st.divider()

# -----------------------------
# Insights: Pain Points & Positives
# -----------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Top Pain Points")
    pp = filtered["pain_point"].value_counts().reset_index()
    pp.columns = ["pain_point", "count"]
    fig_pp = px.bar(pp.head(10), x="pain_point", y="count")
    st.plotly_chart(fig_pp, use_container_width=True)

with c2:
    st.subheader("Top Positive Feedback")
    pf = filtered["positive_feedback"].value_counts().reset_index()
    pf.columns = ["positive_feedback", "count"]
    fig_pf = px.bar(pf.head(10), x="positive_feedback", y="count")
    st.plotly_chart(fig_pf, use_container_width=True)

st.divider()

# -----------------------------
# Actionable Recommendations (simple rule-based)
# -----------------------------
st.subheader("Actionable Branding & Experience Recommendations (Conceptual)")

if total_travelers == 0:
    st.info("No data after filters. Please adjust filters.")
else:
    # Rule-based quick insights
    worst_touchpoint = (
        filtered.groupby("touchpoint")["satisfaction"].mean().sort_values().index[0]
    )
    worst_route = (
        filtered.groupby("route")["satisfaction"].mean().sort_values().index[0]
    )
    top_pp = filtered["pain_point"].value_counts().index[0]
    top_pf = filtered["positive_feedback"].value_counts().index[0]

    recs = [
        f"Prioritize service improvements at **{worst_touchpoint}** touchpoint (lowest avg satisfaction).",
        f"Improve journey experience for **{worst_route}** route (lowest avg satisfaction).",
        f"Top friction to fix: **{top_pp}** (most frequent pain point).",
        f"Brand strength to amplify: **{top_pf}** (most frequent positive feedback).",
        "Use multilingual, tourism-friendly microcopy and wayfinding signage to reduce confusion.",
        "Integrate local cultural storytelling on high-tourist routes to strengthen Global–Local brand identity."
    ]
    for r in recs:
        st.write("• " + r)

st.divider()

# -----------------------------
# Data Preview
# -----------------------------
with st.expander("See filtered data (preview)"):
    st.dataframe(filtered, use_container_width=True)

st.caption("© Conceptual dashboard for proposal purposes – KAI JourneySense.")

