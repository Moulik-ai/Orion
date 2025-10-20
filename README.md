# Orion

Orion is an AI-based virtual voice assistant that automates common tasks on your device. It listens for voice commands (and falls back to typed input if needed), performs actions such as opening websites and applications, playing music, and reading short Wikipedia summaries, and responds with audible speech.

---

## Overview of orion.py

orion.py is the main script for the Orion assistant. It provides:

- A robust text-to-speech (TTS) interface (`speak()`).
- A greeting routine (`wishMe()`).
- Speech recognition input handling with sensible timeouts and fallbacks (`takeCommand()`).
- A simple command dispatcher implemented in the script's main loop that maps recognized phrases to actions (open websites, play music via Spotify, open apps/folders, and a simple email flow).

The script is defensive: it prints helpful debug messages and falls back to typed input if audio components are not available.

---

## Main components and functions

### speak(text)
- Purpose: Convert text to audible speech.
- Backends:
  - Primary attempt: `pyttsx3` (initialized with the `"sapi5"` driver on Windows when available).
  - Fallback: Windows COM SAPI via `win32com.client.Dispatch("SAPI.SpVoice")` (Windows-only).
- Behavior:
  - Honors the `ORION_TTS_BACKEND` environment variable if set to `"pyttsx3"` or `"com"` to prefer one backend.
  - Prints detailed debug messages and exception traces to help diagnose audio/TTS issues.
  - If no backend works, it prints the spoken text to stdout as a last resort.

### wishMe()
- Speaks a time-appropriate greeting based on the current hour:
  - "Good Morning!" / "Good Afternoon!" / "Good Evening!"
  - Followed by "I am Orion. How can I help you today"

### takeCommand(timeout=6, phrase_time_limit=8)
- Purpose: Records audio from the default microphone and returns recognized text or `None`.
- Uses the `SpeechRecognition` package and Google Web Speech API (`recognize_google()` with language `'en-in'`).
- Ambient-noise adjustment: `adjust_for_ambient_noise(source, duration=0.6)`.
- Timeouts: `timeout` and `phrase_time_limit` prevent indefinite blocking.
- Fallbacks:
  - If microphone access fails (PyAudio missing, permission denied, no device), function prompts the user to type the command.
  - If `SpeechRecognition` is not installed or another error occurs, also falls back to typed input.
- Returns the recognized string, or `None` when nothing was recognized or on error.

### Main loop (if __name__ == "__main__")
- Steps:
  1. Call `wishMe()` to greet the user.
  2. Enter an infinite loop calling `takeCommand()` to get voice (or typed) input.
  3. Normalize the command (`.lower().strip()`).
  4. Handle exit phrases: `"exit"`, `"quit"`, `"stop"` — speak a goodbye message and break the loop.
  5. Match phrases and perform actions.

Supported commands (substring matching):
- `wikipedia <term>` — Retrieves a 2-sentence summary from Wikipedia and reads it aloud. Handles disambiguation and page-not-found errors with helpful messages.
- `open youtube` — Opens https://www.youtube.com.
- `open google` — Opens https://www.google.com.
- `open stackoverflow` — Opens https://stackoverflow.com.
- `play music <song/artist>` — Opens Spotify web search for the query (`https://open.spotify.com/search/<query>`).
- `open code` — Attempts to launch VS Code using a hardcoded path (note: path is user-specific and will need updating).
- `the time` — Reads the current local time in HH:MM:SS format.
- `open photos` — Opens a hardcoded OneDrive Pictures folder path (user-specific).
- `open github` — Opens https://github.com.
- `email to moulik` — Prompts for email content and attempts to call a `sendEmail()` function with a hardcoded recipient. (See Limitations.)

Fallback:
- If no known command matches, Orion echoes the recognized text using `speak()`.

---

## Dependencies

Install these to run orion.py:

- pyttsx3
- SpeechRecognition
- wikipedia
- PyAudio (for microphone access on many systems)
- pywin32 (Windows only, for COM SAPI fallback)

A `requirements.txt` is included in this PR to make installation easier.

---

## How to run

1. Create and activate a virtual environment (or use the provided `setup.sh` script to create one):
   - Unix/macOS:
     - python3 -m venv venv
     - source venv/bin/activate
   - Windows (PowerShell):
     - python -m venv venv
     - .\venv\Scripts\Activate.ps1

2. Install dependencies:
   - pip install -r requirements.txt

3. Run Orion:
   - python orion.py

Note: On many systems installing PyAudio may require additional OS packages (PortAudio). See the `setup.sh` script included for guidance.

---

## Limitations & Known Issues

- Platform-specific features:
  - COM SAPI fallback (`win32com`) works only on Windows.
  - Several file/application paths are hardcoded for a specific Windows user (e.g., VS Code path, OneDrive Pictures). These must be made configurable for other users.
- Missing implementation:
  - `sendEmail()` is referenced but not defined in orion.py. Attempting the `email to moulik` command will raise a `NameError` unless `sendEmail()` is implemented or imported.
- Redundancy:
  - There is a duplicated `open google` branch in the code — safe but redundant.
- Network/Permissions:
  - Speech recognition uses the Google Web Speech API; network connectivity is required and heavy use may require an API key or an alternative recognizer.
- Security:
  - Do not hardcode credentials (for email or other services). Use environment variables or secure secrets.

---

## Suggested Improvements

- Replace hardcoded paths with configuration (environment variables or a config file).
- Implement a secure `sendEmail()` using environment variables or OAuth; do not include credentials in the repository.
- Refactor command handling into a modular dispatcher to make it easier to add commands and test behavior.
- Add proper logging with Python's `logging` module instead of `print()`.
- Provide a `requirements.txt` and the included `setup.sh` to simplify environment setup.
- Consider offline recognition/backends for privacy and resilience (pocketsphinx, VOSK, etc).

---

## Conceptual Example: secure sendEmail() (DO NOT HARD-CODE CREDENTIALS)

```python
import os
import smtplib
from email.message import EmailMessage

def sendEmail(to_email, subject, body):
    smtp_server = os.environ.get("ORION_SMTP_SERVER")
    smtp_port = int(os.environ.get("ORION_SMTP_PORT", "587"))
    smtp_user = os.environ.get("ORION_SMTP_USER")
    smtp_pass = os.environ.get("ORION_SMTP_PASS")

    if not smtp_server or not smtp_user or not smtp_pass:
        raise RuntimeError("SMTP credentials not configured in environment")

    msg = EmailMessage()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)
```

Set the environment variables in your shell (example):
- ORION_SMTP_SERVER, ORION_SMTP_PORT, ORION_SMTP_USER, ORION_SMTP_PASS

---

## Recommended next steps (what this PR adds)
- Replace `README.md` with detailed summary and instructions.
- Add `requirements.txt` with dependencies.
- Add `setup.sh` to create a virtual environment and install dependencies.

---

## License & Contributing
There is currently an MIT license placeholder. If you plan to accept contributions, add a LICENSE file and CONTRIBUTING.md with guidelines.

Thank you for using Orion — contributions welcome!
