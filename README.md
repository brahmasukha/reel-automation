# Reel Automation - AI-Powered Video Editing

Automatically transform long-form videos into viral short-form reels using AI. This tool uses Whisper (local) or AI APIs (online) for transcription, GPT-4/Claude/Gemini for intelligent content analysis, and automatically generates CapCut projects with perfectly timed cuts.

## Features

- **Fully Automated Pipeline**: Drop in a video, get reels automatically
- **Flexible Transcription**: Choose local Whisper or fast online AI transcription (Gemini FREE!)
- **AI-Powered Analysis**: Uses GPT-4, Claude, or Gemini to identify compelling narrative segments
- **Professional Editing**: Applies the proven "3-Step Formula" (Hook → Context → Payoff)
- **Zero Manual Editing**: Creates CapCut projects automatically - no manual timeline work
- **User-Friendly GUI**: Simple drag-and-drop interface
- **Works on Low-End Machines**: Online transcription bypasses slow local processing
- **Batch Processing Ready**: Architecture designed for future multi-video processing

## Workflow

```
Input Video → Transcription (Local/Online) → AI Analysis → CapCut Project Generation → Open CapCut
```

The entire process is automated:
1. AI transcribes your video with timestamps (local Whisper OR online AI API)
2. AI analyzes content and identifies viral-worthy segments
3. Automatically creates a CapCut project with cuts applied
4. Opens CapCut with your reels ready to export

**New!** Choose between:
- **Local Transcription**: Use Whisper on your machine (slower, free, offline)
- **Online Transcription**: Use AI APIs for faster transcription (Gemini FREE, OpenAI paid)
  - ⚡ Much faster on low-end machines
  - 🆓 Gemini offers free tier
  - 📖 See [ONLINE_TRANSCRIPTION.md](ONLINE_TRANSCRIPTION.md) for details

## Installation

### Prerequisites

- Python 3.9 or higher
- CapCut installed on Windows
- OpenAI API key OR Anthropic API key
- FFmpeg (will be auto-detected if in PATH or local directory)

### Step 1: Clone or Download

```bash
cd reel-automation
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and add your API keys:

```env
# Choose your AI provider (Gemini is FREE!)
AI_PROVIDER=gemini  # Options: "gemini", "openai", or "anthropic"

# Add your API key
GEMINI_API_KEY=your_gemini_api_key_here  # Get FREE at ai.google.dev
# OR
OPENAI_API_KEY=sk-...your-key-here...
# OR
ANTHROPIC_API_KEY=sk-ant-...your-key-here...

# Model selection (optional)
GEMINI_MODEL=gemini-2.0-flash-exp
OPENAI_MODEL=gpt-4-turbo-preview
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Transcription method (NEW!)
TRANSCRIPTION_METHOD=online  # Options: "local" (Whisper) or "online" (AI API - FASTER!)

# Whisper model (only used if TRANSCRIPTION_METHOD=local)
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
```

**Recommended for low-end machines:**
- Use `TRANSCRIPTION_METHOD=online` for much faster processing
- Use `AI_PROVIDER=gemini` for FREE online transcription
- See [ONLINE_TRANSCRIPTION.md](ONLINE_TRANSCRIPTION.md) for detailed guide

### Step 5: Download FFmpeg (if needed)

If you don't have FFmpeg installed:

1. Download from https://ffmpeg.org/download.html
2. Either:
   - Add to system PATH, OR
   - Place `ffmpeg.exe` in the `reel-automation` folder

## Usage

### GUI Mode (Recommended)

1. Activate virtual environment:
   ```bash
   venv\Scripts\activate
   ```

2. Launch the GUI:
   ```bash
   python gui.py
   ```

3. Click "Browse" to select your video
4. Click "Process Video"
5. Wait for the pipeline to complete
6. CapCut will open with your reels ready!

### Command Line Mode

```bash
venv\Scripts\activate
python pipeline.py "path/to/your/video.mp4"
```

## Configuration Options

Edit `.env` to customize:

| Setting | Description | Default |
|---------|-------------|---------|
| `AI_PROVIDER` | AI service to use | `openai` |
| `OPENAI_API_KEY` | Your OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Your Anthropic API key | - |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4-turbo-preview` |
| `ANTHROPIC_MODEL` | Anthropic model name | `claude-3-5-sonnet-20241022` |
| `WHISPER_MODEL` | Whisper model size | `base` |
| `GAP_BETWEEN_REELS_SECONDS` | Gap between reels on timeline | `10` |
| `MAX_REEL_DURATION` | Maximum reel length | `58` |

