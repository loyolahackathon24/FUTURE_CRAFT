import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.set_page_config(page_title="Insights", initial_sidebar_state="collapsed")
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

genai.configure(api_key='Your API Key')
model = genai.GenerativeModel('gemini-pro')

st.title('Insights')
col1, col2 = st.columns([1, 0.13])

with col1:
    a = st.button("Home")
with col2:
    b = st.button("Logout")
    
if a:
    st.switch_page('pages/dashboard.py')
if b:
    st.switch_page('main.py')       

def load_data(credentials_file='credentials.json'):
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

        # Define the ranges for the profit and spendings sheets
        profit_range = 'profit!A1:D100'  # Adjust the range as needed
        spendings_range = 'loss!A1:D100'  # Adjust the range as needed

        # Get data from the profit sheet
        profit_result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=profit_range
        ).execute()
        profit_data = profit_result.get('values', [])

        # Get data from the spendings sheet
        spendings_result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=spendings_range
        ).execute()
        spendings_data = spendings_result.get('values', [])

        st.success("Data read successfully.")
        return profit_data, spendings_data
    except Exception as e:
        st.error(f"Error reading data from Google Spreadsheet: {e}")
        st.stop()

def main():
    

    profit_data, spendings_data = load_data()

    # Convert data to DataFrames
    profit_df = pd.DataFrame(profit_data, columns=["Amount", "Date"])
    spendings_df = pd.DataFrame(spendings_data, columns=["Amount", "Date", "Categories"])

    # Bar Chart for Loss by Category
    fig2 = px.bar(spendings_df, x="Categories", y="Amount", title="Loss by Category")
    st.plotly_chart(fig2)

    # Generate content using the generative model
    with st.spinner("Analyzing given data with AI model.."):
        response = model.generate_content(f"Read the following data and provide valuable insights. The first table is profit/gains/salary, and the second table is spendings. ALL THE DATA IS INR \n\nProfit Data:\n{profit_df}\n\nSpendings Data:\n{spendings_df}")
    st.write(response.text)

    # Add Home Button to navigate to the dashboard


if __name__ == "__main__":
    main()
