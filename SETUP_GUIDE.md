# Quick Setup Guide

Follow these steps to get the automated reel generation working:

## 1. Install Python

Download and install Python 3.9 or higher from [python.org](https://www.python.org/downloads/)

During installation, **check the box "Add Python to PATH"**

## 2. Setup Virtual Environment

Open Command Prompt in the `reel-automation` folder and run:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

You should see `(venv)` in your command prompt.

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- OpenAI Whisper (for transcription)
- OpenAI Python SDK (for GPT-4)
- Anthropic Python SDK (for Claude)
- Other required packages

## 4. Get API Keys

### Option A: OpenAI (Recommended)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-...`)

### Option B: Anthropic (Claude)

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)

## 5. Configure the Application

1. Copy the example configuration:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in a text editor (Notepad, VS Code, etc.)

3. Add your API key:

   **For OpenAI:**
   ```env
   AI_PROVIDER=openai
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   ```

   **For Anthropic:**
   ```env
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here
   ```

4. Save the file

## 6. Install FFmpeg

### Option A: Add to PATH (Recommended)

1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the ZIP file
3. Add the `bin` folder to your system PATH
4. Restart Command Prompt

### Option B: Place in Project Folder

1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and copy `ffmpeg.exe` to the `reel-automation` folder

## 7. Install CapCut

Download and install CapCut from [capcut.com](https://www.capcut.com)

The default installation location works automatically.

## 8. Test the Setup

Activate the virtual environment (if not already):

**Windows Command Prompt:**
```cmd
venv\Scripts\activate
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**WSL / Linux / Mac:**
```bash
source venv/bin/activate
```

Launch the GUI:

```bash
python gui.py
```

If you see the GUI window with no error messages, you're all set!

## 9. Process Your First Video

1. Click "Browse..." and select a video file
2. Click "Process Video"
3. Wait for the pipeline to complete
4. CapCut will open with your reels ready!

## Troubleshooting

### "python is not recognized"

- Reinstall Python and check "Add to PATH"
- Or use the full path: `C:\Python39\python.exe`

### "pip is not recognized"

- Run: `python -m pip install -r requirements.txt`

### "OPENAI_API_KEY is required"

- Make sure you created the `.env` file (not `.env.example`)
- Make sure you added your actual API key
- No spaces around the `=` sign

### GUI doesn't open

- Make sure virtual environment is activated: `venv\Scripts\activate`
- Try: `python -m gui`

### FFmpeg errors

- Verify FFmpeg is installed: `ffmpeg -version`
- If not found, follow step 6 again

## Common Commands

**Activate virtual environment:**
```bash
venv\Scripts\activate
```

**Deactivate virtual environment:**
```bash
deactivate
```

**Launch GUI:**
```bash
python gui.py
```

**Command line mode:**
```bash
python pipeline.py "path\to\video.mp4"
```

## Next Steps

Once everything is working:

1. Process a test video (10-20 minutes long works well)
2. Review the generated reels in CapCut
3. Export and post to social media!
4. Share with your team

## Need Help?

Check these files for more information:
- `README.md` - Full documentation
- `.env.example` - All configuration options
- GUI log output - Shows detailed error messages

---

Happy reel creating! 🎬
