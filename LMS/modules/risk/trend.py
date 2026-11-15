from datetime import date, timedelta
from sqlalchemy import select
from db.models.orm import StudentRiskHistory


def get_trends(session,student_ids,days=7,threshold=0.05):
    if not student_ids:
        return {}
    
    since=date.today() - timedelta(days=days * 4)
    rows=session.execute(
        select(StudentRiskHistory.student_id,
               StudentRiskHistory.snapshot_date,
               StudentRiskHistory.risk_score)
        .where(StudentRiskHistory.student_id.in_(student_ids),
               StudentRiskHistory.snapshot_date >= since)
        .order_by(StudentRiskHistory.student_id,StudentRiskHistory.snapshot_date)
    ).all()

    by_student={}
    for sid, d, s in rows:
        by_student.setdefault(sid, []).append((d, float(s)))

    target=date.today() - timedelta(days=days)
    out={}
    for sid, pts in by_student.items():
        latest_d, latest_s = pts[-1]
        older=[p for p in pts if p[0] <= target]
        base=older[-1] if older else (pts[0] if pts[0][0] < latest_d else None)
        if base is None:                      
            out[sid] = None
            continue

        diff=latest_s - base[1]
        direction="worse" if diff >= threshold else "better" if diff <= -threshold else "same"
        out[sid]={"direction":direction,"delta":round(diff * 100)}
    return out