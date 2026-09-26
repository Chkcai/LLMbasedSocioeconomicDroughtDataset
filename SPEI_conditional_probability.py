# SPEI_conditional_probability.py
# V2: Conditional probability of meteorological drought propagating into
# reported socioeconomic drought impacts.
#
#   P(reported impact | SPEI class c, timescale tau)
#       = N(reported impact AND SPEI_tau in c) / N(SPEI_tau in c)
#
# Data basis: RF_train_data.mat (368 cities x 15 years), 8 SPEI variants
# (SPEI-M / SPEI-SA at 1/3/6/12-month timescales) + SED binary labels.
# Only the specific SPEI variable and SED are required to be valid (-99
# excluded per cell), so each cell uses the maximum available sample size.
#
# SPEI drought categories (consistent with Figure 12 of the manuscript):
#   no drought      SPEI >  -0.5
#   mild            -1.0 <  SPEI <= -0.5
#   moderate        -1.5 <  SPEI <= -1.0
#   severe          -2.0 <  SPEI <= -1.5
#   extreme                 SPEI <= -2.0
#
# Outputs:
#   Github/spei_conditional_probability.csv  (long table, incl. Wilson 95% CI)

import numpy as np
import pandas as pd
import scipy.io as sio

MAT = "RF_train_data.mat"
OUT = "spei_conditional_probability.csv"

SPEI_VARIANTS = {
    "SPEI-M-1": "SPEI1M", "SPEI-M-3": "SPEI3M",
    "SPEI-M-6": "SPEI6M", "SPEI-M-12": "SPEI12M",
    "SPEI-SA-1": "SPEI1A", "SPEI-SA-3": "SPEI3A",
    "SPEI-SA-6": "SPEI6A", "SPEI-SA-12": "SPEI12A",
}

CATEGORIES = [
    ("no drought", -np.inf, -0.5),   # SPEI > -0.5
    ("mild",       -1.0,    -0.5),
    ("moderate",   -1.5,    -1.0),
    ("severe",     -2.0,    -1.5),
    ("extreme",    -np.inf, -2.0),   # SPEI <= -2.0  (lower bound unused)
]

def in_category(x, name, lo, hi):
    if name == "no drought":
        return x > -0.5
    if name == "extreme":
        return x <= -2.0
    return (x > lo) & (x <= hi)

def wilson_ci(k, n, z=1.959964):
    """Wilson score interval for a binomial proportion."""
    if n == 0:
        return np.nan, np.nan
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)

def main():
    S = sio.loadmat(MAT)
    # SED covers 16 years (2010-2025); SPEI matrices cover 15 years.
    # Consistent with RF_train.m (loops over the first 15 columns), we align
    # SED[:, :15] with the SPEI columns -> analysis window 2010-2024.
    SED = S["SED"].astype(float)[:, :15]  # 368 x 15, values 0/1 (-99 = missing)

    rows = []
    for label, key in SPEI_VARIANTS.items():
        variant, ts = label.rsplit("-", 1)          # SPEI-M / SPEI-SA, timescale
        spei = S[key].astype(float)
        valid = (spei != -99) & (SED != -99)
        for cat, lo, hi in CATEGORIES:
            mask = valid & in_category(spei, cat, lo, hi)
            n = int(mask.sum())
            k = int((SED[mask] == 1).sum())
            p = k / n if n else np.nan
            lo_ci, hi_ci = wilson_ci(k, n)
            rows.append({
                "spei_variant": label,
                "family": variant,                 # SPEI-M or SPEI-SA
                "timescale_months": int(ts),
                "category": cat,
                "n_samples": n,
                "n_impact": k,
                "P_conditional": round(p, 4) if n else np.nan,
                "wilson95_lower": round(lo_ci, 4) if n else np.nan,
                "wilson95_upper": round(hi_ci, 4) if n else np.nan,
            })

    df = pd.DataFrame(rows)
    cat_order = {c: i for i, (c, _, _) in enumerate(CATEGORIES)}
    df["cat_order"] = df["category"].map(cat_order)
    df = df.sort_values(["family", "timescale_months", "cat_order"]).drop(columns="cat_order")
    df.to_csv(OUT, index=False, encoding="utf-8-sig")

    # ---- console summary: pivot P by timescale x category per family ----
    for fam in ["SPEI-M", "SPEI-SA"]:
        sub = df[df["family"] == fam]
        piv_p = sub.pivot(index="category", columns="timescale_months", values="P_conditional")
        piv_p = piv_p.reindex([c for c, _, _ in CATEGORIES])
        piv_n = sub.pivot(index="category", columns="timescale_months", values="n_samples")
        piv_n = piv_n.reindex([c for c, _, _ in CATEGORIES])
        print(f"\n===== {fam} : P(reported impact | category, timescale) =====")
        print(piv_p.round(3).to_string())
        print(f"----- {fam} : sample sizes -----")
        print(piv_n.to_string())

    print(f"\nSaved -> {OUT}")

if __name__ == "__main__":
    main()
