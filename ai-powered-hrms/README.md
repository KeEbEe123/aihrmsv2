# AI-Powered HRMS (FastAPI + Supabase + Twilio WhatsApp)

A lightweight backend to manage leave workflows, substitute allocation, and notifications via WhatsApp.

## Quickstart

1. Create a virtualenv and install deps:
   ```bash
   python -m venv .venv
   .venv/Scripts/activate  # Windows PowerShell
   pip install -r requirements.txt
   ```

2. Copy environment variables:
   ```bash
   copy .env.example .env
   ```
   Fill values: Supabase URL/keys, Twilio SID/token/WhatsApp from, webhook URL.

3. Run dev server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Healthcheck: `GET /health` or root `/`.

## Endpoints
- `POST /webhooks/twilio/whatsapp` — Twilio inbound webhook (WhatsApp messages)

## Environment
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` or `SUPABASE_SERVICE_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`
- `TWILIO_WEBHOOK_URL` (public URL that Twilio calls)
- `OPENAI_API_KEY` (optional for advanced agent)

## Database
Apply schema to Supabase:
```sql
-- see supabase/schema.sql
```

## Conversation Examples
- Teacher: "I need leave on Oct 15 for one day."
- HOD: "approve 42 ravi,anu" or "reject 42"
- Substitute: "confirm 42"

## Notes
- Intent detection is a simple regex stub in `app/ai_agent.py`. Replace with LangChain/OpenAI.
- Twilio signature verification uses `TWILIO_AUTH_TOKEN` and `TWILIO_WEBHOOK_URL`.
- Substitute suggestion is naive; enhance using timetables/workload in DB.


