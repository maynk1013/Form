"""Simulate Lumen accounts forward one month at a time.

A latent account trait moves adoption and churn together. Paid search is a
worse-retaining channel. Starter and small companies churn faster. None of
that is a finding until the SQL measures it.

Money is price-per-seat times seats. Prices and seats are integers, so MRR
values are exact dollars and the bridge ties out.
"""

from __future__ import annotations

import math
import random
from datetime import date, timedelta

from src.config import (
    ADJECTIVES,
    AS_OF_MONTH,
    BANDS,
    CHANNELS,
    DATE_DIM_END,
    DATE_DIM_START,
    HISTORY_START,
    INDUSTRIES,
    N_ACCOUNTS,
    NOUNS,
    PLAN_MIX,
    PLAN_ORDER,
    PLANS,
    PLACES,
    REGIONS,
    SEED,
    SIGNUP_END,
    SIGNUP_START,
)


def _poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    limit = math.exp(-lam)
    count = 0
    product = 1.0
    while product > limit:
        count += 1
        product *= rng.random()
    return count - 1


def _month_starts(start: date, end: date) -> list[date]:
    current = date(start.year, start.month, 1)
    last = date(end.year, end.month, 1)
    months: list[date] = []
    while current <= last:
        months.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def _shift_month(month: date, steps: int) -> date:
    index = month.year * 12 + (month.month - 1) + steps
    return date(index // 12, index % 12 + 1, 1)


def _dim_dates() -> list[tuple]:
    rows = []
    day = DATE_DIM_START
    while day <= DATE_DIM_END:
        rows.append(
            (
                int(day.strftime("%Y%m%d")),
                day.isoformat(),
                day.year,
                (day.month - 1) // 3 + 1,
                day.month,
                day.strftime("%B"),
                day.strftime("%Y-%m"),
                day.day,
                day.strftime("%A"),
                day.weekday() + 1,
                int(day.strftime("%V")),
                1 if day.weekday() >= 5 else 0,
            )
        )
        day += timedelta(days=1)
    return rows


def _dollars(price: int, seats: int) -> float:
    return float(price * seats)


def _pick(rng: random.Random, options: list[tuple]) -> tuple:
    """options are (value, weight) or richer tuples whose last item is the weight."""
    weights = [item[-1] for item in options]
    return rng.choices(options, weights=weights, k=1)[0]


def _classify(prior: float, current: float, kind: str | None) -> str:
    if kind == "new":
        return "New"
    if kind == "reactivation":
        return "Reactivation"
    if current == 0 and prior > 0:
        return "Churn"
    if current > prior:
        return "Expansion"
    if 0 < current < prior:
        return "Contraction"
    return "Retained"


def _move_plan(plan: str, steps: int) -> str:
    index = PLAN_ORDER.index(plan) + steps
    index = max(0, min(len(PLAN_ORDER) - 1, index))
    return PLAN_ORDER[index]


def generate(n_accounts: int = N_ACCOUNTS, seed: int = SEED) -> dict:
    rng = random.Random(seed)
    plans = {
        name: {"plan_id": plan_id, "price": price, "hazard": hazard, "adoption": adoption}
        for plan_id, name, price, _rank, hazard, adoption in PLANS
    }
    channels = [
        {"channel_id": channel_id, "channel_name": name, "channel_group": group, "spend": spend, "hazard": hazard}
        for channel_id, name, group, spend, hazard in CHANNELS
    ]
    months = _month_starts(HISTORY_START, AS_OF_MONTH)
    span_days = (SIGNUP_END - SIGNUP_START).days

    accounts = []
    used_names: set[str] = set()
    for account_id in range(1, n_accounts + 1):
        industry = _pick(rng, INDUSTRIES)
        region = _pick(rng, REGIONS)
        band = _pick(rng, [(item[0], item[1], item[2], item[3], item[4]) for item in BANDS])
        band_name, seat_min, seat_max, band_hazard = band[0], band[1], band[2], band[3]
        plan_name = _pick(rng, PLAN_MIX[band_name])[0]
        channel = rng.choice(channels)
        signup_offset = min(span_days, int(rng.betavariate(1.35, 1.0) * span_days))
        signup = SIGNUP_START + timedelta(days=signup_offset)
        signup_month = date(signup.year, signup.month, 1)
        name = f"{rng.choice(ADJECTIVES)} {rng.choice(PLACES)} {rng.choice(NOUNS)}"
        while name in used_names:
            name = f"{rng.choice(ADJECTIVES)} {rng.choice(PLACES)} {rng.choice(NOUNS)}"
        used_names.add(name)
        accounts.append(
            {
                "account_id": account_id,
                "account_name": name,
                "industry": industry[0],
                "industry_hazard": industry[1],
                "region": region[0],
                "region_hazard": region[1],
                "employee_band": band_name,
                "seat_min": seat_min,
                "seat_max": seat_max,
                "band_hazard": band_hazard,
                "plan": plan_name,
                "seats": rng.randint(seat_min, seat_max),
                "signup": signup,
                "signup_month": signup_month,
                "channel": channel,
                "trait": rng.gauss(0, 1),
            }
        )

    sub_rows: list[tuple] = []
    usage_rows: list[tuple] = []
    ticket_rows: list[tuple] = []
    sub_id = 1
    ticket_id = 1

    for account in accounts:
        active = False
        mrr = 0.0
        plan = account["plan"]
        seats = account["seats"]
        churn_index = None
        start_index = None
        for index, month in enumerate(months):
            if month < account["signup_month"]:
                continue
            trait_now = account["trait"] + rng.gauss(0, 0.28)
            if not active:
                opened = False
                kind = None
                if churn_index is None and month == account["signup_month"]:
                    kind = "new"
                    plan = account["plan"]
                    seats = account["seats"]
                    opened = True
                elif churn_index is not None and index - churn_index >= 3:
                    probability = min(0.22, 0.07 * math.exp(0.25 * account["trait"]))
                    if rng.random() < probability:
                        kind = "reactivation"
                        plan = _move_plan(plan, -1)
                        seats = max(account["seat_min"], int(seats * 0.8))
                        opened = True
                if not opened:
                    continue
                mrr = _dollars(plans[plan]["price"], seats)
                prior = 0.0
                movement = _classify(prior, mrr, kind)
                active = True
                start_index = index
                tenure = 0
            else:
                tenure = index - start_index
                hazard = plans[plan]["hazard"]
                hazard *= account["channel"]["hazard"]
                hazard *= account["industry_hazard"]
                hazard *= account["region_hazard"]
                hazard *= account["band_hazard"]
                if tenure <= 2:
                    hazard *= 1.50
                hazard *= math.exp(-0.75 * trait_now)
                hazard = min(0.55, max(0.002, hazard))
                prior = mrr
                if rng.random() < hazard:
                    sub_rows.append(
                        (sub_id, account["account_id"], month.isoformat(), plans[plan]["plan_id"], seats, 0.0, prior, "Churn")
                    )
                    sub_id += 1
                    score = _score(plans[plan]["adoption"], trait_now, tenure)
                    users, events = _usage(rng, seats, score)
                    usage_rows.append((account["account_id"], month.isoformat(), users, events, score))
                    ticket_id = _tickets(rng, ticket_rows, ticket_id, account["account_id"], month, plan, score, "Churn")
                    active = False
                    mrr = 0.0
                    churn_index = index
                    continue
                new_plan, new_seats, new_mrr = plan, seats, prior
                if trait_now > 0.85 and rng.random() < 0.13:
                    new_plan, new_seats = _expand(rng, plan, seats, account["seat_max"])
                    new_mrr = _dollars(plans[new_plan]["price"], new_seats)
                    if new_mrr <= prior:
                        new_seats += 1
                        new_mrr = _dollars(plans[new_plan]["price"], new_seats)
                    if new_mrr <= prior:
                        new_plan, new_seats, new_mrr = plan, seats, prior
                elif trait_now < -0.7 and rng.random() < 0.11:
                    new_plan, new_seats = _contract(rng, plan, seats, account["seat_min"])
                    new_mrr = _dollars(plans[new_plan]["price"], new_seats)
                    if new_mrr >= prior and new_seats > account["seat_min"]:
                        new_seats -= 1
                        new_mrr = _dollars(plans[new_plan]["price"], new_seats)
                    if new_mrr >= prior:
                        new_plan, new_seats, new_mrr = plan, seats, prior
                plan, seats, mrr = new_plan, new_seats, new_mrr
                movement = _classify(prior, mrr, None)
            score = _score(plans[plan]["adoption"], trait_now, tenure)
            users, events = _usage(rng, seats, score)
            sub_rows.append(
                (sub_id, account["account_id"], month.isoformat(), plans[plan]["plan_id"], seats, mrr, prior, movement)
            )
            sub_id += 1
            usage_rows.append((account["account_id"], month.isoformat(), users, events, score))
            ticket_id = _tickets(rng, ticket_rows, ticket_id, account["account_id"], month, plan, score, movement)

    spend_rows = []
    spend_id = 1
    for index, month in enumerate(months):
        growth = 1 + 0.008 * index
        for channel in channels:
            noise = rng.uniform(0.88, 1.12)
            spend_rows.append(
                (spend_id, month.isoformat(), channel["channel_id"], round(channel["spend"] * growth * noise, 2))
            )
            spend_id += 1

    return {
        "dim_date": _dim_dates(),
        "dim_plan": [(plan_id, name, float(price), rank) for plan_id, name, price, rank, _h, _a in PLANS],
        "dim_channel": [(item["channel_id"], item["channel_name"], item["channel_group"]) for item in channels],
        "dim_account": [
            (
                account["account_id"],
                account["account_name"],
                account["industry"],
                account["region"],
                account["employee_band"],
                account["signup"].isoformat(),
                account["channel"]["channel_id"],
            )
            for account in accounts
        ],
        "fact_subscription_month": sub_rows,
        "fact_usage_monthly": usage_rows,
        "fact_ticket": ticket_rows,
        "fact_marketing_spend": spend_rows,
    }


def _score(baseline: int, trait_now: float, tenure: int) -> int:
    raw = baseline + 15 * trait_now
    if tenure == 0:
        raw -= 8
    return max(5, min(98, int(round(raw))))


def _usage(rng: random.Random, seats: int, score: int) -> tuple[int, int]:
    users = int(round(seats * (score / 100) * rng.uniform(0.55, 1.0)))
    users = min(seats, max(1, users))
    events = users * rng.randint(6, 40)
    return users, events


def _expand(rng: random.Random, plan: str, seats: int, seat_max: int) -> tuple[str, int]:
    if plan != "Enterprise" and rng.random() < 0.55:
        return _move_plan(plan, 1), seats
    bump = {"Starter": 2, "Growth": 4, "Scale": 6, "Enterprise": 8}[plan]
    return plan, min(seat_max + 10, seats + bump)


def _contract(rng: random.Random, plan: str, seats: int, seat_min: int) -> tuple[str, int]:
    if plan != "Starter" and rng.random() < 0.55:
        return _move_plan(plan, -1), seats
    return plan, max(seat_min, seats - rng.randint(1, 4))


def _tickets(rng, rows, ticket_id, account_id, month, plan, score, movement) -> int:
    lam = 0.30
    if score < 40:
        lam += 1.15
    elif score < 55:
        lam += 0.40
    if plan == "Enterprise":
        lam += 0.35
    if movement == "Churn":
        lam += 0.50
    categories = ["Billing", "Bug", "How-to", "Feature request", "Outage"]
    for _ in range(_poisson(rng, lam)):
        if score < 40:
            priority = rng.choices(["Low", "Medium", "High", "Urgent"], weights=[20, 35, 30, 15], k=1)[0]
        else:
            priority = rng.choices(["Low", "Medium", "High", "Urgent"], weights=[48, 34, 14, 4], k=1)[0]
        base_hours = {"Low": 26, "Medium": 18, "High": 10, "Urgent": 5}[priority]
        hours = max(0.5, round(rng.lognormvariate(math.log(base_hours), 0.35), 1))
        center = 4.55 - min(hours, 72) / 90 - (0.7 if score < 40 else 0)
        csat = min(5.0, max(1.0, round(rng.gauss(center, 0.35), 1)))
        opened = date(month.year, month.month, rng.randint(1, 28))
        rows.append(
            (
                ticket_id,
                account_id,
                opened.isoformat(),
                priority,
                rng.choice(categories),
                hours,
                csat,
            )
        )
        ticket_id += 1
    return ticket_id
