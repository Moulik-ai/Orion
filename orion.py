# ==============================================================================
# 1. IMPORTS
# ==============================================================================
import os
import smtplib
import sys
import time
import datetime
import webbrowser
import urllib.parse
import traceback

# Third-party libraries (ensure you have installed them: pip install ...)
import pyttsx3
import requests
import speech_recognition as sr
import wikipedia
from bs4 import BeautifulSoup

# Optional, for SAPI fallback on Windows
if os.name == "nt":
    try:
        import win32com.client
    except ImportError:
        win32com = None
else:
    win32com = None

# ==============================================================================
# 2. CONFIGURATION
# ==============================================================================
# --- Voice Assistant Settings ---
WAKE_WORD = "orion"
ASSISTANT_NAME = "Orion"

# --- Email Settings ---
# WARNING: Storing your email and password directly in the code is not secure.
# It's better to use environment variables or a more secure authentication method.
EMAIL_ADDRESS = "chaudharymoulik1@gmail.com"
EMAIL_PASSWORD = "jlao cbzy bnsq bcbg"

# --- File Paths (Update these to match your system) ---
VS_CODE_PATH = "C:\\Users\\chaud\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
PHOTOS_PATH = "C:\\Users\\chaud\\OneDrive\\Pictures"

# ==============================================================================
# 3. CORE FUNCTIONS (Speak, Listen, etc.)
# ==============================================================================

def speak(text):
    """
    Robust text-to-speech function that tries pyttsx3 first,
    with a fallback to Windows SAPI if available.
    """
    print(f"[{ASSISTANT_NAME}]: {text}")
    try:
        engine = pyttsx3.init("sapi5")
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.05) # Small pause to ensure the driver finishes
    except Exception as e_pyttsx3:
        print(f"[TTS DEBUG] pyttsx3 failed: {e_pyttsx3}")
        # Fallback for Windows if pyttsx3 fails
        if os.name == "nt" and win32com:
            try:
                sapi = win32com.client.Dispatch("SAPI.SpVoice")
                sapi.Speak(text)
            except Exception as e_sapi:
                print(f"[TTS DEBUG] SAPI fallback also failed: {e_sapi}")

def listen_for_wake_word():
    """Passively listens for the wake word and returns True if detected."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"\nListening for wake word '{WAKE_WORD}'...")
        # Note: adjust_for_ambient_noise is not used here for faster, continuous listening.
        audio = r.listen(source)
        try:
            query = r.recognize_google(audio, language='en-in')
            # print(f"Heard: {query}") # Uncomment for debugging
            return WAKE_WORD in query.lower()
        except (sr.UnknownValueError, sr.RequestError):
            # Handles silence, background noise, or connection issues
            return False

def takeCommand():
    """
    Actively listens for a command after the wake word is detected.
    Returns the recognized command as a string or None on failure.
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        speak("How can I help?")
        print("Listening for a command...")
        # Adjust for ambient noise to improve recognition accuracy
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Set timeouts to prevent it from hanging indefinitely
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Please try again.")
            return None

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        return query.lower().strip()
    except sr.UnknownValueError:
        speak("Sorry, I could not understand that. Please say it again.")
        return None
    except sr.RequestError:
        speak("Sorry, my speech service is down. Please check your internet connection.")
        return None

# ==============================================================================
# 4. TASK-SPECIFIC FUNCTIONS (Email, Search, etc.)
# ==============================================================================

def wishMe():
    """Greets the user based on the time of day."""
    hour = datetime.datetime.now().hour
    greeting = ""
    if 0 <= hour < 12:
        greeting = "Good Morning!"
    elif 12 <= hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"

    speak(f"{greeting} I am {ASSISTANT_NAME}. How can I help you today?")

def sendEmail(to, content):
    """Sends an email using the configured Gmail account."""
    try:
        # Establish a secure connection with the Gmail server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        # Login to your email account
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        # Send the email
        server.sendmail(EMAIL_ADDRESS, to, content)
        server.quit()
        return True
    except Exception as e:
        print(f"[EMAIL ERROR]: {e}")
        traceback.print_exc()
        return False

def answer_query(query):
    """Searches Google and scrapes for a direct answer (featured snippet)."""
    speak(f"Searching for {query}...")
    try:
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, headers=headers)
        res.raise_for_status() # Raise an exception for bad status codes (like 404)

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Selectors for Google's featured snippets and knowledge panels
        answer_selectors = [
            "div.BNeawe.iBp4i.AP7Wnd",
            "div.BNeawe.s3v9rd.AP7Wnd",
            "div.kno-rdesc span",
        ]

        for selector in answer_selectors:
            answer_element = soup.select_one(selector)
            if answer_element:
                return answer_element.get_text()
        
        return None # Return None if no snippet is found
    except Exception as e:
        print(f"[WEB SEARCH ERROR]: {e}")
        return None

