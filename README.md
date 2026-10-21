
# 🛍️ Olist E-Commerce Analytics Dashboard

**Exploratory Data Analysis · Business Intelligence · Streamlit**

An end-to-end data analysis project using the Brazilian E-Commerce Public Dataset by Olist to explore monthly transaction trends, product value, customer reviews, and delivery performance.

![Olist E-Commerce Analytics Dashboard](dashboard/dashboard-preview.png)

## 📌 Project Overview

This project analyzes e-commerce transactions to identify business patterns and provide insights into sales activity and delivery performance.

The analysis includes data wrangling, data cleaning, exploratory data analysis (EDA), data aggregation, visualization, and business recommendations. An interactive Streamlit dashboard is provided to explore the results.

## 🎯 Business Questions

1. How did the number of unique orders and total product value change monthly during the analysis period, and which months recorded the highest and lowest values?
2. How did average review scores differ between late and on-time or early deliveries, and which customer states recorded the highest late-delivery rates among states with at least 100 orders containing delivery data?

## 📊 Dashboard

The Streamlit dashboard provides:

- Monthly order trends.
- Monthly product value trends.
- Average customer review scores.
- Delivery delay rate.
- Filters for purchase date and customer state.

**Live dashboard:** Add your deployed Streamlit Community Cloud URL here after deployment.

## 🔎 Analysis Workflow

1. **Data Wrangling** — Load the datasets and inspect their structure.
2. **Data Cleaning** — Handle missing values, data types, and data consistency.
3. **Exploratory Data Analysis** — Examine distributions and summarize key metrics.
4. **Data Aggregation** — Compare monthly transaction patterns and delivery performance by customer state.
5. **Visualization** — Present the findings using charts and an interactive dashboard.
6. **Business Insights** — Interpret the results and formulate recommendations.

## 💡 Key Findings

The final findings are derived from the executed notebook and dashboard.

- **Transaction trends:** Identify the months with the highest and lowest order counts and product values.
- **Delivery performance:** Compare average review scores between late and on-time or early deliveries.
- **Regional performance:** Identify customer states with elevated late-delivery rates using a minimum sample threshold.

Replace these summary statements with numerical findings from the completed analysis before publishing the final version.

## 🛠️ Tech Stack

- Python
- Pandas and NumPy
- Matplotlib and Seaborn
- Jupyter Notebook
- Streamlit

## 📁 Project Structure

```text
submission/
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
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

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or a compatible version.
- pip.
- Git.
- Visual Studio Code (recommended).

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
pip install -r requirements.txt
```

### 4. Run the Streamlit dashboard locally

From the repository root, run:

```bash
streamlit run dashboard/dashboard.py
```

Open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

Press `Ctrl + C` in the terminal to stop the application.

### 5. Run the analysis notebook

Open `notebook.ipynb` in Visual Studio Code, select the project's Python environment, and run the cells sequentially.

Ensure the required datasets are available in the paths referenced by the notebook.

## ⚠️ Notes

- Analysis results depend on the datasets and date range used.
- Delivery metrics exclude records without the required delivery information.
- Review-score comparisons are descriptive and do not establish causation.
- Only datasets required by the project should be included in the repository.

## 👩‍💻 Author

**Fio Octriyanti**

Undergraduate Data Science Student  
State University of Surabaya (UNESA)
# olist-ecommerce-analysis
