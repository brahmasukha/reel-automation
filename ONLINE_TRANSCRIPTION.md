# Online Transcription Guide

This guide explains how to use **online AI transcription** instead of local Whisper for faster processing, especially on low-end machines without GPU.

## Why Use Online Transcription?

- **Faster**: No need to run Whisper locally on your machine
- **No GPU Required**: Transcription happens on AI provider's servers
- **Works on Low-End Machines**: Perfect for teams with basic laptops
- **Same Quality**: Uses powerful AI models (Gemini, GPT, Claude)

## How It Works

When online transcription is enabled:
1. Your video is uploaded to the selected AI provider (Gemini/OpenAI/Claude)
2. The AI transcribes the video/audio
3. The transcript is downloaded and saved locally
4. The rest of the pipeline continues normally (AI analysis → CapCut project)

## Configuration

### Step 1: Choose Your AI Provider

In your `.env` file, make sure you have set your AI provider:

```env
AI_PROVIDER=gemini  # Options: gemini, openai, anthropic
```

### Step 2: Enable Online Transcription

Add or change this line in your `.env` file:

```env
TRANSCRIPTION_METHOD=online  # Change from "local" to "online"
```

That's it! Your `.env` file should look like this:

```env
# AI Configuration
AI_PROVIDER=gemini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Transcription Configuration
TRANSCRIPTION_METHOD=online  # Use AI API for transcription
```

## AI Provider Support

### ✅ Gemini (Recommended - FREE)

**Best for**: Fast, free transcription with video support

- ✅ Supports video files directly (no audio extraction needed)
- ✅ Fast processing
- ✅ FREE tier available at [ai.google.dev](https://ai.google.dev)
- ✅ Recommended model: `gemini-2.0-flash-exp`

**Setup**:
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
TRANSCRIPTION_METHOD=online
```

### ✅ OpenAI (Paid)

**Best for**: High-quality transcription with Whisper API

- ✅ Uses OpenAI's Whisper API (same as local, but cloud-hosted)
- ✅ Extracts audio automatically and uploads to API
- ⚠️ Paid service (usage-based pricing)
- ✅ Excellent accuracy

**Setup**:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo-preview
TRANSCRIPTION_METHOD=online
```

**Note**: OpenAI charges per minute of audio transcribed using Whisper API.

### ⚠️ Claude/Anthropic (Fallback)

**Important**: Claude API does **not** support direct audio/video transcription.

- ❌ No native audio/video support
- ✅ Automatically falls back to local Whisper
- ✅ Still uses Claude for timestamp analysis

**What happens**: If you select `AI_PROVIDER=anthropic` with `TRANSCRIPTION_METHOD=online`, the system will:
1. Use local Whisper for transcription (same as before)
2. Use Claude API for analyzing the transcript and generating timestamps

## Switching Between Local and Online

You can easily switch between local and online transcription:

### Use Local Whisper (Slower, but free):
```env
TRANSCRIPTION_METHOD=local
WHISPER_MODEL=base  # or tiny for faster
```

### Use Online AI (Faster):
```env
TRANSCRIPTION_METHOD=online
```

## Performance Comparison

| Method | Speed | GPU Required | Cost | Best For |
|--------|-------|--------------|------|----------|
| **Local Whisper (tiny)** | Slow | No | Free | Quick tests, short videos |
| **Local Whisper (base)** | Very Slow | No | Free | High quality, offline |
| **Online Gemini** | ⚡ Fast | No | FREE* | Most users |
| **Online OpenAI** | ⚡ Fast | No | Paid | Professional use |

*Free tier with rate limits

## Troubleshooting

### Error: "Video upload failed"

**Problem**: Large video file exceeded API limits

**Solutions**:
- For Gemini: Videos up to ~2GB supported
- For OpenAI: Audio extraction done automatically (no size limit on video, extracted audio must be <25MB)
- Consider using local Whisper for very long videos (>1 hour)

### Error: "API quota exceeded"

**Problem**: You've hit the free tier limit

**Solutions**:
- Wait for quota to reset (usually daily)
- Upgrade to paid tier
- Switch to local transcription temporarily

### Slow Upload Speed

**Problem**: Video upload is taking too long

**Solutions**:
- Check your internet connection
- Use local transcription for large files
- Compress video before processing (lower resolution)

## Cost Estimation

### Gemini (FREE Tier)
- **Cost**: FREE up to rate limits
- **Limits**: 15 requests per minute, 1500 per day
- **For**: Personal projects, small teams

### OpenAI Whisper API (Paid)
- **Cost**: $0.006 per minute of audio
- **Example**: 30-minute video = $0.18
- **For**: Professional use, batch processing

### Claude/Anthropic
- **Transcription**: Not supported (uses local Whisper)
- **Timestamp Analysis**: Included in Claude API pricing

## Best Practices

1. **Start with Gemini**: Free and fast for most use cases
2. **Test with Short Videos**: Try online transcription with a 1-2 minute video first
3. **Monitor Costs**: If using OpenAI, track your API usage
4. **Keep `.env` Secure**: Never commit your API keys to git
5. **Have a Backup**: Keep local Whisper as fallback option

## Example Configurations

### Configuration 1: Free Setup (Recommended)
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your_key
GEMINI_MODEL=gemini-2.0-flash-exp
TRANSCRIPTION_METHOD=online
```

### Configuration 2: High Quality (Paid)
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...your_key
OPENAI_MODEL=gpt-4-turbo-preview
TRANSCRIPTION_METHOD=online
```

### Configuration 3: Offline/No Internet
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...your_key
TRANSCRIPTION_METHOD=local
WHISPER_MODEL=tiny  # Fastest local option
```

## Need Help?

- Check the [README.md](README.md) for general setup
- See [GEMINI_SETUP.md](GEMINI_SETUP.md) for Gemini API setup
- Review [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete installation guide
