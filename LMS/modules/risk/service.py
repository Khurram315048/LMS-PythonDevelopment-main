
from decimal import Decimal
# import joblib
from db.models.orm import StudentRiskScore,StudentRiskHistory
from .features import build_features
from .scoring import rule_score, level_for
from .train import load_model, ml_probability
from datetime import date
# from .train import MODEL_PATH



def compute_and_save(db,student_ids=None,model=None)->list[dict]:
    feats=build_features(db,student_ids)
    newly_high=[]

    for sid, f in feats.items():
        score,reasons=rule_score(f)
        version="rules-v1"
        if model is not None:                     
            score=round(0.5 * score + 0.5 * ml_probability(model, f), 3)
            version="hybrid-v1"

        level=level_for(score)

        row=(db.query(StudentRiskScore)
                 .filter_by(student_id=sid,semester=f["semester"]).first())
        was_high=row is not None and row.risk_level=="High"

        if row is None:
            row=StudentRiskScore(student_id=sid,semester=f["semester"])
            db.add(row)
        row.risk_score=score
        row.risk_level=level
        today=date.today()
        semester=int(f["semester"])
        score_db=Decimal(str(score)).quantize(Decimal("0.001"))

        hist=(db.query(StudentRiskHistory).filter_by(student_id=sid,snapshot_date=today).first())

        if hist is None:
            hist=StudentRiskHistory(
                student_id=sid,
                snapshot_date=today,
                semester=semester,
                risk_score=score_db,
                risk_level=level,
            )
            db.add(hist)
        else:
            if hist.semester != semester:
                hist.semester=semester
            if hist.risk_score != score_db:
                hist.risk_score=score_db
            if hist.risk_level != level:
                hist.risk_level=level

        row.factors,row.model_version,row.is_deleted=reasons, version, False

        if level == "High" and not was_high:
            newly_high.append({
                "student_id":sid,
                "reasons":reasons
                })

    db.commit()
    return newly_high




# def load_model():
#     return joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

