def calculate_safety_score(no_helmet, no_vest):
    score = 100
    score -= no_helmet * 20
    score -= no_vest * 15
    return max(score, 0)

def get_risk_level(score):
    if score > 80:
        return "LOW"
    elif score > 50:
        return "MEDIUM"
    else:
        return "HIGH"