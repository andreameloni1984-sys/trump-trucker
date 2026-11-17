# Gagarin + Sputnik — INVEST Demo confirmation contract

Status: design only; NOT enabled for trading. No broker credentials or orders.

## Mandatory safety invariant
No order may be submitted without a fresh, explicit, one-time user confirmation tied to the exact order details. Default deny. Never submit to live account. No implicit approval from Telegram message delivery, button rendering, chat reply unrelated to order, timeout, or previous approvals.

## Pipeline
1. Gagarin detects technical candidate; Sputnik detects verified news catalyst. Each emits a proposed trade, never an order.
2. Validate broker INVEST instrument, buy-only semantics (no naked short), current price timestamp, liquidity, trading session, available demo cash, position exposure, and risk limits.
3. Send Telegram proposal with unique order ID, instrument, side, quantity, indicative price, max notional, entry condition, stop and take-profit plan, risk, expiration, and account clearly marked DEMO.
4. User explicitly approves that exact proposal via authenticated Telegram interaction. Reject edits, replay, stale proposals, unexpected chat/user IDs, and duplicate approvals. Recheck all conditions and account identity after approval.
5. Only if a supported Trading 212 practice API endpoint and credentials are independently verified, place the single approved demo order with idempotency/reconciliation; otherwise remain signal-only and report unsupported execution.
6. Record submission, broker acceptance/rejection, fill, exits, and result separately; never mark an order filled based on a request alone.

## Controls
- Kill switch defaults to OFF for execution until tested.
- One approval authorizes at most one specific order, not recurring purchases.
- Never persist API keys in code or logs; use protected secrets.
- Stop/TP are plans unless broker confirms supported attached orders.
- No automated real-money trades, no auto-confirmation, no auto-retry that duplicates orders.

## Acceptance tests
- Missing/invalid/expired approval => zero order requests.
- Wrong account or live account => zero order requests.
- Wrong Telegram user/chat, changed price/quantity, duplicate callback => zero order requests.
- Stale quote, insufficient funds, market closed, unsupported instrument => zero order requests.
- Supported practice account and valid fresh approval => at most one order; record actual broker response.
- Failed API call must not be reported as a filled order.
