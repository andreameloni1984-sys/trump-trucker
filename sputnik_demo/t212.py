"""Client minimo Trading 212 Invest — SOLO conto DEMO.

L'indirizzo del conto demo è fisso nel codice: con chiavi del conto reale le
richieste vengono rifiutate da Trading 212 e nessun ordine reale può partire.
Le chiavi non vengono mai stampate.
"""
from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from typing import Any

DEMO_BASE = "https://demo.trading212.com/api/v0"


class T212Error(RuntimeError):
    def __init__(self, status: int, detail: str):
        super().__init__(f"HTTP {status}: {detail}")
        self.status = status
        self.detail = detail


class DemoClient:
    def __init__(self, key: str, secret: str, base: str = DEMO_BASE, pause: float = 1.2):
        if base != DEMO_BASE:
            raise ValueError("Sputnik trader: consentito solo il conto DEMO di Trading 212.")
        token = base64.b64encode(f"{key.strip()}:{secret.strip()}".encode()).decode()
        self._auth = f"Basic {token}"
        self.base = base
        self.pause = pause  # Trading 212 limita le richieste per secondo

    def _call(self, method: str, path: str, body: dict | None = None) -> Any:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data, method=method)
        req.add_unredirected_header("Authorization", self._auth)
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "Sputnik-demo-trader")
        time.sleep(self.pause)
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:200]
            except Exception:  # noqa: BLE001
                detail = ""
            raise T212Error(exc.code, " ".join(detail.split())) from None

    # lettura
    def cash(self) -> dict:
        return self._call("GET", "/equity/account/cash")

    def portfolio(self) -> list[dict]:
        rows = self._call("GET", "/equity/portfolio")
        return rows if isinstance(rows, list) else []

    def instruments(self) -> list[dict]:
        rows = self._call("GET", "/equity/metadata/instruments")
        return rows if isinstance(rows, list) else []

    def orders(self) -> list[dict]:
        rows = self._call("GET", "/equity/orders")
        return rows if isinstance(rows, list) else []

    # ordini (quantità negativa = vendita)
    def market(self, ticker: str, quantity: float) -> dict:
        return self._call("POST", "/equity/orders/market", {"ticker": ticker, "quantity": quantity})

    def stop(self, ticker: str, quantity: float, stop_price: float) -> dict:
        return self._call("POST", "/equity/orders/stop", {
            "ticker": ticker, "quantity": quantity, "stopPrice": stop_price, "timeValidity": "GOOD_TILL_CANCEL"})

    def cancel(self, order_id: Any) -> None:
        self._call("DELETE", f"/equity/orders/{order_id}")
