import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build
import plotly.express as px

# Configuration
st.set_page_config(page_title="AI Financial Assistant", initial_sidebar_state="collapsed")
st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
)

# API Keys
GEMINI_API_KEY = "Your API Key"
BLAND_API_KEY = 'Your API Key'

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def load_data(credentials_file='credentials.json'):
    """
    Load profit and spendings data from Google Sheets
    """
    try:
        # Load Google Sheets API credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        # Build the Google Sheets API service
        service = build('sheets', 'v4', credentials=credentials)
        
        # Define the spreadsheet ID using session_state
        spreadsheet_id = st.session_state['person_url']
        
        # Fetch profit data
        profit_result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='profit!A1:B1000'
        ).execute()
        profit_data = profit_result.get('values', [])[1:]  # Skip header
        
        # Fetch spendings data
        spendings_result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='loss!A1:C1000'
        ).execute()
        spendings_data = spendings_result.get('values', [])[1:]  # Skip header
        
        return profit_data, spendings_data
    
    except Exception as e:
        st.error(f"Error reading financial data: {e}")
        return [], []

def main():
    # Initialize chat messages if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your AI Financial Assistant. Let's analyze your financial data."}
        ]

    # Load financial data
    profit_data, spendings_data = load_data()
    
    # Convert data to DataFrames
    profit_df = pd.DataFrame(profit_data, columns=["Amount", "Date"])
    spendings_df = pd.DataFrame(spendings_data, columns=["Amount", "Date", "Categories"])
    
    # Convert Amount to numeric, handling potential errors
    profit_df['Amount'] = pd.to_numeric(profit_df['Amount'], errors='coerce')
    spendings_df['Amount'] = pd.to_numeric(spendings_df['Amount'], errors='coerce')

    # Create financial analysis with Gemini
    st.title("AI Financial Assistant")
    
    
    # Prepare AI analysis
    ai_analysis_prompt = f"""
Comprehensive Financial Analysis:

Profit Data Overview:
- Total Profit: ₹{profit_df['Amount'].sum():,.2f}
- Number of Profit Entries: {len(profit_df)}

Spending Data Overview:
- Total Spending: ₹{spendings_df['Amount'].sum():,.2f}
- Number of Spending Entries: {len(spendings_df)}
- Spending Breakdown by Category:
{spendings_df.groupby('Categories')['Amount'].sum().to_string()}

Financial Insights Requested:
1. Analyze current financial health
2. Identify spending patterns
3. Suggest potential savings or investment strategies
4. Provide actionable financial recommendations
"""
    
    # Generate AI insights
    with st.spinner("Analyzing financial data..."):
        try:
            response = model.generate_content(ai_analysis_prompt)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error generating AI insights: {e}")
    
    # Bland AI Call Configuration
    st.subheader("Initiate Financial Consultation Call")
    phone_number = st.text_input("Enter Phone Number", placeholder="Enter without country code (e.g., 9876543210)")
    
    if st.button("Start Financial Call") and phone_number:
        # Prepare call task description
        call_task = f"""
Financial Consultation Call Details:

Financial Summary:
- Total Profit: ₹{profit_df['Amount'].sum():,.2f}
- Total Spending: ₹{spendings_df['Amount'].sum():,.2f}
- Spending Categories: {', '.join(spendings_df['Categories'].unique())}

Call Objectives:
1. Discuss financial performance
2. Review spending patterns
3. Provide personalized financial advice
"""
        
        # Initiate Bland AI Call
        headers = {
            'Authorization': BLAND_API_KEY,
            'Content-Type': 'application/json'
        }
        
        call_data = {
            "phone_number": f"+91{phone_number.strip()}",
            "task": call_task,
            "model": "enhanced",
            "voice": "nat",
            "max_duration": 15,
            "record": True
        }
        
        try:
            response = requests.post('https://api.bland.ai/v1/calls', json=call_data, headers=headers)
            if response.status_code == 200:
                call_response = response.json()
                st.success(f"Financial consultation call initiated! Call ID: {call_response.get('id', 'N/A')}")
            else:
                st.error(f"Call initiation failed: {response.text}")
        except Exception as e:
            st.error(f"Error initiating call: {e}")

if __name__ == "__main__":
    main()