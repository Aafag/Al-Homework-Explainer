# AI Homework Explainer

AI Homework Explainer is a small web app that helps students understand homework questions by generating short, educational explanations with Gemini and saving previous questions for review.

## General Idea

The app is designed to help students learn, not just copy answers. A student enters a homework question, the app sends it to the AI service, and the response comes back as a clear explanation. The app also stores past questions and explanations so users can review them later.

## Main Features

- Ask a homework question from a simple web interface
- Generate an AI explanation using Gemini
- Save question history in MongoDB Atlas
- View previous questions and explanations
- Run the same app locally, in Docker, and on Render

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python with Flask
- AI integration: Gemini API
- Database: MongoDB Atlas
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

The app uses MongoDB Atlas for question history. Set `MONGODB_URI` and `MONGODB_DB_NAME` in the environment before starting the app. This works on Render Free because MongoDB Atlas stores the data outside the Render container, so history is not lost when Render restarts or redeploys the service.

## Environment Setup

Create a `.env` file in the project root before running the app.

Minimum variables for the full app:

```env
MONGODB_URI=your_mongodb_atlas_connection_string
MONGODB_DB_NAME=ai_homework_explainer
GEMINI_API_KEY=your_gemini_api_key
```

You can also use `GEMINI_KEY` instead of `GEMINI_API_KEY`.

If you only want to start the UI and backend without Gemini and MongoDB, set:

```env
INIT_EXTERNAL_SERVICES=0
```

## Run On Localhost

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python3 run.py
```

4. Open the app in your browser:

- `http://localhost:5000`

If port `5000` is already in use, run:

```bash
PORT=5001 python3 run.py
```

Then open:

- `http://localhost:5001`

## Run With Docker

Build and start the container with Docker Compose:

```bash
docker compose up --build
```

Open:

- `http://localhost:5000`

If port `5000` is already in use, run:

```bash
APP_PORT=5001 docker compose up --build
```

Then open:

- `http://localhost:5001`

If you are not sure which host port Docker is using, check:

```bash
docker compose ps
```

Look at the `PORTS` column and open the published host port shown there. For example, if it shows `0.0.0.0:5001->5000/tcp`, open `http://localhost:5001`.

You can also run the image without Docker Compose:

```bash
docker build -t ai-homework-explainer .
docker run --rm -p 5000:5000 --env-file .env ai-homework-explainer
```

If you need a different local port:

```bash
docker run --rm -p 5001:5000 --env-file .env ai-homework-explainer
```

## Demo And Run Notes

For the live presentation steps, localhost demo, Docker demo, Render demo, and GitHub Actions trigger flow, use `live-demo-cicd-steps.txt`.

## Team Roles

- Kareem: backend development and API work. Note: Kareem previously used two GitHub accounts (KareemAbdalla and KareemAbdalla2). To avoid confusion and ensure consistent repository access, the team decided to remove KareemAbdalla2 and keep only KareemAbdalla.
- Aafag: frontend development and UI
- Sulistianto: Docker, CI/CD, deployment, and integration support
