# 🛍️ Olist E-Commerce Analytics Dashboard

Dashboard interaktif untuk menganalisis tren transaksi, performa pengiriman, serta kepuasan pelanggan berdasarkan **Olist Brazilian E-Commerce Public Dataset**.

---

## 🛠️ Persiapan Lingkungan (Setup Environment)

### **1. macOS / Linux**

Buka terminal, masuk ke direktori proyek, lalu jalankan perintah berikut:

```bash
# 1. Buat virtual environment (disarankan)
python3 -m venv venv

# 2. Aktifkan virtual environment
source venv/bin/activate

# 3. Install dependencies
pip3 install -r requirements.txt
# Atau jika pip3 belum terhubung:
python3 -m pip install -r requirements.txt

streamlit run dashboard/dashboard.py
# Atau jika perintah streamlit tidak ditemukan:
python3 -m streamlit run dashboard/dashboard.py