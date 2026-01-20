from __future__ import annotations

import hmac
import hashlib
from urllib.parse import urlencode

from fastapi import Request

from app.config import Settings


async def verify_twilio_request(request: Request, settings: Settings) -> bool:
    """Validate Twilio signature for the incoming webhook.

    Twilio signs the request with X-Twilio-Signature header. We compute HMAC-SHA1
    of the full URL + sorted params using the Twilio auth token.
    """
    try:
        signature = request.headers.get("X-Twilio-Signature", "")
        if not signature:
            return False

        # Obtain the url Twilio used (use provided webhook url if configured)
        url = settings.twilio_webhook_url or str(request.url)
        form = await request.form()
        params = dict(sorted(form.items(), key=lambda kv: kv[0]))
        data = (url + urlencode(params)).encode()
        digest = hmac.new(
            key=settings.twilio_auth_token.encode(),
            msg=data,
            digestmod=hashlib.sha1,
        ).digest()

        import base64

        computed = base64.b64encode(digest).decode()
        return hmac.compare_digest(signature, computed)
    except Exception:
        return False


