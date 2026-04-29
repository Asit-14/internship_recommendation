# InternshipT — Project Overview

## Summary

- Title: InternshipT
- Stack: FastAPI (backend), Next.js + React + TypeScript (frontend), PostgreSQL/SQLite (DB), Pydantic schemas, SQLAlchemy ORM.
- Auth: JWT-based; role claims include `student`, `company`, `admin`.

## How to run (backend)

- Create a virtualenv and install dependencies from `backned/requirements.txt`.
- Set environment variables (see `.env`).
- Start server: `uvicorn core.main:app --reload` or run `python run.py`.

## API Base

- Base prefix used in routers: `/api/v1` (see `core.config.settings.api_v1_prefix`).
- Auth: token-based via `Authorization: Bearer <token>` header.

## Major Modules & Responsibilities

- Authentication: `backned/api/v1/endpoints/auth.py` — signup, register-company, login.
- Users: `backned/api/v1/endpoints/user.py` — profile operations, resume upload.
- Internships: `backned/api/v1/endpoints/internship.py` — CRUD + filtering, company/admin role checks.
- Applications: `backned/api/v1/endpoints/application.py` — apply, list personal applications, details, status updates, resume download.
- Recommendations: `backned/api/v1/endpoints/recommendation.py` — skill-based internship recommendations.
- Resume Analyzer: `backned/api/v1/endpoints/resume.py` — upload resume and get recommendations.
- Company: `backned/api/v1/endpoints/company.py` — company-specific endpoints (company internships, applicants).
- Certificates: `backned/api/v1/endpoints/certificate.py` — generate & download certificates (admin restricted).
- Progress: `backned/api/v1/endpoints/progress.py` — add & list progress entries for applications.
- Analytics: `backned/api/v1/endpoints/analytics.py` — admin-only analytic endpoints.
- Admin: `backned/api/v1/endpoints/admin.py` — admin operations (approve companies/users, list/delete resources).

## Important Notes for Frontend Integration

- Login response returns `TokenResponse` with access token — store in client and send as `Authorization: Bearer <token>`.
- Role-based UI: check `role` claim from token or user profile; many routes enforce `require_roles` on the backend.
- File uploads: endpoints use `multipart/form-data` for resume uploads and certificate generation uses file response downloads.

## Docs & Postman

- Machine-readable API summary: `docs/api.json`
- Postman collection (v2.1): `docs/postman_collection.json` — ready to import into Postman; define `baseUrl` and `token` environment variables.

## Next recommended steps

- Auto-generate OpenAPI from running server (`/openapi.json`) and merge with `docs/api.json` for authoritative schema.
- Expand Postman items to include all endpoints and example responses; add pre-request scripts to auto-set `{{token}}` after login.
- Add CI job to validate docs and run backend tests.

## Where to look in the repo

- Routers: `backned/api/v1/endpoints/`
- Services & business logic: `backned/services/`
- Repositories (DB access): `backned/repositories/`
- Schemas: `backned/schemas/`
- Auth/security helpers: `backned/core/security.py`
