# AI Homework Explainer - Backend (Kareem Scope)

Flask backend API for:
- receiving homework questions
- generating explanations using Gemini
- saving and fetching question history from SQLite

## 1) Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill:
- `SQLITE_PATH`
- `GEMINI_API_KEY`
- `PORT`

Example:

```env
SQLITE_PATH=ai_homework_explainer.db
GEMINI_API_KEY=your_api_key_here
PORT=5000
```

## 2) Run

```bash
python3 run.py
```

Server starts on `http://localhost:5000` (or `PORT`).

If `5000` is already used:

```bash
PORT=5001 python3 run.py
```

Then open `http://localhost:5001`.

## 3) Run With Docker

Build:

```bash
docker build -t ai-homework-explainer .
```

Run:

```bash
docker run --rm -p 5000:5000 --env-file .env ai-homework-explainer
```

Open `http://localhost:5000`.

## 4) API Endpoints

- `GET /api/health`
- `POST /api/questions`
  - body:
    ```json
    {
      "question": "Explain Newton's second law with an example."
    }
    ```
- `GET /api/questions?limit=20`
- `GET /api/questions/<id>`

## 5) Example cURL

```bash
curl -X POST http://localhost:5000/api/questions \
  -H "Content-Type: application/json" \
  -d '{"question":"What is photosynthesis?"}'
```
