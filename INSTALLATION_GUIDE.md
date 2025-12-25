# Installation Guide - Reel Automation

## For AMD Radeon Graphics Systems

If you're setting up this project on a laptop with AMD Radeon graphics, follow these steps:

### Step 1: Upgrade pip and setuptools

First, upgrade pip and setuptools to the latest versions:

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Step 2: Install PyTorch (for Whisper)

Install PyTorch CPU version (AMD GPU support requires ROCm which is complex):

```bash
pip install torch torchvision torchaudio
```

### Step 3: Install openai-whisper separately

```bash
pip install openai-whisper
```

If this fails with network errors, try:
```bash
pip install --no-cache-dir openai-whisper
```

Or specify a timeout:
```bash
pip install --default-timeout=100 openai-whisper
```

### Step 4: Install remaining dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Verify installation

```bash
python -c "import whisper; print('Whisper installed successfully!')"
```

---

## Alternative: Use Online Transcription (Recommended for AMD systems)

If local Whisper installation continues to fail, you can use online AI transcription instead:

### 1. Update your `.env` file:

```env
# Use online transcription instead of local Whisper
TRANSCRIPTION_METHOD=online

# Choose your AI provider (gemini, openai, or claude)
AI_PROVIDER=gemini

# Add your API key
GEMINI_API_KEY=your_api_key_here
# OR
OPENAI_API_KEY=your_api_key_here
# OR
CLAUDE_API_KEY=your_api_key_here
```

### 2. Install only the required dependencies:

```bash
pip install -r requirements.txt
```

This will skip the Whisper installation entirely and use cloud-based transcription, which:
- Works on any hardware (no GPU needed)
- Is often faster than local processing
- Produces high-quality transcripts
- Doesn't require large model downloads

---

## Troubleshooting Network Errors

If you see "Connection aborted" or "forcibly closed" errors:

### Option 1: Use a different PyPI mirror

```bash
pip install --index-url https://pypi.org/simple openai-whisper
```

### Option 2: Increase timeout

```bash
pip install --default-timeout=100 openai-whisper
```

### Option 3: Install from GitHub directly

```bash
pip install git+https://github.com/openai/whisper.git
```

### Option 4: Check your antivirus/firewall

Windows Defender or corporate firewalls might be blocking pip connections. Try:
- Temporarily disable antivirus
- Use a VPN
- Connect to a different network

---

## Quick Start After Installation

1. Copy `.env.example` to `.env`
2. Configure your settings in `.env`
3. Run the GUI: `python gui.py`

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)
