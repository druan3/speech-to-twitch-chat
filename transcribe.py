import speech_recognition as sr

# initialize the recognizer
recognizer = sr.Recognizer()

# use the default microphone
with sr.Microphone() as source:
    print("Transcribing... Speak into your microphone (Ctrl+C to stop).")

    while True:
        try:
            print("\nListening...")
            audio = recognizer.listen(source)

            # transcribe using Google speech recognition
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")

        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print(f"Request Error: {e}")
        except KeyboardInterrupt:
            print("\nStopped by user.")
            break