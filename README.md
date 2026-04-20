# NewtonX Assessment

## Introduction

This repository contains a full-stack professional records intake application.
The backend is a Django REST API for creating, listing, bulk importing, CSV parsing, and reporting professional record stats.
The frontend is a Vite React application for reviewing professional records, adding individual records, uploading CSV files, and managing bulk imports.

## Features

- Create professional records with validation for email, phone, and source.
- Bulk import records with partial success and enrichment of existing records.
- Upload CSV files, review valid and failed rows, and correct validation errors before submission.
- List professionals in a table and filter by signup source.
- View dashboard stats for total records, complete records, data completeness, and source-level counts.

## API Overview

- `POST /api/professionals/` creates a professional.
- `GET /api/professionals/` lists professionals and supports `source` filtering.
- `POST /api/professionals/bulk/` creates or enriches records in bulk.
- `POST /api/professionals/upload/csv/` parses CSV uploads and returns valid and failed rows for review.
- `GET /api/professionals/stats/` returns total, complete, and source-level counts.

## Setup Instructions

### Run with Docker Compose

```bash
docker compose up --build
```

The application will be available at:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/professionals/

Stop the stack:

```bash
docker compose down
```

Stop the stack and remove the persisted SQLite volume:

```bash
docker compose down -v
```

### Run Locally

Backend:

```bash
cd backend
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` requests to the backend.

### Checks

Backend:

```bash
cd backend
uv run pytest
uv run python manage.py check
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

## Assumptions and Trade-offs

- When an incoming record matches an existing professional, the existing record source is kept and only missing fields are enriched.
- Duplicate incoming records do not need to be stored separately; they are used only to enrich existing records.
- SQLite is used for local development and Docker Compose persistence to keep setup lightweight.
- The backend currently runs with Django's development server in Docker Compose for assessment/demo usage.

## Estimated Time

Approximately 3 hours.

## Future Scope

- Add a separate `ProfessionalSource` table to store duplicate incoming records for history and backtracking.
- Implement more sophisticated fuzzy matching for better record resolution.
- Prioritize enrichment based on source quality.
- Add structured backend logging.
- Implement PDF upload with LLM-based data extraction for record enrichment.
- Add asynchronous processing for bulk imports so larger batches can be ingested in the background and users can be notified when processing finishes.
