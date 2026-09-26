# manifestation_type_classification.py
# V3 / P1-E: Mine manifestation types from the LLM rationale texts (column G)
# of the confirmed events, upgrading the database from a binary label to
# "binary label + manifestation types".
#
# Confirmed events: Manual Review code 1 (TP) or 4 (FN, manually confirmed).
# Classification: multi-label keyword matching, NON-exclusive categories,
# aligned with the five manifestations in Section 3.1 of the manuscript.
#
# Outputs (all in Github/):
#   1) manifestation_labels.xlsx          event-level 0/1 flags (n = 2299)
#   2) manifestation_composition.xlsx     overall shares, full vs excl. 2020
#   3) manifestation_yearly_trend.xlsx    yearly supply/demand mention shares
#   4) manifestation_verification_sample50.xlsx   random 50 for manual check
#   5) China_Socioeconomic_Drought_Database(2010-2025)_v2.xlsx
#      original database + 4 new manifestation-flag columns

import random
import pandas as pd
import openpyxl

DB = "../China_Socioeconomic_Drought_Database(2010-2025).xlsx"
DB_OUT = "../China_Socioeconomic_Drought_Database(2010-2025)_v3.xlsx"

# ---- keyword dictionary v3 (revised after 50-sample blind verification) ----
# Changes vs v2 (agreement-driven):
#   supply:    + "限制供水"               (missed phrasing in 汕头)
#              ("用水困难" tested and REVERTED: fires on "农业/生产用水困难" = demand-side, supply agreement dropped 90->86)
#   demand:    + "受旱", "缺墒"           (covers "农作物大面积受旱"/"田作物受旱"/"作物受旱"/"耕地缺水缺墒")
#              - "灌溉" (bare)            (fired on response actions & potential language: 渭南/平顶山/北海/怒江)
#              compounds "农田/农作物/农业受旱" absorbed into bare "受旱"
#   emergency: + "应急调度"               (珠海 2016 official dispatch phrasing)
KEYWORDS = {
    "supply": [
        "供水困难", "供水紧张", "供水不足", "供水短缺", "限水", "限时供水",
        "停水", "减压供水", "供水危机", "饮水困难", "吃水困难",
        "水荒", "断水", "限制供水",
    ],
    "demand": [
        "停产", "限产", "生产受限", "工业用水", "企业用水", "无法灌溉",
        "受旱", "缺墒", "绝收", "受灾面积",
    ],
    "emergency": [
        "应急调水", "应急供水", "应急送水", "送水车", "拉水", "运水", "送水",
        "应急调度",
    ],
    "other": ["航运", "水位降低", "生态"],
}
TYPES = ["supply", "demand", "emergency", "other"]

def classify(text):
    return {t: int(any(w in text for w in KEYWORDS[t])) for t in TYPES}

