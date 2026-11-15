import json
import math
from pathlib import Path
from .features import build_features, FEATURE_NAMES

MODEL_PATH=Path(__file__).parent / "risk_model.json"


def _row(f):
    return [f[n] if f[n] is not None else 0.0 for n in FEATURE_NAMES]


def load_model():
    try:
        return json.loads(MODEL_PATH.read_text()) if MODEL_PATH.exists() else None
    except Exception:
        return None


def ml_probability(model,f)->float:
    x = _row(f)
    z=model["intercept"] + sum(
        ((v - m) / s) * w
        for v, m, s, w in zip(x, model["mean"], model["scale"], model["coef"])
    )
    return 1 / (1 + math.exp(-z))


def train():
    import pandas as pd
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score, StratifiedKFold
    from db.session import SessionLocal
    from db.models.orm import StudentResult

    db=SessionLocal()
    try:
        feats=build_features(db)
        labels={}
        for sid, status in (db.query(StudentResult.student_id, StudentResult.result_status)
                              .filter(StudentResult.is_deleted == False).all()):
            labels[sid]=max(labels.get(sid, 0), 1 if status == "Fail" else 0)

        data = [(_row(feats[s]), y) for s, y in labels.items() if s in feats]
        X = pd.DataFrame([d[0] for d in data], columns=FEATURE_NAMES)
        y = pd.Series([d[1] for d in data])

        if y.sum() < 5 or (len(y) - y.sum()) < 5:
            print(f"Not enough data: {len(y)} students, {int(y.sum())} positives. Keep rules only.")
            return

        model=make_pipeline(StandardScaler(),
                              LogisticRegression(class_weight="balanced", max_iter=1000))
        cv = StratifiedKFold(n_splits=5,shuffle=True,random_state=42)
        print("CV ROC-AUC:",cross_val_score(model, X, y, cv=cv, scoring="roc_auc").mean())
        model.fit(X, y)

        sc=model.named_steps["standardscaler"]
        clf=model.named_steps["logisticregression"]
        MODEL_PATH.write_text(json.dumps({
            "mean":sc.mean_.tolist(),
            "scale":sc.scale_.tolist(),
            "coef":clf.coef_[0].tolist(),
            "intercept":float(clf.intercept_[0]),
            "features":FEATURE_NAMES,
        }))
        print("Saved",MODEL_PATH)
    finally:
        db.close()


if __name__ == "__main__":
    train()