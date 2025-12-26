"""Tests for email sender module."""

from patient_intake.email_sender import format_email_body, label_from_id


def test_label_from_id_found():
    """Test label lookup when ID exists."""
    mapping = {"Dog": 1, "Cat": 2}
    assert label_from_id(mapping, 1) == "Dog"
    assert label_from_id(mapping, 2) == "Cat"


def test_label_from_id_not_found():
    """Test label lookup when ID doesn't exist."""
    mapping = {"Dog": 1}
    assert label_from_id(mapping, 99) == ""
    assert label_from_id(mapping, 99, "Unknown") == "Unknown"


def test_format_email_body(
    sample_form_data, sample_extra_fields, sample_species_map, sample_breed_map, sample_sex_map
):
    """Test email body formatting."""
    body = format_email_body(
        sample_form_data,
        sample_extra_fields,
        sample_species_map,
        sample_breed_map,
        sample_sex_map,
    )

    assert "John Doe" in body
    assert "Fluffy" in body
    assert "Canine" in body
    assert "Dr. Smith" in body
    assert "Main St Vet" in body
