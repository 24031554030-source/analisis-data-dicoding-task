
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "main_data.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(
        DATA_PATH,
        parse_dates=["order_purchase_timestamp"]
    )
    df["purchase_month"] = df["purchase_month"].astype(str)
    df["customer_state"] = df["customer_state"].astype(str).str.upper()
    return df


df = load_data()

st.title("🛍️ Olist E-Commerce Analytics Dashboard")
st.caption(
    "Analisis tren pesanan, nilai produk, ulasan pelanggan, "
    "dan performa pengiriman — Brazilian E-Commerce Public Dataset."
)

min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()

state_mapping = {
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

states = sorted(df["customer_state"].dropna().unique().tolist())

state_options = {
    f"{state_mapping.get(code, code)} ({code})": code
    for code in states
}

# Filter
with st.sidebar:
    st.header("Filter")

    date_range = st.date_input(
        "Rentang tanggal pembelian",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    selected_state_names = st.multiselect(
        "Negara bagian pelanggan",
        options=list(state_options.keys()),
        default=[]
    )

    selected_states = [
        state_options[name] for name in selected_state_names
    ]

filtered = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered = filtered[
        filtered["order_purchase_timestamp"].dt.date.between(
            start_date, end_date
        )
    ]

if selected_states:
    filtered = filtered[
        filtered["customer_state"].isin(selected_states)
    ]

if filtered.empty:
    st.warning(
        "Tidak ada data untuk kombinasi filter yang dipilih. "
        "Silakan ubah rentang tanggal atau wilayah."
    )
    st.stop()

# Ringkasan metrik
orders = filtered["order_id"].nunique()
revenue = filtered["order_value"].sum(skipna=True)
avg_review = filtered["review_score"].mean()
late_rate = (
    filtered["is_late"].dropna().astype(float).mean() * 100
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Jumlah pesanan", f"{orders:,.0f}")
c2.metric("Nilai produk", f"R$ {revenue:,.0f}")
c3.metric(
    "Rata-rata ulasan",
    "—" if pd.isna(avg_review) else f"{avg_review:.2f}/5"
)
c4.metric(
    "Tingkat keterlambatan",
    "—" if pd.isna(late_rate) else f"{late_rate:.1f}%"
)

# Tren bulanan
monthly = (
    filtered.dropna(subset=["order_purchase_timestamp"])
    .groupby("purchase_month", as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        revenue=("order_value", "sum"),
        avg_review=("review_score", "mean")
    )
    .sort_values("purchase_month")
)

left, right = st.columns(2)

with left:
    st.subheader("Tren jumlah pesanan per bulan")
    fig_orders = px.line(
        monthly,
        x="purchase_month",
        y="orders",
        markers=True,
        labels={
            "purchase_month": "Bulan",
            "orders": "Jumlah pesanan"
        }
    )
    st.plotly_chart(fig_orders, use_container_width=True)

with right:
    st.subheader("Nilai produk per bulan")
    fig_revenue = px.bar(
        monthly,
        x="purchase_month",
        y="revenue",
        labels={
            "purchase_month": "Bulan",
            "revenue": "Nilai produk (BRL)"
        }
    )
    st.plotly_chart(fig_revenue, use_container_width=True)

# Ulasan dan performa pengiriman
left, right = st.columns(2)

with left:
    st.subheader("Skor ulasan berdasarkan ketepatan pengiriman")

    tmp = filtered.dropna(
        subset=["delivery_delay_days", "review_score"]
    ).copy()

    tmp["Status pengiriman"] = tmp["delivery_delay_days"].gt(0).map({
        True: "Terlambat",
        False: "Tepat waktu/lebih cepat"
    })

    review = (
        tmp.groupby("Status pengiriman", as_index=False)
        .agg(
            avg_review=("review_score", "mean"),
            orders=("order_id", "nunique")
        )
    )

    if not review.empty:
        fig_review = px.bar(
            review,
            x="Status pengiriman",
            y="avg_review",
            labels={
                "Status pengiriman": "Status pengiriman",
                "avg_review": "Rata-rata skor (1–5)"
            },
            text_auto=".2f"
        )
        st.plotly_chart(fig_review, use_container_width=True)
    else:
        st.info("Data ulasan dan pengiriman belum tersedia untuk filter ini.")

with right:
    st.subheader("Wilayah dengan keterlambatan tertinggi")

    state = (
        filtered.groupby("customer_state", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            late_rate=(
                "is_late",
                lambda s: s.dropna().astype(float).mean() * 100
            )
        )
    )

    state = state[state["orders"] >= 100].copy()
    state = state.sort_values(
        "late_rate", ascending=False
    ).head(10)

    state["Nama wilayah"] = state["customer_state"].map(
        lambda code: f"{state_mapping.get(code, code)} ({code})"
    )

    if not state.empty:
        fig_state = px.bar(
            state.sort_values("late_rate"),
            x="late_rate",
            y="Nama wilayah",
            orientation="h",
            labels={
                "late_rate": "Keterlambatan (%)",
                "Nama wilayah": "Negara bagian"
            },
            text_auto=".1f"
        )
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        st.info(
            "Tidak ada wilayah dengan minimal 100 pesanan "
            "pada filter yang dipilih."
        )

# Tabel data dan unduhan
with st.expander("Lihat data yang digunakan"):
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        "Unduh data terfilter (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        "olist_filtered.csv",
        "text/csv"
    )

st.caption(
    "Sumber: Olist Brazilian E-Commerce Public Dataset. "
    "Nilai produk merupakan penjumlahan harga item dan tidak termasuk ongkos kirim."
)
