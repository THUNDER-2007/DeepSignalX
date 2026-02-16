from flask import Flask, render_template, request, jsonify
import os
import cv2
import numpy as np
import librosa

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

# ================= IMAGE =================
def detect_image(path):
    img = cv2.imread(path)
    img = cv2.resize(img, (224, 224))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    score = 0
    variance = np.var(gray)

    if variance < 500:
        score += 0.3

    temp_path = "temp.jpg"
    cv2.imwrite(temp_path, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    recompressed = cv2.imread(temp_path)
    diff = cv2.absdiff(img, recompressed)

    if np.mean(diff) > 10:
        score += 0.3

    ai_score = min(variance / 1000, 1)
    score += 0.4 * ai_score

    if score > 0.5:
        return "Fake", round(score * 100, 2)
    else:
        return "Real", round((1 - score) * 100, 2)

# ================= VIDEO =================
def detect_video(path):
    cap = cv2.VideoCapture(path)
    suspicious = 0
    total = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or total > 60:
            break

        total += 1

        if total % 30 == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if np.var(gray) < 500:
                suspicious += 1

    cap.release()

    ratio = suspicious / max(total, 1)

    if ratio > 0.4:
        return "Fake", round(ratio * 100, 2)
    else:
        return "Real", round((1 - ratio) * 100, 2)

# ================= AUDIO =================
def detect_audio(path):
    y, sr = librosa.load(path, sr=16000)
    pitch = librosa.yin(y, fmin=50, fmax=300)
    variation = np.std(pitch)

    if variation < 5:
        return "Fake", 75
    else:
        return "Real", 80

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["file"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    if filepath.lower().endswith(('.jpg','.png','.jpeg')):
        result, confidence = detect_image(filepath)
    elif filepath.lower().endswith(('.mp4','.avi','.mov')):
        result, confidence = detect_video(filepath)
    elif filepath.lower().endswith(('.wav','.mp3')):
        result, confidence = detect_audio(filepath)
    else:
        return jsonify({"result":"Unsupported File","confidence":0})

    return jsonify({"result":result,"confidence":confidence})

if __name__ == "__main__":
    app.run(debug=True)
