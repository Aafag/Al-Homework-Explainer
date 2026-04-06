# Live Demo Instructions

## Demo Order

1. Show the app on localhost
2. Show the app from Docker
3. Show the app on Render
4. Show the GitHub Actions workflow
5. Trigger a new workflow run live

## Before The Demo

- Make sure `.env` has a valid `GEMINI_API_KEY`
- Make sure Docker Desktop is running
- Make sure the Render URL works
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

```bash
docker build -t ai-homework-explainer .
docker run --rm -p 5000:5000 --env-file .env ai-homework-explainer
```

If port `5000` is busy:

```bash
docker run --rm -p 5001:5000 --env-file .env ai-homework-explainer
```

Open:

- `http://localhost:5000`
- or `http://localhost:5001`

## 3. Show Render

Open:

- your Render homepage URL
- your Render health endpoint: `/api/health`

Show:

- the deployed site is live
- the app loads in the browser

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

Make one very small frontend text change in `frontend/index.html`, then run:

```bash
git add frontend/index.html
git commit -m "demo: trigger actions workflow"
git push origin main
```

Then show:

1. the new workflow run starting in GitHub Actions
2. the running jobs
3. the deploy after the workflow passes
4. the updated live site after refresh

## Backup Plan

- If `5000` is busy, use `5001`
- If Gemini fails, show the UI and health endpoint
- If Render is slow, show the last successful deployment
- If Actions is slow, show the workflow file and the latest successful run
