# -*- coding: utf-8 -*-
"""
app/services/message_service.py

Sends SMS messages to a list of phone numbers. This is currently a
STUB — it doesn't talk to any real SMS gateway yet, it just reports
every number as sent successfully. When you're ready to wire up a
real provider (e.g. an Algerian SMS gateway, Twilio, etc.), this is
the one function to change — app/ui/messages.py never needs to know
how sending actually happens.

TODO: replace the body of send_sms() with a real API call. A typical
gateway either accepts one request per number, or a single batch
request with a list of numbers — whichever shape it needs, keep the
(success_numbers, failed_numbers) return contract the same so the UI
doesn't have to change.
"""

from typing import List, Tuple


def send_sms(phone_numbers: List[str], message: str) -> Tuple[List[str], List[str]]:
    """
    Send `message` to every number in `phone_numbers`.

    Returns (success_numbers, failed_numbers). Right now everything
    "succeeds" since there's no real gateway wired up yet.
    """
    if not message.strip():
        return [], list(phone_numbers)

    success_numbers = []
    failed_numbers = []

    for number in phone_numbers:
        number = (number or "").strip()
        if not number:
            continue
        # TODO: real API call goes here, e.g.:
        #   ok = sms_gateway.send(to=number, text=message)
        #   (success_numbers if ok else failed_numbers).append(number)
        success_numbers.append(number)

    return success_numbers, failed_numbers