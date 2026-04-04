# Week 13 Demo and Presentation Notes

## Live demo rehearsal

Use one small visible frontend change for the live CI/CD demonstration. Good examples:

- change the heading text in `frontend/index.html`
- change the submit button label in `frontend/index.html`
- change one short helper sentence in the interface

Suggested demo flow:

1. Show the current live site in the browser.
2. Make one small visible text change locally.
3. Commit and push the change to `main`.
4. Open GitHub Actions and show the CI job running first.
5. Show the Docker Hub repository receiving the new image tags.
6. Show Render starting a new deploy from the updated image.
7. Refresh the live site and confirm the visible text change is now deployed.

## Demo checklist

- Confirm `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, and `RENDER_DEPLOY_HOOK_URL` are set in GitHub.
- Confirm the Render service has the required production environment variables.
- Confirm Docker Hub contains the `ai-homework-explainer` repository.
- Confirm the Render health check is set to `/api/health`.
- Keep one sample homework question ready for the AI explanation feature.
- Keep one existing saved question ready to show database persistence.

## Suggested slide outline

1. Project overview
   - what the AI Homework Explainer does
   - who the target users are
2. System architecture
   - frontend
   - Flask backend
   - Gemini API
   - MongoDB Atlas
3. Main features
   - AI explanation generation
   - question history
   - clean frontend workflow
4. DevOps contribution
   - Docker containerization
   - GitHub Actions CI/CD
   - Render deployment flow
5. GitHub team process
   - issues
   - branches
   - pull requests
   - commit history
6. Testing and validation
   - unit tests
   - linting
   - Docker smoke test
7. Lessons learned
   - integrating AI safely
   - handling shared environment variables
   - keeping deployment reproducible
8. Next improvements
   - stronger prompt controls
   - richer answer formatting
   - authentication and student accounts

## Personal talking points for DevOps

- Explain that the same Docker image is used for local testing and production deployment.
- Explain that the CI job blocks bad code from reaching the release step.
- Explain that only pushes to `main` publish to Docker Hub and trigger Render.
- Explain that secrets stay in GitHub Actions and Render instead of the repository.
