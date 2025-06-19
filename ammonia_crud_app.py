import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# Load CSV data
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Save data back to CSV
def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# File path to the CSV file
csv_file = "ammonia_assets.csv"

# Load the data
df = load_data(csv_file)

st.title("Ammonia Assets CRUD Tool")

# Sidebar filters
st.sidebar.header("Filter Options")
for column in ['market', 'sector', 'product', 'country_name', 'region', 'super_region']:
    if column in df.columns:
        options = st.sidebar.multiselect(f"Filter by {column}", df[column].dropna().unique())
        if options:
            df = df[df[column].isin(options)]

# Search bar
search_term = st.text_input("Search", "")
if search_term:
    df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]

# Display the filtered data
st.subheader("Ammonia Assets Table")
st.dataframe(df)

# Create new entry
st.subheader("Add New Entry")
with st.form("add_form"):
    new_entry = {}
    for column in df.columns:
        if df[column].dtype == 'int64' or df[column].dtype == 'float64':
            new_entry[column] = st.number_input(column, value=0.0 if df[column].dtype == 'float64' else 0)
        elif 'date' in column.lower():
            new_entry[column] = st.date_input(column, value=datetime.today()).strftime('%Y-%m-%d')
        else:
            new_entry[column] = st.text_input(column, "")
    submitted = st.form_submit_button("Add Entry")
    if submitted:
        df = df.append(new_entry, ignore_index=True)
        save_data(df, csv_file)
        st.success("New entry added successfully.")

# Update or delete entry
st.subheader("Update or Delete Entry")
row_index = st.number_input("Enter row index to update/delete", min_value=0, max_value=len(df)-1, step=1)
if st.button("Load Entry"):
    selected_row = df.iloc[row_index]
    with st.form("update_form"):
        updated_entry = {}
        for column in df.columns:
            if df[column].dtype == 'int64' or df[column].dtype == 'float64':
                updated_entry[column] = st.number_input(column, value=selected_row[column])
            elif 'date' in column.lower():
                updated_entry[column] = st.date_input(column, value=pd.to_datetime(selected_row[column])).strftime('%Y-%m-%d')
            else:
                updated_entry[column] = st.text_input(column, value=str(selected_row[column]))
        update = st.form_submit_button("Update Entry")
        delete = st.form_submit_button("Delete Entry")
        if update:
            for col in df.columns:
                df.at[row_index, col] = updated_entry[col]
            save_data(df, csv_file)
            st.success("Entry updated successfully.")
        if delete:
            df = df.drop(index=row_index).reset_index(drop=True)
            save_data(df, csv_file)
            st.success("Entry deleted successfully.")
