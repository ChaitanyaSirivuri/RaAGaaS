<h1 align="center">
  <i>RaAGaaS:</i> Retrieval and Augmented Generation as a Service
</h1>

<p align="center">
  <a href="https://github.com/chaitanyasirivuri/raagaas">
    <img src="https://img.shields.io/badge/raagaas-0.1.0-blue.svg" alt="Version">
  </a>
  <a href="https://www.python.org/">
    <img alt="Made with Python" src="https://img.shields.io/badge/Made%20with-Python-1f425f.svg?color=purple">
  </a>
  <a href="https://github.com/chaitanyasirivuri/raagaas/blob/main/LICENSE">
    <img alt="MIT License" src="https://img.shields.io/github/license/chaitanyasirivuri/raagaas.svg?color=green">
  </a>
</p>

## Quickstart

1. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (and adjust secrets if needed).

2. Start the stack:

   ```bash
   docker compose up --build
   ```

3. Open the UI at `http://localhost:3000`. Create your **first API key** from **API Keys** (no auth required for the very first key). Paste the key into the top bar; it is stored in the browser.

4. Create a **collection**, upload a small PDF from the collection page, wait until the document status is **done**, then use **Query** via the API or add a chat message on **Chat**.

### API smoke test

```bash
# 1) Create API key (first call only — no Authorization header)
curl -s -X POST http://localhost:8000/v1/keys -H "Content-Type: application/json" -d "{\"scopes\":[\"query\",\"ingest\",\"admin\"]}"

# 2) Create collection (replace $KEY)
curl -s -X POST http://localhost:8000/v1/collections -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d "{\"name\":\"demo\"}"

# 3) Upload PDF, query (use collection id from step 2)
```

### Development (hot reload)

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Quality gates

- Backend: `cd backend && uv run ruff check . && uv run ruff format .`
- Frontend: `cd frontend && bun run lint` (runs `tsc --noEmit`)

See `SPEC.md` for architecture and provider interfaces.