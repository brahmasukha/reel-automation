# 🎬 START HERE - Reel Automation v2.0

## Welcome to Your Automated Reel Generation System!

This tool transforms long-form videos into viral short-form reels **automatically** using AI.

---

## 🚀 Quick Start (3 Steps)

### 1️⃣ Setup (First Time Only - 10 minutes)

**Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration file
copy .env.example .env

# Edit .env and add your API key (see below)
```

**WSL / Linux / Mac:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# Create configuration file
cp .env.example .env

# Edit .env and add your API key (see below)
```

### 2️⃣ Get API Key (2 minutes)

Choose **ONE**:

**Option A: Google Gemini (FREE!)** 👈 **RECOMMENDED**
1. Go to [ai.google.dev](https://ai.google.dev)
2. Click "Get API key in Google AI Studio"
3. Sign in with Google account
4. Click "Create API key"
5. Copy the key (starts with `AIza...`)

**Option B: OpenAI (GPT-4)** (Paid - ~$0.02-0.05/video)
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create account / Sign in
3. Go to API Keys
4. Create new key
5. Copy the key (starts with `sk-...`)

**Option C: Anthropic (Claude)** (Paid - ~$0.02-0.05/video)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create account / Sign in
3. Go to API Keys
4. Create new key
5. Copy the key (starts with `sk-ant-...`)

**Add to `.env` file:**
```env
# For Gemini (FREE - Recommended)
AI_PROVIDER=gemini
GEMINI_API_KEY=AIza...your-key-here

# OR for OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here

# OR for Anthropic
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

📘 **Detailed Gemini setup**: See [GEMINI_SETUP.md](GEMINI_SETUP.md)

**⚡ NEW: Fast Online Transcription (Recommended for Low-End Machines)**

If Whisper is too slow on your machine, enable online transcription:

```env
# Add this to your .env file
TRANSCRIPTION_METHOD=online  # Much faster than local Whisper!
```

This uses your AI provider's API for transcription:
- ✅ **Gemini**: FREE, supports video directly
- ✅ **OpenAI**: Uses Whisper API (paid)
- ✅ **Claude**: Falls back to local (no audio support)

📖 **Full guide**: See [ONLINE_TRANSCRIPTION.md](ONLINE_TRANSCRIPTION.md)

### 3️⃣ Run the Application

**Windows - Double-click**: `Launch_Reel_Automation.bat`

**Or via command line:**

**Windows:**
```cmd
venv\Scripts\activate
python gui.py
```

**WSL / Linux / Mac:**
```bash
source venv/bin/activate
python3 gui.py
```

---

## 📖 What You'll See

```
┌─────────────────────────────────────────┐
│      Reel Automation                    │
│  Turn long videos into viral reels      │
├─────────────────────────────────────────┤
│                                         │
│  Select Video: [Browse...              ]│
│                                         │
│  ☑ Open CapCut when complete            │
│                                         │
│  Progress: [████████░░░░░] 75%          │
│  Status: Creating CapCut project...     │
│                                         │
│  Log:                                   │
│  ┌─────────────────────────────────┐   │
│  │ Transcribing video...           │   │
│  │ AI analysis complete!           │   │
│  │ Generated 5 reels successfully! │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Process Video]  [Cancel] [Clear Log] │
└─────────────────────────────────────────┘
```

---

## 🎯 How to Use

1. Click **Browse** → Select your video (MP4, MOV, etc.)
2. Click **Process Video**
3. ☕ Wait 5-10 minutes (depends on video length)
4. ✅ CapCut opens with your reels ready to export!

---

## 📁 Important Files

### 📘 Read These First

| File | Description | When to Read |
|------|-------------|--------------|
| **START_HERE.md** | This file! Quick start guide | Right now! |
| **SETUP_GUIDE.md** | Detailed setup instructions | Having setup issues? |
| **QUICK_REFERENCE.md** | Command cheat sheet | Daily usage |
| **README.md** | Full documentation | Want to learn more |

### 🔧 Configuration Files

| File | Purpose | Action Required |
|------|---------|-----------------|
| `.env.example` | Configuration template | DON'T EDIT |
| `.env` | Your configuration | ✅ CREATE & EDIT THIS |
| `requirements.txt` | Python dependencies | Already provided |

### 💻 Application Files

| File | What It Does |
|------|--------------|
| `gui.py` | Main application (GUI) |
| `pipeline.py` | Automation engine |
| `config.py` | Configuration loader |
| `ai_timestamp_generator.py` | AI integration |
| `capcut_project_generator.py` | Project creator |

### 🚀 Launchers

| File | Platform | How to Use |
|------|----------|------------|
| `Launch_Reel_Automation.bat` | Windows | Double-click |

### 📚 Advanced Documentation

| File | For Who |
|------|---------|
| `ARCHITECTURE.md` | Developers wanting technical details |
| `PROJECT_SUMMARY.md` | Understanding what changed |

---

## ⚙️ Configuration Options

Edit `.env` to customize:

```env
# === REQUIRED: Choose AI Provider ===
AI_PROVIDER=gemini              # Options: "gemini" (FREE!), "openai", or "anthropic"

