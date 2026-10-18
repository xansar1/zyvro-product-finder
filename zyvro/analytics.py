"""Transparent descriptive heuristics and assumption-driven unit economics."""
from __future__ import annotations
import math
from typing import Any
import pandas as pd

COMPONENT_WEIGHTS = {"rating": 25, "review_signal": 20,
                     "review_gap_proxy": 25, "price_fit": 15, "data_completeness": 15}

def _num(value: Any) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (ValueError, TypeError):
        return None

def score_candidate(item: dict) -> dict:
    """0..100 heuristic; review counts are NOT verified demand/competition metrics."""
    rating, reviews, price = (_num(item.get(k)) for k in ('rating', 'reviews', 'price'))
    rating_ok = rating is not None and 0 <= rating <= 5
    review_ok = reviews is not None and reviews >= 0
    price_ok = price is not None and price > 0
    currency = item.get('currency')
    if currency == 'USD':
        lower, upper = 8, 85
    else:  # INR values in demo and amazon.in
        lower, upper = 399, 4500
    # Fixed cost/price band is merely an illustrative filter, not a current-market estimate.
    price_fit = (0 if not price_ok else max(0.0, 1.0 - abs(price - (lower + upper)/2) / ((upper-lower)/2)))
    components = {
        'rating': (rating / 5 if rating_ok else 0) * 25,
        'review_signal': (min(1.0, math.log1p(reviews)/math.log1p(5000)) if review_ok else 0) * 20,
        'review_gap_proxy': (max(0.0, 1.0 - reviews/3000) if review_ok else 0) * 25,
        'price_fit': price_fit * 15,
        'data_completeness': (int(rating_ok)+int(review_ok)+int(price_ok))/3 * 15,
    }
    score = round(sum(components.values()), 1)
    tier = 'Strong heuristic fit' if score >= 70 else 'Moderate heuristic fit' if score >= 50 else 'Limited evidence'
    return {**item, 'opportunity_score': score, 'tier': tier,
            'review_density_proxy': ('Lower' if reviews < 250 else 'Medium' if reviews < 1500 else 'Higher') if review_ok else 'Unknown',
            'data_fields_present': sum([rating_ok, review_ok, price_ok]),
            'components': {k: round(v, 1) for k, v in components.items()}}

def rank_candidates(records: list[dict]) -> list[dict]:
    scored = [score_candidate(r) for r in records]
    return sorted(scored, key=lambda r: (r['opportunity_score'],r.get('title','')), reverse=True)

def economics(selling_price:float, cost:float, shipping:float, fee_percent:float,
             ads:float, returns:float, other:float=0) -> dict:
    """Scenario only: uses user's assumptions; never predicts actual ROI or sales."""
    values = [selling_price,cost,shipping,fee_percent,ads,returns,other]
    if any((v is None or not math.isfinite(v) or v < 0) for v in values):
        raise ValueError('Costs and prices must be non-negative finite numbers')
    if selling_price <= 0 or fee_percent > 100:
        raise ValueError('Selling price must be positive and fee percent must be 0..100')
    fee = selling_price * fee_percent / 100
    total_cost = cost + shipping + fee + ads + returns + other
    profit = selling_price - total_cost
    return {'selling_price':round(selling_price,2),'fees':round(fee,2),
            'total_cost':round(total_cost,2),'unit_profit':round(profit,2),
            'net_margin_percent': round(100*profit/selling_price,1),
            'break_even': round(total_cost,2)}

def frame_for_table(records:list[dict])->pd.DataFrame:
    columns = ['title','category','price','currency','rating','reviews','opportunity_score','tier','review_density_proxy','source','url']
    if not records:return pd.DataFrame(columns=columns)
    df=pd.DataFrame(records)
    for col in columns:
        if col not in df.columns: df[col]=None
    return df[columns]
