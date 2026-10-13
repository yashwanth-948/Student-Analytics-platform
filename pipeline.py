import json
import sqlite3
from pathlib import Path

import pandas as pd

from scoring import score_students

DATA = Path("data")
DB = "campus.db"
log = []


def note(source, issue, action, count):
    if count:
        log.append({"source": source, "issue": issue, "action": action, "rows_affected": int(count)})


def load(name):
    return pd.read_csv(DATA / f"{name}.csv")


def clean_all():
    acad, att, lms, eng = load("academic"), load("attendance"), load("lms"), load("engagement")
    plc, skl, fb = load("placement"), load("skills"), load("feedback")

    n = att.duplicated("student_id").sum()
    att = att.drop_duplicates("student_id", keep="first")
    note("attendance", "duplicate student_id", "kept first record", n)

    dept_map = {"computer science": "CSE", "cse": "CSE", "ece": "ECE", "mech": "MECH",
                "civil": "CIVIL", "it": "IT"}
    raw = acad["department"].astype(str).str.strip().str.lower()
    changed = (acad["department"] != raw.map(dept_map)).sum()
    acad["department"] = raw.map(dept_map).fillna(acad["department"])
    note("academic", "inconsistent department names", "standardised to short codes", changed)

    for col in ["aptitude", "coding", "mock_interview"]:
        before = plc[col].isna().sum()
        plc[col] = pd.to_numeric(plc[col], errors="coerce")
        note("placement", f"non-numeric value in {col}", "converted to NaN for imputation",
             plc[col].isna().sum() - before)

    for col in ["overall_att", "min_subject_att"]:
        bad = (att[col] > 100).sum()
        att[col] = att[col].clip(upper=100)
        note("attendance", f"{col} above 100%", "capped at 100", bad)

    m = acad
    for df in (att, lms, eng, plc, skl, fb):
        m = m.merge(df, on="student_id", how="left")

    for col in m.select_dtypes("number").columns:
        miss = m[col].isna().sum()
        if miss:
            m[col] = m[col].fillna(m.groupby("department")[col].transform("median")).fillna(m[col].median())
            note("merged", f"missing {col}", "imputed with department median", miss)
    return m


def main():
    merged = clean_all()
    scored = score_students(merged)
    scored["contributions"] = scored["contributions"].apply(json.dumps)

    con = sqlite3.connect(DB)
    scored.to_sql("students", con, if_exists="replace", index=False)
    pd.DataFrame(log).to_sql("cleaning_log", con, if_exists="replace", index=False)
    con.execute("CREATE INDEX IF NOT EXISTS idx_risk ON students(risk_tier)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_dept ON students(department)")
    con.commit()
    con.close()

    print(f"{len(scored)} students scored -> {DB}")
    print(scored["risk_tier"].value_counts().to_string())
    print(pd.DataFrame(log).to_string(index=False))


if __name__ == "__main__":
    main()