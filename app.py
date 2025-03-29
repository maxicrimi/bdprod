import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import logging
from styles import get_css, main_header, section_header, custom_container

# Set page configuration - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="BD_PRODUCCIÓN (2025)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Set up logging to debug data loading issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets Credentials and Scopes
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "1rKwNqAClGicTUkf0H6ZtwcQd4zH43Q9fh6PQ9AUeIHg"

def initialize_gsheets_client():
    """Initialize Google Sheets client with credentials"""
    try:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Failed to authenticate with Google Sheets: {e}")
        logger.error(f"Authentication error: {e}")
        return None

def get_dataframe(worksheet):
    """
    Fetch all values from a worksheet, ensure unique headers, and convert to DataFrame.
    """
    try:
        data = worksheet.get_all_values()
        if not data:
            logger.warning(f"No data found in worksheet: {worksheet.title}")
            return pd.DataFrame()
        
        # Assume the first row is the header
        header = data[0]
        
        # Ensure unique column names for pandas DataFrame
        seen = {}
        unique_header = []
        for col in header:
            # Handle empty column headers
            if not col.strip():
                col = "Unnamed"
                
            if col in seen:
                seen[col] += 1
                unique_header.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                unique_header.append(col)
        
        # Create DataFrame with data after header row
        df = pd.DataFrame(data[1:], columns=unique_header)
        
        # Convert empty strings to NaN for better data handling
        df = df.replace('', pd.NA)
        
        logger.info(f"Loaded {len(df)} rows from worksheet: {worksheet.title}")
        return df
    except Exception as e:
        logger.error(f"Error fetching data from worksheet {worksheet.title if hasattr(worksheet, 'title') else 'unknown'}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def load_data():
    """Load data from Google Sheets with caching for performance"""
    client = initialize_gsheets_client()
    
    if client is None:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        sheets = client.open_by_key(SHEET_ID)
        
        # Get both worksheets
        try:
            sheet1 = sheets.worksheet("BD_INICIO_OPERARIOS")
            data1 = get_dataframe(sheet1)
        except Exception as e:
            logger.error(f"Error with BD_INICIO_OPERARIOS: {e}")
            data1 = pd.DataFrame()
            
        try:
            sheet2 = sheets.worksheet("BD_TERMINACION_OPERARIOS")
            data2 = get_dataframe(sheet2)
        except Exception as e:
            logger.error(f"Error with BD_TERMINACION_OPERARIOS: {e}")
            data2 = pd.DataFrame()
            
        return data1, data2
    except Exception as e:
        st.error(f"Error loading spreadsheet: {e}")
        logger.error(f"Error loading spreadsheet: {e}")
        return pd.DataFrame(), pd.DataFrame()

def format_boolean_columns(df, keywords):
    """Format boolean columns based on keywords"""
    for col in df.columns:
        if any(keyword in col.upper() for keyword in keywords):
            try:
                df[col] = df[col].apply(
                    lambda x: True if str(x).strip().lower() in ["true", "yes", "1", "x", "✓"] else False
                )
            except Exception as e:
                logger.warning(f"Could not convert column {col} to boolean: {e}")
    return df

def main():
    # Apply custom CSS
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # Main header
    st.markdown(main_header(), unsafe_allow_html=True)
    
    # Create a clean dashboard layout
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.markdown("""
        <div style='padding: 1rem;'>
            <img src="https://via.placeholder.com/150x150?text=Logo" alt="Company Logo" style="width: 150px; height: auto; margin-bottom: 1rem;">
        </div>
        """, unsafe_allow_html=True)
        
        # Add a refresh button
        if st.button("🔄 Refresh Data", key="refresh_button"):
            st.cache_data.clear()
            st.experimental_rerun()
            
        # Add dashboard controls
        st.markdown("<div style='padding-top: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown(section_header("Controls"), unsafe_allow_html=True)
        
        # Add date filters if needed
        date_filter = st.date_input("Filter by date")
    
    with col2:
        # Display a brief introduction with loading state
        with st.spinner("Fetching data from Google Sheets..."):
            # Load the data from both sheets
            data1, data2 = load_data()
        
        # First table section
        st.markdown(section_header("BD_INICIO_OPERARIOS"), unsafe_allow_html=True)
        
        if not data1.empty:
            # Format boolean columns
            data1 = format_boolean_columns(data1, ["INICIO", "CORTE"])
            
            # Display the dataframe
            st.dataframe(data1, use_container_width=True)
        else:
            st.warning("No data available in 'BD_INICIO_OPERARIOS'. Check your connection and sheet access.")
        
        # Second table section
        st.markdown(section_header("BD_TERMINACION_OPERARIOS"), unsafe_allow_html=True)
        
        if not data2.empty:
            # Format boolean columns
            data2 = format_boolean_columns(data2, ["INICIO", "TERMINACIÓN", "TERMINACION"])
            
            # Display the dataframe
            st.dataframe(data2, use_container_width=True)
        else:
            st.warning("No data available in 'BD_TERMINACION_OPERARIOS'. Check your connection and sheet access.")

    # Add a footer
    st.markdown("""
    <div style="text-align: center; margin-top: 2rem; padding: 1rem; background-color: #f8f9fa; border-radius: 8px;">
        <p style="color: #6c757d !important; font-size: 0.8rem;">
            © 2025 Company Name. All rights reserved. | Dashboard Version 1.0
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