def main():
    wb = openpyxl.load_workbook(DB, read_only=True)

    events = []  # (year, city, code, text)
    for ws in wb.worksheets:
        if ws.title == "Introduction":
            continue
        year = ws.title
        for row in ws.iter_rows(min_row=2, values_only=True):
            code = str(row[7]).strip() if row[7] is not None else ""
            if code not in ("1", "4"):
                continue
            city = row[1] if row[1] is not None else row[0]
            text = str(row[6]).strip() if row[6] else ""
            events.append({"year": year, "city": city, "review_code": code,
                           "text": text})
    wb.close()

    df = pd.DataFrame(events)
    flags = df["text"].apply(lambda s: classify(s) if s else {t: 0 for t in TYPES})
    for t in TYPES:
        df[t] = flags.apply(lambda d: d[t])
    df["has_text"] = (df["text"] != "").astype(int)
    df["unmatched"] = ((df["has_text"] == 1) &
                       (df[TYPES].sum(axis=1) == 0)).astype(int)

    n_all = len(df)
    n_txt = df["has_text"].sum()
    print(f"confirmed events: {n_all} (expect 2299)")
    print(f"with rationale text: {n_txt} ({n_txt/n_all*100:.1f}%)")

    # ---------- 1) event-level labels ----------
    out1 = df[["year", "city", "review_code", "has_text"] + TYPES +
              ["unmatched", "text"]]
    out1.to_excel("manifestation_labels.xlsx", index=False)

    # ---------- 2) overall composition: full vs excluding 2020 ----------
    def composition(sub):
        st = sub[sub["has_text"] == 1]
        n = len(st)
        row = {"n_with_text": n}
        for t in TYPES:
            row[f"{t}_count"] = int(st[t].sum())
            row[f"{t}_share"] = round(st[t].mean(), 4)
        row["unmatched_count"] = int(st["unmatched"].sum())
        row["unmatched_share"] = round(st["unmatched"].mean(), 4)
        return row

    comp = pd.DataFrame({
        "full_sample": composition(df),
        "excluding_2020": composition(df[df["year"] != "2020"]),
    }).T
    comp.to_excel("manifestation_composition.xlsx")
    print("\n===== composition (share among records WITH text) =====")
    print(comp.to_string())

    # ---------- 3) yearly trend (supply vs demand share) ----------
    st = df[df["has_text"] == 1]
    tr = st.groupby("year").agg(
        n_with_text=("has_text", "sum"),
        supply_share=("supply", "mean"),
        demand_share=("demand", "mean"),
        emergency_share=("emergency", "mean"),
        other_share=("other", "mean"),
        unmatched_share=("unmatched", "mean"),
    ).round(4).reset_index()
    # add missing-text counts per year for annotation
    miss = df[df["has_text"] == 0].groupby("year").size().rename("n_no_text")
    tr = tr.merge(miss, on="year", how="left").fillna({"n_no_text": 0})
    tr["n_no_text"] = tr["n_no_text"].astype(int)
    tr.to_excel("manifestation_yearly_trend.xlsx", index=False)
    print("\n===== yearly trend =====")
    print(tr.to_string(index=False))

    # ---------- 4) random 50 sample for manual verification ----------
    # NOTE: only generate once — never overwrite the user-filled file on reruns
    import os
    if not os.path.exists("manifestation_verification_sample50.xlsx"):
        random.seed(42)
        pool = st.index.tolist()
        samp_idx = random.sample(pool, 50)
        samp = df.loc[samp_idx, ["year", "city", "text"]].copy()
        # blind verification: user fills their own 0/1; model labels kept aside
        for t in TYPES:
            samp[f"user_{t}"] = ""
        model = df.loc[samp_idx, TYPES].reset_index(drop=True)
        samp = samp.reset_index(drop=True)
        with pd.ExcelWriter("manifestation_verification_sample50.xlsx") as xw:
            samp.to_excel(xw, sheet_name="blind_to_fill", index=False)
            model.to_excel(xw, sheet_name="model_labels_hidden", index=False)
        print("\nverification sample saved (blind sheet + hidden model labels)")
    else:
        print("\nverification sample exists (user-filled) -> skipped regeneration")

    # ---------- 5) upgraded database with 4 new columns ----------
    label_map = {}
    for _, r in df.iterrows():
        # flags are only meaningful when a rationale text exists;
        # for events without text store None -> leave cells blank
        if int(r["has_text"]) == 1:
            label_map[(str(r["year"]), str(r["city"]))] = {t: int(r[t]) for t in TYPES}
        else:
            label_map[(str(r["year"]), str(r["city"]))] = None

    wb2 = openpyxl.load_workbook(DB)
    headers = ["Manifestation_SupplySide", "Manifestation_DemandSide",
               "Manifestation_EmergencyResponse", "Manifestation_Other"]
    for ws in wb2.worksheets:
        if ws.title == "Introduction":
            continue
        year = str(ws.title)
        # write headers at columns I-L (9-12)
        for j, h in enumerate(headers):
            ws.cell(row=1, column=9 + j, value=h)
        for row in ws.iter_rows(min_row=2):
            code = str(row[7].value).strip() if row[7].value is not None else ""
            if code not in ("1", "4"):
                continue
            city = str(row[1].value if row[1].value is not None else row[0].value)
            lab = label_map.get((year, city))
            if lab is None:
                continue  # no rationale text -> leave the new columns blank
            for j, t in enumerate(TYPES):
                ws.cell(row=row[0].row, column=9 + j, value=lab[t])
    wb2.save(DB_OUT)
    print(f"upgraded database saved -> {DB_OUT}")

if __name__ == "__main__":
    main()
