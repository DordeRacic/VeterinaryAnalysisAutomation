"""API client for pro4eyes.com backend."""

import requests
import streamlit as st

from patient_intake.config import CATALOGUE_URL, PATIENT_ADD_URL, SERVICE_TOKEN


@st.cache_data(ttl=3600)
def fetch_reference_data() -> tuple[dict, dict, dict]:
    """
    Fetch species, breed, and sex reference data from the API.

    Returns:
        Tuple of (species_map, breed_map, sex_map) dictionaries
        mapping names to IDs.
    """
    headers = {"service-token": SERVICE_TOKEN}
    try:
        response = requests.get(CATALOGUE_URL, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as exc:
        st.error("Unable to load reference data from the server. Please check your connection or try again later.")
        return {}, {}, {}
    except ValueError as exc:
        # Covers JSON decoding errors and other value issues from response.json()
        st.error("Received invalid reference data from the server. Please try again later.")
        return {}, {}, {}

    try:
        species_map = {item["name"]: int(item["id"]) for item in data["species"]}
        breed_map = {item["name"]: int(item["id"]) for item in data["breed"]}
        sex_map = {item["name"]: int(item["id"]) for item in data["sex"]}
    except (KeyError, TypeError, ValueError) as exc:
        # Handles missing keys, wrong types, or non-iterable data structures
        st.error("Reference data from the server is incomplete or malformed. Please try again later.")
        return {}, {}, {}
    return species_map, breed_map, sex_map


def submit_patient(payload: dict) -> requests.Response:
    """
    Submit a new patient to the backend API.

    Args:
        payload: Patient data to submit

    Returns:
        Response object from the API
    """
    headers = {"Content-Type": "application/json", "service-token": SERVICE_TOKEN}
    return requests.post(PATIENT_ADD_URL, headers=headers, json=payload, timeout=20)
