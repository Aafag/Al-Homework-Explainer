# Live Demo Instructions

## Demo Order

1. Show the app on localhost
2. Show the app from Docker
3. Show the app on Render
4. Show the GitHub Actions workflow
5. Trigger a new workflow run live

## Before The Demo

- Make sure `.env` has valid `MONGODB_URI` and `GEMINI_API_KEY` values
- Make sure Docker Desktop is running
- Make sure the Render URL works
- Make sure the Render service has `MONGODB_URI` set from MongoDB Atlas
- Make sure GitHub Actions is accessible
- Prepare one sample question

Sample question:

```text
Explain Newton's second law with a simple example.
```

## 1. Run On Localhost

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

If port `5000` is busy:

```bash
PORT=5001 python3 run.py
```

Open:

- `http://localhost:5000`
- or `http://localhost:5001`

Show:

- the homepage
- one submitted question
- the generated explanation
- the saved history

## 2. Run With Docker

Recommended command for the demo:

```bash
docker compose up --build
```

This uses the MongoDB Atlas connection from your `.env`, so Docker and Render can show the same saved question history.

If your `.env` uses `GEMINI_KEY` instead of `GEMINI_API_KEY`, Docker Compose supports that too.

If port `5000` is busy:

```bash
APP_PORT=5001 docker compose up --build
```

Open:

- `http://localhost:5000`
- or `http://localhost:5001`

If you use plain `docker run`, pass the MongoDB environment variables:

```bash
docker build -t ai-homework-explainer .
docker run --rm -p 5000:5000 --env-file .env \
  -e MONGODB_URI="$MONGODB_URI" \
  -e MONGODB_DB_NAME="${MONGODB_DB_NAME:-ai_homework_explainer}" \
  ai-homework-explainer
```

If port `5000` is busy:

```bash
docker run --rm -p 5001:5000 --env-file .env \
  -e MONGODB_URI="$MONGODB_URI" \
  -e MONGODB_DB_NAME="${MONGODB_DB_NAME:-ai_homework_explainer}" \
  ai-homework-explainer
```

## 3. Show Render

Before showing history persistence, confirm Render is using MongoDB Atlas:

- Open the `ai-homework-explainer` web service in Render.
- Go to the environment variables section.
- Confirm `MONGODB_URI` exists and contains the MongoDB Atlas connection string.
- Confirm `MONGODB_DB_NAME` is set to `ai_homework_explainer`.

Do not commit the MongoDB URI into the repository. Add it only in Render as an environment variable. If the app cannot connect, check the Atlas database user's password and Atlas Network Access allowlist.

Open:

- your Render homepage URL
- your Render health endpoint: `/api/health`

Show:

- the deployed site is live
- the app loads in the browser
- a submitted question remains in history after refreshing the page

## 4. Show GitHub Actions

Open GitHub:

- `Actions` tab
- `CI/CD` workflow

Show:

- lint step
- test step
- Docker build step
- health check step
- deploy stage on `main`

## 5. Trigger The Workflow Live

Create a small demo branch, make one tiny frontend text change, push the branch, then merge it to `main`.

Suggested branch name:

```bash
git checkout -b demo/workflow-trigger
```

Make one very small text change in `frontend/index.html`, then run:

```bash
git add frontend/index.html
git commit -m "demo: trigger actions workflow"
git push origin demo/workflow-trigger
```

Then open GitHub and:

1. show the branch push triggering GitHub Actions
2. show the workflow run on the branch
3. open the branch or pull request
4. merge the branch into `main`
5. show the new workflow run triggered on `main`
6. show the deploy after the `main` workflow passes
7. refresh the live site and show the visible text change

If you want to create the pull request from the terminal:

```bash
gh pr create --base main --head demo/workflow-trigger --title "demo: trigger workflow" --body "Small frontend text change for live CI/CD demo."
```

What to explain:

- branch pushes trigger the validation workflow
- merging to `main` triggers the production path
- the `main` workflow is the one that can publish and deploy

## Backup Plan

- If `5000` is busy, use `5001`
- If Gemini fails, show the UI and health endpoint
- If Render is slow, show the last successful deployment
- If Actions is slow, show the workflow file and the latest successful run
