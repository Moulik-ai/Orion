# Orion

## Project Description
Orion is an AI-based virtual voice assistant that can automate your device through voice commands. It uses text-to-speech (TTS) and speech recognition to interact with users, allowing them to search Wikipedia, open websites, play music, check the time, and perform various system operations hands-free.

## Detailed Summary of orion.py

### Main Components

The `orion.py` script consists of four primary components:

1. **speak(text)** - Text-to-speech output function
2. **wishMe()** - Greeting function based on time of day
3. **takeCommand()** - Speech recognition input function
4. **Main loop** - Command processing and execution

### Function Descriptions

#### speak(text)
The `speak()` function converts text to speech with robust fallback handling:

**Behavior:**
- Attempts to use `pyttsx3` library first with SAPI5 driver (lazy initialization on each call)
- Falls back to `win32com.client` SAPI dispatch on Windows if pyttsx3 fails
- Backend preference can be controlled via `ORION_TTS_BACKEND` environment variable (`"pyttsx3"` or `"com"`)
- Includes comprehensive debug logging to diagnose audio issues
- Prints text to console as final fallback if all TTS backends fail

**Cross-platform notes:**
- `pyttsx3` works on Linux, macOS, and Windows
- `win32com` fallback is Windows-only

#### wishMe()
Greets the user based on the current time:
- **Morning (0:00-11:59):** "Good Morning!"
- **Afternoon (12:00-17:59):** "Good Afternoon!"
- **Evening (18:00-23:59):** "Good Evening!"
- Follows up with: "I am Orion. How can I help you today"

#### takeCommand(timeout=6, phrase_time_limit=8)
Captures voice input from the user's microphone using Google's speech recognition API.

**Behavior:**
- Adjusts for ambient noise (0.6 seconds)
- Listens for speech with configurable timeout
- Uses `speech_recognition` library with Google Speech API
- Returns recognized text as a string or `None` on failure

**Fallback handling:**
- If `SpeechRecognition` is not installed → prompts for typed input
- If microphone fails or times out → prompts for typed input
- If speech is unclear → returns `None`
- If internet/API request fails → returns `None`

### Main Loop

The main execution loop runs indefinitely until the user says "exit", "quit", or "stop".

**Command flow:**
1. Calls `wishMe()` on startup
2. Continuously calls `takeCommand()` to listen for commands
3. Converts command to lowercase and strips whitespace
4. Matches command patterns and executes corresponding actions

### Supported Commands

| Command Pattern | Action |
|----------------|---------|
| `"wikipedia [search term]"` | Searches Wikipedia and speaks a 2-sentence summary |
| `"open youtube"` | Opens YouTube in default browser |
| `"open google"` | Opens Google in default browser |
| `"open stackoverflow"` | Opens Stack Overflow in default browser |
| `"open github"` | Opens GitHub in default browser |
| `"play music [song name]"` | Opens Spotify search for the specified song |
| `"open code"` | Opens VS Code (hardcoded path - see Limitations) |
| `"the time"` | Speaks the current time in HH:MM:SS format |
| `"open photos"` | Opens Photos folder (hardcoded path - see Limitations) |
| `"email to moulik"` | Prompts for email content and sends via `sendEmail()` (see Limitations) |
| `"exit"`, `"quit"`, `"stop"` | Exits the assistant |
| Any other text | Echoes back what was said |

### Examples

```
User: "Wikipedia artificial intelligence"
Orion: "Searching Wikipedia... According to Wikipedia, [2-sentence summary]"

User: "Open YouTube"
Orion: "Opening YouTube" [Opens browser]

User: "Play music Bohemian Rhapsody"
Orion: "Opening Spotify search for Bohemian Rhapsody" [Opens Spotify]

User: "What's the time?"
Orion: "Sir, it's currently 14:32:45"

User: "Exit"
Orion: "Goodbye!" [Program terminates]
```

## Dependencies

Orion requires the following Python packages:

- **pyttsx3** - Text-to-speech conversion
- **SpeechRecognition** - Speech-to-text conversion via Google API
- **wikipedia** - Wikipedia API wrapper for searching articles
- **PyAudio** - Audio I/O for microphone access (required by SpeechRecognition)
- **pywin32** - Windows COM API access (Windows only, for SAPI fallback)

### Installation

Install dependencies using pip:

```bash
pip install pyttsx3 SpeechRecognition wikipedia pyaudio pywin32
```

Or use the provided `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Platform-specific notes:**
- **Windows:** PyAudio and pywin32 should install via pip
- **Linux:** May need to install PortAudio first: `sudo apt-get install portaudio19-dev python3-pyaudio`
- **macOS:** May need to install PortAudio via Homebrew: `brew install portaudio`

## How to Run the Assistant

1. **Install dependencies** (see above)
2. **Run the script:**
   ```bash
   python orion.py
   ```
3. **Wait for greeting** - Orion will greet you based on the time of day
4. **Speak your commands** or type them if microphone is unavailable
5. **Exit** by saying "exit", "quit", or "stop"

### Optional: Use the setup script

A cross-platform setup script is provided to automate environment setup:

```bash
# On Linux/macOS
bash setup.sh

