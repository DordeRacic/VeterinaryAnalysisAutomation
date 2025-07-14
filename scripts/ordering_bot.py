# stokes_order_form.py
import streamlit as st
from datetime import date
import pandas as pd
# from chewy_order import place_chewy_order
from stokes_order_bot import place_stokes_order
# from wedgewood_order import place_wedgewood_order  # Placeholder for future

st.title("Pharmacy - Medication Order Form")

# Load credentials from Excel
@st.cache_data
def load_credentials():
    df = pd.read_excel("credentials.xlsx")  # Must contain columns: website, email, password
    return df

cred_df = load_credentials()

with st.form("pharmacy_form"):
    st.subheader("Patient Info")
    first_name = st.text_input("Patient First Name")
    last_name = st.text_input("Patient Last Name")
    allergy = st.selectbox("Allergy Status", ["No known allergies", "Allergic"])

    st.subheader("Medication")
    use_favorite = st.checkbox("Use Favorite Drug")
    favorite_drug = st.text_input("Favorite Drug Name") if use_favorite else None
    drug_search = st.text_input("Search for Drug") if not use_favorite else None
    quantity = st.number_input("Quantity", min_value=1)
    pricing = st.text_input("Pricing Option (if applicable)")

    st.subheader("Instructions")
    instructions = st.text_area("Dosing Instructions")
    days_supply = st.number_input("Days Supply", min_value=1)
    refill_type = st.selectbox("Refill Type", ["None", "PRN", "Until Date", "# of Refills"])
    refills = None
    if refill_type == "Until Date":
        refills = st.date_input("Refill Until Date", value=date.today())
    elif refill_type == "# of Refills":
        refills = st.number_input("Number of Refills", min_value=0)

    st.subheader("Pharmacy Selection")
    pharmacy = st.selectbox("Select Pharmacy", ["Stokes", "Chewy", "Wedgewood"])

    st.subheader("Confirmation")
    agree_1 = st.checkbox("Confirm order accuracy")
    agree_2 = st.checkbox("Acknowledge legal terms")

    submitted = st.form_submit_button("Submit Order")

if submitted:
    if not all([first_name, last_name, quantity, instructions, days_supply, agree_1, agree_2]):
        st.error("Please complete all required fields.")
    else:
        cred_row = cred_df[cred_df["website"].str.contains(pharmacy, case=False)]
        if cred_row.empty:
            st.error(f"No credentials found for {pharmacy} in Excel.")
        else:
            email = cred_row.iloc[0]["email"]
            password = cred_row.iloc[0]["password"]

            order_data = {
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "allergy": allergy,
                "drug": favorite_drug if use_favorite else drug_search,
                "quantity": quantity,
                "pricing": pricing,
                "instructions": instructions,
                "days_supply": days_supply,
                "refill_type": refill_type,
                "refills": refills,
                "agreed": agree_1 and agree_2,
            }

            st.success(f"Order information collected. Submitting to {pharmacy}...")
            try:
                if pharmacy == "Stokes":
                    place_stokes_order(order_data)
                elif pharmacy == "Chewy":
                    place_chewy_order(
                        email, password, order_data["drug"], order_data["quantity"]
                    )
                elif pharmacy == "Wedgewood":
                    st.warning("Wedgewood automation not implemented yet.")

                st.success("Order placed successfully.")
            except Exception as e:
                st.error(f"Failed to place order: {e}")
