"""Campaign-local estimated admission control, never a provider invoice limit.

Reservations are charged in full and never refunded: fast completions, warmups,
failed attempts and uncertain cancellation outcomes all consume their allowance.
This intentionally trades utilization for a simple concurrency-safe upper ledger.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation


def positive_usd(value) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("USD amount must be positive and finite") from exc
    if not amount.is_finite() or amount <= 0:
        raise ValueError("USD amount must be positive and finite")
    return amount


class CampaignBudget:
    """Single-event-loop ledger; reserve has no await/check-then-launch race.

    Separate processes/campaigns have separate caps, even when appending to the
    same report. Provider-internal retries must fit the per-attempt allowance.
    """

    def __init__(self, cap):
        self.cap = positive_usd(cap)
        self.charged = Decimal(0)
        self.in_flight = Decimal(0)
        self.stopped = False
        self.reservations = 0

    def reserve(self, amount: Decimal) -> bool:
        if self.stopped or self.charged + amount > self.cap:
            self.stopped = True
            return False
        self.charged += amount
        self.in_flight += amount
        self.reservations += 1
        return True

    def complete(self, amount: Decimal) -> None:
        self.in_flight -= amount

    def snapshot(self) -> dict:
        return {"cap_usd": float(self.cap), "charged_estimate_usd": float(self.charged),
                "in_flight_estimate_usd": float(self.in_flight), "reservations": self.reservations,
                "admission_stopped": self.stopped, "billing_verified": False,
                "policy": "full_attempt_reservations_no_refunds_including_warmups_and_retries",
                "limitations": "Unverified estimates, not an invoice cap. Separate campaigns do not share a cap; "
                "storage, egress, model fees, late creation, retry amplification and failed teardown may exceed estimates."}
