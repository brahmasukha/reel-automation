# Gemini API Quota Management

## Understanding Gemini Free Tier Limits

Google Gemini's **FREE tier** has the following limits:

- **15 requests per minute (RPM)**
- **1,500 requests per day (RPD)**
- **1 million tokens per minute (TPM)**

## How Many API Calls Does This App Make?

For **each video** processed with `TRANSCRIPTION_METHOD=online`:

1. **Upload video file** (1 request)
2. **Request transcription** (1 request)
3. **Analyze transcript for timestamps** (1 request)

**Total: 3 requests per video**

### With Free Tier:
- **Per minute**: Up to 5 videos (15 requests / 3 = 5)
- **Per day**: Up to 500 videos (1,500 requests / 3 = 500)

## What Happens When You Hit the Quota?

### Error Message:
```
Gemini API quota exceeded. Please wait a few minutes and try again.
```

### What the App Does:
1. ✅ Your **transcript is already saved** (as `.transcript.txt`)
2. ⚠️ The **timestamp analysis** failed
3. 💡 You have **two options**:

## Solution 1: Wait and Retry (Recommended)

The rate limit resets every minute. Just wait and try again:

### If you hit the **per-minute limit** (15 RPM):
- **Wait**: 1-2 minutes
- **Then**: Run the pipeline again with the same video
- **Result**: It will use the saved transcript and continue

### If you hit the **daily limit** (1,500 RPD):
- **Wait**: Until the next day (resets at midnight PST)
- **Or**: Use Solution 2 below

## Solution 2: Use Local Whisper for Transcription

If you're hitting quota often, use Gemini only for timestamp analysis (cheaper on quota):

### Update your `.env`:
```env
# Use local Whisper for transcription
TRANSCRIPTION_METHOD=local
WHISPER_MODEL=tiny  # or base (faster on low-end machines)

# Still use Gemini for timestamp analysis
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
```

### Result:
- **Transcription**: Local Whisper (slow but FREE, no quota)
- **Timestamp Analysis**: Gemini (fast, uses only 1 request per video)
- **Per minute**: Up to 15 videos (15 requests / 1 = 15)
- **Per day**: Up to 1,500 videos

## Solution 3: Increase Rate Limit Delay

If you're processing multiple videos and hitting quota:

### Update your `.env`:
```env
# Increase delay between API calls (default: 5 seconds)
GEMINI_API_DELAY_SECONDS=10  # Wait 10 seconds between calls
```

### Trade-off:
- ✅ **Pros**: Less likely to hit quota
- ⚠️ **Cons**: Processing takes longer

### Calculation:
- **5 seconds delay**: ~45 seconds per video (3 calls × 5s = 15s + processing time)
- **10 seconds delay**: ~60 seconds per video (3 calls × 10s = 30s + processing time)

## Solution 4: Batch Processing Strategy

For teams processing many videos:

### Option A: Process During Off-Hours
- Schedule video processing during night/off-hours
- Spread 1,500 daily requests across 24 hours
- ~62 videos per hour maximum

### Option B: Round-Robin with Multiple API Keys
1. Get multiple FREE Gemini API keys (different Google accounts)
2. Rotate keys in `.env` when one hits quota
3. Each key gets separate quota limits

**Note**: This is within Google's terms of service for personal use.

### Option C: Upgrade to Paid Tier
- **Cost**: Pay-as-you-go pricing
- **Limits**: Much higher (millions of requests per day)
- **Best for**: Professional use, large teams

## Best Practices to Avoid Quota Issues

### 1. **Process One Video at a Time**
Don't queue multiple videos in rapid succession.

**Good**:
```
Video 1 → Wait → Video 2 → Wait → Video 3
```

**Bad**:
```
Video 1, Video 2, Video 3 (all at once)
```

### 2. **Use Local Whisper When Possible**
If your machine isn't too slow, use local Whisper:
```env
TRANSCRIPTION_METHOD=local
WHISPER_MODEL=base
```

### 3. **Increase Delay for Batch Jobs**
Processing 10+ videos? Increase the delay:
```env
GEMINI_API_DELAY_SECONDS=10
```

### 4. **Monitor Your Usage**
- Keep track of how many videos you process per day
- Free tier = 500 videos/day maximum
- If exceeding, consider paid tier

### 5. **Reuse Transcripts**
The app saves transcripts as `.transcript.txt` files.
- If transcription succeeded but timestamp analysis failed
- Just run the pipeline again
- It will reuse the saved transcript (no extra API calls)

## Quota Reset Times

### Per-Minute Limit (15 RPM):
- **Resets**: Every 60 seconds
- **Strategy**: Wait 1-2 minutes between bursts

### Daily Limit (1,500 RPD):
- **Resets**: Midnight Pacific Time (PST/PDT)
- **Strategy**: Plan daily processing volume

## Troubleshooting Common Quota Issues

### Issue 1: "Quota exceeded" immediately
**Cause**: You processed too many videos in the last minute

**Solution**:
```bash
# Wait 1-2 minutes, then try again
# Or increase delay:
GEMINI_API_DELAY_SECONDS=10
```

### Issue 2: "Quota exceeded" after ~500 videos
**Cause**: Hit daily limit (1,500 requests ÷ 3 = 500 videos)

**Solution**:
- Wait until tomorrow
- Or switch to local transcription for remaining videos
- Or upgrade to paid tier

### Issue 3: Transcript saved but timestamps failed
**Cause**: Quota hit during timestamp analysis

**Solution**:
```bash
# Just run the pipeline again with the same video
# It will reuse the saved transcript
python3 pipeline.py "your_video.mp4"
```

## Cost Comparison

| Method | Speed | Cost | Quota Limit |
|--------|-------|------|-------------|
| **Online (Gemini)** | ⚡ Fast (2-4 min) | FREE | 500 videos/day |
| **Local (Whisper tiny)** | Slow (15-20 min) | FREE | Unlimited |
| **Local (Whisper base)** | Very Slow (25-35 min) | FREE | Unlimited |
| **Hybrid (Local + Gemini)** | Slow (25-30 min) | FREE | 1,500 videos/day |
| **Paid Gemini Tier** | ⚡ Fast (2-4 min) | ~$0.25/video | Much higher |

## Recommended Configurations

### For Individual Use (1-10 videos/day):
```env
AI_PROVIDER=gemini
TRANSCRIPTION_METHOD=online
GEMINI_API_DELAY_SECONDS=5
```

### For Small Teams (10-50 videos/day):
```env
AI_PROVIDER=gemini
TRANSCRIPTION_METHOD=online
GEMINI_API_DELAY_SECONDS=10  # Increased delay
```

### For Heavy Use (50-500 videos/day):
```env
AI_PROVIDER=gemini
TRANSCRIPTION_METHOD=local  # Use local for transcription
WHISPER_MODEL=tiny
GEMINI_API_DELAY_SECONDS=5
```

### For Enterprise (500+ videos/day):
- Consider upgrading to **Gemini Paid Tier**
- Or use multiple FREE API keys (round-robin)
- Or use **OpenAI** (paid but reliable)

## Summary

✅ **Default delay of 5 seconds** should work for most users

✅ **Transcript is saved** even if quota exceeded during analysis

✅ **Just retry** after waiting 1-2 minutes

✅ **Use local Whisper** if you frequently hit quota

✅ **Increase delay to 10 seconds** for batch processing

✅ **Max FREE usage**: ~500 videos/day with online transcription

---

**Questions?** Check [ONLINE_TRANSCRIPTION.md](ONLINE_TRANSCRIPTION.md) for more details on online transcription.
