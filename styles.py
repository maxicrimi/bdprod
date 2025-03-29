# styles.py - Contains all styling for the Streamlit dashboard

def get_css():
    """
    Returns custom CSS styling for the dashboard with professional aesthetics and light mode.
    """
    return """
    <style>
        /* Import Titillium Web font from Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700&display=swap');

        /* Apply Titillium Web font globally and set light background */
        * {
            font-family: 'Titillium Web', sans-serif !important;
        }

        /* Force light mode for the entire app */
        html, body, [class*="css"] {
            color: #333 !important;
            background-color: white !important;
        }
        
        /* Main app container - enforce light mode */
        .stApp {
            background-color: #ffffff !important;
        }

        /* Streamlit containers */
        .css-1d391kg, .css-12oz5g7, .css-1r6slb0, .css-keje6w, .st-emotion-cache-1r6slb0 {
            background-color: #ffffff !important;
        }
        
        /* Dark mode overrides - reset any dark mode styling */
        [data-testid="stAppViewContainer"] {
            background-color: #ffffff !important;
        }
        
        /* Ensure sidebar is in light mode */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa !important;
        }

        /* Header styling */
        .main-header {
            text-align: center;
            padding: 2rem;
            background-color: #658c68 !important;
            color: white !important;
            font-size: 2.5rem;
            font-weight: 600;
            border-radius: 8px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Section headers */
        .section-header {
            color: #658c68 !important;
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            padding-left: 1rem;
            border-left: 5px solid #658c68;
        }

        /* Container styling */
        .custom-container {
            background-color: #ffffff !important;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #e0e0e0 !important;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        /* Force light mode for all elements */
        .stDataFrame, .stTable {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        /* Style for data editor in light mode */
        [data-testid="stDataEditor"] {
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
        }

        /* Style for table headers */
        .stDataFrame thead tr th, .stTable thead tr th {
            background-color: #658c68 !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 10px !important;
            border-bottom: 2px solid #557a56 !important;
        }

        /* Style for table rows */
        .stDataFrame tbody tr td, .stTable tbody tr td {
            background-color: #ffffff !important;
            color: #333333 !important;
            border-bottom: 1px solid #e0e0e0 !important;
            padding: 8px !important;
        }
        
        /* Style for editable cells */
        .stDataEditor-cell {
            color: #333333 !important;
            background-color: #ffffff !important;
        }

        /* Alternating row colors for better readability */
        .stDataFrame tbody tr:nth-child(even) td {
            background-color: #f8f9fa !important;
        }

        /* Hover effect on table rows */
        .stDataFrame tbody tr:hover td {
            background-color: #f0f7f1 !important;
        }

        /* Text color overrides */
        p, span, div, h1, h2, h3, h4, h5, h6 {
            color: #333333 !important;
        }
        
        /* Light mode tabs */
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f8f9fa !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #333333 !important;
        }
        
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #658c68 !important;
        }

        /* Streamlit button styling */
        .stButton > button {
            background-color: #658c68 !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
        }

        .stButton > button:hover {
            background-color: #557a56 !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        }

        /* Success message styling */
        .element-container div[data-testid="stAlert"] {
            background-color: #d4edda !important;
            color: #155724 !important;
            border: 1px solid #c3e6cb !important;
            padding: 10px !important;
            border-radius: 6px !important;
        }

        /* Spinner color */
        .stSpinner > div > div > div {
            border-color: #658c68 transparent transparent !important;
        }
        
        /* Toggle button styling */
        [data-testid="stToggle"] {
            color: #658c68 !important;
        }

        /* Streamlit warning message styling */
        .stAlert {
            background-color: #f8d7da !important;
            color: #721c24 !important;
            border: 1px solid #f5c6cb !important;
            padding: 10px !important;
            border-radius: 6px !important;
        }

        /* Streamlit info message styling */
        .stInfo {
            background-color: #e8f4f8 !important;
            color: #0c5460 !important;
            border: 1px solid #d1ecf1 !important;
            padding: 10px !important;
            border-radius: 6px !important;
        }

        /* Checkbox styling */
        input[type="checkbox"] {
            accent-color: #658c68 !important;
        }

        /* Status indicators */
        .status-complete {
            color: #28a745 !important;
            font-weight: bold !important;
        }

        .status-pending {
            color: #ffc107 !important;
            font-weight: bold !important;
        }

        .status-not-started {
            color: #dc3545 !important;
            font-weight: bold !important;
        }
    </style>
    """

def main_header(title="BD_PRODUCCIÓN (2025)"):
    """
    Returns HTML for the main header with the given title.
    """
    return f"""
    <div class="main-header">
        {title}
    </div>
    """

def section_header(title):
    """
    Returns HTML for a section header with the given title.
    """
    return f"""
    <div class="section-header">
        {title}
    </div>
    """

def custom_container(content):
    """
    Returns HTML for a custom container with the given content.
    """
    return f"""
    <div class="custom-container">
        {content}
    </div>
    """
