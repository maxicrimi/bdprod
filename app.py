import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging
from styles import get_css, main_header, section_header

# Set page configuration
st.set_page_config(
    page_title="BD_PRODUCCIÓN (2025)",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets Credentials and Scopes
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "1rKwNqAClGicTUkf0H6ZtwcQd4zH43Q9fh6PQ9AUeIHg"

def initialize_gsheets_client():
    try:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Failed to authenticate with Google Sheets: {e}")
        logger.error(f"Authentication error: {e}")
        return None

def get_dataframe(worksheet):
    try:
        data = worksheet.get_all_values()
        if not data:
            logger.warning(f"No data found in worksheet: {worksheet.title}")
            return pd.DataFrame()
        
        header = data[0]
        df = pd.DataFrame(data[1:], columns=header).replace('', pd.NA)
        logger.info(f"Loaded {len(df)} rows from worksheet: {worksheet.title}")
        return df
    except Exception as e:
        logger.error(f"Error fetching data from worksheet {worksheet.title}: {e}")
        return pd.DataFrame()

def update_sheet_data(worksheet, df):
    try:
        data = [df.columns.tolist()] + df.fillna('').values.tolist()
        worksheet.clear()
        worksheet.update(data)
        logger.info(f"Successfully updated worksheet: {worksheet.title}")
    except Exception as e:
        logger.error(f"Error updating worksheet {worksheet.title}: {e}")
        st.error(f"Failed to update data: {e}")

@st.cache_data(ttl=300)
def load_data():
    client = initialize_gsheets_client()
    if client is None:
        return pd.DataFrame(), pd.DataFrame(), None
    
    try:
        sheets = client.open_by_key(SHEET_ID)
        sheet1 = sheets.worksheet("BD_INICIO_OPERARIOS")
        sheet2 = sheets.worksheet("BD_TERMINACION_OPERARIOS")
        return get_dataframe(sheet1), get_dataframe(sheet2), sheets
    except Exception as e:
        st.error(f"Error loading spreadsheet: {e}")
        return pd.DataFrame(), pd.DataFrame(), None

def format_boolean_columns(df, keywords):
    for col in df.columns:
        if any(keyword in col.upper() for keyword in keywords):
            df[col] = df[col].apply(lambda x: str(x).strip().lower() in ["true", "yes", "1", "x", "✓"])
    return df

def main():
    st.markdown(get_css(), unsafe_allow_html=True)
    st.markdown(main_header(), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.markdown("""<div style='padding: 1rem;'>
            <img src='https://via.placeholder.com/150x150?text=Logo' style='width: 150px;'>
        </div>""", unsafe_allow_html=True)
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    with col2:
        with st.spinner("Fetching data from Google Sheets..."):
            data1, data2, sheets_client = load_data()
        
        tab1, tab2 = st.tabs(["BD_INICIO_OPERARIOS", "BD_TERMINACION_OPERARIOS"])
        
        for tab, data, sheet_name in zip([tab1, tab2], [data1, data2], ["BD_INICIO_OPERARIOS", "BD_TERMINACION_OPERARIOS"]):
            with tab:
                st.markdown(section_header(sheet_name), unsafe_allow_html=True)
                if not data.empty:
                    data = format_boolean_columns(data, ["INICIO", "TERMINACIÓN", "TERMINACION", "CORTE"])
                    edited_data = st.data_editor(data, use_container_width=True, key=f"edit_{sheet_name}")
                    if sheets_client:
                        try:
                            sheet = sheets_client.worksheet(sheet_name)
                            update_sheet_data(sheet, edited_data)
                            st.success("Changes saved automatically!")
                        except Exception as e:
                            st.error(f"Error saving data: {e}")
                            logger.error(f"Error saving to {sheet_name}: {e}")
                else:
                    st.warning(f"No data available in '{sheet_name}'.")

if __name__ == "__main__":
    main()
