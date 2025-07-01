import streamlit as st 
import pandas as pd 
import plotly.express as px 
import json 
import os 

st.set_page_config(
    page_title="Simple Finance App", 
    page_icon = "💰", 
    layout="wide")

def load_transactions(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        #Cleaning Data 
            #Stripping white space in the header column
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].str.replace(",","").astype(float)
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")

        
        st.write(df)
        return df 
    except Exception as e:
        st.error(f"Error Processing file : {str(e)}")
        return None

def main():
    st.title("Simple Finance Dashboard")

    uploaded_file = st.file_uploader("Upload your transaction CSV file", type=["csv"])

    if uploaded_file is not None: 
        df = load_transactions(uploaded_file)

        if df is not None:
            debits_df = df[df["Debit/Credit"] == "Debit"].copy()
            credits_df = df[df["Debit/Credit"] == "Credit"].copy()

            tabl1, tabl2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
            with tabl1:
                st.write(debits_df)
            with tabl2:
                st.write(credits_df)

main()