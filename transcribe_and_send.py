import speech_recognition as sr
import irc.client
import os
import time
from dotenv import load_dotenv

# load Twitch credentials from .env
load_dotenv()
TWITCH_NICK = os.getenv("TWITCH_NICK")
TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")

# function to send a message to Twitch chat
def send_to_twitch(message):

    # attempt to connect to twitch chat
    print("Connecting to Twitch IRC...")

    reactor = irc.client.Reactor()
    try:
        conn = reactor.server().connect("irc.chat.twitch.tv", 6667, TWITCH_NICK, password=TWITCH_TOKEN)
    except irc.client.ServerConnectionError as e:
        print(f"IRC connection error: {e}")
        return
    
    def on_connect(connection, event):
        print("Connected! Joining channel and sending message...")
        connection.join(TWITCH_CHANNEL)
        connection.privmsg(TWITCH_CHANNEL, message)
        print(f"Sent to chat: {message}")
        time.sleep(1)
        connection.quit()

    conn.add_global_handler("welcome", on_connect)
    
    for _ in range(10):
        reactor.process_once(timeout=1)
        time.sleep(0.1)
    
# initialize the recognizer
recognizer = sr.Recognizer()

# use the default microphone
with sr.Microphone() as source:
    print("Listening... Speak clearly. (Ctrl+C to stop)")

    while True:
        try:
            print("\nListening...")
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)

            print(f"You said: {text}")
            send_to_twitch(text)

        except sr.UnknownValueError:
            print("Couldn't understand audio.")
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break