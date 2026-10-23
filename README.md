# 🛍️ Olist E-Commerce Analytics Dashboard

**Exploratory Data Analysis · Business Intelligence · Streamlit**

An end-to-end data analysis project using the Brazilian E-Commerce Public Dataset by Olist to explore monthly order trends, product value, customer reviews, and delivery performance.

![Olist E-Commerce Analytics Dashboard](dashboard/dashboard-preview.png)

## 📌 Project Overview

This project explores e-commerce transaction data to understand order trends, product value, customer satisfaction, and delivery performance. It combines data wrangling, data cleaning, exploratory data analysis (EDA), aggregation, visualization, and business recommendations in an interactive Streamlit dashboard.

## 🎯 Business Questions

1. How did monthly order counts and product value change during the analysis period, and which months recorded the highest and lowest values?
2. How did average customer review scores differ between late and on-time or early deliveries?
3. Which customer states recorded the highest late-delivery rates among states with at least 100 orders containing delivery data?

## 📊 Dashboard

The interactive dashboard provides:

- Monthly order trends.
- Monthly product value trends.
- Average customer review scores.
- Delivery performance indicators.
- Filters for purchase date and customer state.
- Regional comparisons of late-delivery rates.

**Live dashboard:** Add your deployed Streamlit Community Cloud URL after deployment.

## 🔎 Analysis Workflow

1. **Data Wrangling** — Load and inspect the required datasets.
2. **Data Cleaning** — Handle missing values, data types, and data consistency.
3. **Exploratory Data Analysis** — Explore transaction patterns, customer reviews, and delivery performance.
4. **Data Aggregation** — Summarize monthly metrics and compare delivery performance by customer state.
5. **Visualization** — Present the results through charts and an interactive dashboard.
6. **Business Insights** — Interpret the findings and develop data-informed recommendations.

## 💡 Key Findings

*The numerical findings below should be completed using the latest executed notebook and dashboard data.*

- **Transaction trends:** Report the months with the highest and lowest order counts and product values.
- **Customer satisfaction:** Compare average review scores for late deliveries and on-time or early deliveries.
- **Regional delivery performance:** Highlight customer states with the highest late-delivery rates among states with at least 100 orders containing delivery data.

## 🛠️ Tech Stack

- Python
- Pandas and NumPy
- Matplotlib and Seaborn
- Plotly
- Jupyter Notebook
- Streamlit

## 📁 Project Structure

```text
olist-ecommerce-analysis/
├── dashboard/
│   ├── dashboard.py
│   ├── main_data.csv
│   └── dashboard-preview.png
├── data/
│   ├── customers_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── data_1.csv
│   └── data_2.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

*The structure above is illustrative. Keep only files and folders that actually exist in the repository.*

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or a compatible version
- pip
- Git
- Visual Studio Code (recommended)

### 1. Clone the repository

```bash
git clone https://github.com/24031554030-source/olist-ecommerce-analysis.git
cd olist-ecommerce-analysis
```

### 2. Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
py -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Run the dashboard

From the repository root:

```bash
streamlit run dashboard/dashboard.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

Press `Ctrl + C` to stop the application.

### 5. Run the analysis notebook

Open `notebook.ipynb` in Visual Studio Code, select the project's Python environment, and execute the cells sequentially.

Ensure that the required datasets are available at the paths referenced by the notebook. If the notebook generates the dashboard dataset, regenerate `dashboard/main_data.csv` after making analysis changes.

## ⚠️ Notes and Limitations

- Results depend on the datasets, cleaning steps, and analysis period.
- Delivery metrics exclude records without the required delivery information.
- Regional comparisons include only states meeting the minimum sample threshold of 100 orders with delivery data.
- Review-score comparisons are descriptive and do not establish causation.
- Include only files permitted by the project requirements and ensure that all referenced files exist.

## 👩‍💻 Author

**Fio Octriyanti**

Undergraduate Data Science Student  
State University of Surabaya (UNESA)
