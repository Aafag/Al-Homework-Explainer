# Live Demo Guide

This guide gives you a step-by-step script for demonstrating the project in class.

## Demo Order

Use this order during the presentation:

1. Run the app on localhost
2. Run the app from Docker
3. Show the deployed Render version
4. Show the CI/CD pipeline in GitHub Actions

This order is the safest because it starts with the environment you control most and ends with deployment automation.

## Before Class

Check these items before the live demo:

- Make sure `.env` exists and contains a valid `GEMINI_API_KEY`
- Make sure dependencies are installed
- Make sure Docker Desktop is running
- Make sure the Render deployment URL is available
- Make sure GitHub Actions has a recent successful run on `main`
- Prepare one sample homework question to submit in the app

Suggested sample question:

```text
Explain Newton's second law with a simple real-life example.
```

## 1. Demo The App On Localhost

Open a terminal in the project root and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

If port `5000` is already used, run:

```bash
PORT=5001 python3 run.py
```

Then open the browser:

- `http://localhost:5000`
- or `http://localhost:5001` if you used port `5001`

What to say:

- "This is the application running locally on my machine."
- "The frontend and Flask backend are served together."
- "When I submit a question, the app generates an explanation and stores it in SQLite."

What to show:

- The home page loads
- Enter a homework question
- Submit the question
- The explanation appears
- The saved history appears in the UI

Optional health check:

```bash
curl http://127.0.0.1:5000/api/health
```

## 2. Demo The App From Docker

Build the image:

```bash
docker build -t ai-homework-explainer .
```

Run the container:

```bash
docker run --rm -p 5000:5000 --env-file .env ai-homework-explainer
```

If port `5000` is already used on your machine, run:

```bash
docker run --rm -p 5001:5000 --env-file .env ai-homework-explainer
```

Then open:

- `http://localhost:5000`
- or `http://localhost:5001`

What to say:

- "Now I am running the same application from a Docker container."
- "The browser still uses localhost, but the app is being served by the container."
- "This makes the runtime reproducible across machines."

What to show:

- The Docker build completes successfully
- The container starts successfully
- The app loads in the browser from localhost
- The health endpoint responds

Optional health check:

```bash
curl http://127.0.0.1:5000/api/health
```

If using port `5001`:

```bash
curl http://127.0.0.1:5001/api/health
```

## 3. Demo The Render Deployment

Open the deployed Render URL in the browser.

What to say:

- "This is the deployed version of the application on Render."
- "It uses the same containerized app structure as the local Docker deployment."
- "This shows the project running in a hosted environment, not just on my laptop."

What to show:

- The site loads publicly
- The homepage is reachable
- The health endpoint works
- If credentials are configured, submit one sample question

Suggested checks:

- Open the homepage
- Open `/api/health`

Example:

```text
https://your-render-url.onrender.com
https://your-render-url.onrender.com/api/health
```

If the instructor asks how deployment works:

- GitHub Actions builds and validates the project
- The Docker image is published
- Render pulls the latest image or is triggered by the deploy hook

## 4. Demo The CI/CD Pipeline

Open GitHub and navigate to:

- Repository `Actions` tab
- The `CI/CD` workflow

### How To Trigger The Workflow Live

Use one very small visible frontend change so the instructor can see the workflow start and then see the deployed result later.

Safe examples:

- change one heading in `frontend/index.html`
- change one button label in `frontend/index.html`
- change one short helper sentence in the UI

Suggested live trigger steps:

1. Open the current live site and show its current text.
2. Make one small text change locally.
3. Commit the change.
4. Push the change to `main`.
5. Open the `Actions` tab immediately.
6. Show the new workflow run starting from that push.
7. Open the running job and show the steps in progress.
8. After the workflow completes, show Render redeploying.
9. Refresh the live site and show the visible text change.

Commands for the live trigger:

```bash
git add frontend/index.html
git commit -m "demo: trigger ci workflow"
git push origin main
```

What to say:

- "I am making a very small frontend text change so I can safely trigger the pipeline live."
- "This push starts GitHub Actions automatically because the workflow runs on push."
- "After validation passes, the deployment flow publishes the container image and triggers Render."

What to show in the workflow:

1. Install dependencies
2. Run `ruff`
3. Run `pytest`
4. Build the Docker image
5. Start the built container
6. Check `/api/health`
7. On `main`, publish the Docker image
8. Trigger the Render deployment hook

What to say:

- "Every push and pull request runs the validation pipeline."
- "The workflow checks code quality, runs tests, builds Docker, and smoke-tests the container."
- "Pushes to `main` can also publish the image and trigger deployment."

### Important Demo Advice

- Make the live trigger change before class and rehearse it once.
- Keep the change harmless and easy to explain.
- Do not change backend logic during the live trigger.
- If you do not want to alter the final UI text permanently, prepare a tiny wording change that is still acceptable to keep.

## Short Demo Script

If you want a compact speaking script, use this:

1. "First, I will show the app running locally on localhost."
2. "Second, I will run the same app from Docker and open it in the browser."
3. "Third, I will show the deployed version on Render."
4. "Finally, I will show the CI/CD workflow that validates and deploys the app."

## Backup Plan

If something fails during the demo:

- If localhost port `5000` is busy, switch to `5001`
- If Gemini fails, show the app UI and explain that the API key is environment-based
- If Render is slow, show the Render dashboard and the last successful deployment
- If GitHub Actions is loading slowly, show the workflow YAML file in the repository
- If you cannot trigger a new run live, show the most recent successful run and explain the trigger step using the exact `git push` command

## Files To Know During The Demo

- `README.md`
- `README_BACKEND.md`
- `Dockerfile`
- `docker-compose.yml`
- `render.yaml`
- `.github/workflows/ci.yml`

## Final Rehearsal Checklist

- Run the app locally once before class
- Run the Docker container once before class
- Open the Render deployment before class
- Confirm the GitHub Actions page is accessible
- Keep one browser tab ready for localhost
- Keep one browser tab ready for Render
- Keep one GitHub tab ready for Actions
