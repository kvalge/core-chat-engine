# Quickstart: Core Chat Engine

## Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama (for local LLM)

## Setup

### 1. Clone and Install Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Create .env from example
cp .env.example .env

# Edit .env with your settings
# OLLAMA_BASE_URL=http://localhost:11434
# DATABASE_URL=sqlite:///chat.db
```

### 3. Start Backend

```bash
uvicorn main:app --reload
# API available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 4. Install and Start Frontend

```bash
cd frontend
npm install
npm run dev
# Frontend at http://localhost:5173
```

### 5. Verify Ollama

```bash
# Ensure Ollama is running
ollama list
# Should show llama3.2 and/or mistral

# Start if not running
ollama serve
```

## First Run

1. Open http://localhost:5173
2. A default project is created automatically
3. Configure backend in Settings (if needed)
4. Start chatting!

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Project Structure

```
backend/
├── src/
│   ├── api/routes/     # API endpoints
│   ├── services/       # Business logic
│   ├── models/        # DB and schemas
│   └── main.py        # App entry
└── tests/

frontend/
├── src/
│   ├── components/    # React components
│   ├── pages/        # Page components
│   ├── services/     # API clients
│   └── App.tsx       # App entry
└── tests/
```

## Troubleshooting

### Ollama not connecting
- Check: Is `ollama serve` running?
- Verify base URL in settings

### Streaming not working
- Check browser console for errors
- Verify SSE support enabled

### File upload fails
- Check file size limit (25MB max)
- Verify file type is supported