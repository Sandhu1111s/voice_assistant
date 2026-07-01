import datetime
import os
import time
import webbrowser as wb

import pyautogui
import pyjokes
import pyttsx3
import pywhatkit
import speech_recognition as sr
import wikipedia

ASSISTANT_NAME = "Friday"
LISTEN_TIMEOUT = 5
LISTEN_COOLDOWN = 2.5

engine = pyttsx3.init()
engine.setProperty("voice", engine.getProperty("voices")[0].id)
engine.setProperty("rate", 150)
engine.setProperty("volume", 1)

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1
recognizer.dynamic_energy_threshold = True
microphone = sr.Microphone()

URL_COMMANDS = {
    "open youtube": "https://youtube.com",
    "open yt": "https://youtube.com",
    "open google": "https://google.com",
    "open chatgpt": "https://chatgpt.com",
}


def speak(text: str, *, echo: bool = True) -> None:
    if echo:
        print(text)
    engine.say(text)
    engine.runAndWait()


def tell_time() -> None:
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak(f"The current time is {current_time}")


def date() -> None:
    now = datetime.datetime.now()
    speak(f"The current date is {now.strftime('%B')} {now.day}, {now.year}")


def wishme() -> None:
    speak("Welcome back, sir.")

    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        speak("Good morning!")
    elif 12 <= hour < 17:
        speak("Good afternoon!")
    elif 17 <= hour < 24:
        speak("Good evening!")
    else:
        speak("Good night. See you tomorrow.")

    speak(f"{ASSISTANT_NAME} at your service. How may I assist you?")


def screenshot() -> None:
    img_path = os.path.join(
        os.path.expanduser("~/Pictures"),
        f"jarvis_screenshot_{datetime.datetime.now():%Y%m%d_%H%M%S}.png",
    )
    os.makedirs(os.path.dirname(img_path), exist_ok=True)
    pyautogui.screenshot().save(img_path)
    speak(f"Screenshot saved to {img_path}.")


def init_microphone() -> None:
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.8)


def takecmd() -> str | None:
    with microphone as source:
        try:
            audio = recognizer.listen(
                source,
                timeout=LISTEN_TIMEOUT,
                phrase_time_limit=8,
            )
        except sr.WaitTimeoutError:
            return None

    try:
        query = recognizer.recognize_google(audio, language="en-in").lower()
        print(f"You: {query}")
        return query
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        speak("Speech recognition service is unavailable.")
        return None
    except Exception as exc:
        speak(f"An error occurred: {exc}")
        return None


def play_song() -> None:
    speak("Which song would you like to play?")
    song = takecmd()
    if song:
        speak(f"Playing {song} on YouTube.")
        pywhatkit.playonyt(song)
    else:
        speak("Sorry, I could not find the song name.")


def search_wikipedia(query: str) -> None:
    try:
        speak("Searching Wikipedia...")
        result = wikipedia.summary(query, sentences=4)
        speak(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("Multiple results found. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("I could not find anything on Wikipedia.")
    except Exception:
        speak("I could not find anything on Wikipedia.")


def open_site(query: str) -> bool:
    for phrase, url in URL_COMMANDS.items():
        if phrase in query:
            wb.open(url)
            time.sleep(LISTEN_COOLDOWN)
            return True
    return False


def handle_query(query: str) -> bool:
    """Process a voice command. Returns False when the assistant should exit."""
    if "time" in query:
        tell_time()
    elif "date" in query:
        date()
    elif "wikipedia" in query:
        search_wikipedia(query.replace("wikipedia", "").strip())
    elif "play" in query:
        play_song()
    elif open_site(query):
        pass
    elif "screenshot" in query:
        screenshot()
    elif "tell me a joke" in query:
        speak(pyjokes.get_joke())
    elif "shutdown" in query:
        speak("Shutting down the system, sir.")
        os.system("shutdown /s /f /t 1")
        return False
    elif "restart" in query:
        speak("Restarting the system, sir.")
        os.system("shutdown /r /f /t 1")
        return False
    elif "offline" in query or "exit" in query:
        speak("Going offline. Have a good day!")
        return False

    return True


if __name__ == "__main__":
    init_microphone()
    wishme()
    while True:
        command = takecmd()
        if command and not handle_query(command):
            break
