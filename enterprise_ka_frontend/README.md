# Enterprise KA Frontend (Next.js)

Minimal Next.js UI to exercise the FastAPI backend in `enterprise_ka`.

## Prereqs
- Node 18+ (matches Next 14 requirements)
- Backend running locally or reachable over the network

## Setup
```bash
cd enterprise_ka_frontend
cp .env.example .env.local  # edit NEXT_PUBLIC_API_URL if backend not on localhost:8000
npm install
```

## Run
```bash
npm run dev
# open http://localhost:3000
```

## How to use
- Set **Backend URL** to your FastAPI base (no trailing slash).
- Ask a question; switch **Prompt template** to compare `grounded_concise` vs `grounded_reasoned`.
- Toggle **debug** to see rendered system/user prompts and guardrail signals returned by the backend.

## Build/Prod
```bash
npm run build
npm run start
```
