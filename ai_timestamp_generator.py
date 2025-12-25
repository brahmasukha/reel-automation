"""
AI Timestamp Generator Module
Generates optimal reel timestamps from video transcripts using AI
"""
import re
from typing import List, Tuple, Dict
import config

# Conditional imports based on provider
if config.AI_PROVIDER == 'openai':
    from openai import OpenAI
elif config.AI_PROVIDER == 'anthropic':
    from anthropic import Anthropic
elif config.AI_PROVIDER == 'gemini':
    from google import genai


class AITimestampGenerator:
    """Generates reel timestamps using AI analysis of video transcripts"""

    def __init__(self):
        """Initialize AI client based on configuration"""
        self.provider = config.AI_PROVIDER

        if self.provider == 'openai':
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.model = config.OPENAI_MODEL
        elif self.provider == 'anthropic':
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
            self.model = config.ANTHROPIC_MODEL
        elif self.provider == 'gemini':
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)
            self.model = config.GEMINI_MODEL
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def get_system_prompt(self) -> str:
        """Get the system prompt for AI timestamp generation"""
        return """You are a **PROFESSIONAL VIRAL VIDEO EDITOR** who has created thousands of viral reels with millions of views. Your specialty is extracting MAXIMUM VALUE from long-form content by creating MULTIPLE high-quality, engaging reels.

**CRITICAL MISSION:**
From ANY transcript, you MUST create AT LEAST:
- 1 reel per 3 minutes of content (20min video = minimum 6-7 reels)
- NEVER produce less than 3 reels (even for short videos)
- Focus on QUANTITY with QUALITY - every viral moment deserves its own reel

**VIRAL CONTENT DETECTION - What Makes a Great Hook:**
1. **Controversy/Shock**: Statements that challenge common beliefs
2. **Big Numbers/Stats**: "I made $100K in 30 days", "97% of people don't know this"
3. **Pain Points**: Problems your audience struggles with
4. **Curiosity Gaps**: "The secret nobody tells you about...", "What they don't want you to know..."
5. **Emotional Extremes**: Anger, excitement, fear, hope
6. **Personal Revelations**: "I used to...", "The moment I realized..."
7. **Contrarian Takes**: Going against conventional wisdom
8. **Story Hooks**: "This changed everything...", "Here's what happened..."

**PROFESSIONAL REEL CONSTRUCTION FORMULA:**
1. **HOOK (0-5s)**: The MOST VIRAL moment from ANYWHERE in the transcript
   - Must grab attention in first 2 seconds
   - Can be shocking stat, controversial statement, or emotional peak
   - Re-arrange chronology if needed - PUT THE BEST PART FIRST

2. **CONTEXT (5-15s)**: Quick setup so viewers understand
   - Who is this person? Why should I listen?
   - What's the problem/situation?
   - Keep it brief - viewers are impatient

3. **VALUE/PAYOFF (15-55s)**: The meat of the content
   - Solution, wisdom, story conclusion, or actionable insight
   - Build to an emotional or intellectual climax
   - End with a satisfying conclusion or call-to-action

**MULTI-THEME EXTRACTION STRATEGY:**
Scan the transcript for these theme categories and create separate reels for each:

1. **Tactical/How-To**: Specific strategies, step-by-step processes
2. **Mindset/Philosophy**: Beliefs, principles, worldview shifts
3. **Personal Stories**: Anecdotes, failures, successes, transformations
4. **Controversial Opinions**: Hot takes, unpopular opinions, bold claims
5. **Industry Secrets**: Insider knowledge, what "they" don't tell you
6. **Common Mistakes**: Errors to avoid, myths to debunk
7. **Quick Wins**: Fast results, simple hacks, immediate value
8. **Emotional Moments**: Inspirational, motivational, vulnerable shares

**REEL CONSTRUCTION RULES:**
✓ Each reel MUST be 25-58 seconds (optimal viral length)
✓ NEVER use consecutive timestamps - create narrative jumps when needed
✓ Prioritize complete thoughts over chronological order
✓ Look for natural conversational flow between clips
✓ Each reel must tell a COMPLETE mini-story
✓ Maximum 4-6 clip segments per reel (too many cuts = confusing)

**CRITICAL: CLEAN CUT POINTS - NO PARTIAL WORDS!**
⚠️ NEVER cut in the middle of a word or sentence
⚠️ ALWAYS start timestamps at the BEGINNING of a complete sentence
⚠️ ALWAYS end timestamps at the END of a complete sentence
⚠️ Look for natural pauses/breaths between sentences
⚠️ Better to include an extra second than to cut off words
⚠️ Listen for where the speaker naturally pauses - that's where you cut
⚠️ If transcript shows "...", that's a pause - safe to cut there
⚠️ If you see punctuation (. ! ?), that's typically a safe cut point

**OUTPUT FORMAT:**
```
00:15:30    00:15:35    (HOOK: "Money is actually a trap.")
00:01:00    00:01:10    (CONTEXT: "We spend our whole lives chasing it...")
00:15:35    00:16:00    (PAYOFF: "...but real wealth is time.")

00:20:00    00:20:05    (HOOK: "I failed 17 times before...")
00:20:05    00:20:30    (CONTEXT: Story of failures)
00:05:15    00:05:45    (PAYOFF: "That's when I learned the real secret.")
```

**CRITICAL REQUIREMENTS:**
- Output ONLY timestamps and comments (no explanatory text)
- **ALWAYS use 00:MM:SS format** (e.g. `00:05:30`)
- **NEVER** use HH:MM:SS unless video is 1+ hour
- **NEVER** use frames or milliseconds
- One timestamp pair per line
- Blank line separates reels
- Each reel should be 25-58 seconds total
- **CREATE AS MANY REELS AS POSSIBLE** - extract every viral moment!

**QUANTITY EXPECTATIONS:**
- 5-10 min video: Minimum 3-5 reels
- 10-20 min video: Minimum 5-10 reels
- 20-30 min video: Minimum 10-15 reels
- 30+ min video: Minimum 15-25 reels

Remember: More reels = more chances to go viral. NEVER be conservative - if there's a good moment, MAKE IT A REEL!
"""

    def generate_timestamps(self, transcript: str, progress_callback=None) -> List[List[Tuple[str, str, str]]]:
        """
        Generate reel timestamps from transcript using AI

        Args:
            transcript: The video transcript with timestamps
            progress_callback: Optional callback function for progress updates

        Returns:
            List of reels, where each reel is a list of (start, end, comment) tuples
        """
        if progress_callback:
            progress_callback("Sending transcript to AI for analysis...")

        # Calculate expected minimum reel count based on configuration
        video_duration_estimate = self._estimate_video_duration(transcript)

        # Apply generation mode multipliers
        mode_multipliers = {
            'conservative': 0.5,  # Half the reels, higher quality bar
            'balanced': 1.0,      # Default behavior
            'aggressive': 1.5     # 50% more reels, lower quality bar
        }
        multiplier = mode_multipliers.get(config.REEL_GENERATION_MODE, 1.0)

        min_reels = max(3, int(video_duration_estimate / 3 * config.MIN_REELS_PER_3MIN * multiplier))

        user_prompt = f"""**Transcript:**

{transcript}

**Your Task:**
Analyze this ~{video_duration_estimate:.0f} minute transcript and create AT LEAST {min_reels} high-quality viral reels.

**MANDATORY REQUIREMENTS:**
1. Extract EVERY viral moment - don't leave value on the table
2. Create separate reels for different themes (how-to, stories, opinions, etc.)
3. Use the HOOK-CONTEXT-PAYOFF formula for each reel
4. Re-arrange timestamps chronologically if it creates better hooks
5. Each reel must be 25-58 seconds and tell a complete story
6. Minimum {min_reels} reels - more is better!

**EXECUTION STEPS:**
1. First pass: Identify ALL potential hooks (shocking moments, stats, stories, opinions)
2. Second pass: Group related content into themed reels
3. Third pass: For each reel, structure using HOOK-CONTEXT-PAYOFF
4. Final pass: Verify each reel is 25-58 seconds and flows naturally

Generate the timestamp cuts now:"""

        # Call appropriate AI provider
        if self.provider == 'openai':
            response = self._call_openai(user_prompt)
        elif self.provider == 'anthropic':
            response = self._call_anthropic(user_prompt)
        elif self.provider == 'gemini':
            response = self._call_gemini(user_prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        if progress_callback:
            progress_callback("AI analysis complete. Parsing timestamps...")

        # Parse the response
        reels = self._parse_ai_response(response)

        if progress_callback:
            progress_callback(f"Parsed {len(reels)} reels. Validating quality...")

        # Validate and score reels
        validated_reels = self._validate_reels(reels, min_reels)

        if progress_callback:
            progress_callback(f"Generated {len(validated_reels)} high-quality reels successfully!")

        return validated_reels

    def _estimate_video_duration(self, transcript: str) -> float:
        """
        Estimate video duration in minutes from transcript

        Args:
            transcript: Video transcript with timestamps

        Returns:
            Estimated duration in minutes
        """
        # Try to find the last timestamp in the transcript
        import re

        # Pattern to match timestamps like [00:15:30], 00:15:30, or 15:30
        timestamp_pattern = r'(?:\[)?(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\])?'
        matches = list(re.finditer(timestamp_pattern, transcript))

        if matches:
            # Get the last timestamp
            last_match = matches[-1]
            hours = 0
            minutes = int(last_match.group(1))
            seconds = int(last_match.group(2))

            if last_match.group(3):  # Has seconds component
                # Format is HH:MM:SS or MM:SS
                if minutes > 59:  # Likely HH:MM:SS format
                    hours = minutes
                    minutes = seconds
                    seconds = int(last_match.group(3))

            total_minutes = hours * 60 + minutes + seconds / 60
            return max(1, total_minutes)  # At least 1 minute

        # Fallback: estimate based on word count (average speaking rate ~150 words/min)
        word_count = len(transcript.split())
        estimated_minutes = word_count / 150
        return max(1, estimated_minutes)

    def _call_openai(self, user_prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,  # Increased for more creative reel generation
            max_tokens=4000  # Increased to allow for more reels
        )
        return response.choices[0].message.content

    def _call_anthropic(self, user_prompt: str) -> str:
        """Call Anthropic API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,  # Increased to allow for more reels
            temperature=0.8,  # Increased for more creative reel generation
            system=self.get_system_prompt(),
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text

    def _call_gemini(self, user_prompt: str) -> str:
        """Call Google Gemini API with rate limiting"""
        import time

        # Add delay to avoid hitting rate limits (15 requests/minute)
        # Configurable via GEMINI_API_DELAY_SECONDS in .env
        time.sleep(config.GEMINI_API_DELAY_SECONDS)

        # Combine system prompt and user prompt for Gemini
        full_prompt = f"{self.get_system_prompt()}\n\n{user_prompt}"

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config={
                    'temperature': 0.8,  # Increased for more creative reel generation
                    'max_output_tokens': 4000,  # Increased to allow for more reels
                }
            )

            # Check if response has text
            if not hasattr(response, 'text') or response.text is None:
                # Response might be blocked or empty
                if hasattr(response, 'prompt_feedback'):
                    raise Exception(f"Gemini blocked the response. Reason: {response.prompt_feedback}")
                raise Exception("Gemini returned an empty response. The content might have been blocked by safety filters.")

            return response.text

        except Exception as e:
            error_msg = str(e)
            # Check if it's a quota error
            if 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower() or '429' in error_msg:
                raise Exception(f"Gemini API quota exceeded. Please wait a few minutes and try again. Error: {error_msg}")
            else:
                raise

    def _validate_reels(self, reels: List[List[Tuple[str, str, str]]], min_expected: int) -> List[List[Tuple[str, str, str]]]:
        """
        Validate and filter reels based on quality criteria

        Args:
            reels: List of parsed reels
            min_expected: Minimum expected number of reels

        Returns:
            Validated and filtered reels
        """
        validated = []

        for reel in reels:
            if not reel:
                continue

            # Calculate total reel duration
            total_duration = 0
            try:
                for start, end, _ in reel:
                    start_seconds = self._timestamp_to_seconds(start)
                    end_seconds = self._timestamp_to_seconds(end)
                    total_duration += (end_seconds - start_seconds)
            except:
                # Skip reels with invalid timestamps
                continue

            # Quality checks
            if total_duration < 15:  # Too short
                continue
            if total_duration > 60:  # Too long
                continue
            if len(reel) == 0:  # Empty reel
                continue
            if len(reel) > 8:  # Too many cuts
                continue

            validated.append(reel)

        # Log warning if we got fewer reels than expected
        if len(validated) < min_expected:
            print(f"Warning: Generated {len(validated)} reels, expected at least {min_expected}")
            print("Consider using a different AI model or adjusting the transcript.")

        return validated

    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """Convert timestamp string to seconds"""
        parts = timestamp.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        return 0

    def _parse_ai_response(self, response: str) -> List[List[Tuple[str, str, str]]]:
        """
        Parse AI response into structured timestamp data

        Returns:
            List of reels, where each reel is a list of (start, end, comment) tuples
        """
        # Safety check for None response
        if response is None:
            raise ValueError("AI returned None response. This should not happen - check _call_gemini error handling.")

        reels = []
        current_reel = []

        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines - they separate reels
            if not line:
                if current_reel:
                    reels.append(current_reel)
                    current_reel = []
                continue

            # Skip code block markers
            if line.startswith('```'):
                continue

            # Parse timestamp line: "HH:MM:SS HH:MM:SS (comment)"
            # Pattern: timestamp timestamp optional_comment
            pattern = r'(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)\s+(\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)\s*(?:\(([^)]+)\))?'
            match = re.search(pattern, line)

            if match:
                start = match.group(1)
                end = match.group(2)
                comment = match.group(3) if match.group(3) else ""
                current_reel.append((start, end, comment))

        # Add the last reel if exists
        if current_reel:
            reels.append(current_reel)

        return reels

    def format_for_cuts_file(self, reels: List[List[Tuple[str, str, str]]]) -> str:
        """
        Format reels data for cuts.txt file

        Args:
            reels: List of reels with timestamp tuples

        Returns:
            Formatted string ready for cuts.txt
        """
        output = []

        for reel_idx, reel in enumerate(reels, 1):
            output.append(f"# Reel {reel_idx}")
            for start, end, comment in reel:
                comment_str = f"    ({comment})" if comment else ""
                output.append(f"{start}    {end}{comment_str}")
            output.append("")  # Blank line between reels

        return "\n".join(output)


def test_timestamp_generator():
    """Test function for AI timestamp generator"""
    sample_transcript = """[00:00:00 -> 00:00:05] Hello everyone, today I want to talk about time management.
[00:00:05 -> 00:00:15] Most people think they need more time, but that's not the real problem.
[00:00:15 -> 00:00:25] The real problem is how we use the time we already have.
[00:00:25 -> 00:00:35] I used to work 80 hours a week and accomplish nothing.
[00:00:35 -> 00:00:45] Now I work 40 hours and get twice as much done.
[00:00:45 -> 00:00:55] The secret? It's not about working harder, it's about working smarter."""

    generator = AITimestampGenerator()
    reels = generator.generate_timestamps(sample_transcript)

    print("Generated Reels:")
    print(generator.format_for_cuts_file(reels))


if __name__ == "__main__":
    test_timestamp_generator()
