import streamlit as st
import pandas as pd
import re
from datetime import datetime
import os

# File path
CSV_FILE = "ammonia_assets.csv"

# Load data
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame()

# Save data
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Validate input
def validate_input(row):
    errors = []

    # value must be positive
    if 'value' in row and (pd.isna(row['value']) or row['value'] <= 0):
        errors.append("Value must be a positive number.")

    # start_date must be before end_date
    try:
        start = pd.to_datetime(row['start_date'])
        end = pd.to_datetime(row['end_date'])
        if start >= end:
            errors.append("Start date must be before end date.")
    except:
        errors.append("Invalid date format for start_date or end_date.")

    # country_name must not be empty
    if not row.get('country_name') or str(row['country_name']).strip() == "":
        errors.append("Country name must not be empty.")

    # forecast_month_year must match Mon-YYYY
    if not re.match(r"^[A-Z][a-z]{2}-\\d{4}$", str(row.get('forecast_month_year', ''))):
        errors.append("Forecast month-year must be in format Mon-YYYY (e.g., Jan-2023).")

    return errors

# Streamlit UI
st.title("Ammonia Assets CRUD Tool")

df = load_data()

# Display data
st.subheader("Current Data")
if not df.empty:
    st.dataframe(df)
else:
    st.info("No data available.")

# Create new entry
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

# Delete entry
st.subheader("Delete Entry")
if not df.empty:
    row_to_delete = st.number_input("Enter row index to delete", min_value=0, max_value=len(df)-1, step=1)
    if st.button("Delete"):
        df = df.drop(index=row_to_delete).reset_index(drop=True)
        save_data(df)
        st.success("Entry deleted.")
        st.experimental_rerun()

# Update entry
st.subheader("Update Entry")
if not df.empty:
    row_to_update = st.number_input("Enter row index to update", min_value=0, max_value=len(df)-1, step=1)
    if st.button("Load Row"):
        st.session_state['update_row'] = df.loc[row_to_update].to_dict()

    if 'update_row' in st.session_state:
        with st.form("update_form"):
            updated_entry = {}
            for col in columns:
                default = st.session_state['update_row'].get(col, "")
                if col in ['value']:
                    updated_entry[col] = st.number_input(f"{col} (update)", value=float(default) if default != "" else 0.0)
                elif col in ['subdivision', 'scenario_name', 'id_country', 'id_region', 'id_super_region']:
                    updated_entry[col] = st.number_input(f"{col} (update)", value=int(default) if default != "" else 0)
                elif 'date' in col:
                    try:
                        default_date = pd.to_datetime(default).date()
                    except:
                        default_date = datetime.today().date()
                    updated_entry[col] = st.date_input(f"{col} (update)", value=default_date)
                else:
                    updated_entry[col] = st.text_input(f"{col} (update)", value=str(default))

            update_submit = st.form_submit_button("Update
