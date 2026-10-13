"""Step 1: generate 7 messy source CSVs (replace with real college data if you have it)."""
import numpy as np
import pandas as pd
from pathlib import Path

N = 500
rng = np.random.default_rng(42)
OUT = Path("data")
OUT.mkdir(exist_ok=True)

ids = [f"S{1000 + i}" for i in range(N)]
ability = rng.normal(0, 1, N)       # hidden "academic ability"
effort = rng.normal(0, 1, N)        # hidden "engagement/effort"
prep = 0.4 * ability + rng.normal(0, 1, N)  # placement preparation


def clip(a, lo, hi):
    return np.clip(a, lo, hi)


depts = rng.choice(["CSE", "ECE", "MECH", "CIVIL", "IT"], N)
years = rng.choice([1, 2, 3, 4], N)

academic = pd.DataFrame({
    "student_id": ids,
    "name": [f"Student {i}" for i in range(N)],
    "department": depts,
    "year": years,
    "cgpa": clip(6.8 + 1.3 * ability + 0.3 * effort, 3.5, 10).round(2),
    "backlogs": clip(np.round(1.2 - 1.1 * ability + rng.normal(0, 0.8, N)), 0, 8).astype(int),
    "subject_avg": clip(62 + 12 * ability + 4 * effort + rng.normal(0, 5, N), 20, 100).round(1),
})

overall_att = clip(85 + 8 * effort + 3 * ability + rng.normal(0, 5, N), 30, 100)
attendance = pd.DataFrame({
    "student_id": ids,
    "overall_att": overall_att.round(1),
    "min_subject_att": clip(overall_att - rng.uniform(3, 20, N), 15, 100).round(1),
})

lms = pd.DataFrame({
    "student_id": ids,
    "logins_per_week": clip(5 + 2.5 * effort + rng.normal(0, 1.5, N), 0, 20).round(1),
    "assignment_completion": clip(70 + 14 * effort + 4 * ability + rng.normal(0, 8, N), 0, 100).round(1),
})

engagement = pd.DataFrame({
    "student_id": ids,
    "events": clip(np.round(3 + 2 * effort + rng.normal(0, 1.5, N)), 0, 15).astype(int),
    "clubs": clip(np.round(1.2 + 0.8 * effort + rng.normal(0, 0.8, N)), 0, 5).astype(int),
    "hackathons": clip(np.round(0.8 + 0.8 * prep + rng.normal(0, 0.8, N)), 0, 6).astype(int),
    "certifications": clip(np.round(1.5 + 1.0 * prep + rng.normal(0, 1, N)), 0, 8).astype(int),
})

placement = pd.DataFrame({
    "student_id": ids,
    "aptitude": clip(58 + 13 * prep + rng.normal(0, 7, N), 5, 100).round(1),
    "coding": clip(52 + 16 * prep + rng.normal(0, 9, N), 0, 100).round(1),
    "mock_interview": clip(55 + 13 * prep + 3 * effort + rng.normal(0, 8, N), 5, 100).round(1),
})

skills = pd.DataFrame({
    "student_id": ids,
    "tech_skill": clip(55 + 14 * prep + rng.normal(0, 8, N), 5, 100).round(1),
    "soft_skill": clip(60 + 8 * effort + 4 * prep + rng.normal(0, 9, N), 10, 100).round(1),
})

feedback = pd.DataFrame({
    "student_id": ids,
    "satisfaction": clip(3.4 + 0.4 * effort + 0.2 * ability + rng.normal(0, 0.6, N), 1, 5).round(1),
    "faculty_feedback": clip(3.5 + 0.5 * effort + 0.3 * ability + rng.normal(0, 0.5, N), 1, 5).round(1),
})

# ---- inject realistic mess so the cleaning step has something to do ----
academic["department"] = academic["department"].replace({"CSE": "Computer Science"}).where(
    rng.random(N) > 0.1, academic["department"].str.lower() + " ")
academic.loc[rng.choice(N, 8, replace=False), "cgpa"] = np.nan
attendance.loc[rng.choice(N, 6, replace=False), "overall_att"] = attendance["overall_att"] + 20   # >100
attendance = pd.concat([attendance, attendance.sample(12, random_state=1)])                      # duplicates
lms.loc[rng.choice(N, 15, replace=False), "logins_per_week"] = np.nan
placement.loc[rng.choice(N, 25, replace=False), "coding"] = np.nan
placement["aptitude"] = placement["aptitude"].astype(object)
placement.loc[rng.choice(N, 5, replace=False), "aptitude"] = "N/A"
feedback = feedback.drop(rng.choice(N, 20, replace=False))                                       # missing students

for name, df in {"academic": academic, "attendance": attendance, "lms": lms, "engagement": engagement,
                 "placement": placement, "skills": skills, "feedback": feedback}.items():
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"wrote data/{name}.csv  ({len(df)} rows)")