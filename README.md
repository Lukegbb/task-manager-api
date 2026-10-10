# Task Manager API

![CI](https://github.com/Lukegbb/task-manager-api/actions/workflows/ci.yml/badge.svg)

A REST API to manage **projects and tasks**, built with **Django REST Framework**, **JWT authentication** and **PostgreSQL**, fully containerised with **Docker** and tested on every push with **GitHub Actions**.

## Features

- **JWT authentication** – register, obtain and refresh tokens (`djangorestframework-simplejwt`)
- **Projects & tasks** – full CRUD; each user only sees and edits their own data
- **Filtering, search and ordering** – e.g. `/api/tasks/?status=done&priority=3&search=login&ordering=due_date`
- **Pagination** and **rate limiting**
- **Project statistics** – `/api/projects/{id}/stats/` returns task counts per status
- **Interactive docs** – OpenAPI schema + Swagger UI (`drf-spectacular`)
- **Automated tests** with `APITestCase`, run in CI against PostgreSQL

## Tech stack

Python 3.12 · Django 5 · Django REST Framework · Simple JWT · django-filter · drf-spectacular · PostgreSQL · Docker / Docker Compose · GitHub Actions

## Getting started

### With Docker (recommended)

```bash
git clone https://github.com/Lukegbb/task-manager-api.git
cd task-manager-api
docker compose up --build
```

The API runs at http://localhost:8000 and the docs at http://localhost:8000/api/docs/.

### Locally (SQLite)

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Run the tests

```bash
python manage.py test
```

## API overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Create an account |
| POST | `/api/auth/token/` | Get access + refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh the access token |
| GET / POST | `/api/projects/` | List / create projects |
| GET / PUT / PATCH / DELETE | `/api/projects/{id}/` | Retrieve / update / delete a project |
| GET | `/api/projects/{id}/stats/` | Task counts by status |
| GET / POST | `/api/tasks/` | List (filter, search, order) / create tasks |
| GET / PUT / PATCH / DELETE | `/api/tasks/{id}/` | Retrieve / update / delete a task |

### Example

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "email": "demo@example.com", "password": "Str0ng-pass-123"}'

# 2. Get a token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "Str0ng-pass-123"}'

# 3. Create a project
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Website redesign"}'
```

## Project structure

```
├── config/              # Django settings, URLs, WSGI
├── tasks/
│   ├── models.py        # Project and Task models
│   ├── serializers.py   # Validation and ownership checks
│   ├── views.py         # ViewSets + stats action
│   ├── urls.py          # Router
│   └── tests/           # API tests
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | SQLite file | e.g. `postgres://user:pass@host:5432/db` |
| `DJANGO_SECRET_KEY` | dev key | Set a strong value in production |
| `DJANGO_DEBUG` | `True` | `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts |
