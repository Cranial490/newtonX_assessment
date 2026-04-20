# NewtonX Assessment Frontend

React + TypeScript frontend for the NewtonX professional records intake application.
The app lets users view dashboard metrics, add individual professionals, upload CSV files, and review bulk records before submission.

## Features

- Dashboard view at `/` with professional records, source filtering, and summary stats.
- Manual add flow for creating a single professional record.
- Bulk upload view at `/bulk` for staging and submitting multiple records.
- CSV upload support for loading valid rows from uploaded files into the bulk review grid.
- Dashboard stats panel backed by the stats API for total records, complete records, and source-level counts.

## Extension

- Added upload CSV support to add bulk professional records from `.csv` files.
- Added dashboard stats integration using `GET /api/professionals/stats/`.

## Tech Stack

- React 19
- TypeScript
- Vite
- React Router
- TanStack Query
- Tailwind CSS

## Setup

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend runs on Vite's local dev server. API requests to `/api` are proxied to the Django backend at `http://127.0.0.1:8000`.

## Available Scripts

```bash
npm run dev
npm run build
npm run lint
npm run preview
```

## Backend Requirements

Run the backend before using the frontend locally:

```bash
cd ../backend
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Expected API endpoints:

- `GET /api/professionals/`
- `POST /api/professionals/`
- `POST /api/professionals/bulk/`
- `POST /api/professionals/upload/csv/`
- `GET /api/professionals/stats/`

## CSV Upload Format

CSV uploads should include these columns:

```text
full_name,email,phone,company_name,job_title,source
```

Valid rows are loaded into the bulk upload grid for review before submission. Invalid rows are surfaced with validation errors so they can be corrected.

## Checks

Run linting:

```bash
npm run lint
```

Build production assets:

```bash
npm run build
```
