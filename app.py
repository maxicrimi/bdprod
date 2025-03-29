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
    initial_sidebar_state="collapsed",
    # Force light theme
    menu_items={
        'Theme': 'light'
    }
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

def update_sheet_data(worksheet, df, include_header=True):
    """
    Update Google Sheet with dataframe data
    
    Args:
        worksheet: gspread worksheet object
        df: pandas DataFrame with data to update
        include_header: Whether to include the DataFrame header as first row
    """
    try:
        # Convert DataFrame to list of lists for gspread
        if include_header:
            data = [df.columns.tolist()] + df.fillna('').values.tolist()
        else:
            data = df.fillna('').values.tolist()
        
        # Clear existing content and update with new data
        worksheet.clear()
        worksheet.update(data)
        
        logger.info(f"Successfully updated worksheet: {worksheet.title}")
        return True
    except Exception as e:
        logger.error(f"Error updating worksheet {worksheet.title if hasattr(worksheet, 'title') else 'unknown'}: {e}")
        st.error(f"Failed to update data: {e}")
        return False

@st.cache_data(ttl=300)  # Cache data for 5 minutes
def load_data():
    """Load data from Google Sheets with caching for performance"""
    client = initialize_gsheets_client()
    
    if client is None:
        return pd.DataFrame(), pd.DataFrame(), None
    
    try:
        sheets = client.open_by_key(SHEET_ID)
        
        # Get both worksheets
        try:
            sheet1 = sheets.worksheet("BD_INICIO_OPERARIOS")
            data1 = get_dataframe(sheet1)
        except Exception as e:
            logger.error(f"Error with BD_INICIO_OPERARIOS: {e}")
            data1 = pd.DataFrame()
            sheet1 = None
            
        try:
            sheet2 = sheets.worksheet("BD_TERMINACION_OPERARIOS")
            data2 = get_dataframe(sheet2)
        except Exception as e:
            logger.error(f"Error with BD_TERMINACION_OPERARIOS: {e}")
            data2 = pd.DataFrame()
            sheet2 = None
            
        return data1, data2, sheets
    except Exception as e:
        st.error(f"Error loading spreadsheet: {e}")
        logger.error(f"Error loading spreadsheet: {e}")
        return pd.DataFrame(), pd.DataFrame(), None

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
    
    # Force light mode with inline CSS
    st.markdown("""
        <style>
        html, body, [class*="css"] {
            color: #333 !important;
            background-color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
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
        
        # Add a section for data editing mode
        st.markdown(section_header("Edit Mode"), unsafe_allow_html=True)
        edit_mode = st.toggle("Enable editing", value=False)
    
    with col2:
        # Display a brief introduction with loading state
        with st.spinner("Fetching data from Google Sheets..."):
            # Load the data from both sheets
            data1, data2, sheets_client = load_data()
        
        # Tab navigation for the two datasets
        tab1, tab2 = st.tabs(["BD_INICIO_OPERARIOS", "BD_TERMINACION_OPERARIOS"])
        
        with tab1:
            st.markdown(section_header("BD_INICIO_OPERARIOS"), unsafe_allow_html=True)
            
            if not data1.empty:
                # Format boolean columns
                data1 = format_boolean_columns(data1, ["INICIO", "CORTE"])
                
                # If edit mode is enabled, use an editable dataframe
                if edit_mode:
                    edited_data1 = st.data_editor(
                        data1, 
                        use_container_width=True,
                        key="edit_data1",
                        num_rows="dynamic"
                    )
                    
                    # Add save button for the edited data
                    if st.button("Save Changes to BD_INICIO_OPERARIOS"):
                        if sheets_client:
                            try:
                                # Get the worksheet and update it
                                sheet1 = sheets_client.worksheet("BD_INICIO_OPERARIOS")
                                success = update_sheet_data(sheet1, edited_data1)
                                if success:
                                    st.success("Data saved successfully!")
                                    # Clear cache to reload the updated data
                                    st.cache_data.clear()
                            except Exception as e:
                                st.error(f"Error saving data: {e}")
                                logger.error(f"Error saving to BD_INICIO_OPERARIOS: {e}")
                else:
                    # Display read-only dataframe
                    st.dataframe(data1, use_container_width=True)
            else:
                st.warning("No data available in 'BD_INICIO_OPERARIOS'. Check your connection and sheet access.")
        
        with tab2:
            st.markdown(section_header("BD_TERMINACION_OPERARIOS"), unsafe_allow_html=True)
            
            if not data2.empty:
                # Format boolean columns
                data2 = format_boolean_columns(data2, ["INICIO", "TERMINACIÓN", "TERMINACION"])
                
                # If edit mode is enabled, use an editable dataframe
                if edit_mode:
                    edited_data2 = st.data_editor(
                        data2, 
                        use_container_width=True,
                        key="edit_data2",
                        num_rows="dynamic"
                    )
                    
                    # Add save button for the edited data
                    if st.button("Save Changes to BD_TERMINACION_OPERARIOS"):
                        if sheets_client:
                            try:
                                # Get the worksheet and update it
                                sheet2 = sheets_client.worksheet("BD_TERMINACION_OPERARIOS")
                                success = update_sheet_data(sheet2, edited_data2)
                                if success:
                                    st.success("Data saved successfully!")
                                    # Clear cache to reload the updated data
                                    st.cache_data.clear()
                            except Exception as e:
                                st.error(f"Error saving data: {e}")
                                logger.error(f"Error saving to BD_TERMINACION_OPERARIOS: {e}")
                else:
                    # Display read-only dataframe
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