# Then activate the virtual environment
source venv/bin/activate

# Run Orion
python orion.py
```

See `setup.sh` for Windows-specific instructions.

## Limitations and Known Issues

### 1. Hardcoded File Paths
- **VS Code path:** `C:\\Users\\chaud\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe`
- **Photos folder:** `C:\\Users\\chaud\\OneDrive\\Pictures`
- **Impact:** "open code" and "open photos" commands only work on the developer's machine
- **Fix needed:** Use environment variables or cross-platform path detection

### 2. Missing sendEmail() Function
- The `sendEmail()` function is **called but not defined** in the code
- **Impact:** "email to moulik" command will fail with `NameError`
- **Fix needed:** Implement the function (see Suggested Improvements below)

### 3. Duplicate Command Branch
- Line 237-239 contains a duplicate `'open google'` condition (already handled at line 212-214)
- **Impact:** Redundant code, second branch never executes
- **Fix needed:** Remove duplicate or repurpose for different URL

### 4. Platform-Specific Features
- `os.startfile()` is Windows-only (used for "open code" and "open photos")
- **Impact:** Commands will fail on Linux/macOS
- **Fix needed:** Use `subprocess.run(['open', path])` on macOS or `subprocess.run(['xdg-open', path])` on Linux

### 5. Internet Dependency
- Speech recognition requires active internet connection (uses Google API)
- Wikipedia search requires internet
- **Impact:** Commands fail offline (though typed input fallback helps)

### 6. PyAudio Installation Complexity
- PyAudio can be challenging to install on some systems
- **Impact:** Microphone may not work, but typed input fallback is available

## Suggested Improvements

### High Priority
1. **Implement sendEmail() function** - Add proper email sending with security best practices
2. **Remove hardcoded paths** - Use configurable settings or environment variables
3. **Remove duplicate 'open google' branch**
4. **Add cross-platform support** - Use platform-agnostic file opening methods

### Medium Priority
5. **Add configuration file** - Store user preferences, paths, and email settings
6. **Improve error messages** - More user-friendly feedback
7. **Add logging** - File-based logging for debugging
8. **Command aliasing** - Allow users to define custom command phrases

### Low Priority
9. **Add more commands** - Weather, news, calendar integration, etc.
10. **GUI interface** - Visual feedback and control panel
11. **Offline mode** - Pocketsphinx for offline speech recognition
12. **Multi-language support** - Support for languages beyond English

## Recommended Next Steps

1. **Fix critical issues:**
   - Implement `sendEmail()` function (see example below)
   - Remove hardcoded paths or make them configurable
   - Remove duplicate code branches

2. **Improve portability:**
   - Test on Linux and macOS
   - Add platform detection for system commands
   - Update documentation with platform-specific setup instructions

3. **Enhance security:**
   - Never commit credentials to repository
   - Use environment variables or secure credential storage
   - Implement OAuth2 for email if possible

4. **Add testing:**
   - Unit tests for each function
   - Mock tests for speech recognition and TTS
   - Integration tests for command processing

## Secure sendEmail() Implementation Example

Here's a conceptual example of how to implement `sendEmail()` securely using environment variables:

```python
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def sendEmail(to, content):
    """
    Sends email using SMTP with credentials from environment variables.
    
    Required environment variables:
        ORION_EMAIL_ADDRESS - Sender email address
        ORION_EMAIL_PASSWORD - App-specific password (NOT your main password)
        ORION_SMTP_SERVER - SMTP server (default: smtp.gmail.com)
        ORION_SMTP_PORT - SMTP port (default: 587)
    
    Example setup:
        export ORION_EMAIL_ADDRESS="your-email@gmail.com"
        export ORION_EMAIL_PASSWORD="your-app-specific-password"
    
    For Gmail:
        1. Enable 2-factor authentication
        2. Generate app-specific password at:
           https://myaccount.google.com/apppasswords
        3. Use the generated password, NOT your Gmail password
    """
    sender_email = os.getenv("ORION_EMAIL_ADDRESS")
    sender_password = os.getenv("ORION_EMAIL_PASSWORD")
    smtp_server = os.getenv("ORION_SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("ORION_SMTP_PORT", "587"))
    
    if not sender_email or not sender_password:
        raise ValueError(
            "Email credentials not configured. "
            "Please set ORION_EMAIL_ADDRESS and ORION_EMAIL_PASSWORD "
            "environment variables."
        )
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to
    message["Subject"] = "Message from Orion Assistant"
    message.attach(MIMEText(content, "plain"))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
    except Exception as e:
        raise Exception(f"Failed to send email: {str(e)}")
```

**Important:** Never commit passwords or API keys to your repository. Always use environment variables or secure credential storage systems.

---

## License
[License details to be added]

## Contributing
[Contributing guidelines to be added]

---

**Note:** This is a learning project and demonstration of voice assistant capabilities. For production use, additional security hardening, error handling, and testing would be required.
