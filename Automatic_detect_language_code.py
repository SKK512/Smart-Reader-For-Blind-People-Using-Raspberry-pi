import pytesseract
import cv2
from gtts import gTTS
import os
import re
import time

# --------------------- SET TESSERACT PATH ---------------------
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata/'

# --------------------- SPEAK FUNCTION -------------------------
def speak_sen(text, lang):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")

    if os.system("mpg123 output.mp3") != 0:
        os.system("omxplayer output.mp3")

# --------------------- SMART LANGUAGE DETECTION ---------------
def smart_language_detect(text):
    devanagari_count = len(re.findall(r'[\u0900-\u097F]', text))
    total_chars = len(text)

    if total_chars == 0:
        return "eng", "en"

    if devanagari_count / total_chars > 0.30:
        return "mar", "mr"
    else:
        return "eng", "en"

# ------------------ AUTO TEXT PRESENCE CHECK ------------------
def text_present(frame):
    # fast OCR detection (only checks if ANY text exists)
    text = pytesseract.image_to_string(frame, lang="eng+mar").strip()
    return len(text) > 5, text  # True if meaningful text appears

# --------------------------------------------------------------
print("Auto Capture OCR Started...")
speak_sen("Camera started. Place the document under the camera.", "en")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    speak_sen("Camera error. Unable to start camera.", "en")
    print("Error: Could not open camera.")
    exit()

text_detected_time = 0
capture_delay =  10 # seconds of stable text before auto-capture

# --------------------------- MAIN LOOP -------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error.")
        speak_sen("Camera error.", "en")
        break

    cv2.imshow("Auto Capture OCR - Hold document steady", frame)

    # ---------- Check if text is present in the frame ----------
    detected, preview_text = text_present(frame)

    if detected:
        if text_detected_time == 0:
            text_detected_time = time.time()

        # Text stable for required delay?
        if time.time() - text_detected_time >= capture_delay:
            print("Auto-capturing...")
            speak_sen("Text detected. Reading now.", "en")

            image_path = "captured_auto.jpg"
            cv2.imwrite(image_path, frame)

            # Full OCR
            final_text = pytesseract.image_to_string(frame, lang="eng+mar").strip()
            print("\nExtracted Text:\n", final_text)

            # Detect language
            OCR_LANG, TTS_LANG = smart_language_detect(final_text)
            print("Detected Language:", OCR_LANG)

            if final_text:
                speak_sen(final_text, TTS_LANG)
            else:
                msg = "No text found." if TTS_LANG == "en" else "काहीही मजकूर आढळला नाही."
                speak_sen(msg, TTS_LANG)

            text_detected_time = 0  # Reset after reading
    else:
        text_detected_time = 0  # Reset if text disappears

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        speak_sen("Exiting program.", "en")
        break

cap.release()
cv2.destroyAllWindows()
