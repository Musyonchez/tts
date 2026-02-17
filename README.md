# Web Novel TTS Reader

Reads web novel chapters aloud using Windows built-in voices (SAPI via pyttsx3).
Automatically advances to the next chapter when done.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
# Start from chapter 1 (default)
venv\Scripts\python.exe read_novel.py

# Start from a specific chapter
venv\Scripts\python.exe read_novel.py https://freewebnovel.com/novel/beast-taming-abyssal-descent/chapter-5
```

## Customise voice / speed

Edit the settings near the top of `main()` in `read_novel.py`:

```python
engine.setProperty("voice", voices[1].id)  # 0 = David, 1 = Zira
engine.setProperty("rate", 175)            # words per minute
engine.setProperty("volume", 1.0)          # 0.0 – 1.0
```

List available voices:

```bash
venv\Scripts\python.exe -c "import pyttsx3; e=pyttsx3.init(); [print(i, v.name) for i,v in enumerate(e.getProperty('voices'))]"
```