## How It Works

### 1. Transcription (Whisper AI)

The video is transcribed using OpenAI's Whisper model with precise timestamps:

```
[00:00:05 -> 00:00:15] Today I want to talk about time management.
[00:00:15 -> 00:00:25] The real problem is how we use our time.
```

### 2. AI Content Analysis

The transcript is sent to GPT-4 or Claude with a specialized prompt that:

- Identifies compelling narrative themes
- Applies the "3-Step Formula" (Hook → Context → Payoff)
- Ensures smooth audio flow between cuts
- Keeps each reel under 58 seconds
- Can re-arrange segments for maximum impact

### 3. CapCut Project Generation

A complete CapCut project is automatically created:

- Project folder with unique ID
- Video file copied to project
- `draft_info.json` generated with all cuts applied
- Multiple reels separated by gaps on timeline

### 4. Launch CapCut

CapCut opens with your project loaded and ready to export!

## Project Structure

```
reel-automation/
├── gui.py                          # GUI application (main entry point)
├── pipeline.py                     # Pipeline orchestrator (can run standalone)
├── config.py                       # Configuration management
├── ai_timestamp_generator.py      # AI integration (OpenAI/Anthropic)
├── capcut_project_generator.py    # CapCut project creation
├── transcribe.py                  # Legacy transcription script
├── automate_cuts.py               # Legacy automation script
├── requirements.txt               # Python dependencies
├── .env                           # Your configuration (create from .env.example)
├── .env.example                   # Configuration template
└── README.md                      # This file
```

## Troubleshooting

### "OPENAI_API_KEY is required"

Make sure you've created a `.env` file and added your API key:

```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here
```

### "CapCut executable not found"

The tool searches these locations:
- `%LOCALAPPDATA%\JianyingPro\Apps\JianyingPro.exe`
- `C:\Program Files\JianyingPro\JianyingPro.exe`
- `C:\Program Files (x86)\JianyingPro\JianyingPro.exe`

If CapCut is installed elsewhere, it will still create the project - you just need to open CapCut manually.

### "FFmpeg not found"

Download FFmpeg and either:
1. Add it to your system PATH
2. Place `ffmpeg.exe` in the `reel-automation` folder

### Whisper Model Size

For faster processing, use `tiny` or `base`:
```env
WHISPER_MODEL=tiny  # Fastest, less accurate
WHISPER_MODEL=base  # Good balance (default)
WHISPER_MODEL=small # Better accuracy, slower
```

## API Costs

### OpenAI (GPT-4 Turbo)
- ~$0.01 - $0.03 per video (depending on transcript length)
- Whisper transcription is free (runs locally)

### Anthropic (Claude 3.5 Sonnet)
- ~$0.01 - $0.03 per video (depending on transcript length)
- Whisper transcription is free (runs locally)

## Future Enhancements

The codebase is designed for future expansion:

- **Batch Processing**: Process multiple videos at once
- **Custom Prompts**: Create your own narrative formulas
- **Export Automation**: Auto-export reels from CapCut
- **Video Hosting**: Auto-upload to social platforms
- **Analytics**: Track which reels perform best

## Tips for Best Results

1. **Video Quality**: Use clear audio - Whisper works best with clean speech
2. **Content Type**: Works best with talking-head videos, interviews, podcasts
3. **Video Length**: 10-60 minute videos work well
4. **Review Before Posting**: Always review the generated reels in CapCut before exporting
5. **Adjust Gaps**: Modify `GAP_BETWEEN_REELS_SECONDS` if you want tighter spacing

## Support

For issues, questions, or contributions:
- Check the log output in the GUI for detailed error messages
- Ensure your API keys are valid
- Verify CapCut is properly installed

## License

This project is for personal and team use. Ensure you comply with:
- OpenAI's Terms of Service
- Anthropic's Terms of Service
- CapCut's Terms of Service

---

**Made with AI** - Powered by Whisper, GPT-4/Claude, and CapCut
