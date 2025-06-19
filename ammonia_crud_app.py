import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os

CSV_FILE = "ammonia_assets.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        for date_col in ['start_date', 'end_date']:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        return df
    else:
        return pd.DataFrame()

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def validate_input(row):
    errors = []
    if 'value' in row and (pd.isna(row['value']) or row['value'] <= 0):
        errors.append("Value must be a positive number.")
    try:
        start = pd.to_datetime(row['start_date'])
        end = pd.to_datetime(row['end_date'])
        if start >= end:
            errors.append("Start date must be before end date.")
    except:
        errors.append("Invalid date format for start_date or end_date.")
    if not row.get('country_name') or str(row['country_name']).strip() == "":
        errors.append("Country name must not be empty.")
    if not re.match(r"^[A-Z][a-z]{2}-\d{4}$", str(row.get('forecast_month_year', ''))):
        errors.append("Forecast month-year must be in format Mon-YYYY (e.g., Jan-2023).")
    return errors

dropdown_options = {
    "market": ["Asia", "Europe", "North America", "South America", "Africa", "Middle East", "Oceania"],
    "sector": ["Agricultural", "Industrial", "Residential"],
    "series_type": ["Forecast", "Historical"],
    "carbon_intensity": ["High", "Low", "Medium"],
    "product": ["Ammonia", "Nitrate", "Urea"],
    "frequency": ["Monthly", "Quarterly", "Yearly"],
    "metric": ["Consumption", "Export", "Production"],
    "unit": ["kg", "liters"],
    "vintage": ["2020", "2022", "2023"],
    "forecast_name": ["Base", "Optimistic", "Pessimistic"],
    "forecast_month_year": ["Jan-2023", "Feb-2023", "Mar-2023"],
    "forecast_name_full": ["Base Case 2023", "Optimistic Scenario", "Pessimistic Outlook"],
    "country_name": ["Canada", "Germany", "India", "USA"],
    "region": ["East", "North", "South", "West"],
    "super_region": ["APAC", "Americas", "EMEA"],
    "country_opec_oecd": ["Non-OECD", "OECD", "OPEC"]
}

st.set_page_config(layout="wide")
st.title("Ammonia Assets - Excel Style Editor with Filters")

if "rerun_flag" not in st.session_state:
    st.session_state.rerun_flag = False

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Data")
filter_columns = ['market', 'sector', 'product', 'country_name']
filters = {}
for col in filter_columns:
    if col in df.columns:
        options = sorted(df[col].dropna().unique())
        selected = st.sidebar.multiselect(f"Filter by {col}", options, default=options)
        filters[col] = selected

# Apply filters
filtered_df = df.copy()
for col, selected_values in filters.items():
    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]

# Editable data editor
st.subheader("Editable Table")
edited_df = st.data_editor(
    filtered_df,
    num_rows="dynamic",
    use_container_width=True
)

if st.button("Save Changes"):
    df.update(edited_df)
    save_data(df)
    st.success("Changes saved to ammonia_assets.csv")

# Trigger rerun if flag is set
if st.session_state.rerun_flag:
    st.session_state.rerun_flag = False
    st.rerun()
