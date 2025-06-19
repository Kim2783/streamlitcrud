import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os

CSV_FILE = "ammonia_assets.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
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
    if not re.match(r"^[A-Z][a-z]{2}-\\d{4}$", str(row.get('forecast_month_year', ''))):
        errors.append("Forecast month-year must be in format Mon-YYYY (e.g., Jan-2023).")
    return errors

st.title("Ammonia Assets CRUD Tool")
df = load_data()

st.subheader("Current Data")
if not df.empty:
    st.dataframe(df)
else:
    st.info("No data available.")

st.subheader("Add New Entry")
with st.form("add_form"):
    new_entry = {}
    columns = [
        'market', 'subdivision', 'sector', 'series_type', 'data_source_name',
        'carbon_intensity', 'product', 'start_date', 'end_date',
        'uploaded_at_utc_date', 'uploaded_at_utc_time', 'dataset_type_name',
        'scenario_name', 'frequency', 'metric', 'unit', 'value', 'vintage',
        'forecast_name', 'forecast_month_year', 'forecast_name_full',
        'id_country', 'country_name', 'id_region', 'region', 'id_super_region',
        'super_region', 'country_opec_oecd', 'source_ids', 'source_ids_batch',
        'transform_utc_time', 'partition_0'
    ]
    for col in columns:
        if col in ['value']:
            new_entry[col] = st.number_input(col, value=0.0)
        elif col in ['subdivision', 'scenario_name', 'id_country', 'id_region', 'id_super_region']:
            new_entry[col] = st.number_input(col, value=0)
        elif 'date' in col:
            new_entry[col] = st.date_input(col)
        else:
            new_entry[col] = st.text_input(col)
    submitted = st.form_submit_button("Add Entry")
    if submitted:
        errors = validate_input(new_entry)
        if errors:
            for err in errors:
                st.error(err)
        else:
            df = df.append(new_entry, ignore_index=True)
            save_data(df)
            st.success("Entry added successfully.")
            st.experimental_rerun()

st.subheader("Delete Entry")
if not df.empty:
    row_to_delete = st.number_input("Enter row index to delete", min_value=0, max_value=len(df)-1, step=1)
    if st.button("Delete"):
        df = df.drop(index=row_to_delete).reset_index(drop=True)
        save_data(df)
        st
