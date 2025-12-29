"""Pytest fixtures for patient intake form tests."""

import pytest


@pytest.fixture
def sample_form_data():
    """Sample form data for testing."""
    return {
        "patient_name": "Fluffy",
        "patient_species": 1,
        "patient_breed": 1,
        "patient_sex": 1,
        "birthday_day": 15,
        "birthday_month": 6,
        "birthday_year": 2020,
        "patient_owner_firstname": "John",
        "patient_owner_lastname": "Doe",
        "patient_address": "123 Main St",
        "patient_email": "john@example.com",
        "patient_phone": "5551234567",
        "address": "123 Main St",
        "email": "john@example.com",
        "phone": "5551234567",
        "city": "Des Moines",
        "state": "IA",
        "zip": "50309",
        "company_id": 1,
    }


@pytest.fixture
def sample_extra_fields():
    """Sample extra fields for testing."""
    return {
        "sec_owner_firstname": "Jane",
        "sec_owner_lastname": "Doe",
        "work_no": "5559876543",
        "alt_no": "",
        "employer": "Acme Corp",
        "drive_lic": "IA12345",
        "owner_day": 1,
        "owner_month": 1,
        "owner_year": 1980,
        "prev_visit": "No",
        "color": "Brown",
        "breed_not_listed": "",
        "pet_prev_visit": "No",
        "doctor": "Dr. Smith",
        "clinic_name": "Main St Vet",
    }


@pytest.fixture
def sample_species_map():
    """Sample species mapping for testing."""
    return {"Canine": 1, "Feline": 2, "Equine": 3}


@pytest.fixture
def sample_breed_map():
    """Sample breed mapping for testing."""
    return {"Labrador": 1, "Siamese": 2, "Arabian": 3}


@pytest.fixture
def sample_sex_map():
    """Sample sex mapping for testing."""
    return {"Male": 1, "Female": 2, "Castrated male": 3, "Spayed female": 4}
