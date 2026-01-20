from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api import api_router as _api_router
from app.config import get_settings, Settings
from app.handlers import LeaveService
from app.utils import verify_twilio_request


router = APIRouter()


@router.get("/health", tags=["health"])  # separate from root
async def health() -> dict:
    return {"status": "healthy"}


@router.post("/webhooks/twilio/whatsapp", tags=["webhooks"])  # inbound WhatsApp
async def twilio_whatsapp_webhook(
    request: Request,
    settings: Settings = Depends(get_settings),
):
    # Verify Twilio signature (reject if invalid)
    if not settings.twilio_skip_signature and not await verify_twilio_request(request, settings):
        return PlainTextResponse("Invalid signature", status_code=status.HTTP_403_FORBIDDEN)

    form = await request.form()
    from_number = str(form.get("From", ""))
    body = str(form.get("Body", "")).strip()

    leave_service = LeaveService(settings=settings)
    result = await leave_service.process_incoming_message(from_number=from_number, message_body=body)
    # Twilio expects a 200 with TwiML or plain message; we'll just ack here, notifier will send outbound
    return JSONResponse(result)


@router.post("/simulate/whatsapp", tags=["simulate"])  # dev helper without Twilio
async def simulate_whatsapp(request: Request, settings: Settings = Depends(get_settings)):
    payload = await request.json()
    from_number = str(payload.get("from", ""))
    body = str(payload.get("body", "")).strip()
    leave_service = LeaveService(settings=settings)
    result = await leave_service.process_incoming_message(from_number=from_number, message_body=body)
    return JSONResponse(result)


# expose to main
api_router = _api_router
api_router.include_router(router)


