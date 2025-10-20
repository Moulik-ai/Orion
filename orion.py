import pyttsx3 #pip install pyttsx3
import speech_recognition as sr #pip install speechRecognition
import datetime
import os
import wikipedia 
import webbrowser
import urllib.parse
import smtplib



def speak(text):
    """
    Robust speak: try pyttsx3 first (lazy init each call), then win32com SAPI fallback.
    Prints debug info and exceptions so we see why sound may be missing.
    """
    import sys, traceback, os, time
    t = str(text)

    print("[TTS DEBUG] speak() called. sys.executable:", sys.executable)
    print("[TTS DEBUG] ORION_TTS_BACKEND:", os.getenv("ORION_TTS_BACKEND"))

    backend_pref = os.getenv("ORION_TTS_BACKEND")
    tried = []

    def try_pyttsx3():
        try:
            import pyttsx3
        except Exception as e:
            print("[TTS DEBUG] pyttsx3 import failed:", e)
            return False
        try:
            # create engine fresh each call to avoid stale state
            engine = pyttsx3.init("sapi5")
            # try to set a voice safely
            try:
                voices = engine.getProperty("voices")
                if voices:
                    engine.setProperty("voice", voices[0].id)
            except Exception:
                pass
            print("[TTS DEBUG] pyttsx3 engine created, calling say/runAndWait()")
            engine.say(t)
            engine.runAndWait()
            # small pause to ensure underlying driver finishes
            time.sleep(0.05)
            print("[TTS DEBUG] pyttsx3 runAndWait completed")
            return True
        except Exception as e:
            print("[TTS DEBUG] pyttsx3 speak failed:", type(e).__name__, e)
            traceback.print_exc()
            return False

    def try_com():
        if os.name != "nt":
            print("[TTS DEBUG] COM SAPI not available on non-Windows")
            return False
        try:
            import win32com.client
        except Exception as e:
            print("[TTS DEBUG] win32com import failed:", e)
            return False
        try:
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            print("[TTS DEBUG] win32com SAPI dispatch ok, calling Speak()")
            sapi.Speak(t)
            print("[TTS DEBUG] win32com Speak returned")
            return True
        except Exception as e:
            print("[TTS DEBUG] win32com Speak failed:", type(e).__name__, e)
            traceback.print_exc()
            return False

    # Determine order
    order = []
    if backend_pref == "com":
        order = ["com", "pyttsx3"]
    elif backend_pref == "pyttsx3":
        order = ["pyttsx3", "com"]
    else:
        order = ["pyttsx3", "com"]

    for b in order:
        tried.append(b)
        ok = False
        if b == "pyttsx3":
            ok = try_pyttsx3()
        else:
            ok = try_com()
        if ok:
            return

    print("[TTS DEBUG] all backends failed (tried:", tried, ") — printing text fallback:")
    print(t)

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")

    else:
        speak("Good Evening!")

    speak("I am Orion. How can I help you today")       

# Replace existing takeCommand() and the main block with this:

def takeCommand(timeout=6, phrase_time_limit=8):
    """
    Returns recognized text (string) or None on failure.
    Uses ambient-noise adjustment and timeouts so it won't hang forever.
    """
    if sr is None:
        print("SpeechRecognition not installed; falling back to typed input.")
        try:
            return input("Type your command: ").strip() or None
        except (EOFError, KeyboardInterrupt):
            return None

    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise (0.6s)...")
            try:
                r.adjust_for_ambient_noise(source, duration=0.6)
            except Exception:
                pass
            print("Listening...")
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        print("Listening timed out (no speech detected).")
        return None
    except Exception as e:
        # Typical causes: PyAudio missing, permission denied, no device, etc.
        print("Could not open microphone or listen:", e)
        # fallback to typed input so program remains usable
        try:
            return input("Type your command instead: ").strip() or None
        except (EOFError, KeyboardInterrupt):
            return None

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        return query
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print("Recognition request failed (check internet):", e)
        return None
    except Exception as e:
        print("Recognition error:", e)
        return None


if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand()
        if query is None:
            # nothing recognized or microphone unavailable; retry
            continue

        query = query.lower().strip()
        # allow typed or spoken exit
        if query in ("exit", "quit", "stop"):
            speak("Goodbye!")
            break

        if 'wikipedia' in query:
            speak("Searching Wikipedia...")
            # remove the keyword and strip whitespace
            search_term = query.replace("wikipedia", "").strip()
            if not search_term:
                speak("What should I search on Wikipedia?")
                continue

            try:
                # call may raise network/request exceptions or wikipedia-specific exceptions
                results = wikipedia.summary(search_term, sentences=2)
            except Exception as e:
                # handle common wikipedia exceptions and network issues
                # import optional exceptions at runtime to avoid hard import dependency problems
                try:
                    from wikipedia import exceptions as wiki_ex
                except Exception:
                    wiki_ex = None

                if wiki_ex and isinstance(e, getattr(wiki_ex, "DisambiguationError", Exception)):
                    speak("Your query is ambiguous. Please be more specific.")
                    print("Disambiguation options (sample):", getattr(e, "options", [])[:6])
                elif wiki_ex and isinstance(e, getattr(wiki_ex, "PageError", Exception)):
                    speak("I couldn't find a Wikipedia page for that.")
                else:
                    print("Wikipedia / network error:", e)
                    speak("I couldn't reach Wikipedia. Please check your internet connection and try again.")
                continue

            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")

        elif 'open google' in query:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")

        elif 'open stackoverflow' in query:
            speak("Opening Stack Overflow")
            webbrowser.open("https://stackoverflow.com")

        elif 'play music' in query:
            search_term = query.replace('play music', '').strip()
            if not search_term:
                speak("Which song should I play?")
                continue


            speak(f"Opening Spotify search for {search_term}")

             # open the Spotify web search (this will normally open the desktop app if protocol registered)
            url = "https://open.spotify.com/search/" + urllib.parse.quote(search_term)

            webbrowser.open(url)
        elif 'open code' in query:
            codePath = "C:\\Users\\chaud\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            os.startfile(codePath)

        elif 'open google' in query:
            speak("Opening Google")
            webbrowser.open("https://www.google.com")
        
        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, it's currently {strTime}")

        elif 'open photos' in query:
            photospath = "C:\\Users\\chaud\\OneDrive\\Pictures"
            os.startfile(photospath)

        elif 'open github' in query:
            speak("Opening GitHub")
            webbrowser.open("https://github.com")
  
        elif 'email to moulik' in query:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "chaudharymoulik1@gmail.com"    
                sendEmail(to, content)
                speak("Email has been sent!")
            except Exception as e:
                print(e)
                speak("Sorry, I am not able to send this email")

        else:
            # Fallback: echo what was said
            print("You said:", query)
            speak(f"You said: {query}")