def box_center(box):
    cx = (box["x1"] + box["x2"]) / 2
    cy = (box["y1"] + box["y2"]) / 2
    return cx, cy

def point_in_box(x, y, box):
    return box["x1"] <= x <= box["x2"] and box["y1"] <= y <= box["y2"]

def evaluate_safety(data):
    persons = [b for b in data["boxes"] if b["class"] == "person"]
    helmets = [b for b in data["boxes"] if b["class"] == "helmet"]
    vests = [b for b in data["boxes"] if b["class"] == "vest"]

    no_helmet = 0
    no_vest = 0

    for person in persons:
        has_helmet = False
        has_vest = False

        for helmet in helmets:
            hx, hy = box_center(helmet)
            if point_in_box(hx, hy, person):
                has_helmet = True
                break

        for vest in vests:
            vx, vy = box_center(vest)
            if point_in_box(vx, vy, person):
                has_vest = True
                break

        if not has_helmet:
            no_helmet += 1
        if not has_vest:
            no_vest += 1

    alerts = []

    if len(persons) == 0:
        return {
            "risk": "Yok",
            "alerts": ["Çalışan tespit edilmedi."],
            "no_helmet": 0,
            "no_vest": 0
        }

    if no_helmet > 0:
        alerts.append(f"⚠️ {no_helmet} çalışan baret kullanmıyor.")
    if no_vest > 0:
        alerts.append(f"⚠️ {no_vest} çalışan yelek kullanmıyor.")

    if no_helmet == 0 and no_vest == 0:
        alerts.append("✅ Tespit edilen çalışanlarda temel KKE uyumu sağlanıyor.")

    if no_helmet > 0 or no_vest > 1:
        risk = "Yüksek"
    elif no_helmet > 0 or no_vest > 0:
        risk = "Orta"
    else:
        risk = "Düşük"

    return {
        "risk": risk,
        "alerts": alerts,
        "no_helmet": no_helmet,
        "no_vest": no_vest
    }