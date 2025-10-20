# tts_full_diag.py
import sys, platform, traceback, subprocess, os, time

print("=== ENV ===")
print("sys.executable:", sys.executable)
print("python version:", sys.version.replace("\n"," "))
print("platform:", platform.platform())
print("ORION_TTS_BACKEND:", os.getenv("ORION_TTS_BACKEND"))
print()

def safe(func):
    try:
        func()
    except Exception:
        traceback.print_exc()

print("=== winsound.Beep test (basic audio) ===")
def beep_test():
    if os.name == 'nt':
        import winsound
        print("Calling winsound.Beep(750,200)...")
        winsound.Beep(750, 200)
        print("winsound.Beep returned")
    else:
        print("winsound not available on this OS")

safe(beep_test)
print()

print("=== PowerShell SAPI test (invoke PowerShell) ===")
def pwsh_sapi_test():
    if os.name != 'nt':
        print("PowerShell SAPI test skipped (not Windows)")
        return
    # runs a PowerShell call that uses System.Speech (this will TTS from PowerShell)
    cmd = [
        "powershell", "-NoProfile", "-Command",
        'Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak("PowerShell speech test from Python")'
    ]
    print("Running PowerShell command to speak via System.Speech ...")
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    print("PowerShell exitcode:", p.returncode)
    print("PowerShell stdout:", repr(p.stdout)[:400])
    print("PowerShell stderr:", repr(p.stderr)[:400])

safe(pwsh_sapi_test)
print()

print("=== pyttsx3 test ===")
def pyttsx3_test():
    try:
        import pyttsx3
    except Exception as e:
        print("pyttsx3 import failed:", e)
        raise

    print("pyttsx3 module:", getattr(pyttsx3, "__file__", "<no __file__>"))
    try:
        engine = pyttsx3.init("sapi5")
        print("pyttsx3.init succeeded, engine:", engine)
    except Exception as e:
        print("pyttsx3.init failed:", e)
        raise

    try:
        voices = engine.getProperty("voices")
        print("voices count:", len(voices))
        for i, v in enumerate(voices[:6]):
            print(" voice", i, "->", getattr(v, "id", None))
    except Exception as e:
        print("getProperty voices failed:", e)

    try:
        print("Calling engine.say + runAndWait ...")
        engine.say("Hello from pyttsx3 test.")
        engine.runAndWait()
        print("pyttsx3 runAndWait completed")
    except Exception as e:
        print("pyttsx3 speak failed:", e)
        raise

safe(pyttsx3_test)
print()

print("=== win32com SAPI test (pywin32) ===")
def win32com_test():
    if os.name != 'nt':
        print("win32com test skipped (not Windows)")
        return
    try:
        import win32com.client
    except Exception as e:
        print("win32com import failed:", e)
        raise

    try:
        sapi = win32com.client.Dispatch("SAPI.SpVoice")
        print("win32com SAPI dispatch ok:", sapi)
        sapi.Speak("Hello from win32com S A P I test from Python")
        print("win32com Speak returned")
    except Exception as e:
        print("win32com SAPI speak failed:", e)
        raise

safe(win32com_test)
print()

print("=== End of diagnostics ===")