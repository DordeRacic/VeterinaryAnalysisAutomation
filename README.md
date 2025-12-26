# Patient Intake Form

Veterinary patient intake form application for Animal Eye Iowa. Built with Streamlit.

## Features

- Web-based form for collecting veterinary patient intake data
- Integration with backend API for data submission
- Automated PDF generation of filled intake forms
- Email delivery of completed forms
- CAPTCHA protection against automated submissions

## Local Development

### Installation

1. Install Poetry (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Configure secrets:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit secrets.toml with your credentials
   ```

### Running Locally

```bash
poetry run streamlit run patient_intake/app.py
```

### Development Commands

```bash
# Run tests
poetry run pytest

# Run linter
poetry run ruff check .

# Run type checker
poetry run mypy patient_intake/
```

## Docker

### Build and Run

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker compose up --build

# Or run in background
docker compose up -d --build
```

The app will be available at http://localhost:8501

### Build Image Only

```bash
docker build -t patient-intake-form .
```

## AWS Deployment

### Option 1: ECS Fargate (Recommended)

1. Push image to ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
   docker tag patient-intake-form:latest <account>.dkr.ecr.us-east-1.amazonaws.com/patient-intake-form:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/patient-intake-form:latest
   ```

2. Create ECS task definition with environment variables from AWS Secrets Manager

3. Deploy to Fargate with ALB

### Option 2: App Runner

1. Push to ECR (same as above)
2. Create App Runner service pointing to ECR image
3. Configure environment variables in App Runner console

### Environment Variables

| Variable | Description |
|----------|-------------|
| `SERVICE_TOKEN` | API authentication token |
| `CATALOGUE_URL` | API endpoint for catalogues |
| `PATIENT_ADD_URL` | API endpoint for patient submission |
| `SMTP_SERVER` | SMTP server address |
| `SMTP_PORT` | SMTP port (usually 587) |
| `SENDER_EMAIL` | Email sender address |
| `SENDER_PASSWORD` | Email sender password/app password |
| `RECIPIENT_EMAIL` | Email recipient address |

## Project Structure

```
patient-intake-form/
├── pyproject.toml           # Poetry configuration
├── Dockerfile               # Docker build file
├── docker-compose.yml       # Docker Compose config
├── .env.example             # Environment template
├── patient_intake/          # Main package
│   ├── app.py               # Streamlit application
│   ├── config.py            # Configuration (env vars + secrets)
│   ├── api_client.py        # Backend API integration
│   ├── captcha.py           # CAPTCHA functionality
│   ├── email_sender.py      # Email sending
│   └── pdf_generator.py     # PDF generation
├── templates/               # PDF templates
└── tests/                   # Test directory
```
