"""State-resolved comparative ecology primitives (v1, standard-library only).

These are measurement utilities and synthetic-test fixtures, NOT estimates from
wild animal observations. Empirical inference requires source-verified events,
original grouping, matched availability and an independent holdout design.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from math import log, isfinite
from random import Random
from statistics import mean, median


def conditional_information(records, *, identity="identity", state="state", context="context"):
    """Plug-in I(identity;state|context) in nats, descriptive ONLY.

    Observations must be detection-effort corrected or calibrated separately.
    Equal events are NOT independent biological sampling units.
    """
    if not records:
        raise ValueError("at least one observation required")
    counts = Counter()
    by_context = Counter()
    identities = Counter()
    states = Counter()
    for rec in records:
        vals = (rec[context], rec[identity], rec[state])
        if any(v is None for v in vals):
            raise ValueError("context, identity and state cannot be missing")
        c, i, s = vals
        counts[c, i, s] += 1
        by_context[c] += 1
        identities[c, i] += 1
        states[c, s] += 1
    n = sum(counts.values())
    out = 0.0
    for (c, i, s), nij in counts.items():
        out += nij / n * log(nij * by_context[c] / (identities[c, i] * states[c, s]))
    return max(0.0, out)  # guard floating point noise only


def _slope(x, y):
    mx = mean(x)
    my = mean(y)
    den = sum((a - mx) ** 2 for a in x)
    if den == 0:
        raise ValueError("insufficient availability variation within one individual")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / den


def matched_availability_buffering(events, *, draws=1999, seed=20261115):
    """Compare used-depth coupling with a time-matched pseudo-use null.

    Each event has individual, event_id, time, used, alternatives (1+ depths).
    Returns equal-individual mean slopes, null median, and Monte Carlo lower tail.
    Unlike the published Louis pooled-within-bird estimator, this v1 utility
    explicitly weights individuals equally; DO NOT use to reproduce 0.162.
    """
    if draws < 99:
        raise ValueError("draws must be >= 99")
    grouped = defaultdict(list)
    seen = set()
    for rec in events:
        for key in ("individual", "event_id", "time", "used", "alternatives"):
            if key not in rec:
                raise ValueError(f"missing required matched-event field: {key}")
        ident = rec["individual"]
        key = (ident, rec["event_id"])
        if key in seen:
            raise ValueError("duplicated matched-event identifier")
        seen.add(key)
        a = rec["alternatives"]
        if not isinstance(a, (list, tuple)) or not a:
            raise ValueError("each matched event needs its own availability set")
        if any(not isinstance(v, (int, float)) or not isfinite(v) for v in a):
            raise ValueError("alternative depths must be numeric")
        if not isinstance(rec["used"], (int, float)) or not isfinite(rec["used"]):
            raise ValueError("used depth must be numeric")
        grouped[ident].append((float(mean(a)), float(rec["used"]), [float(v) for v in a]))
    if not grouped:
        raise ValueError("at least one individual is required")
    observed = {}
    for ident, es in grouped.items():
        if len(es) < 3:
            raise ValueError("at least 3 independent events per individual are required")
        observed[str(ident)] = _slope([e[0] for e in es], [e[1] for e in es])
    obs = mean(observed.values())
    rng = Random(seed)
    nulls = []
    for _ in range(draws):
        slopes = []
        for es in grouped.values():
            slopes.append(_slope([e[0] for e in es], [rng.choice(e[2]) for e in es]))
        nulls.append(mean(slopes))
    null_median = median(nulls)
    return {
        "n_individuals": len(grouped),
        "n_events": sum(map(len, grouped.values())),
        "individual_observed_slopes": observed,
        "observed_equal_individual_slope": obs,
        "pseudo_use_null_median_slope": null_median,
        "coupling_reduction_relative_to_null": (1 - obs / null_median) if null_median else None,
        "lower_tail_monte_carlo_p": (1 + sum(v <= obs for v in nulls)) / (draws + 1),
        "evidence_class": "calculation_only_requires_independent_field_validation",
    }


def origin_to_destination_state_retention(steps):
    """Within-step retention against actual origin-matched available endpoints.

    All categorical state classes must be source-defined and mutually exclusive.
    Raises on absent origin state: do not guess it from previous CSV row order.
    """
    individual = defaultdict(list)
    seen = set()
    for st in steps:
        for key in ("individual", "step_id", "origin_state", "observed_destination_state", "available_destination_states", "species", "timestamp"):
            if key not in st or st[key] is None:
                raise ValueError(f"origin/destination schema STOP: missing {key}")
        key = (st["individual"], st["step_id"])
        if key in seen:
            raise ValueError("step strata are not unique")
        seen.add(key)
        options = st["available_destination_states"]
        if not isinstance(options, (list, tuple)) or len(options) == 0 or any(s is None for s in options):
            raise ValueError("matched available destinations are required")
        observed = float(st["origin_state"] == st["observed_destination_state"])
        null = mean(float(st["origin_state"] == s) for s in options)
        individual[str(st["individual"])].append(observed - null)
    if not individual:
        raise ValueError("no valid steps")
    per_individual = {i: mean(v) for i, v in individual.items()}
    return {
        "n_individuals": len(individual),
        "n_steps": sum(map(len, individual.values())),
        "per_individual_retention_excess": per_individual,
        "equal_individual_retention_excess": mean(per_individual.values()),
        "individuals_positive": sum(x > 0 for x in per_individual.values()),
        "evidence_class": "calculation_only_requires_provenance_and_group_holdout",
    }

