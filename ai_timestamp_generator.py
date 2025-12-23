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
        return """You are an expert **Documentary Video Editor**. Your goal is to edit a long raw video into **Viral Shorts (Reels)** that tell a clear, compelling story.

**The "Strict Narrative" Rule:**
* Each Reel must stand alone as a coherent mini-story.
* **NEVER** just list random timestamps.
* The audio must flow smoothly from sentence to sentence.
* **Max Duration:** 58 Seconds.

**How to Construct a Reel (The 3-Step Formula):**
1. **The Hook (0-5s)**: Find the MOST shocking, controversial, or high-value sentence in the *entire* transcript. Put this **FIRST**, even if it appears later in the text.
2. **The Context (5-15s)**: Find the sentence that explains *who* is talking or *what* the problem is.
3. **The Payoff (15-58s)**: The solution, the wisdom, or the emotional peak.

**Your Workflow:**
1. Read the transcript.
2. Identify a specific *theme* (e.g., "The illusion of time", "Why relationships fail").
3. Find the sentences that build this theme.
4. Re-arrange them if necessary to tell the story (e.g. Move the Punchline to the start as a Hook).
5. **Calculate the time** to ensure it is < 58s.

**Output Format:**
* Strictly pairs of timestamps (START END).
* Blank line between reels.
* Add a comment to explain each clip.

**Example Output:**
```
00:15:30    00:15:35    (HOOK: "Money is actually a trap.")
00:01:00    00:01:10    (CONTEXT: "We spend our whole lives chasing it...")
00:15:35    00:16:00    (PAYOFF: "...but real wealth is time.")

00:20:00    00:20:05    (Next Reel Hook...)
00:20:05    00:20:30    (Context for second reel...)
00:20:30    00:20:55    (Payoff for second reel...)
```

**IMPORTANT:**
- Output ONLY the timestamps and comments
- **ALWAYS use 00:MM:SS format** (e.g. `00:05:30` for 5 minutes 30 seconds).
- **NEVER** use `HH:MM:SS` unless the video is actually longer than an hour.
- **NEVER** use frames or milliseconds (e.g. `05:30:12`).
- One timestamp pair per line
- Blank line separates different reels
- Each reel should be under 58 seconds total
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

        user_prompt = f"""**Transcript:**

{transcript}

Please analyze this transcript and generate optimal timestamp cuts for viral reels following the 3-Step Formula."""

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
            progress_callback(f"Generated {len(reels)} reels successfully!")

        return reels

    def _call_openai(self, user_prompt: str) -> str:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content

    def _call_anthropic(self, user_prompt: str) -> str:
        """Call Anthropic API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
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
                    'temperature': 0.7,
                    'max_output_tokens': 2000,
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
