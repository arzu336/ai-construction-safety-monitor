from ultralytics import YOLO
from PIL import Image
import os

MODEL_PATH = "C:/Users/sahip/runs/detect/train4/weights/best.pt"
model = YOLO(MODEL_PATH)

def detect_ppe(image_path, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)

    results = model(image_path)
    result = results[0]

    boxes = []
    counts = {"helmet": 0, "vest": 0, "person": 0}

    print("Model class names:", model.names)

    for box in result.boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        class_name = str(model.names[cls_id]).lower()

        print("Tespit edilen sınıf:", class_name, "conf:", conf)

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        boxes.append({
            "class": class_name,
            "conf": conf,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2
        })

        if class_name in ["helmet", "hardhat", "hard_hat"]:
            counts["helmet"] += 1
        elif class_name in ["vest", "safety_vest", "reflective_vest"]:
            counts["vest"] += 1
        elif class_name in ["person", "worker", "people"]:
            counts["person"] += 1

    output_path = os.path.join(output_dir, "result.jpg")
    plotted = result.plot()
    Image.fromarray(plotted[..., ::-1]).save(output_path)

    print("Son sayımlar:", counts)

    return {
        "helmet": counts["helmet"],
        "vest": counts["vest"],
        "person": counts["person"],
        "boxes": boxes,
        "output_image": output_path
    }