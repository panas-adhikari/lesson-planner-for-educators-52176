# Lesson Planner for Educators

A lightweight Lesson Planner app for teachers to create courses, add topics, schedule lessons, and track student progress.

## Containers

- Backend (Django + DRF): `lesson-planner-for-educators-52176/course_planner_backend` (runs on port **3001**)
- Frontend (React): `lesson-planner-for-educators-52175/course_planner_frontend` (runs on port **3000**)

## Backend API

Base URL: `/api`

Key endpoints:
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`
- `GET /api/dashboard/`
- `GET/POST /api/courses/`
- `GET/PUT/DELETE /api/courses/{id}/`
- `GET/POST /api/courses/{id}/topics/`
- `GET/POST /api/courses/{id}/lessons/`
- `GET/POST /api/students/`
- `GET/POST /api/courses/{id}/progress/`

Swagger UI: `/docs/`

## Environment variables

See:
- `course_planner_backend/.env.example`
- `course_planner_frontend/.env.example`