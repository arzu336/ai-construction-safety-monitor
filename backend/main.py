from fastapi import FastAPI, UploadFile, File
import shutil
from services.detection_service.detector import detect_ppe
import threading
import time
from services.video_service.video_processor import process_video
import services.risk_service.risk_analysis as calculate_safety_score

app = FastAPI()

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

latest_data = {
    "worker_count": 0,
    "helmet": 0,
    "vest": 0,
    "no_helmet": 0,
    "no_vest": 0,
    "safety_score": 100,
    "risk_level": "LOW"
}

def detection_loop():
    while True:
        try:
            result = detect_ppe("test.jpg")

            helmet = result["helmet"]
            vest = result["vest"]
            person = result["person"]

            no_helmet = max(person - helmet, 0)
            no_vest = max(person - vest, 0)

            score = calculate_safety_score(no_helmet, no_vest)
            risk = get_risk_level(score)

            latest_data.update({
                "worker_count": person,
                "helmet": helmet,
                "vest": vest,
                "no_helmet": no_helmet,
                "no_vest": no_vest,
                "safety_score": score,
                "risk_level": risk,
                "boxes": result["boxes"],
                "output_image": result["output_image"]
            })

        except Exception as e:
            print("Detection error:", e)

        time.sleep(2)

@app.get("/")
def home():
    return {"message": "AI Construction Safety Monitor API çalışıyor"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        file_path = f"temp_{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = detect_ppe(file_path)

        helmet = result["helmet"]
        vest = result["vest"]
        person = result["person"]

        no_helmet = max(person - helmet, 0)
        no_vest = max(person - vest, 0)

        score = calculate_safety_score(no_helmet, no_vest)
        risk = get_risk_level(score)

        alerts = []
        if no_helmet > 0:
            alerts.append(f"{no_helmet} çalışan baretsiz tespit edildi.")
        if no_vest > 0:
            alerts.append(f"{no_vest} çalışan yeleksiz tespit edildi.")
        if not alerts:
            alerts.append("Herhangi bir güvenlik ihlali tespit edilmedi.")

        return {
            "worker_count": person,
            "helmet": helmet,
            "vest": vest,
            "no_helmet": no_helmet,
            "no_vest": no_vest,
            "safety_score": score,
            "risk_level": risk,
            "boxes": result["boxes"],
            "output_image": result["output_image"],
            "alerts": alerts
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze-video")
async def analyze_video(file: UploadFile = File(...)):
    try:
        file_path = f"temp_{file.filename}"
        output_path = f"processed_{file.filename.rsplit('.', 1)[0]}.mp4"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = process_video(file_path, output_path=output_path, frame_skip=5)
        return result

    except Exception as e:
        return {"error": str(e)}
   
@app.get("/status")
def get_status():
    return latest_data

thread = threading.Thread(target=detection_loop, daemon=True)
thread.start()