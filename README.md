Project setup

- Create venv: `python3 -m venv .venv`
- Activate (bash/zsh): `source .venv/bin/activate`
- Activate (fish): `source .venv/bin/activate.fish`
- Activate (Windows PowerShell): `.venv\\Scripts\\Activate.ps1`
- Install deps: `pip install -r requirements.txt`

Quick check

Run: `python -c "import dynamiq; print(dynamiq.__version__)"`

Environment

- Create `.env` at project root with: `OPENAI_KEY=your-key-here`
- `.env` is gitignored.
- The app loads `.env` in `app/main.py` and uses `OPENAI_KEY`.

Web demo

- Backend (FastAPI)
  - Run: `uvicorn server.main:app --reload --port 8000`

- Frontend (React + Tailwind)
  - cd `web`
  - Install deps: `npm install` or `pnpm install`
  - Dev: `npm run dev` (Vite proxy forwards `/api` to `http://localhost:8000`)

Streaming API

- Endpoint: `POST /api/chat/stream`
- Body: `{ "message": "..." }`
- Response: NDJSON lines with events
  - `{ "type": "tool_call", "name": "...", "args": {...} }`
  - `{ "type": "tool_result", "name": "...", "result": "..." }`
  - `{ "type": "content_delta", "text": "..." }`
  - `{ "type": "done" }`
