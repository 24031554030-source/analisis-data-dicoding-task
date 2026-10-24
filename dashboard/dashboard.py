from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# =====================================================
# 1. KONFIGURASI HALAMAN
# =====================================================
st.set_page_config(
    page_title="Olist | E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# 2. CUSTOM CSS (GRADIENT THEME)
# =====================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

/* HIDE STREAMLIT HEADER */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
    height: 0 !important;
}

/* MAIN BACKGROUND */
.stApp {
    background:
        radial-gradient(circle at 5% 0%, rgba(123,104,238,.13), transparent 28%),
        radial-gradient(circle at 95% 10%, rgba(236,112,181,.12), transparent 25%),
        linear-gradient(135deg, #f7f8ff, #fbfaff 55%, #fff7fb);
    font-family: 'DM Sans', sans-serif;
    color: #202641;
}

/* SIDEBAR OVERVIEW LIST */
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li p {
    color: #ffffff !important;
    opacity: 1 !important;
}

/* MAIN CONTENT CONTAINER */
.block-container {
    max-width: 1500px;
    padding-top: 0.8rem !important;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -0.035em;
    color: #252642;
}

/* HERO BANNER */
.hero {
    padding: 30px 34px;
    border-radius: 24px;
    background: linear-gradient(115deg, #625bd9, #8b72e9 52%, #df79b9);
    color: white;
    box-shadow: 0 15px 38px rgba(105, 91, 208, .16);
    margin-bottom: 25px;
}

.hero-kicker {
    font-size: .75rem;
    letter-spacing: .16em;
    text-transform: uppercase;
    font-weight: 700;
    opacity: .9;
}

.hero h1 {
    color: #ffffff !important;
    margin: 9px 0;
    font-size: 2.45rem;
}

.hero p {
    color: #ffffff !important;
    margin-bottom: 0;
    font-size: 1rem;
}

/* KPI CARDS */
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(220, 213, 242, 0.9);
    border-radius: 18px;
    padding: 20px 16px;
    box-shadow: 0 7px 22px rgba(45, 55, 100, .04);
}

[data-testid="stMetricLabel"] p {
    color: #514b6d !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: #302b63 !important;
    font-family: 'Manrope', sans-serif;
    font-size: clamp(1.05rem, 1.45vw, 1.5rem) !important;
    font-weight: 800;
    line-height: 1.25;
    white-space: normal !important;
    overflow-wrap: anywhere;
}

/* SECTION TEXT */
.section-note {
    color: #625c7d;
    font-size: .92rem;
    margin-top: -10px;
    margin-bottom: 18px;
}

/* DOWNLOAD BUTTON */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(105deg, #6b62df, #c66ebf) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: linear-gradient(105deg, #554bc9, #b957a7) !important;
    color: #ffffff !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# =====================================================
# 3. MEMUAT DATA
# =====================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "main_data.csv"

STATE_MAPPING = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso",
    "PA": "Pará",
    "PB": "Paraíba",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "PR": "Paraná",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RO": "Rondônia",
    "RR": "Roraima",
    "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina",
    "SE": "Sergipe",
    "SP": "São Paulo",
    "TO": "Tocantins",
}


@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)

    if "order_id" not in data.columns or "order_purchase_timestamp" not in data.columns:
        raise ValueError(
            "main_data.csv harus memiliki kolom order_id dan "
            "order_purchase_timestamp."
        )

    data["order_purchase_timestamp"] = pd.to_datetime(
        data["order_purchase_timestamp"], errors="coerce"
    )

    # main_data.csv dari notebook berisi data pesanan dan pengiriman. Lengkapi
    # metrik dashboard dari dataset sumber jika kolom-kolom tersebut belum ada.
    source_dir = BASE_DIR.parent / "data"

    if "purchase_month" not in data.columns:
        if "year_month" in data.columns:
            data["purchase_month"] = data["year_month"]
        else:
            data["purchase_month"] = data["order_purchase_timestamp"].dt.strftime("%Y-%m")

    if "order_value" not in data.columns:
        items_path = source_dir / "order_items_dataset.csv"
        if items_path.exists():
            items = pd.read_csv(items_path, usecols=["order_id", "price"])
            items["price"] = pd.to_numeric(items["price"], errors="coerce")
            values = items.groupby("order_id", as_index=False)["price"].sum()
            data = data.merge(values.rename(columns={"price": "order_value"}), on="order_id", how="left")
        else:
            data["order_value"] = float("nan")

    if "review_score" not in data.columns:
        reviews_path = source_dir / "order_reviews_dataset.csv"
        if reviews_path.exists():
            reviews = pd.read_csv(reviews_path, usecols=["order_id", "review_score"])
            reviews["review_score"] = pd.to_numeric(reviews["review_score"], errors="coerce")
            reviews = reviews.groupby("order_id", as_index=False)["review_score"].mean()
            data = data.merge(reviews, on="order_id", how="left")
        else:
            data["review_score"] = float("nan")

    if "customer_state" not in data.columns:
        customers_path = source_dir / "customers_dataset.csv"
        if customers_path.exists() and "customer_id" in data.columns:
            customers = pd.read_csv(customers_path, usecols=["customer_id", "customer_state"])
            data = data.merge(customers.drop_duplicates("customer_id"), on="customer_id", how="left")
        else:
            data["customer_state"] = "TIDAK DIKETAHUI"

    if "delivery_delay_days" not in data.columns:
        delivered_col = "order_delivered_customer_date"
        estimated_col = "order_estimated_delivery_date"
        if delivered_col in data.columns and estimated_col in data.columns:
            delivered = pd.to_datetime(data[delivered_col], errors="coerce")
            estimated = pd.to_datetime(data[estimated_col], errors="coerce")
            data["delivery_delay_days"] = (delivered - estimated).dt.total_seconds() / 86400
        elif "is_late" in data.columns:
            data["delivery_delay_days"] = pd.to_numeric(data["is_late"], errors="coerce").map(
                {1: 1, 0: 0, True: 1, False: 0}
            )
        else:
            data["delivery_delay_days"] = float("nan")

    for col in ["order_value", "review_score", "delivery_delay_days"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data["purchase_month"] = data["purchase_month"].astype("string")
    data["customer_state"] = (
        data["customer_state"].fillna("TIDAK DIKETAHUI").astype(str).str.upper()
    )

    return data


try:
    df = load_data(str(DATA_PATH))
except Exception as error:
    st.error(f"Gagal memuat data: {error}")
    st.info("Pastikan file main_data.csv berada di folder yang sama dengan dashboard.py.")
    st.stop()

if df.empty or df["order_purchase_timestamp"].dropna().empty:
    st.error("Dataset kosong atau tidak memiliki tanggal pembelian yang valid.")
    st.stop()

# =====================================================
# 4. HEADER & SIDEBAR
# =====================================================
st.markdown(
    """
<div class="hero">
    <div class="hero-kicker">Business Intelligence · Olist Brazil</div>
    <h1>🛍️ Olist E-Commerce Analytics</h1>
    <p>Dashboard interaktif untuk mengeksplorasi tren transaksi, pengalaman pelanggan, dan performa pengiriman.</p>
</div>
""",
    unsafe_allow_html=True,
)

valid_dates = df["order_purchase_timestamp"].dropna()
min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

states = sorted(state for state in df["customer_state"].unique() if state != "TIDAK DIKETAHUI")
state_options = {f"{STATE_MAPPING.get(code, code)} ({code})": code for code in states}

with st.sidebar:
    st.title("📊 Filter Dashboard")
    date_range = st.date_input(
        "Rentang tanggal pembelian",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    selected_state_names = st.multiselect(
        "Negara bagian pelanggan",
        options=list(state_options.keys()),
        default=[],
        placeholder="Semua wilayah",
    )
    st.divider()
    st.caption(f"Periode data: {min_date} — {max_date}")

# Filtering
filtered = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[filtered["order_purchase_timestamp"].dt.date.between(start_date, end_date)]

if selected_state_names:
    selected_states = [state_options[name] for name in selected_state_names]
    filtered = filtered[filtered["customer_state"].isin(selected_states)]

if filtered.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Silakan ubah rentang filter.")
    st.stop()

# =====================================================
# 5. METRIK UTAMA (KPI)
# =====================================================
total_orders = filtered["order_id"].nunique()
total_value = filtered["order_value"].sum(min_count=1)
average_review = filtered["review_score"].mean()

delivery_data = filtered.dropna(subset=["delivery_delay_days"])
late_rate = (
    (delivery_data["delivery_delay_days"] > 0).mean() * 100
    if not delivery_data.empty
    else float("nan")
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("🧾 Pesanan Unik", f"{total_orders:,.0f}")
c2.metric("💰 Total Nilai Produk", "—" if pd.isna(total_value) else f"R$ {total_value:,.2f}")
c3.metric("⭐ Rata-rata Skor Ulasan", "—" if pd.isna(average_review) else f"{average_review:.2f} / 5")
c4.metric("🚚 Tingkat Keterlambatan", "—" if pd.isna(late_rate) else f"{late_rate:.2f}%")

# =====================================================
# 6. TREN TRANSAKSI BULANAN
# =====================================================
st.divider()
st.subheader("📈 Tren Transaksi Bulanan")

monthly = (
    filtered.dropna(subset=["purchase_month"])
    .groupby("purchase_month", as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        revenue=("order_value", "sum"),
    )
    .sort_values("purchase_month")
)

left, right = st.columns(2)

with left:
    fig_orders = px.line(
        monthly,
        x="purchase_month",
        y="orders",
        markers=True,
        title="Jumlah Pesanan per Bulan",
        labels={"purchase_month": "Bulan", "orders": "Jumlah Pesanan Unik"},
    )
    fig_orders.update_traces(line_color="#7668e8", marker_color="#d879bc")
    fig_orders.update_layout(template="plotly_white", margin=dict(l=15, r=15, t=50, b=25))
    st.plotly_chart(fig_orders, use_container_width=True)

with right:
    fig_revenue = px.bar(
        monthly,
        x="purchase_month",
        y="revenue",
        title="Total Nilai Produk per Bulan (BRL)",
        labels={"purchase_month": "Bulan", "revenue": "Total Nilai Produk"},
    )
    fig_revenue.update_traces(marker_color="#8a78e8")
    fig_revenue.update_layout(template="plotly_white", margin=dict(l=15, r=15, t=50, b=25))
    st.plotly_chart(fig_revenue, use_container_width=True)

# =====================================================
# 7. ANALISIS PENGIRIMAN & ULASAN
# =====================================================
st.divider()
st.subheader("🚚 Pengiriman & Pengalaman Pelanggan")

delivery_review = filtered.dropna(subset=["delivery_delay_days", "review_score"]).copy()
delivery_review["Status Pengiriman"] = (delivery_review["delivery_delay_days"] > 0).map(
    {True: "Terlambat", False: "Tepat waktu / lebih cepat"}
)

review_summary = (
    delivery_review.groupby("Status Pengiriman", as_index=False)
    .agg(avg_review=("review_score", "mean"), orders=("order_id", "nunique"))
)

left, right = st.columns(2)

with left:
    fig_review = px.bar(
        review_summary,
        x="Status Pengiriman",
        y="avg_review",
        text="avg_review",
        color="Status Pengiriman",
        color_discrete_map={"Tepat waktu / lebih cepat": "#7568e8", "Terlambat": "#dc79b9"},
        range_y=[0, 5.5],
        title="Rata-rata Skor Ulasan menurut Status Pengiriman",
        hover_data={"orders": True, "avg_review": ":.2f"},
    )
    fig_review.update_traces(
        texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False
    )
    fig_review.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig_review, use_container_width=True)

with right:
    state_delivery = filtered.dropna(subset=["delivery_delay_days"]).drop_duplicates(
        subset=["order_id"]
    )
    if state_delivery.empty:
        st.info("Tidak ada data pengiriman yang valid untuk filter ini.")
    else:
        state_summary = (
            state_delivery.assign(is_late=state_delivery["delivery_delay_days"] > 0)
            .groupby("customer_state", as_index=False)
            .agg(
                orders_with_delivery=("order_id", "nunique"),
                late_rate=("is_late", "mean"),
            )
        )
        state_summary["late_rate"] *= 100

        priority_states = (
            state_summary[state_summary["orders_with_delivery"] >= 100]
            .sort_values("late_rate", ascending=False)
            .head(10)
            .copy()
        )

        if priority_states.empty:
            st.info("Tidak ada wilayah dengan minimal 100 pesanan yang memiliki data pengiriman.")
        else:
            priority_states["Nama Wilayah"] = priority_states["customer_state"].map(
                lambda code: f"{STATE_MAPPING.get(code, code)} ({code})"
            )

            fig_state = px.bar(
                priority_states.sort_values("late_rate"),
                x="late_rate",
                y="Nama Wilayah",
                orientation="h",
                text="late_rate",
                title="Top 10 Wilayah Keterlambatan Tertinggi (≥100 pesanan)",
                labels={"late_rate": "Keterlambatan (%)", "Nama Wilayah": "Wilayah"},
                hover_data={"orders_with_delivery": True, "late_rate": ":.2f"},
            )
            fig_state.update_traces(
                texttemplate="%{text:.2f}%", textposition="outside",
                marker_color="#dc79b9", cliponaxis=False,
            )
            fig_state.update_layout(template="plotly_white")
            st.plotly_chart(fig_state, use_container_width=True)

# =====================================================
# 8. DATA & UNDUHAN
# =====================================================
st.divider()
st.subheader("📄 Detail Data Terfilter")

st.dataframe(filtered, use_container_width=True, hide_index=True)
st.download_button(
    "⬇️ Unduh Data Terfilter (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="olist_filtered.csv",
    mime="text/csv",
    use_container_width=True,
)
