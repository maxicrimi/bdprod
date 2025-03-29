import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging
from styles import get_css, main_header, section_header

st.set_page_config(page_title="BD_PRODUCCIÓN (2025)", layout="wide")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "1rKwNqAClGicTUkf0H6ZtwcQd4zH43Q9fh6PQ9AUeIHg"

def initialize_gsheets_client():
    try:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Failed to authenticate with Google Sheets: {e}")
        return None

def get_dataframe(worksheet):
    try:
        data = worksheet.get_all_values()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data[1:], columns=data[0]).replace('', pd.NA)
        return df
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def update_sheet_data(worksheet, df):
    try:
        worksheet.update([df.columns.tolist()] + df.fillna('').values.tolist())
    except Exception as e:
        logger.error(f"Error updating worksheet: {e}")

def load_data():
    client = initialize_gsheets_client()
    if not client:
        return pd.DataFrame(), pd.DataFrame(), None
    try:
        sheets = client.open_by_key(SHEET_ID)
        return get_dataframe(sheets.worksheet("BD_INICIO_OPERARIOS")), get_dataframe(sheets.worksheet("BD_TERMINACION_OPERARIOS")), sheets
    except Exception as e:
        st.error(f"Error loading spreadsheet: {e}")
        return pd.DataFrame(), pd.DataFrame(), None

def main():
    st.markdown(get_css(), unsafe_allow_html=True)
    st.markdown(main_header(), unsafe_allow_html=True)
    data1, data2, sheets_client = load_data()
    tab1, tab2 = st.tabs(["BD_INICIO_OPERARIOS", "BD_TERMINACION_OPERARIOS"])
    
    with tab1:
        st.markdown(section_header("BD_INICIO_OPERARIOS"), unsafe_allow_html=True)
        if not data1.empty and sheets_client:
            edited_data1 = st.data_editor(data1, use_container_width=True, key="edit_data1", num_rows="dynamic")
            update_sheet_data(sheets_client.worksheet("BD_INICIO_OPERARIOS"), edited_data1)
        else:
            st.warning("No data available.")
    
    with tab2:
        st.markdown(section_header("BD_TERMINACION_OPERARIOS"), unsafe_allow_html=True)
        if not data2.empty and sheets_client:
            edited_data2 = st.data_editor(data2, use_container_width=True, key="edit_data2", num_rows="dynamic")
            update_sheet_data(sheets_client.worksheet("BD_TERMINACION_OPERARIOS"), edited_data2)
        else:
            st.warning("No data available.")

if __name__ == "__main__":
    main()
