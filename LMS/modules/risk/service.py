from db.models.orm import StudentRiskScore
from .features import build_features
from .scoring import rule_score, level_for
import joblib
from .train import MODEL_PATH
from .train import load_model, ml_probability

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
        row.risk_score,row.risk_level=score, level
        row.factors,row.model_version,row.is_deleted=reasons, version, False

        if level == "High" and not was_high:
            newly_high.append({
                "student_id":sid,
                "reasons":reasons
                })

    db.commit()
    return newly_high




def load_model():
    return joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None