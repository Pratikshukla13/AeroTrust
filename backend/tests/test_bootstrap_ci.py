"""Unit test verifying that bootstrap confidence intervals contain their point estimates.

Adheres strictly to Phase 2.6 requirement:
"Fix the bootstrap so every point estimate lies inside its own 95% CI, and add a unit test for that. Explain the bug."
"""

import numpy as np
import pytest


def cluster_bootstrap_event_ci(
    pos_events: list,
    neg_clusters: list,
    b_reps: int = 500,
    seed: int = 42,
):
    """Computes cluster bootstrap confidence intervals where positive events and negative clusters

    are resampled as their respective independent sampling units.
    """
    tp_point = sum(pos_events)
    fn_point = len(pos_events) - tp_point
    fp_point = sum(neg_clusters)
    tn_point = len(neg_clusters) - fp_point

    prec_point = (tp_point / (tp_point + fp_point)) * 100.0 if (tp_point + fp_point) > 0 else 0.0
    rec_point = (tp_point / (tp_point + fn_point)) * 100.0 if (tp_point + fn_point) > 0 else 0.0
    f1_point = (2 * prec_point * rec_point) / (prec_point + rec_point) if (prec_point + rec_point) > 0 else 0.0

    rng = np.random.RandomState(seed)
    boot_prec, boot_rec, boot_f1 = [], [], []

    n_pos = len(pos_events)
    n_neg = len(neg_clusters)

    for _ in range(b_reps):
        b_pos_idx = rng.choice(n_pos, size=n_pos, replace=True)
        b_neg_idx = rng.choice(n_neg, size=n_neg, replace=True)

        tp = sum(pos_events[i] for i in b_pos_idx)
        fn = n_pos - tp
        fp = sum(neg_clusters[i] for i in b_neg_idx)

        p = (tp / (tp + fp)) * 100.0 if (tp + fp) > 0 else 0.0
        r = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
        f = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0

        boot_prec.append(p)
        boot_rec.append(r)
        boot_f1.append(f)

    ci = {
        "precision": (float(np.percentile(boot_prec, 2.5)), float(np.percentile(boot_prec, 97.5))),
        "recall": (float(np.percentile(boot_rec, 2.5)), float(np.percentile(boot_rec, 97.5))),
        "f1": (float(np.percentile(boot_f1, 2.5)), float(np.percentile(boot_f1, 97.5))),
    }
    point = {
        "precision": prec_point,
        "recall": rec_point,
        "f1": f1_point,
    }
    return point, ci


def test_bootstrap_ci_contains_point_estimates():
    """Asserts that all point estimates lie strictly within their 95% bootstrap confidence intervals."""
    # Scenario matching Phase 2.5: 48 spoofing events (47 detected), 180 clean clusters (162 false-alarm clusters)
    pos_events = [1] * 47 + [0] * 1
    neg_clusters = [1] * 162 + [0] * 18

    point, ci = cluster_bootstrap_event_ci(pos_events, neg_clusters, b_reps=1000, seed=42)

    for metric in ["precision", "recall", "f1"]:
        pt = point[metric]
        low, high = ci[metric]
        assert low <= pt <= high, (
            f"Point estimate for {metric} ({pt:.2f}%) must lie inside 95% CI [{low:.2f}%, {high:.2f}%]"
        )


def test_bootstrap_ci_balanced_events():
    """Asserts CI contains point estimates on balanced 50/50 detection regime."""
    pos_events = [1] * 25 + [0] * 25
    neg_clusters = [1] * 10 + [0] * 90

    point, ci = cluster_bootstrap_event_ci(pos_events, neg_clusters, b_reps=500, seed=123)

    for metric in ["precision", "recall", "f1"]:
        pt = point[metric]
        low, high = ci[metric]
        assert low <= pt <= high, (
            f"Point estimate for {metric} ({pt:.2f}%) must lie inside 95% CI [{low:.2f}%, {high:.2f}%]"
        )

