# AI Homework Explainer

AI Homework Explainer is a small web app that helps students understand homework questions by generating short, educational explanations with Gemini and saving previous questions for review.

## General Idea

The app is designed to help students learn, not just copy answers. A student enters a homework question, the app sends it to the AI service, and the response comes back as a clear explanation. The app also stores past questions and explanations so users can review them later.

## Main Features

- Ask a homework question from a simple web interface
- Generate an AI explanation using Gemini
- Save question history locally in SQLite and on Render in Postgres
- View previous questions and explanations
- Run the same app locally, in Docker, and on Render

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python with Flask
- AI integration: Gemini API
- Database: SQLite locally, Render Postgres in deployment
- Containerization: Docker
- CI/CD: GitHub Actions
- Deployment: Render

## How It Works

1. The user opens the web app.
2. The user enters a homework question.
3. Flask sends the question to Gemini.
4. Gemini returns an explanation.
5. The app saves the question and explanation in the configured database.
6. The frontend displays the result and the saved history.

## Project Structure

- `frontend/`: static UI files
- `app/`: Flask app, routes, database, and Gemini service
- `run.py`: local app entrypoint
- `Dockerfile`: container build definition
- `render.yaml`: Render deployment config
- `.github/workflows/ci.yml`: CI/CD pipeline

## Database Behavior

The app uses SQLite by default for local development. If `DATABASE_URL` is set, the app uses Postgres instead. The Render Blueprint in `render.yaml` creates a Render Postgres database and passes its connection string as `DATABASE_URL`, so saved questions survive web service restarts and redeploys.

## Demo And Run Notes

For the live presentation steps, localhost demo, Docker demo, Render demo, and GitHub Actions trigger flow, use `README_Instructions.md`.

## Team Roles

- Kareem: backend development and API work
- Aafag: frontend development and UI
- Sulistianto: Docker, CI/CD, deployment, and integration support
