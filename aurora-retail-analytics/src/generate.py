"""Build the Aurora star schema in memory.

Mechanisms, documented in docs/methodology.md:
- Holiday months and weekends produce more orders.
- Furniture is discounted harder, returned more often, and almost never
  sells more than one unit, so deep discounts do not buy volume.
- Corporate buyers take shallower discounts and return less.
- Store demand weights and the annual plan shares are different on purpose.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from src.config import (
    CATEGORY_WEIGHT,
    COMPANY_MONTHLY_BASE,
    DATE_DIM_END,
    DATE_DIM_START,
    DISCOUNT_OPTIONS,
    N_CUSTOMERS,
    N_ORDERS,
    PRODUCTS,
    RETURN_P,
    SALES_END,
    SALES_START,
    SEED,
    SEGMENT_RETURN_MULT,
    SEGMENTS,
    STORES,
    FIRST_NAMES,
    LAST_NAMES,
    season_factor,
    trend_factor,
)


def _picker(rng: random.Random, weights: list[float]):
    total = float(sum(weights))
    cumulative: list[float] = []
    running = 0.0
    for weight in weights:
        running += weight
        cumulative.append(running)

    def pick() -> int:
        target = rng.random() * total
        lo = 0
        hi = len(cumulative) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if target > cumulative[mid]:
                lo = mid + 1
            else:
                hi = mid
        return lo

    return pick


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


def _daterange(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def _dim_date_rows() -> list[tuple]:
    rows = []
    for day in _daterange(DATE_DIM_START, DATE_DIM_END):
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
    return rows


def _products() -> list[dict]:
    per_category: dict[str, int] = {}
    for product in PRODUCTS:
        per_category[product[2]] = per_category.get(product[2], 0) + 1
    rows = []
    for index, (sku, name, category, subcategory, cost_ratio, list_price, inner) in enumerate(PRODUCTS, start=1):
        rows.append(
            {
                "product_id": index,
                "sku": sku,
                "product_name": name,
                "category": category,
                "subcategory": subcategory,
                "unit_cost": round(list_price * cost_ratio, 2),
                "list_price": float(list_price),
                "weight": CATEGORY_WEIGHT[category] * inner / per_category[category],
            }
        )
    return rows


def _quantity(rng: random.Random, category: str, segment: str) -> int:
    if category == "Furniture":
        qty = 1 if rng.random() < 0.94 else 2
    elif category == "Textiles":
        qty = rng.randint(1, 3)
    else:
        qty = rng.randint(1, 2)
    if segment == "Corporate" and category != "Furniture" and rng.random() < 0.35:
        qty += 1
    return qty


def _discount(rng: random.Random, category: str, segment: str) -> float:
    options = DISCOUNT_OPTIONS[category]
    rate = rng.choices(
        [item[0] for item in options],
        weights=[item[1] for item in options],
        k=1,
    )[0]
    if segment == "Corporate" and rate > 0.10 and rng.random() < 0.65:
        rate = 0.10
    return rate


def _returned(rng: random.Random, category: str, segment: str, discount: float) -> int:
    probability = RETURN_P[category] * SEGMENT_RETURN_MULT[segment]
    if discount >= 0.20:
        probability *= 1.50
    if discount >= 0.30:
        probability *= 1.25
    return 1 if rng.random() < min(probability, 0.55) else 0


def generate(n_orders: int = N_ORDERS, n_customers: int = N_CUSTOMERS, seed: int = SEED) -> dict:
    """Return insert-ready rows for every warehouse table."""
    rng = random.Random(seed)
    stores = [
        {
            "store_id": store_id,
            "store_name": name,
            "city": city,
            "state": state,
            "region": region,
            "opened_date": opened,
            "sq_ft": sq_ft,
            "demand_weight": demand,
            "target_share": target_share,
        }
        for store_id, name, city, state, region, opened, sq_ft, demand, target_share in STORES
    ]
    products = _products()
    store_pick = _picker(rng, [store["demand_weight"] for store in stores])

    customers = []
    for customer_id in range(1, n_customers + 1):
        home = stores[store_pick()]
        segment = rng.choices(
            [item[0] for item in SEGMENTS],
            weights=[item[1] for item in SEGMENTS],
            k=1,
        )[0]
        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                "segment": segment,
                "city": home["city"],
                "state": home["state"],
                "region": home["region"],
                "home_store_index": stores.index(home),
            }
        )
    customer_weights = [(rng.random() ** 2.4) + 0.02 for _ in customers]
    customer_pick = _picker(rng, customer_weights)

    calendar_days = _daterange(SALES_START, SALES_END)
    day_weights = []
    for day in calendar_days:
        weight = season_factor(day.month) * trend_factor(day)
        weight *= 1.18 if day.weekday() >= 5 else 0.94
        day_weights.append(weight)
    order_days = rng.choices(calendar_days, weights=day_weights, k=n_orders)

    fact_rows = []
    line_id = 1
    first_order: dict[int, str] = {}
    for order_number, order_day in enumerate(order_days, start=1):
        customer = customers[customer_pick()]
        if rng.random() < 0.80:
            store = stores[customer["home_store_index"]]
        else:
            store = stores[rng.randrange(len(stores))]
        n_lines = rng.choices([1, 2, 3, 4], weights=[34, 36, 20, 10], k=1)[0]
        used: set[int] = set()
        order_id = f"SO-{100000 + order_number}"
        order_iso = order_day.isoformat()
        first_order.setdefault(customer["customer_id"], order_iso)
        if order_iso < first_order[customer["customer_id"]]:
            first_order[customer["customer_id"]] = order_iso
        for _ in range(n_lines):
            available = [index for index in range(len(products)) if products[index]["product_id"] not in used]
            if not available:
                break
            weights = [products[index]["weight"] for index in available]
            product = products[available[_picker(rng, weights)()]]
            used.add(product["product_id"])
            discount = _discount(rng, product["category"], customer["segment"])
            fact_rows.append(
                (
                    line_id,
                    order_id,
                    order_iso,
                    store["store_id"],
                    product["product_id"],
                    customer["customer_id"],
                    _quantity(rng, product["category"], customer["segment"]),
                    product["list_price"],
                    discount,
                    product["unit_cost"],
                    _returned(rng, product["category"], customer["segment"], discount),
                )
            )
            line_id += 1

    return _assemble(stores, products, customers, first_order, fact_rows)


def _assemble(stores, products, customers, first_order, fact_rows) -> dict:
    share = sum(store["target_share"] for store in stores)
    if abs(share - 1) > 1e-9:
        raise RuntimeError(f"Store target shares must sum to 1 (got {share}).")
    active_ids = {row[5] for row in fact_rows}
    customer_rows = []
    for customer in customers:
        if customer["customer_id"] not in active_ids:
            continue
        customer_rows.append(
            (
                customer["customer_id"],
                customer["customer_name"],
                customer["segment"],
                customer["city"],
                customer["state"],
                customer["region"],
                first_order[customer["customer_id"]],
            )
        )
    customer_rows.sort(key=lambda row: row[0])
    fact_rows.sort(key=lambda row: (row[2], row[1], row[0]))

    target_rows = []
    for month in _month_starts(SALES_START, SALES_END):
        planned = COMPANY_MONTHLY_BASE * season_factor(month.month) * trend_factor(month)
        for store in stores:
            target_rows.append(
                (
                    store["store_id"],
                    month.isoformat(),
                    round(planned * store["target_share"], 2),
                )
            )

    store_rows = [
        (
            store["store_id"],
            store["store_name"],
            store["city"],
            store["state"],
            store["region"],
            store["opened_date"],
            store["sq_ft"],
        )
        for store in stores
    ]
    product_rows = [
        (
            product["product_id"],
            product["sku"],
            product["product_name"],
            product["category"],
            product["subcategory"],
            product["unit_cost"],
            product["list_price"],
        )
        for product in products
    ]
    return {
        "dim_date": _dim_date_rows(),
        "dim_store": store_rows,
        "dim_product": product_rows,
        "dim_customer": customer_rows,
        "fact_sales": fact_rows,
        "fact_store_target": target_rows,
    }
