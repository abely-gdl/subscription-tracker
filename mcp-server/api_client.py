"""HTTP client for the .NET Subscription Tracker API."""
import logging
import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
API_KEY = os.getenv("API_KEY", "")

_HEADERS = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}


def _client() -> httpx.Client:
    return httpx.Client(base_url=BASE_URL, headers=_HEADERS, timeout=10.0)


def get_all_subscriptions() -> list[dict[str, Any]]:
    with _client() as c:
        r = c.get("/subscriptions")
        r.raise_for_status()
        return r.json()


def get_subscription(subscription_id: str) -> dict[str, Any]:
    with _client() as c:
        r = c.get(f"/subscriptions/{subscription_id}")
        r.raise_for_status()
        return r.json()


def get_subscriptions_by_category(category: str) -> list[dict[str, Any]]:
    with _client() as c:
        r = c.get(f"/subscriptions/category/{category}")
        r.raise_for_status()
        return r.json()


def add_subscription(data: dict[str, Any]) -> dict[str, Any]:
    with _client() as c:
        r = c.post("/subscriptions", json=data)
        r.raise_for_status()
        return r.json()


def update_subscription(subscription_id: str, data: dict[str, Any]) -> dict[str, Any]:
    with _client() as c:
        r = c.put(f"/subscriptions/{subscription_id}", json=data)
        r.raise_for_status()
        return r.json()


def delete_subscription(subscription_id: str) -> bool:
    with _client() as c:
        r = c.delete(f"/subscriptions/{subscription_id}")
        return r.status_code == 204
