import cv2
import os
from services.detection_service.detector import detect_ppe

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

def process_video(video_path, output_path="output_video.mp4", frame_skip=5):
    cap = cv2.VideoCapture(video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    if fps <= 0:
        fps = 25

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    processed_frames = 0

    total_no_helmet = 0
    total_no_vest = 0
    total_score = 0

    max_no_helmet = 0
    max_no_vest = 0
    worst_score = 100
    worst_frame_index = -1

    os.makedirs("temp_frames", exist_ok=True)

    last_processed_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Her frame'i yazmak için varsayılan olarak orijinal frame'i kullan
        frame_to_write = frame

        # Sadece belirli aralıklarla model çalıştır
        if frame_count % frame_skip == 0:
            frame_path = f"temp_frames/frame_{frame_count}.jpg"
            cv2.imwrite(frame_path, frame)

            result = detect_ppe(frame_path)

            person = result["person"]
            helmet = result["helmet"]
            vest = result["vest"]

            no_helmet = max(person - helmet, 0)
            no_vest = max(person - vest, 0)

            score = calculate_safety_score(no_helmet, no_vest)

            total_no_helmet += no_helmet
            total_no_vest += no_vest
            total_score += score
            processed_frames += 1

            max_no_helmet = max(max_no_helmet, no_helmet)
            max_no_vest = max(max_no_vest, no_vest)

            if score < worst_score:
                worst_score = score
                worst_frame_index = frame_count

            processed_frame = cv2.imread(result["output_image"])
            if processed_frame is not None:
                frame_to_write = processed_frame
                last_processed_frame = processed_frame

        else:
            # Ara frame'lerde son işlenmiş frame varsa onu kullan
            if last_processed_frame is not None:
                frame_to_write = last_processed_frame

        out.write(frame_to_write)
        frame_count += 1

    cap.release()
    out.release()

    average_score = int(total_score / processed_frames) if processed_frames > 0 else 100
    risk_level = get_risk_level(average_score)

    alerts = []
    if max_no_helmet > 0:
        alerts.append(f"Videoda en fazla {max_no_helmet} baretsiz çalışan tespit edildi.")
    if max_no_vest > 0:
        alerts.append(f"Videoda en fazla {max_no_vest} yeleksiz çalışan tespit edildi.")
    if processed_frames == 0:
        alerts.append("Video işlenemedi veya uygun frame bulunamadı.")
    if not alerts and processed_frames > 0:
        alerts.append("Videoda belirgin bir KKE ihlali tespit edilmedi.")

    return {
        "total_frames": frame_count,
        "processed_frames": processed_frames,
        "frame_skip": frame_skip,
        "total_no_helmet": total_no_helmet,
        "total_no_vest": total_no_vest,
        "average_safety_score": average_score,
        "risk_level": risk_level,
        "worst_score": worst_score if processed_frames > 0 else 100,
        "worst_frame_index": worst_frame_index,
        "max_no_helmet": max_no_helmet,
        "max_no_vest": max_no_vest,
        "alerts": alerts,
        "output_video": output_path
    }