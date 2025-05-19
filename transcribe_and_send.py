import os
import time
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from faster_whisper import WhisperModel
from irc.client import Reactor, ServerConnectionError

last_sent_time = 0
last_sent_text = ""

# load Twitch credentials from .env
load_dotenv()
TWITCH_NICK = os.getenv("TWITCH_NICK")
TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")

def calculate_cooldown(message: str) -> float:
    word_count = len(message.strip().split())

    if word_count <= 2:
        return 2 # short reaction
    elif word_count <= 6:
        return 4 # medium comment
    else:
        return 6 # long message

# new function to keep connection alive
def connect_to_twitch():
    reactor = Reactor()
    try:
        conn = reactor.server().connect("irc.chat.twitch.tv", 6667, TWITCH_NICK, password=TWITCH_TOKEN)
    except ServerConnectionError as e:
        print("IRC connection failed: {e}")
        return None, None
    
    def on_connect(connection, event):
        print("Connected to Twitch chat.")
        connection.join(TWITCH_CHANNEL)

    conn.add_global_handler("welcome", on_connect)

    # wait for connection
    for _ in range(10):
        reactor.process_once(timeout=1)
        time.sleep(0.1)

    return reactor, conn

# function to send a message to Twitch chat
def send_to_twitch(connection, message):
    global last_sent_time

    current_time = time.time()
    cooldown = calculate_cooldown(message)

    if message.strip().lower() == last_sent_text.strip().lower():
        print(f"Duplicate message ignored: {message}")
        return

    if current_time - last_sent_time < cooldown:
        print(f"Cooldown active. Skipped: {message}")
        return
    
    if connection:
        connection.privmsg(TWITCH_CHANNEL, message)
        last_sent_time = current_time
        last_sent_text = message.strip().lower()
        print(f"Sent: {message}")

# main loop to transcribe and send message
def main():
    print("Loading Whisper model...")
    model = WhisperModel("base", device="cpu")

    samplerate = 16000
    duration = 5 # seconds of recording

    print(f"Connecting to Twitch...")
    reactor, conn = connect_to_twitch()

    if not conn:
        print("Could not connect to Twitch. Exiting.")
        return
    
    print("Listening for speech... (Ctrl+C to stop)")

    while True:
        try:
            print("\nListening...")
            audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
            sd.wait()

            audio_data = np.squeeze(audio)

            segments, _ = model.transcribe(audio_data, language="en", beam_size=1)
            for segment in segments:
                text = segment.text.strip()
                if text:
                    print(f"You said: {text}")
                    send_to_twitch(conn, text)

        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()