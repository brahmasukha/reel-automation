# CapCut Reels Automation - Windows Setup

## Prerequisites

### 1. Install Python
1. Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation

### 2. Install FFmpeg
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH:
   - Search "Environment Variables" in Windows
   - Edit "Path" variable
   - Add new entry: `C:\ffmpeg\bin`

### 3. Install Whisper
Open Command Prompt and run:
```
pip install openai-whisper
```

## Installation

1. Create a folder: `C:\CapCutAutomation`
2. Copy all these files into it:
   - `automate_cuts.py`
   - `transcribe.py`
   - `tool_apply_cuts.py`
   - `AI_Prompt.md`
   - `cuts.txt`
   - `Get_Transcript.bat`
   - `Apply_Cuts.bat`

## Usage

### Step 1: Get Transcript
1. Double-click `Get_Transcript.bat`
2. Drag your video file into the window and press Enter
3. Wait for transcript to open

### Step 2: Get Timestamps from AI
1. Open `AI_Prompt.md`
2. Copy the prompt + your transcript into ChatGPT
3. Copy the timestamps into `cuts.txt`

### Step 3: Apply Cuts
1. Open CapCut and create a new project with your video
2. Close CapCut to save
3. Double-click `Apply_Cuts.bat`
4. Reopen CapCut to see the result!

## CapCut Project Location (Windows)
Your friend's projects will be in:
`C:\Users\[USERNAME]\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft\`
