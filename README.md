# Lore Prototype

A minimal prototype for collecting human wisdom.

## Run

pip install -r requirements.txt
uvicorn main:app --reload

Open:
http://127.0.0.1:8000/docs

## Bootstrap Admin (Deployment)

On startup, the backend ensures one admin user exists in the database.
If the configured bootstrap email already exists, that user is promoted to admin.
If it does not exist, the user is created as admin.

Optional environment variables:
- ENABLE_BOOTSTRAP_ADMIN=true
- BOOTSTRAP_ADMIN_EMAIL=admin@lore.app
- BOOTSTRAP_ADMIN_USERNAME=lore_admin
- BOOTSTRAP_ADMIN_PASSWORD=Admin1234!
- DATABASE_HOST_REGEX=expected-host-pattern

Important:
- Change BOOTSTRAP_ADMIN_PASSWORD in production.
- Change OPENAI_API_KEY if it was ever committed to source control.
- Set DATABASE_HOST_REGEX in deployment to fail startup when DATABASE_URL points to an unexpected host.

## First Lore Entry

POST /lore

{
  "person": "Retired Teacher",
  "profession": "Teacher",
  "years_experience": 35,
  "question": "What took you years to learn?",
  "lore": "Children learn best when they feel safe.",
  "tags": ["education", "children"]
}
