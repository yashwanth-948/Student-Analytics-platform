import numpy as np
import pandas as pd

# indicator -> (pillar, weight). Weights sum to 100.
INDICATORS = {
    "cgpa_score":            ("Academic", 20),
    "backlog_score":         ("Academic", 8),
    "subject_avg":           ("Academic", 7),
    "overall_att":           ("Attendance", 12),
    "min_subject_att":       ("Attendance", 8),
    "login_score":           ("Engagement", 6),
    "assignment_completion": ("Engagement", 8),
    "activity_score":        ("Engagement", 6),
    "aptitude":              ("Placement", 5),
    "coding":                ("Placement", 5),
    "mock_interview":        ("Placement", 4),
    "tech_skill":            ("Placement", 3),
    "soft_skill":            ("Placement", 3),
    "satisfaction_score":    ("Feedback", 3),
    "faculty_score":         ("Feedback", 2),
}
PILLARS = ["Academic", "Attendance", "Engagement", "Placement", "Feedback"]
LABELS = {
    "cgpa_score": "CGPA", "backlog_score": "Backlogs", "subject_avg": "Subject marks",
    "overall_att": "Overall attendance", "min_subject_att": "Weakest-subject attendance",
    "login_score": "LMS logins", "assignment_completion": "Assignment completion",
    "activity_score": "Clubs/events/certs", "aptitude": "Aptitude", "coding": "Coding",
    "mock_interview": "Mock interviews", "tech_skill": "Technical skills", "soft_skill": "Soft skills",
    "satisfaction_score": "Student satisfaction", "faculty_score": "Faculty feedback",
}
ACTIONS = {
    "High academics, low placement readiness": "Enrol in coding bootcamp and mock-interview drills",
    "Disengaged & at risk": "Mentor outreach this week; check attendance and personal barriers",
    "Capable but disengaged": "Nudge towards clubs, hackathons and LMS activity",
    "All-round high performer": "Invite as peer mentor; stretch with internships",
    "Steady / monitor": "Routine monitoring",
}


def add_derived(df):
    d = df.copy()
    d["cgpa_score"] = d["cgpa"] * 10
    d["backlog_score"] = (100 - d["backlogs"] * 25).clip(0, 100)
    d["login_score"] = (d["logins_per_week"] / 10 * 100).clip(0, 100)
    activity = d["events"] * 5 + d["clubs"] * 8 + d["hackathons"] * 10 + d["certifications"] * 8
    d["activity_score"] = activity.clip(0, 100)
    d["satisfaction_score"] = d["satisfaction"] / 5 * 100
    d["faculty_score"] = d["faculty_feedback"] / 5 * 100
    return d


def score_students(df):
    d = add_derived(df)
    ind = list(INDICATORS)
    weights = pd.Series({k: v[1] for k, v in INDICATORS.items()})

    contrib = d[ind].mul(weights / 100)
    d["success_score"] = contrib.sum(axis=1).round(1)

    for p in PILLARS:
        cols = [k for k, v in INDICATORS.items() if v[0] == p]
        d[f"{p.lower()}_pct"] = (contrib[cols].sum(axis=1) / weights[cols].sum() * 100).round(1)

    gap = weights - contrib
    d["top_drivers"] = [", ".join(LABELS[c] for c in contrib.loc[i].div(weights).nlargest(3).index) for i in d.index]
    d["top_drags"] = [", ".join(LABELS[c] for c in gap.loc[i].nlargest(3).index) for i in d.index]
    d["contributions"] = [
        {LABELS[c]: round(float(contrib.loc[i, c]), 2) for c in ind} for i in d.index]

    d["academic_risk"] = (
        (d["cgpa"] < 6) | (d["overall_att"] < 75) | (d["backlogs"] >= 3) | (d["academic_pct"] < 45))
    d["placement_risk"] = d["placement_pct"] < 50
    tier = np.where(d["success_score"] < 52, "High", np.where(d["success_score"] < 65, "Medium", "Low"))
    tier = np.where((d["academic_risk"] & d["placement_risk"] & (d["success_score"] < 60))
                    | (d["overall_att"] < 65), "High", tier)
    d["risk_tier"] = tier

    conds = [
        (d["overall_att"] < 65) | ((d["engagement_pct"] < 40) & (d["academic_pct"] < 55)),
        (d["academic_pct"] >= 70) & (d["placement_pct"] < 55),
        (d["academic_pct"] >= 60) & (d["engagement_pct"] < 45),
        (d["academic_pct"] >= 70) & (d["placement_pct"] >= 65) & (d["engagement_pct"] >= 55),
    ]
    names = ["Disengaged & at risk", "High academics, low placement readiness",
             "Capable but disengaged", "All-round high performer"]
    d["segment"] = np.select(conds, names, default="Steady / monitor")
    d["recommended_action"] = d["segment"].map(ACTIONS)
    return d