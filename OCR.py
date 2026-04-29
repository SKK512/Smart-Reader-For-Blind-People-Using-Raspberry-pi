import pytesseract
import cv2
from gtts import gTTS
import pyttsx3
import os
import time

# Initialize camera (0 = default camera, change if multiple cameras)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("Press 'c' to capture image, 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    cv2.imshow("Live Camera - Press 'c' to Capture", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        # Save captured frame
        image_path = "captured.jpg"
        cv2.imwrite(image_path, frame)
        print(f"Image saved as {image_path}")

        # OCR: extract text from image
        image = cv2.imread(image_path)
        extracted_text = pytesseract.image_to_string(image)
        print("Extracted Text:\n", extracted_text)

        # Try offline TTS with pyttsx3
        try:
            engine = pyttsx3.init()

            # List voices (only once, not every loop ideally)
            voices = engine.getProperty('voices')
            print("\nAvailable Voices:")
            for idx, voice in enumerate(voices):
                print(f"{idx}: {voice.name} ({voice.id})")

            engine.setProperty('voice', voices[0].id)  # Choose first available voice
            engine.setProperty('rate', 125)

            engine.say("Starting text-to-speech.")
            engine.say(extracted_text if extracted_text.strip() else "No text detected.")
            engine.runAndWait()

        except Exception as e:
            print("pyttsx3 failed, falling back to gTTS.")
            print("Error:", str(e))

            language = 'en'
            tts = gTTS(text=extracted_text or "No text detected.", lang=language, slow=False)
            tts.save("output.mp3")

            # Play audio
            if os.system("mpg123 output.mp3") != 0:
                os.system("omxplayer output.mp3")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
