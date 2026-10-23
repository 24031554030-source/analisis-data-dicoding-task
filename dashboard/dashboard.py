
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Olist E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "main_data.csv"


@st.cache_data
def load_data():
    date_columns = [
        "order_purchase_timestamp",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    df = pd.read_csv(DATA_PATH)

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    required_columns = [
        "order_id",
        "order_purchase_timestamp",
        "purchase_month",
        "order_value",
        "review_score",
        "customer_state",
        "delivery_delay_days",
        "is_late",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(
            "Kolom berikut tidak ditemukan di main_data.csv: "
            + ", ".join(missing)
            + ". Ekspor ulang analysis_df dari notebook terbaru."
        )

    df["purchase_month"] = df["purchase_month"].astype(str)
    df["customer_state"] = (
        df["customer_state"].fillna("Tidak diketahui").astype(str).str.upper()
    )

    df["order_value"] = pd.to_numeric(df["order_value"], errors="coerce")
    df["review_score"] = pd.to_numeric(df["review_score"], errors="coerce")
    df["delivery_delay_days"] = pd.to_numeric(
        df["delivery_delay_days"], errors="coerce"
    )
    df["is_late"] = pd.to_numeric(df["is_late"], errors="coerce")

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()


st.title("🛍️ Olist E-Commerce Analytics Dashboard")
st.caption(
    "Analisis tren transaksi, pengalaman pelanggan, dan performa pengiriman "
    "berdasarkan Olist Brazilian E-Commerce Public Dataset."
)


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


# Filter tanggal dan wilayah
min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()

states = sorted(
    df.loc[
        df["customer_state"] != "TIDAK DIKETAHUI",
        "customer_state"
    ].dropna().unique().tolist()
)

state_options = {
    f"{state_mapping.get(code, code)} ({code})": code
    for code in states
}

with st.sidebar:
    st.header("Filter Dashboard")

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
    )

filtered = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered = filtered[
        filtered["order_purchase_timestamp"].dt.date.between(
            start_date, end_date
        )
    ]

if selected_state_names:
    selected_states = [
        state_options[name] for name in selected_state_names
    ]
    filtered = filtered[
        filtered["customer_state"].isin(selected_states)
    ]

if filtered.empty:
    st.warning(
        "Tidak ada data untuk filter yang dipilih. "
        "Silakan ubah rentang tanggal atau wilayah."
    )
    st.stop()


# Ringkasan metrik
total_orders = filtered["order_id"].nunique()
total_value = filtered["order_value"].sum()
average_review = filtered["review_score"].mean()

delivery_data = filtered.dropna(subset=["delivery_delay_days"])
late_rate = (
    delivery_data["delivery_delay_days"].gt(0).mean() * 100
    if not delivery_data.empty
    else float("nan")
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Jumlah Pesanan", f"{total_orders:,.0f}")
c2.metric("Total Nilai Produk", f"R$ {total_value:,.2f}")
c3.metric(
    "Rata-rata Skor Ulasan",
    "—" if pd.isna(average_review) else f"{average_review:.2f}/5",
)
c4.metric(
    "Tingkat Keterlambatan",
    "—" if pd.isna(late_rate) else f"{late_rate:.2f}%",
)


# Grafik 1 dan 2: tren transaksi bulanan
st.subheader("Tren Transaksi Bulanan")

monthly = (
    filtered.groupby("purchase_month", as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        revenue=("order_value", "sum"),
    )
)

# Format YYYY-MM dari notebook memungkinkan pengurutan kronologis
monthly = monthly.sort_values("purchase_month")

left, right = st.columns(2)

with left:
    fig_orders = px.line(
        monthly,
        x="purchase_month",
        y="orders",
        markers=True,
        labels={
            "purchase_month": "Bulan Pembelian",
            "orders": "Jumlah Pesanan Unik",
        },
        title="Jumlah Pesanan per Bulan",
    )
    fig_orders.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_orders, use_container_width=True)

with right:
    fig_revenue = px.bar(
        monthly,
        x="purchase_month",
        y="revenue",
        labels={
            "purchase_month": "Bulan Pembelian",
            "revenue": "Total Nilai Produk (BRL)",
        },
        title="Total Nilai Produk per Bulan",
    )
    fig_revenue.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_revenue, use_container_width=True)


