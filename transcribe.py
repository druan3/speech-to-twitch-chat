import speech_recognition as sr

# initialize the recognizer
recognizer = sr.Recognizer()

# use the default microphone
with sr.Microphone() as source:
    print("Listening... (say something)")
    audio = recognizer.listen(source)

    try:
        # convert speech to text
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said.")
    except sr.RequestError as e:
        print(f"Error with the recognition service: {e}")