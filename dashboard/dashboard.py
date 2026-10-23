
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================================================
# 1. KONFIGURASI
# =========================================================
st.set_page_config(
    page_title="Olist | E-Commerce Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
    }
    div[data-testid="stMetric"] {
        background: rgba(128,128,128,0.07);
        border: 1px solid rgba(128,128,128,0.18);
        padding: 16px;
        border-radius: 12px;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.55rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "main_data.csv"

STATE_MAPPING = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá",
    "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará",
    "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul", "MT": "Mato Grosso",
    "PA": "Pará", "PB": "Paraíba", "PE": "Pernambuco",
    "PI": "Piauí", "PR": "Paraná", "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte", "RO": "Rondônia",
    "RR": "Roraima", "RS": "Rio Grande do Sul",
    "SC": "Santa Catarina", "SE": "Sergipe",
    "SP": "São Paulo", "TO": "Tocantins",
}

CHART_TEMPLATE = "plotly_white"


# =========================================================
# 2. MEMUAT DAN MEMVALIDASI DATA
# =========================================================
@st.cache_data
def load_data(path):
    data = pd.read_csv(path)

    required = [
        "order_id",
        "order_purchase_timestamp",
        "purchase_month",
        "order_value",
        "review_score",
        "customer_state",
        "delivery_delay_days",
    ]

    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(
            "Kolom tidak ditemukan: "
            + ", ".join(missing)
            + ". Periksa kembali main_data.csv dari notebook."
        )

    data["order_purchase_timestamp"] = pd.to_datetime(
        data["order_purchase_timestamp"], errors="coerce"
    )

    data["purchase_month"] = data["purchase_month"].astype("string")

    data["customer_state"] = (
        data["customer_state"]
        .fillna("TIDAK DIKETAHUI")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    for col in ["order_value", "review_score", "delivery_delay_days"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    return data


try:
    df = load_data(str(DATA_PATH))
except Exception as error:
    st.error(f"Gagal memuat data: {error}")
    st.info(
        "Pastikan main_data.csv berada di folder yang sama "
        "dengan dashboard.py."
    )
    st.stop()

if df.empty:
    st.warning("Dataset tidak memiliki baris data.")
    st.stop()

valid_dates = df["order_purchase_timestamp"].dropna()

if valid_dates.empty:
    st.error("Tidak ditemukan tanggal pembelian yang valid.")
    st.stop()


# =========================================================
# 3. HEADER DASHBOARD
# =========================================================
st.title("🛍️ Olist E-Commerce Analytics")
st.markdown(
    """
    Dashboard analisis transaksi, pengalaman pelanggan, dan performa
    pengiriman berdasarkan **Olist Brazilian E-Commerce Public Dataset**.
    """
)

with st.expander("Panduan membaca dashboard"):
    st.markdown(
        """
        - **Jumlah pesanan:** jumlah `order_id` unik.
        - **Nilai produk:** total `order_value` dalam BRL, tidak termasuk ongkir.
        - **Skor ulasan:** rata-rata skor pada skala 1–5.
        - **Terlambat:** `delivery_delay_days > 0`.
        - **Data pengiriman tersedia:** baris dengan nilai
          `delivery_delay_days` yang tidak kosong.
        - **Analisis wilayah:** hanya wilayah dengan minimal 100 baris
          yang memiliki data pengiriman.
        """
    )


# =========================================================
# 4. FILTER
# =========================================================
min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

states = sorted(
    state for state in df["customer_state"].unique()
    if state != "TIDAK DIKETAHUI"
)

state_options = {
    f"{STATE_MAPPING.get(code, code)} ({code})": code
    for code in states
}

with st.sidebar:
    st.header("🔎 Filter Dashboard")

    date_range = st.date_input(
        "Rentang tanggal pembelian",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    selected_state_names = st.multiselect(
        "Negara bagian pelanggan",
        options=list(state_options.keys()),
        help="Kosongkan jika ingin melihat seluruh wilayah.",
    )

    st.divider()
    st.caption("Semua grafik dan metrik mengikuti filter yang dipilih.")

filtered = df.copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["order_purchase_timestamp"].dt.date.between(
            start_date, end_date
        )
    ]
elif isinstance(date_range, (tuple, list)) and len(date_range) == 1:
    selected_date = date_range[0]
    filtered = filtered[
        filtered["order_purchase_timestamp"].dt.date == selected_date
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
        "Tidak ada data untuk filter tersebut. "
        "Coba ubah rentang tanggal atau pilihan wilayah."
    )
    st.stop()


# Status pengiriman dihitung dari satu definisi yang konsisten.
delivery_available = filtered["delivery_delay_days"].notna()
is_late = filtered["delivery_delay_days"].gt(0)

total_orders = filtered["order_id"].nunique()
total_value = filtered["order_value"].sum()
average_review = filtered["review_score"].mean()

delivery_data = filtered.loc[delivery_available]
late_rate = (
    delivery_data["delivery_delay_days"].gt(0).mean() * 100
    if not delivery_data.empty
    else float("nan")
)


# =========================================================
# 5. KPI
# =========================================================
st.subheader("Ringkasan Kinerja")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Jumlah Pesanan", f"{total_orders:,.0f}")
k2.metric("Total Nilai Produk", f"R$ {total_value:,.2f}")
k3.metric(
    "Rata-rata Skor Ulasan",
    "—" if pd.isna(average_review) else f"{average_review:.2f} / 5",
)
k4.metric(
    "Tingkat Keterlambatan",
    "—" if pd.isna(late_rate) else f"{late_rate:.2f}%",
)

coverage = len(delivery_data) / len(filtered) * 100
st.caption(
    f"{len(filtered):,} baris data ditampilkan · "
    f"{coverage:.1f}% baris memiliki informasi pengiriman."
)

st.divider()


# =========================================================
# 6. TREN TRANSAKSI BULANAN
# =========================================================
st.subheader("1. Tren Transaksi Bulanan")
st.caption(
    "Amati perubahan jumlah pesanan dan total nilai produk dari waktu ke waktu."
)

monthly = (
    filtered.dropna(subset=["purchase_month"])
    .groupby("purchase_month", as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        revenue=("order_value", "sum"),
    )
    .sort_values("purchase_month")
)

if monthly.empty:
    st.info("Tidak tersedia data bulanan untuk filter ini.")
else:
    left, right = st.columns(2)

    with left:
        fig_orders = px.line(
            monthly,
            x="purchase_month",
            y="orders",
            markers=True,
            title="Jumlah Pesanan per Bulan",
            labels={
                "purchase_month": "Bulan Pembelian",
                "orders": "Jumlah Pesanan Unik",
            },
            template=CHART_TEMPLATE,
        )
        fig_orders.update_traces(line_width=3, marker_size=7)
        fig_orders.update_layout(
            xaxis_tickangle=-45,
            margin=dict(l=15, r=15, t=60, b=15),
            hovermode="x unified",
        )
        st.plotly_chart(fig_orders, use_container_width=True)

    with right:
        fig_revenue = px.bar(
            monthly,
            x="purchase_month",
            y="revenue",
            title="Total Nilai Produk per Bulan",
            labels={
                "purchase_month": "Bulan Pembelian",
                "revenue": "Total Nilai Produk (BRL)",
            },
            template=CHART_TEMPLATE,
        )
        fig_revenue.update_layout(
            xaxis_tickangle=-45,
            margin=dict(l=15, r=15, t=60, b=15),
        )
        fig_revenue.update_traces(
            hovertemplate=(
                "Bulan: %{x}<br>"
                "Nilai produk: R$ %{y:,.2f}<extra></extra>"
            )
        )
        st.plotly_chart(fig_revenue, use_container_width=True)

st.divider()


# =========================================================
# 7. BUSINESS QUESTION 1
# =========================================================
st.subheader("2. Apakah Keterlambatan Berkaitan dengan Skor Ulasan?")
st.markdown(
    """
    Bandingkan rata-rata skor ulasan pada pesanan terlambat dan pesanan
    yang tiba tepat waktu atau lebih cepat. Perbedaan skor menunjukkan
    hubungan pada data yang diamati, bukan bukti sebab-akibat.
    """
)

review_data = filtered.dropna(
    subset=["delivery_delay_days", "review_score", "order_id"]
).copy()

review_data["Status Pengiriman"] = review_data[
    "delivery_delay_days"
].gt(0).map({
    True: "Terlambat",
    False: "Tepat waktu/lebih cepat",
})

review_summary = (
    review_data.groupby("Status Pengiriman", as_index=False)
    .agg(
        avg_review=("review_score", "mean"),
        orders=("order_id", "nunique"),
    )
)

status_order = ["Tepat waktu/lebih cepat", "Terlambat"]
review_summary["Status Pengiriman"] = pd.Categorical(
    review_summary["Status Pengiriman"],
    categories=status_order,
    ordered=True,
)
review_summary = review_summary.sort_values("Status Pengiriman")

if review_summary.empty:
    st.info("Data ulasan dan pengiriman belum cukup untuk perbandingan.")
else:
    left, right = st.columns([1.4, 1])

    with left:
        fig_review = px.bar(
            review_summary,
            x="Status Pengiriman",
            y="avg_review",
            text="avg_review",
            color="Status Pengiriman",
            color_discrete_map={
                "Tepat waktu/lebih cepat": "#2A9D8F",
                "Terlambat": "#E76F51",
            },
            range_y=[0, 5.5],
            title="Rata-rata Skor Ulasan menurut Status Pengiriman",
            labels={
                "Status Pengiriman": "Status Pengiriman",
                "avg_review": "Rata-rata Skor Ulasan (1–5)",
            },
            template=CHART_TEMPLATE,
        )
        fig_review.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig_review.update_layout(
            showlegend=False,
            margin=dict(l=15, r=15, t=60, b=15),
        )
        st.plotly_chart(fig_review, use_container_width=True)

    with right:
        st.markdown("**Ringkasan kelompok**")

        scores = {}
        for _, row in review_summary.iterrows():
            status = str(row["Status Pengiriman"])
            scores[status] = row["avg_review"]
            st.metric(
                status,
                f'{row["avg_review"]:.2f} / 5',
                help=f'{row["orders"]:,} pesanan unik',
            )
            st.caption(f'{row["orders"]:,} pesanan unik')

        on_time = "Tepat waktu/lebih cepat"
        late = "Terlambat"

        if on_time in scores and late in scores:
            difference = scores[on_time] - scores[late]
            st.info(
                f"Selisih skor rata-rata: **{difference:.2f} poin** "
                "(tepat waktu/lebih cepat dikurangi terlambat)."
            )

st.divider()


# =========================================================
# 8. BUSINESS QUESTION 2
# =========================================================
st.subheader("3. Negara Bagian dengan Tingkat Keterlambatan Tertinggi")
st.markdown(
    """
    Wilayah diurutkan berdasarkan persentase keterlambatan pengiriman.
    Analisis hanya mencakup wilayah dengan minimal **100 baris yang
    memiliki data pengiriman tersedia**.
    """
)

state_summary = (
    filtered.groupby("customer_state", as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        orders_with_delivery_data=("delivery_delay_days", "count"),
        late_rate=(
            "delivery_delay_days",
            lambda values: (
                values.dropna().gt(0).mean() * 100
                if values.notna().any()
                else float("nan")
            ),
        ),
    )
)

priority_states = (
    state_summary[
        state_summary["orders_with_delivery_data"] >= 100
    ]
    .dropna(subset=["late_rate"])
    .sort_values("late_rate", ascending=False)
    .copy()
)

priority_states["Nama Wilayah"] = priority_states[
    "customer_state"
].map(
    lambda code: f"{STATE_MAPPING.get(code, code)} ({code})"
)

if priority_states.empty:
    st.info(
        "Belum ada wilayah yang memenuhi batas 100 baris dengan data "
        "pengiriman pada filter saat ini. Perluas rentang tanggal atau "
        "hapus filter wilayah."
    )
else:
    left, right = st.columns([1.5, 1])

    top_state = priority_states.iloc[0]

    with left:
        plot_state = priority_states.head(10).sort_values("late_rate")

        fig_state = px.bar(
            plot_state,
            x="late_rate",
            y="Nama Wilayah",
            orientation="h",
            text="late_rate",
            title="10 Wilayah dengan Tingkat Keterlambatan Tertinggi",
            labels={
                "late_rate": "Tingkat Keterlambatan (%)",
                "Nama Wilayah": "Negara Bagian Pelanggan",
            },
            template=CHART_TEMPLATE,
        )
        fig_state.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False,
            marker_color="#457B9D",
            hovertemplate=(
                "%{y}<br>"
                "Tingkat keterlambatan: %{x:.2f}%<extra></extra>"
            ),
        )
        fig_state.update_layout(
            xaxis_ticksuffix="%",
            margin=dict(l=15, r=55, t=60, b=15),
        )
        st.plotly_chart(fig_state, use_container_width=True)

    with right:
        st.markdown("**Temuan utama pada filter saat ini**")
        st.metric("Tingkat keterlambatan tertinggi", f'{top_state["late_rate"]:.2f}%')
        st.write(f'**Wilayah:** {top_state["Nama Wilayah"]}')
        st.write(
            "**Baris dengan data pengiriman:** "
            f'{top_state["orders_with_delivery_data"]:,}'
        )
        st.write(f'**Pesanan unik:** {top_state["orders"]:,}')
        st.caption(
            "Peringkat dapat berubah saat filter tanggal atau wilayah diubah."
        )

    with st.expander("Lihat tabel perbandingan wilayah"):
        display_states = priority_states[
            [
                "Nama Wilayah",
                "customer_state",
                "orders",
                "orders_with_delivery_data",
                "late_rate",
            ]
        ].rename(
            columns={
                "Nama Wilayah": "Nama Wilayah",
                "customer_state": "Kode Wilayah",
                "orders": "Pesanan Unik",
                "orders_with_delivery_data": "Baris Data Pengiriman",
                "late_rate": "Tingkat Keterlambatan (%)",
            }
        )

        st.dataframe(
            display_states,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Tingkat Keterlambatan (%)": st.column_config.NumberColumn(
                    format="%.2f%%"
                )
            },
        )

st.divider()


# =========================================================
# 9. DATA DAN UNDUHAN
# =========================================================
with st.expander("Lihat data setelah filter"):
    st.caption(
        "Tabel ini menampilkan data dari main_data.csv yang sesuai "
        "dengan filter dashboard."
    )
    st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.download_button(
        label="⬇️ Unduh data terfilter (CSV)",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="olist_filtered.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption(
    "Sumber: Olist Brazilian E-Commerce Public Dataset. "
    "Nilai produk menggunakan kolom order_value dan tidak termasuk ongkos kirim. "
    "Keterlambatan ditentukan dari delivery_delay_days > 0 pada baris "
    "yang memiliki data selisih pengiriman."
)
