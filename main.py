import json
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

DB = "campus.db"
app = FastAPI(title="Smart Campus Analytics API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

LIST_COLS = ("student_id, name, department, year, cgpa, overall_att, success_score, academic_risk, "
             "placement_risk, risk_tier, segment, academic_pct, attendance_pct, engagement_pct, placement_pct")


def q(sql, params=()):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(sql, params).fetchall()]
    con.close()
    return rows


def fix(row):
    for k in ("academic_risk", "placement_risk"):
        if k in row:
            row[k] = bool(row[k])
    return row


@app.get("/students")
def students(department: Optional[str] = None, year: Optional[int] = None, risk_tier: Optional[str] = None,
             segment: Optional[str] = None, search: Optional[str] = None, sort: str = "success_score",
             order: str = "asc", limit: int = 100, offset: int = 0):
    allowed = {"success_score", "cgpa", "overall_att", "student_id", "name"}
    if sort not in allowed:
        raise HTTPException(400, f"sort must be one of {sorted(allowed)}")
    where, p = [], []
    for col, val in (("department", department), ("year", year), ("risk_tier", risk_tier), ("segment", segment)):
        if val is not None:
            where.append(f"{col} = ?")
            p.append(val)
    if search:
        where.append("(name LIKE ? OR student_id LIKE ?)")
        p += [f"%{search}%"] * 2
    w = ("WHERE " + " AND ".join(where)) if where else ""
    direction = "DESC" if order.lower() == "desc" else "ASC"
    total = q(f"SELECT COUNT(*) AS n FROM students {w}", p)[0]["n"]
    rows = q(f"SELECT {LIST_COLS} FROM students {w} ORDER BY {sort} {direction} LIMIT ? OFFSET ?",
             p + [limit, offset])
    return {"total": total, "items": [fix(r) for r in rows]}


@app.get("/students/{student_id}")
def student(student_id: str):
    rows = q("SELECT * FROM students WHERE student_id = ?", (student_id,))
    if not rows:
        raise HTTPException(404, "Student not found")
    r = fix(rows[0])
    r["contributions"] = json.loads(r["contributions"])
    return r


@app.get("/summary")
def summary():
    kpi = q("""SELECT COUNT(*) AS students, ROUND(AVG(success_score),1) AS avg_score,
               SUM(academic_risk) AS academic_risk, SUM(placement_risk) AS placement_risk,
               SUM(risk_tier='High') AS high_risk FROM students""")[0]
    return {
        "kpis": kpi,
        "risk_distribution": q("SELECT risk_tier, COUNT(*) AS count FROM students GROUP BY risk_tier"),
        "segments": q("SELECT segment, COUNT(*) AS count, ROUND(AVG(success_score),1) AS avg_score "
                      "FROM students GROUP BY segment ORDER BY count DESC"),
        "by_department": q("""SELECT department, COUNT(*) AS students, ROUND(AVG(success_score),1) AS avg_score,
                              SUM(risk_tier='High') AS high_risk FROM students GROUP BY department"""),
        "by_year": q("SELECT year, ROUND(AVG(success_score),1) AS avg_score, ROUND(AVG(overall_att),1) AS avg_att "
                     "FROM students GROUP BY year ORDER BY year"),
        "pillar_averages": q("""SELECT ROUND(AVG(academic_pct),1) AS academic, ROUND(AVG(attendance_pct),1) AS attendance,
                                ROUND(AVG(engagement_pct),1) AS engagement, ROUND(AVG(placement_pct),1) AS placement
                                FROM students""")[0],
        "score_histogram": q("SELECT CAST(success_score/10 AS INT)*10 AS bucket, COUNT(*) AS count "
                             "FROM students GROUP BY bucket ORDER BY bucket"),
    }


@app.get("/insights")
def insights():
    out = []
    n = q("SELECT COUNT(*) AS n FROM students WHERE segment='High academics, low placement readiness'")[0]["n"]
    out.append(f"{n} students have strong academics but low placement readiness - target with coding/mock-interview programmes.")
    n = q("SELECT COUNT(*) AS n FROM students WHERE overall_att < 75")[0]["n"]
    out.append(f"{n} students are below the 75% attendance threshold.")
    d = q("SELECT department, ROUND(AVG(success_score),1) AS s FROM students GROUP BY department ORDER BY s LIMIT 1")[0]
    out.append(f"{d['department']} has the lowest average Success Score ({d['s']}).")
    hi = q("SELECT COUNT(*) AS n FROM students WHERE risk_tier='High'")[0]["n"]
    out.append(f"{hi} students are in the High-risk tier and need intervention first.")
    slope = q("""SELECT (AVG(assignment_completion*cgpa) - AVG(assignment_completion)*AVG(cgpa)) /
                 (AVG(assignment_completion*assignment_completion) - AVG(assignment_completion)*AVG(assignment_completion))
                 AS slope FROM students""")[0]["slope"]
    out.append(f"Each +10 points of assignment completion goes with roughly +{round(slope * 10, 2)} CGPA points.")
    return {"insights": out}


@app.get("/cleaning-log")
def cleaning_log():
    return q("SELECT * FROM cleaning_log")