# Grafik 3: skor ulasan berdasarkan status pengiriman
st.subheader("Pengiriman dan Pengalaman Pelanggan")

left, right = st.columns(2)

with left:
    delivery_review = filtered.dropna(
        subset=["delivery_delay_days", "review_score"]
    ).copy()

    delivery_review["Status Pengiriman"] = (
        delivery_review["delivery_delay_days"]
        .gt(0)
        .map({
            True: "Terlambat",
            False: "Tepat waktu/lebih cepat",
        })
    )

    review_summary = (
        delivery_review.groupby("Status Pengiriman", as_index=False)
        .agg(
            avg_review=("review_score", "mean"),
            orders=("order_id", "nunique"),
        )
    )

    fig_review = px.bar(
        review_summary,
        x="Status Pengiriman",
        y="avg_review",
        text="avg_review",
        range_y=[0, 5],
        labels={
            "Status Pengiriman": "Status Pengiriman",
            "avg_review": "Rata-rata Skor Ulasan (1–5)",
        },
        title="Skor Ulasan berdasarkan Status Pengiriman",
    )
    fig_review.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig_review, use_container_width=True)

    st.caption(
        "Status ditentukan dari selisih tanggal pengiriman aktual "
        "dan estimasi pengiriman pada notebook."
    )


# Grafik 4: wilayah prioritas logistik
with right:
    state_summary = (
        filtered.groupby("customer_state", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            orders_with_delivery_data=("delivery_delay_days", "count"),
            late_rate=(
                "is_late",
                lambda s: s.dropna().mean() * 100,
            ),
        )
    )

    # Konsisten dengan notebook:
    # minimal 100 pesanan dengan data keterlambatan tersedia
    priority_states = (
        state_summary[
            state_summary["orders_with_delivery_data"] >= 100
        ]
        .dropna(subset=["late_rate"])
        .sort_values("late_rate", ascending=False)
        .head(10)
        .copy()
    )

    priority_states["Nama Wilayah"] = priority_states[
        "customer_state"
    ].map(
        lambda code: f"{state_mapping.get(code, code)} ({code})"
    )

    if not priority_states.empty:
        plot_state = priority_states.sort_values("late_rate")

        fig_state = px.bar(
            plot_state,
            x="late_rate",
            y="Nama Wilayah",
            orientation="h",
            text="late_rate",
            labels={
                "late_rate": "Tingkat Keterlambatan (%)",
                "Nama Wilayah": "Negara Bagian Pelanggan",
            },
            title="Wilayah dengan Keterlambatan Tertinggi",
        )
        fig_state.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
        )
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        st.info(
            "Belum ada wilayah yang memenuhi minimal 100 pesanan "
            "dengan data keterlambatan pada filter ini."
        )


# Tabel data
with st.expander("Lihat ringkasan wilayah"):
    if "priority_states" in locals() and not priority_states.empty:
        st.dataframe(
            priority_states[
                [
                    "customer_state",
                    "orders",
                    "orders_with_delivery_data",
                    "late_rate",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Tidak ada data wilayah yang memenuhi batas sampel.")

with st.expander("Lihat data yang digunakan"):
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        label="Unduh data terfilter (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="olist_filtered.csv",
        mime="text/csv",
    )


st.caption(
    "Sumber: Olist Brazilian E-Commerce Public Dataset. "
    "Nilai produk dihitung dari penjumlahan harga item (`order_value`), "
    "tidak termasuk ongkos kirim."
)