# ==============================================================================
# 5. MAIN EXECUTION LOOP
# ==============================================================================
if __name__ == "__main__":
    wishMe()
    while True:
        # 1. Passively wait for the wake word
        if listen_for_wake_word():
            # 2. Actively listen for a command
            query = takeCommand()

            if query is None:
                continue # If no command heard, go back to listening for wake word

            # ----------------- COMMAND PROCESSING LOGIC -----------------
            # Prioritize commands for faster response time.
            # Local/quick commands first, network/slow commands last.

            # --- Quick, Local Commands ---
            if 'the time' in query:
                strTime = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"Sir, the time is {strTime}")

            elif 'open code' in query or 'open visual studio' in query:
                try:
                    os.startfile(VS_CODE_PATH)
                    speak("Opening Visual Studio Code.")
                except Exception:
                    speak("Sorry, I could not find Visual Studio Code at the specified path.")

            elif 'open photos' in query:
                try:
                    os.startfile(PHOTOS_PATH)
                    speak("Opening your pictures folder.")
                except Exception:
                    speak("Sorry, I could not find your pictures folder.")

            # --- Web Browser Commands ---
            elif 'open youtube' in query:
                speak("Opening YouTube")
                webbrowser.open("https://www.youtube.com")

            elif 'open google' in query:
                speak("Opening Google")
                webbrowser.open("https://www.google.com")

            elif 'open stack overflow' in query:
                speak("Opening Stack Overflow")
                webbrowser.open("https://stackoverflow.com")

            elif 'open github' in query:
                speak("Opening GitHub")
                webbrowser.open("https://github.com")

            # --- Music Search ---
            elif 'play' in query:
                search_term = query.replace('play', '').strip()
                if search_term:
                    speak(f"Playing {search_term} on YouTube")
                    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_term)}"
                    webbrowser.open(url)
                else:
                    speak("Which song or artist should I play?")

            # --- Wikipedia Search ---
            elif 'wikipedia' in query:
                speak("Searching Wikipedia...")
                search_term = query.replace("wikipedia", "").strip()
                if not search_term:
                    speak("What should I search on Wikipedia?")
                    continue
                try:
                    # Fetching 2 sentences from the summary
                    results = wikipedia.summary(search_term, sentences=2)
                    speak("According to Wikipedia...")
                    speak(results)
                except wikipedia.exceptions.PageError:
                    speak(f"Sorry, I couldn't find a Wikipedia page for {search_term}.")
                except wikipedia.exceptions.DisambiguationError:
                     speak(f"{search_term} is ambiguous. Please be more specific.")
                except Exception as e:
                    print(f"[WIKIPEDIA ERROR]: {e}")
                    speak("Sorry, an error occurred while searching Wikipedia.")

            # --- Email Commands ---
            elif 'email to papa' in query or 'email to father' in query:
                speak("What should I say in the email?")
                content = takeCommand()
                if content:
                    to = "naveengadhwal23@gmail.com"
                    if sendEmail(to, content):
                        speak("Email has been sent to Papa!")
                    else:
                        speak("Sorry, I was unable to send the email.")
                else:
                    speak("Message not clear. Email cancelled.")
            
            elif 'email' in query:
                speak("What should I say in the email?")
                content = takeCommand()
                if content:
                    to = "chaudharymoulik1@gmail.com" # Default email
                    if sendEmail(to, content):
                        speak("Email has been sent!")
                    else:
                        speak("Sorry, I was unable to send the email.")
                else:
                    speak("Message not clear. Email cancelled.")

            elif 'tell me about yourself' in query or 'who are you' in query:
                speak(f"I am {ASSISTANT_NAME}, your personal assistant. I can help you with various tasks like searching the web, sending emails, opening applications, and more.")

            elif 'tell me about' in query or 'who is' in query or 'what is' in query or 'search for' in query:
                search_term = query.replace("tell me about", "").replace("who is", "").replace("what is", "").replace("search for", "").strip()
                if search_term:
                    speak(f"Searching for {search_term}...")
                    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(search_term)}")
                else:
                    speak("What should I search for?")

            # --- Exit Command ---
            elif query in ("exit", "quit", "stop", "goodbye", "turn off"):
                speak("Goodbye!")
                break

            # --- Fallback: General Question Answering ---
            else:
                direct_answer = answer_query(query)
                if direct_answer:
                    speak(direct_answer)
                else:
                    speak(f"I couldn't find a direct answer. Here are the Google search results for {query}.")
                    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")