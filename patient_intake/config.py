"""Configuration management for patient intake form.

Supports both environment variables (for Docker/AWS) and Streamlit secrets (for local dev).
Environment variables take precedence.
"""

import os
from pathlib import Path

import streamlit as st


def _get_config(env_key: str, secrets_section: str, secrets_key: str) -> str:
    """Get config from environment variable or Streamlit secrets."""
    value = os.environ.get(env_key)
    if value:
        return value
    try:
        return st.secrets[secrets_section][secrets_key]
    except (KeyError, FileNotFoundError):
        raise ValueError(f"Missing config: set {env_key} env var or {secrets_section}.{secrets_key} in secrets.toml")


# === API CONFIGURATION ===
SERVICE_TOKEN = _get_config("SERVICE_TOKEN", "api", "service_token")
CATALOGUE_URL = _get_config("CATALOGUE_URL", "url", "catalogue_url")
PATIENT_ADD_URL = _get_config("PATIENT_ADD_URL", "url", "patient_add_url")

# === PATHS ===
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
PDF_TEMPLATE_PATH = TEMPLATES_DIR / "intake_form_template.pdf"


def get_email_config() -> dict:
    """Get email configuration from environment or Streamlit secrets."""
    env_config = {
        "smtp_server": os.environ.get("SMTP_SERVER"),
        "smtp_port": os.environ.get("SMTP_PORT"),
        "sender_email": os.environ.get("SENDER_EMAIL"),
        "sender_password": os.environ.get("SENDER_PASSWORD"),
        "recipient_email": os.environ.get("RECIPIENT_EMAIL"),
    }

    # If all env vars are set, use them
    if all(env_config.values()):
        env_config["smtp_port"] = int(env_config["smtp_port"])
        return env_config

    # Fall back to Streamlit secrets
    try:
        return dict(st.secrets["email"])
    except (KeyError, FileNotFoundError):
        raise ValueError("Missing email config: set SMTP_* env vars or email section in secrets.toml")
