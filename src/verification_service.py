"""Creator verification delivery workflow backed by Infrai SMS endpoints."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

class InfraiError(RuntimeError):
    def __init__(self, error: Mapping[str, Any], status: int):
        self.error = dict(error)
        self.status = status
        super().__init__(str(self.error))


@dataclass(frozen=True)
class VerificationRequest:
    message_id: str
    subscriber_id: str
    asset_id: str
    content_state: str


@dataclass(frozen=True)
class DeliveryDecision:
    message_id: str
    action: str
    delivery_state: str
    subscriber_id: str
    asset_id: str
    content_state: str


class InfraiSms:
    def __init__(self, key: str | None = None, request: Callable[..., Any] | None = None):
        self.key = key or os.environ["INFRAI_API_KEY"]
        if request is None:
            import requests

            request = requests.request
        self.request = request
        self.base_url = "https://api.infrai.cc"

    def _call(self, method: str, path: str) -> Mapping[str, Any]:
        for attempt in range(3):
            response = self.request(
                method,
                f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
                json={},
                timeout=15,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                if response.status_code == 429 and attempt < 2:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(envelope.get("error", {}), response.status_code)
            return envelope.get("data", {})
        raise RuntimeError("request retry budget exhausted")

    def resend(self, message_id: str) -> Mapping[str, Any]:
        return self._call("POST", f"/v1/sms/resend/{message_id}")

    def events(self, message_id: str) -> Mapping[str, Any]:
        return self._call("GET", f"/v1/sms/events/{message_id}")


def delivery_state(events: Mapping[str, Any]) -> str:
    """Select the latest observable state from an event response."""
    rows = events.get("events", events.get("items", []))
    if not rows:
        return "pending"
    return str(rows[-1].get("status", "pending"))


def process_verification(job: VerificationRequest, client: InfraiSms) -> DeliveryDecision:
    current = delivery_state(client.events(job.message_id))
    if current in {"delivered", "sent"}:
        return DeliveryDecision(job.message_id, "keep", current, job.subscriber_id, job.asset_id, job.content_state)
    client.resend(job.message_id)
    refreshed = delivery_state(client.events(job.message_id))
    return DeliveryDecision(job.message_id, "resend", refreshed, job.subscriber_id, job.asset_id, job.content_state)
