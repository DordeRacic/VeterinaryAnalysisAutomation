import streamlit as st
import json
import re
import requests
import random
import io
from pathlib import Path
import fitz
import smtplib
from email.message import EmailMessage


# === CONFIGURATION ===
SERVICE_TOKEN = st.secrets['api']['service_token_prod']
CATALOGUE_URL = st.secrets['url']['catalogue_url']
PATIENT_ADD_URL = st.secrets['url']['patient_add_url']

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


# === SEND EMAIL AUTOMATICALLY ===
def format_email_body(payload, extra_fields):
    lines = []
    species_label = next(k for k, v in species_map.items() if v == payload['patient_species'])
    breed_label = next(k for k, v in breed_map.items() if v == payload['patient_breed'])
    sex_label = next(k for k,v in sex_map.items() if v == payload['patient_sex'])

    lines.append("**Owner Information**")
    lines.append(f"Name: {payload.get('patient_owner_firstname', '')} {payload.get('patient_owner_lastname', '')}")
    lines.append(f"Secondary Contact: {extra_fields.get('sec_owner_firstname', '')} {extra_fields.get('sec_owner_lastname')}")
    lines.append(f"Address: {payload.get('patient_address', '')}")
    lines.append(f"City/State/ZIP: {payload.get('city', '')}, {payload.get('state', '')} {payload.get('zip', '')}")
    lines.append(f"Phone: {payload.get('phone', '')}")
    lines.append(f"Email: {payload.get('email', '')}")
    lines.append(f"Work Phone: {extra_fields.get('work_no', '')}")
    lines.append(f"Alt Phone: {extra_fields.get('alt_no', '')}")
    lines.append(f"Employer: {extra_fields.get('employer', '')}")
    lines.append(f"Driver's License: {extra_fields.get('drive_lic', '')}")
    lines.append(f"DOB: {extra_fields.get('owner_month')}/{extra_fields.get('owner_day')}/{extra_fields.get('owner_year')}")
    lines.append(f"Previous Client: {extra_fields.get('prev_visit')}")

    lines.append("\n**Patient Information**")
    lines.append(f"Pet Name: {payload['patient_name']}")
    lines.append(f"Species: {species_label}")
    lines.append(f"Breed: {breed_label}")
    lines.append(f"Breed (if not listed):{breed_non_listed}")
    lines.append(f"Sex: {sex_label}")
    lines.append(f"Color: {extra_fields.get('color', '')}")
    lines.append(f"Birthday: {payload['birthday_month']}/{payload['birthday_day']}/{payload['birthday_year']}")
    lines.append(f"Seen Before: {extra_fields.get('pet_prev_visit')}")

    lines.append("\n**Referring Veterinarian**")
    lines.append(f"Doctor: {extra_fields.get('doctor', '')}")
    lines.append(f"Clinic: {extra_fields.get('clinic_name', '')}")

    return "\n".join(lines)

