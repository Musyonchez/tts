# Web Novel TTS Reader

Reads web novel chapters aloud using Windows built-in voices (SAPI).

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## freewebnovel.py — auto-fetch & read

Fetches chapters directly from freewebnovel.com (no Cloudflare) and auto-advances.

```bash
# Start from a default chapter
venv\Scripts\python.exe sites\freewebnovel.py

# Start from a specific chapter
venv\Scripts\python.exe sites\freewebnovel.py https://freewebnovel.com/novel/beast-taming-abyssal-descent/chapter-5
```

---

## fictionzone/ — extension + collect + read

fictionzone.net is Cloudflare-protected, so content is saved via a browser extension.

### Workflow

**1. Save chapters in browser**

Load the Brave extension from `fictionzone/extension/` (developer mode).
On any chapter page, click **"💾 Save for TTS"** — saves a JSON file to:
```
Downloads\fictionzone-tts\
```
> Tip: turn off *"Ask where to save each file before downloading"* in `brave://settings/downloads` while batch-saving, then turn it back on.

**2. Collect into content folder**

```bash
venv\Scripts\python.exe fictionzone\collect.py
```

Moves JSONs to `fictionzone\content\<novel>\chapter-XXXX.txt` and archives originals to `Downloads\fictionzone-tts\processed\`.

**3. Generate run commands**

```bash
venv\Scripts\python.exe fictionzone\list_commands.py
```

Writes ready-to-run commands to `fictionzone\commands\<novel>.txt`.

**4. Read chapters aloud**

```bash
# Read whole novel from chapter 1
venv\Scripts\python.exe fictionzone\fictionzone.py fictionzone\content\<novel>

# Start from a specific chapter
venv\Scripts\python.exe fictionzone\fictionzone.py fictionzone\content\<novel>\chapter-0005.txt
```

---

## Customise voice / speed

All scripts use win32com SAPI. Edit the `RATE` and `VOLUME` variables (or in `main()` for sites scripts):

```python
RATE = 6      # -10 (slowest) to 10 (fastest), 0 ≈ 180 wpm
VOLUME = 100  # 0–100
```
