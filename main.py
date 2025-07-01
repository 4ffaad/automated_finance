import streamlit as st 
import pandas as pd 
import plotly.express as px 
import json 
import os 

st.set_page_config(
    page_title="Simple Finance App", 
    page_icon = "💰", 
    layout="wide")

category_file = "categories.json"

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorized": []
    }

if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)

def save_categories():
    with open(category_file,"w") as f:
        json.dump(st.session_state.categories, f)

def categorize_transaction(df):
    df["Category"] = "Uncategorized"

    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorized" or not keywords:
            continue

        lowered_keywords = [keyword.lower().strip() for keyword in keywords]

        for idx, row in df.iterrows():
            details = row["Details"].lower().strip()
            if details in lowered_keywords:
                df.at[idx,"Category"] = category
    return df

def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    return False

def load_transactions(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        #Cleaning Data 
            #Stripping white space in the header column
        df.columns = [col.strip() for col in df.columns]
        df["Amount"] = df["Amount"].str.replace(",","").astype(float)
        df["Date"] = pd.to_datetime(df["Date"], format="%d %b %Y")

        return categorize_transaction(df)
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

            st.session_state.debits_df = debits_df.copy()

            tabl1, tabl2 = st.tabs(["Expenses (Debits)", "Payments (Credits)"])
            
            with tabl1:
                new_category = st.text_input("New Category Name")
                add_button = st.button("Add Category")

                if add_button and new_category:
                    normalized_input = new_category.strip().lower()
                    existing_normalized = [cat.lower() for cat in st.session_state.categories.keys()]

                    if normalized_input not in existing_normalized:
                        st.session_state.categories[new_category.strip()] = []
                        save_categories()
                        st.rerun()
                    else:
                        st.warning(f"Category '{new_category}' already exists (case-insensitive check).")

                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.debits_df[["Date", "Details", "Amount", "Category"]],
                    column_config={
                        "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
                        "Amount": st.column_config.NumberColumn("Amount", format="%.2f AED"),
                        "Category": st.column_config.SelectboxColumn(
                            "Category",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"
                )

                save_button = st.button("Apply Changes", type="primary")
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_cat = row["Category"]
                        if new_cat != st.session_state.debits_df.at[idx, "Category"]:
                            details = row["Details"]
                            st.session_state.debits_df.at[idx, "Category"] = new_cat
                            add_keyword_to_category(new_cat, details)

                                    

            with tabl2:
                st.write(credits_df)
            

main()