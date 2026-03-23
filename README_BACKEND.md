# AI Homework Explainer - Backend (Kareem Scope)

Flask backend API for:
- receiving homework questions
- generating explanations using Gemini
- saving and fetching question history from MongoDB Atlas

## 1) Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill:
- `MONGODB_URI`
- `GEMINI_API_KEY`

## 2) Run

```bash
python run.py
```

Server starts on `http://localhost:5000` (or `PORT`).

## 3) API Endpoints

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

## 4) Example cURL

```bash
curl -X POST http://localhost:5000/api/questions ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"What is photosynthesis?\"}"
```
