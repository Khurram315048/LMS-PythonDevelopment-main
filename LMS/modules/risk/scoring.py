def _linear(value,good,bad):
    if value is None:
        return None
    
    t=(value - good) / (bad - good)
    return max(0.0,min(1.0,t))


WEIGHTS={
    "attendance":0.35,
    "gpa": 0.30,
    "fails": 0.15,
    "fees": 0.10,
    "assign":0.10
    }


def rule_score(f:dict)->tuple[float,list[str]]:
    parts={
        "attendance": _linear(f["attendance_pct"],85,50),
        "gpa": _linear(f["prev_gpa"],3.0,1.5),
        "fails":min(f["fail_count"] / 3, 1.0),
        "fees":min(f["fee_due_count"] / 3, 1.0),
        "assign":_linear(f["assignment_avg"],70,30),
    }
    if f["gpa_trend"] < -0.3 and parts["gpa"] is not None:   
        parts["gpa"]=min(1.0, parts["gpa"] + 0.2)

  
    used={k: v for k, v in parts.items() if v is not None}
    total_w=sum(WEIGHTS[k] for k in used)
    score=sum(WEIGHTS[k] * v for k, v in used.items()) / total_w if total_w else 0.0

    reasons=[]
    if parts["attendance"] and parts["attendance"] > 0.3:
        reasons.append(f"Low attendance ({f['attendance_pct']}%)")

    if parts["gpa"] and parts["gpa"] > 0.3:
        reasons.append(f"Low GPA last semester ({f['prev_gpa']})")

    if f["gpa_trend"] < -0.3:
        reasons.append(f"GPA dropped by {abs(f['gpa_trend'])}")

    if f["fail_count"]:
        reasons.append(f"{f['fail_count']} failed subject(s)")

    if f["fee_due_count"]:
        reasons.append(f"{f['fee_due_count']} unpaid fee(s)")

    if parts["assign"] and parts["assign"] > 0.3:
        reasons.append(f"Weak assignments/quizzes ({f['assignment_avg']}%)")

    return round(score,3),reasons


def level_for(score:float)->str:
    return "High" if score >= 0.60 else "Medium" if score >= 0.35 else "Low"