def send_email_with_pdf(pdf_bytes, filename, patient_name, payload, extra_fields):
    email_config = st.secrets['email']

    msg = EmailMessage()
    msg['Subject'] = f"New Patient Intake: {patient_name}"
    msg['From'] = email_config['sender_email']
    msg['To'] = email_config['recipient_email']
    msg.set_content(format_email_body(payload, extra_fields))


    msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename=filename)

    try:
        with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
            server.starttls()
            server.login(email_config["sender_email"], email_config["sender_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email failed to send: {e}")
        return False
# === CAPTCHA ===
if "captcha_passed" not in st.session_state:
    st.session_state.captcha_passed = False

if not st.session_state.captcha_passed:
    if "captcha_answer" not in st.session_state:
        a, b = random.randint(1, 9), random.randint(1, 9)
        st.session_state.captcha_question = f"{a} + {b}"
        st.session_state.captcha_answer = str(a + b)

    st.markdown("### Please solve this to begin:")
    st.write(f"**{st.session_state.captcha_question} = ?**")
    captcha_input = st.text_input("Answer:")

    if st.button("Verify CAPTCHA", key="captcha_button"):
        if captcha_input.strip() == st.session_state.captcha_answer:
            st.success("CAPTCHA passed!")
            st.session_state.captcha_passed = True
            del st.session_state["captcha_answer"]
            del st.session_state["captcha_question"]
            st.rerun()
        else:
            st.error("Incorrect answer. Please try again.")
    st.stop()

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

#=== CLIENT AREA ===
with col1:
    with st.container(border=True):
        st.subheader("Client Information")
        owner_name = st.text_input("Full Name (First and Last):")
        sec_owner_name = st.text_input("Full Name of Secondary Contact:")
        email = st.text_input("Email address:")
        cell_no = st.text_input("Phone number (10 digits):")
        work_no = st.text_input("Work phone:")
        alt_no = st.text_input("Alternative phone:")
        employer= st.text_input("Employer:")
        drive_lic = st.text_input("Driver's Licensce (IF writing check):")
        owner_address = st.text_input("Address:")


        city_col, state_col , zip_col = st.columns(3)
        with city_col:
            city = st.text_input("City:")
        with state_col:
            state = st.text_input("State (2-letter):")
        with zip_col:
            zip_code = st.text_input("Zip Code:")

        dob = st.markdown("**Owner's Date of Birth**")
        dob_col1, dob_col2, dob_col3 = st.columns(3)
        with dob_col1:
            owner_day = st.selectbox("Day", list(range(1, 32)))
        with dob_col2:
            owner_month = st.selectbox("Month", list(range(1, 13)))
        with dob_col3:
            owner_year = st.selectbox("Year", list(range(1920, 2010)))

        prev_visit = st.selectbox("Have you been to our facility before?", ["Yes", "No"])

# === ADD CANINE INDEX FOR SPECIES ===
species_keys = sorted(species_map.keys())
canine_index = species_keys.index("Canine")

# === PATIENT AREA ===
with col2:
    with st.container(border=True):
        st.subheader("Pet Information")
        pet_name = st.text_input("Pet Name:")
        breed_options = [""] + sorted(breed_map.keys())
        breed = st.selectbox("Breed", breed_options, index= 0)
        breed_non_listed = st.text_input("Breed (if not listed):")
        color = st.text_input("Color")
        dob = st.markdown("**Patient's Date of Birth**")
        dob_col1, dob_col2, dob_col3 = st.columns(3)
        with dob_col1:
            day = st.selectbox("Day", list(range(1, 32)), key='pet_day')
        with dob_col2:
            month = st.selectbox("Month", list(range(1,13)),key='pet_month')
        with dob_col3:
            year = st.selectbox("Year", list(range(2000, 2025)), key='pet_year')
        patient_sex = st.selectbox("Sex", sorted(sex_map.keys()))
        patient_species = st.selectbox("Species", species_keys, index= canine_index)
        pet_prev_visit = st.selectbox("Has this pet been at our facility before?", ['Yes','No'])

# === PRIMARY CARE VETERINARIAN INFO
        doctor = st.text_input("Doctor")
        clinic_name = st.text_input("Clinic Name")

agree = st.checkbox("I confirm the information is correct.")
submit_button = st.button("Submit")

def fill_pdf_with_fitz(payload, extra_fields):
    pdf_path = Path(__file__).resolve().parents[1] / "files" / "Client Information Sheet - CR, QC 2025- Updated.pdf"
    doc = fitz.open(pdf_path)
    page = doc[0]



    # Set base font and size
    font_size = 10
    font = "helv"  # Helvetica

    def draw(x, y, text):
        if text:
            page.insert_text((x, y), str(text), fontsize=font_size, fontname=font)


    # === CLIENT INFO ===
    draw(207, 173, f"{payload['patient_owner_firstname']}")
    draw(391, 173, payload.get('patient_owner_lastname', ''))
    draw(207, 193, extra_fields.get("sec_owner_firstname", ""))
    draw(391, 193, extra_fields.get("sec_owner_lastname", ""))
    draw(91, 217, payload.get('patient_address', ''))
    draw(330, 217, f"{payload.get('city', '')}")
    draw(448, 217, payload.get('state', ''))
    draw(511, 217, payload.get('zip', ''))
    draw(121, 236, payload.get('phone', ''))
    draw(116, 298, payload.get('email', ''))
    draw(386, 233, extra_fields.get("work_no", ""))
    draw(137, 254, extra_fields.get("alt_no", ""))
    draw(442, 254, extra_fields.get("employer", ""))
    draw(213, 276, extra_fields.get("drive_lic", ""))
    draw(493, 277, f"{extra_fields.get('owner_month')}/{extra_fields.get('owner_day')}/{extra_fields.get('owner_year')}")
    #draw(294, 320, f"Been here before? {extra_fields.get('prev_visit')}")
    owner_visit_coord = {"Yes": (230, 318),
                       "No": (270, 318)}
    coords_owner = owner_visit_coord.get(extra_fields.get('prev_visit'))
    if coords_owner:
        draw(*coords_owner, 'X')

    # === PET INFO ===
    species_label = next(k for k, v in species_map.items() if v == payload['patient_species'])
    breed_label = next(k for k, v in breed_map.items() if v == payload['patient_breed'])
    draw(85, 358, payload['patient_name'])
    draw(483, 359, species_label)  # Consider converting ID to label if needed
    draw(80, 379, breed_label)    # Same here
    draw(80, 379, breed_non_listed)    # Same here
    draw(483, 401, f"{payload['birthday_month']}/{payload['birthday_day']}/{payload['birthday_year']}")
    age = 2025 - payload['birthday_year']
    draw(400, 380, f"{age}")
    draw(287, 378, extra_fields.get("color", ""))
    #draw(320, 422, f"Seen before? {extra_fields.get('pet_prev_visit')}")
    pet_visit_coord = {"Yes": (260,420),
                       "No": (296,420)}
    coords_pet = pet_visit_coord.get(extra_fields.get('pet_prev_visit'))
    if coords_pet:
        draw(*coords_pet, 'X')
    draw(88, 458, extra_fields.get("doctor", ""))
    draw(308, 458, extra_fields.get("clinic_name", ""))
    sex_coords = {
        "Male": [(136, 403), (335, 403)],  # (gender box, castration blank)
        "Female": [(82, 403), (335, 403)],
        "Castrated male": [(136, 403), (299, 403)],  # (gender box, castrated box)
        "Spayed female": [(82, 403), (299, 403)]
    }

    sex_label = next(k for k, v in sex_map.items() if v == payload["patient_sex"])

    coords = sex_coords.get(sex_label)
    if coords:
        for coord in coords:
            draw(*coord, 'X')

#TODO: Revert the ID to the name for species and breed. Add conditional label filling for gender and sprayed neutered (4 combinations max)
    # Save to in-memory PDF buffer
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output


if submit_button:
    all_valid = True
    st.write("Form submitted")

    if not re.fullmatch(r"[A-Za-z'-]+ [A-Za-z'-]+([A-Za-z'-]+)*", owner_name):
        st.warning("Please enter your full name (first and last).")
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
    if not zip_code:
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
                # Collect extra fields from form for the PDF
                # Split secondary owner name
                sec_first, sec_last = ("", "")
                if sec_owner_name and " " in sec_owner_name:
                    sec_first, sec_last = sec_owner_name.split(" ", 1)
                elif sec_owner_name:
                    sec_first = sec_owner_name  # fallback if only one name entered

                extra_fields = {
                    "sec_owner_firstname": sec_first,
                    "sec_owner_lastname": sec_last,
                    "work_no": work_no,
                    "alt_no": alt_no,
                    "employer": employer,
                    "drive_lic": drive_lic,
                    "owner_day": owner_day,
                    "owner_month": owner_month,
                    "owner_year": owner_year,
                    "prev_visit": prev_visit,
                    "color": color,
                    "breed_not_listed": breed_non_listed,
                    "pet_prev_visit": pet_prev_visit,
                    "doctor": doctor,
                    "clinic_name": clinic_name
                }

                pdf_filled = fill_pdf_with_fitz(payload, extra_fields)
                send_email_with_pdf(
                    pdf_bytes=pdf_filled.getvalue(),
                    filename=f"{payload['patient_name']}_intake_form.pdf",
                    patient_name=payload["patient_name"],
                    payload=payload,
                    extra_fields= extra_fields
                )

                st.success(f"Patient uploaded successfully! ID: {result['patient_id']}")
                st.balloons()
            else:
                st.error(f"API Error: {result.get('message', response.text)}")
                st.stop()

        except Exception as e:
            st.error(f"Request failed: {e}")
            st.stop()
