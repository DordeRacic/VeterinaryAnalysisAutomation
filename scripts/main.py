import streamlit as st
import json
from pathlib import Path
import re
import requests

# === CONFIGURATION ===
SERVICE_TOKEN = st.secrets['api']['service_token']
CATALOGUE_URL = "http://test.pro4eyes.com/api/external_catalogues.php"
PATIENT_ADD_URL = "http://test.pro4eyes.com/api/external_patient_add.php"

# === CACHING REFERENCE DATA (Species, Breeds, Sex IDs) ===
@st.cache_data(ttl=3600)
def fetch_reference_data():
    headers = {"service-token": SERVICE_TOKEN}
    response = requests.get(CATALOGUE_URL, headers=headers)
    data = response.json()
    species_map = {item["name"]: int(item["id"]) for item in data["species"]}
    breed_map = {item["name"]: int(item["id"]) for item in data["breed"]}
    sex_map = {item["name"]: int(item["id"]) for item in data["sex"]}
    return species_map, breed_map, sex_map

species_map, breed_map, sex_map = fetch_reference_data()

# === LOCAL FALLBACK STORAGE ===
base_path = Path(__file__).resolve().parents[1]
data_path = base_path / 'files' / 'data.json'
data_path.parent.mkdir(exist_ok=True)

if data_path.exists():
    with open(data_path, 'r') as f:
        local_data = json.load(f)
else:
    local_data = []

# === UI FORM ===
st.markdown("""
<style>
.responsive-box {
    width: 100%;
    max-width: 480px;
    padding: 1rem;
    border: 1px solid #CCC;
    border-radius: 10px;
    background-color: #f9f9f9;
    margin: 0 auto;
}

/* Optional: Adjust width on really small screens */
@media screen and (max-width: 768px) {
    .responsive-box {
        max-width: 100%;
    }
}
</style>
""", unsafe_allow_html=True)




st.header("Patient Intake Form")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("Owner Information")
        owner_name = st.text_input("Full Name (First and Last):")
        email = st.text_input("Email address:")
        cell_no = st.text_input("Phone number (10 digits):")
        owner_address = st.text_input("Address:")

        city_col, state_col , zip_col = st.columns(3)
        with city_col:
            city = st.text_input("City:")
        with state_col:
            state = st.text_input("State (2-letter):")
        with zip_col:
            zip_code = st.text_input("Zip Code (optional):")


with col2:
    with st.container(border=True):
        st.subheader("Patient Information")
        pet_name = st.text_input("Pet Name:")
        breed = st.selectbox("Breed", sorted(breed_map.keys()))
        dob_col1, dob_col2, dob_col3 = st.columns(3)
        with dob_col1:
            day = st.selectbox("Day", list(range(1, 32)))
        with dob_col2:
            month = st.selectbox("Month", list(range(1,13)))
        with dob_col3:
            year = st.selectbox("Year", list(range(2000, 2025)))
        patient_sex = st.selectbox("Sex", sorted(sex_map.keys()))
        patient_species = st.selectbox("Species", sorted(species_map.keys()))

agree = st.checkbox("I confirm the information is correct.")
submit_button = st.button("Submit")

if submit_button:
    all_valid = True

    if not re.fullmatch(r"[A-Za-z'-]+ [A-Za-z'-]+([A-Za-z'-]+)*", owner_name):
        st.warning("Please enter your full name (first and last).")
        all_valid = False

    if not re.fullmatch(r"[^@\\s]+@[^@\\s]+\\.[^@\\s]+", email):
            st.warning("Please enter a valid email address.")
            all_valid = False

    if not re.fullmatch(r"\d{10}", cell_no):
        st.warning("Please enter a valid phone number (10 digits only).")
        all_valid = False

    if not re.fullmatch(r"[A-Za-z ]+", pet_name):
        st.warning("Please enter a valid pet name (letters and spaces only).")
        all_valid = False

    if not agree:
        st.warning("Please check the confirmation box.")
        all_valid = False

    if all_valid:
        first, last = owner_name.split(" ", 1)
        payload = {
            "company_id": 1,
            "patient_name": pet_name,
            "patient_species": species_map.get(patient_species),
            "patient_breed": breed_map.get(breed),
            "patient_sex": sex_map.get(patient_sex),
            "birthday_day": day,
            "birthday_month": month,
            "birthday_year": year,
            "patient_owner_firstname": first,
            "patient_owner_lastname": last,

            # Legacy fields (required for validation)
            "patient_address": owner_address,
            "patient_email": email,
            "patient_phone": cell_no,

            # Modern fields that actually populate the SQL
            "address": owner_address,
            "email": email,
            "phone": cell_no,
            "city": city,
            "state": state,
            "zip": zip_code
        }

        headers = {
            "Content-Type": "application/json",
            "service-token": SERVICE_TOKEN
        }

        try:
            response = requests.post(PATIENT_ADD_URL, headers=headers, json=payload)
            result = response.json()

            if response.status_code == 200 and result.get("result") == "success":
                st.success(f"Patient uploaded successfully! ID: {result['patient_id']}")
                st.balloons()
            else:
                st.error(f"API Error: {result.get('message', response.text)}")
                raise Exception("API returned failure")

        except Exception as e:
            st.warning("API submission failed. Saving locally as backup.")
            local_data.append(payload)
            with open(data_path, 'w') as f:
                json.dump(local_data, f, indent=2)
            st.success("Data saved locally.")
