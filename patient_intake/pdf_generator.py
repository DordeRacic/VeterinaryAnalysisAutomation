"""PDF generation for patient intake forms."""

import io
from datetime import datetime

import fitz

from patient_intake.config import PDF_TEMPLATE_PATH
from patient_intake.email_sender import label_from_id


def fill_pdf_with_fitz(
    payload: dict, extra_fields: dict, species_map: dict, breed_map: dict, sex_map: dict
) -> io.BytesIO:
    """
    Fill the PDF template with form data.

    Args:
        payload: Main form data (patient info, owner info)
        extra_fields: Additional form fields
        species_map: Species name to ID mapping
        breed_map: Breed name to ID mapping
        sex_map: Sex name to ID mapping

    Returns:
        BytesIO buffer containing the filled PDF
    """
    doc = fitz.open(PDF_TEMPLATE_PATH)
    page = doc[0]

    font_size = 10
    font = "helv"

    def draw(x: float, y: float, text) -> None:
        if text is not None:
            page.insert_text((x, y), str(text), fontsize=font_size, fontname=font)

    # === CLIENT INFO ===
    draw(207, 173, f"{payload['patient_owner_firstname']}")
    draw(391, 173, payload.get("patient_owner_lastname", ""))
    draw(207, 193, extra_fields.get("sec_owner_firstname", ""))
    draw(391, 193, extra_fields.get("sec_owner_lastname", ""))
    draw(91, 217, payload.get("patient_address", ""))
    draw(330, 217, f"{payload.get('city', '')}")
    draw(448, 217, payload.get("state", ""))
    draw(511, 217, payload.get("zip", ""))
    draw(121, 236, payload.get("phone", ""))
    draw(116, 298, payload.get("email", ""))
    draw(386, 233, extra_fields.get("work_no", ""))
    draw(137, 254, extra_fields.get("alt_no", ""))
    draw(442, 254, extra_fields.get("employer", ""))
    draw(213, 276, extra_fields.get("drive_lic", ""))
    draw(
        493,
        277,
        f"{extra_fields.get('owner_month')}/"
        f"{extra_fields.get('owner_day')}/{extra_fields.get('owner_year')}",
    )
    owner_visit_coord = {"Yes": (230, 318), "No": (270, 318)}
    coords_owner = owner_visit_coord.get(extra_fields.get("prev_visit"))
    if coords_owner:
        draw(*coords_owner, "X")

    # === PET INFO ===
    species_label = label_from_id(species_map, payload.get("patient_species"))
    breed_label = label_from_id(breed_map, payload.get("patient_breed"))
    draw(85, 358, payload["patient_name"])
    draw(483, 359, species_label)
    draw(80, 379, breed_label)
    draw(175, 379, extra_fields.get("breed_not_listed", ""))
    draw(
        483,
        401,
        f"{payload['birthday_month']}/{payload['birthday_day']}/{payload['birthday_year']}",
    )
    age = datetime.now().year - payload["birthday_year"]
    draw(400, 380, f"{age}")
    draw(287, 378, extra_fields.get("color", ""))
    pet_visit_coord = {"Yes": (260, 420), "No": (296, 420)}
    coords_pet = pet_visit_coord.get(extra_fields.get("pet_prev_visit"))
    if coords_pet:
        draw(*coords_pet, "X")
    draw(88, 458, extra_fields.get("doctor", ""))
    draw(308, 458, extra_fields.get("clinic_name", ""))

    sex_coords = {
        "Male": [(136, 403), (335, 403)],
        "Female": [(82, 403), (335, 403)],
        "Castrated male": [(136, 403), (299, 403)],
        "Spayed female": [(82, 403), (299, 403)],
    }
    sex_label = label_from_id(sex_map, payload.get("patient_sex"))
    coords = sex_coords.get(sex_label)
    if coords:
        for coord in coords:
            draw(*coord, "X")

    # Save to in-memory PDF buffer
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)
    return output
