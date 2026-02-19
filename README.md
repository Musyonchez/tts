# Web Novel TTS Reader

Reads web novel chapters aloud using Windows built-in voices (SAPI via pyttsx3).

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Scripts

### freewebnovel.py — auto-fetch & auto-advance

Fetches chapters directly (no Cloudflare protection on that site) and auto-advances to the next chapter.

```bash
# Start from chapter 1 (default)
venv\Scripts\python.exe freewebnovel.py

# Start from a specific chapter
venv\Scripts\python.exe freewebnovel.py https://freewebnovel.com/novel/beast-taming-abyssal-descent/chapter-5
```

---

### fictionzone/fictionzone.py — paste HTML, save & read

fictionzone.net is Cloudflare-protected, so you copy the page body HTML manually
via a browser extension, then pipe it in.

**Steps:**
1. Open the chapter in your browser
2. Use a browser extension (e.g. *Copy HTML* / *SelectAll + Copy Outer HTML*) to copy the full `<body>` HTML
3. Run one of the commands below

```powershell
# Pipe from clipboard (PowerShell)
Get-Clipboard | venv\Scripts\python.exe fictionzone\fictionzone.py C:\path\to\save

# Or from a saved HTML file
venv\Scripts\python.exe fictionzone\fictionzone.py C:\path\to\save chapter.html
```

Chapters are saved to:
```
<save_dir>\content\<novel-name>\chapter-XXXX.txt
```

---

## Customise voice / speed

Edit the settings in `main()` / `speak()` in the relevant script:

```python
engine.setProperty("voice", voices[1].id)  # 0 = David, 1 = Zira
engine.setProperty("rate", 175)            # words per minute
engine.setProperty("volume", 1.0)          # 0.0 – 1.0
```

List available voices:

```bash
venv\Scripts\python.exe -c "import pyttsx3; e=pyttsx3.init(); [print(i, v.name) for i,v in enumerate(e.getProperty('voices'))]"
```