# === REQUIRED: Add Your API Key ===
GEMINI_API_KEY=AIza...          # Get FREE from ai.google.dev
# OR
OPENAI_API_KEY=sk-...           # Get from platform.openai.com
# OR
ANTHROPIC_API_KEY=sk-ant-...    # Get from console.anthropic.com

# === NEW: Transcription Method ===
TRANSCRIPTION_METHOD=online     # "online" (FASTER!) or "local" (slower)

# === OPTIONAL: Fine-Tuning ===
WHISPER_MODEL=base              # Speed: tiny, base, small, medium, large (only for local)
GAP_BETWEEN_REELS_SECONDS=10    # Gap between reels on timeline
MAX_REEL_DURATION=58            # Maximum reel length in seconds
```

---

## 🎬 The Workflow (Fully Automated)

```
YOU:                    Select video → Click "Process"
                                ↓
WHISPER AI:             Transcribes with timestamps
                                ↓
GPT-4/CLAUDE:           Analyzes content, finds viral segments
                                ↓
AUTO GENERATOR:         Creates CapCut project with cuts
                                ↓
CAPCUT:                 Opens with reels ready!
                                ↓
YOU:                    Review → Export → Post! 🎉
```

**Time**: 5-10 minutes (all automatic)
**Cost**: ~$0.02-$0.05 per video

---

## 🆘 Troubleshooting

### "OPENAI_API_KEY is required"
- Did you create `.env` file? (copy from `.env.example`)
- Did you add your actual API key?
- No spaces around `=` sign

### "Virtual environment not found"
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### "FFmpeg not found"
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Place `ffmpeg.exe` in this folder
- Or add to system PATH

### "CapCut executable not found"
- Install CapCut from [capcut.com](https://www.capcut.com)
- Or: Project still created, open CapCut manually

### GUI won't start
```bash
# Make sure virtual env is activated
venv\Scripts\activate
python gui.py
```

---

## 💡 Tips for Best Results

✅ **Clear Audio**: Whisper works best with clean speech
✅ **10-60 Min Videos**: Optimal length for reel generation
✅ **Talking Head**: Best for interviews, podcasts, vlogs
✅ **Review First**: Always check reels before posting
✅ **Start with `base` model**: Good balance of speed/quality

---

## 📊 What to Expect

### Processing Time (30-min video)

**Local Whisper (slower):**
- **Transcription**: 15-30 minutes (no GPU)
- **AI Analysis**: 10-30 seconds
- **Project Creation**: < 5 seconds
- **Total**: ~15-30 minutes

**Online AI (FASTER!):**
- **Transcription**: 1-3 minutes ⚡
- **AI Analysis**: 10-30 seconds
- **Project Creation**: < 5 seconds
- **Total**: ~2-4 minutes ⚡

### Output
- **Number of Reels**: 3-8 (depends on content)
- **Reel Length**: 15-58 seconds each
- **Format**: Vertical (9:16)
- **Quality**: Original video quality

### Cost Per Video

**Local Transcription:**
- **Whisper**: FREE (runs locally)
- **AI Analysis**: ~$0.02-$0.05 (or FREE with Gemini)
- **Total**: FREE to $0.05 per video

**Online Transcription:**
- **Gemini**: FREE (with limits) ⚡
- **OpenAI Whisper API**: ~$0.18 for 30-min video
- **AI Analysis**: ~$0.02-$0.05 (or FREE with Gemini)
- **Total**: FREE to $0.25 per video

---

## 🎓 Next Steps

### After Your First Video

1. ✅ Review generated reels in CapCut
2. ✅ Adjust settings in `.env` if needed
3. ✅ Process more videos
4. ✅ Share with your team!

### Share with Team

1. Send them this folder (or git repo)
2. Point them to `SETUP_GUIDE.md`
3. Each person creates their own `.env`
4. Start creating reels!

### Go Further

- Read `README.md` for advanced features
- Check `ARCHITECTURE.md` to understand how it works
- Customize AI prompts (see `ai_timestamp_generator.py`)

---

## 🤝 Team Rollout

### For Team Members

**Step 1**: Get access to this folder
**Step 2**: Follow "Quick Start" above
**Step 3**: Get API key from team lead (or create your own)
**Step 4**: Create `.env` with your/shared API key
**Step 5**: Start processing videos!

### For Team Lead

**Step 1**: Decide on API key strategy:
- Option A: Shared key (easier, shared cost tracking)
- Option B: Individual keys (cost per person)

**Step 2**: Share this folder with team

**Step 3**: Host setup session (15 minutes):
- Walk through setup
- Everyone processes a test video
- Answer questions

**Step 4**: Create guidelines:
- Video naming conventions
- Where to save projects
- Quality review process

---

## 📈 Future Enhancements

The system is designed for growth:

- ✨ **Batch Processing**: Process multiple videos at once
- ✨ **Custom Prompts**: Different narrative formulas
- ✨ **Auto-Export**: Export reels automatically
- ✨ **Social Upload**: Auto-post to platforms
- ✨ **Analytics**: Track which reels perform best

---

## 🎯 Success Checklist

Before your first video, make sure:

- [ ] Python 3.9+ installed
- [ ] Virtual environment created (`venv` folder exists)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created (copied from `.env.example`)
- [ ] API key added to `.env`
- [ ] CapCut installed on your computer
- [ ] FFmpeg available (in PATH or local folder)

Then:

- [ ] Launch application (`Launch_Reel_Automation.bat`)
- [ ] See GUI without errors
- [ ] Process a test video (10-20 min video works well)
- [ ] Review reels in CapCut
- [ ] Export and celebrate! 🎉

---

## 📞 Help Resources

| Issue | Solution |
|-------|----------|
| Setup problems | See `SETUP_GUIDE.md` |
| Slow transcription | See `ONLINE_TRANSCRIPTION.md` |
| Gemini quota exceeded | See `GEMINI_QUOTA_MANAGEMENT.md` |
| How does it work? | See `README.md` |
| Technical questions | See `ARCHITECTURE.md` |
| Quick commands | See `QUICK_REFERENCE.md` |
| What changed? | See `PROJECT_SUMMARY.md` |

---

## 🎉 You're Ready!

1. Complete the setup (10 minutes)
2. Process your first video (5 minutes)
3. Review the reels in CapCut
4. Export and share!

**Questions?** Check the documentation files above!

**Ready?** Run `Launch_Reel_Automation.bat` to begin! 🚀

---

Made with ❤️ using Python, Whisper AI, GPT-4/Claude, and CapCut
