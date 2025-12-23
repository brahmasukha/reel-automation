"""
Online Transcription Module
Transcribes videos using AI APIs instead of local Whisper
"""
import os
import subprocess
import tempfile
import datetime
import config

# Conditional imports based on provider
if config.AI_PROVIDER == 'openai':
    from openai import OpenAI
elif config.AI_PROVIDER == 'anthropic':
    from anthropic import Anthropic
elif config.AI_PROVIDER == 'gemini':
    from google import genai


class OnlineTranscriber:
    """Transcribes videos using AI APIs"""

    def __init__(self, log_callback=None):
        """
        Initialize transcriber with configured AI provider

        Args:
            log_callback: Optional callback function for log messages
        """
        self.provider = config.AI_PROVIDER
        self.log_callback = log_callback

        if self.provider == 'openai':
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        elif self.provider == 'anthropic':
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
            self.model = config.ANTHROPIC_MODEL
        elif self.provider == 'gemini':
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)
            self.model = config.GEMINI_MODEL
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def log(self, message: str):
        """Log a message with encoding error handling"""
        try:
            if self.log_callback:
                self.log_callback(message)
            else:
                print(message)
        except UnicodeEncodeError:
            # If encoding fails, replace problematic characters
            safe_message = message.encode('utf-8', errors='replace').decode('utf-8')
            if self.log_callback:
                self.log_callback(safe_message)
            else:
                print(safe_message)

    def transcribe(self, video_path: str) -> str:
        """
        Transcribe video using online AI API

        Args:
            video_path: Path to the video file

        Returns:
            Formatted transcript string with timestamps
        """
        self.log(f"Using {self.provider.upper()} API for online transcription...")

        if self.provider == 'gemini':
            return self._transcribe_with_gemini(video_path)
        elif self.provider == 'openai':
            return self._transcribe_with_openai(video_path)
        elif self.provider == 'anthropic':
            return self._transcribe_with_anthropic(video_path)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _transcribe_with_gemini(self, video_path: str) -> str:
        """
        Transcribe video using Gemini API (supports video files directly)

        Args:
            video_path: Path to the video file

        Returns:
            Formatted transcript string
        """
        import time
        import shutil
        import tempfile

        self.log("Uploading video to Gemini API...")

        # Add a small delay to avoid hitting rate limits
        # Gemini free tier: 15 requests/minute
        time.sleep(config.GEMINI_API_DELAY_SECONDS)

        # Get the video file name (without path) for display (handle encoding issues)
        try:
            video_filename = os.path.basename(video_path)
            # Try to encode to ASCII to detect special characters
            video_filename.encode('ascii')
            self.log(f"File: {video_filename}")
            temp_video_path = None
        except (UnicodeEncodeError, UnicodeDecodeError):
            self.log("File name contains special characters, creating temporary copy...")
            # Create a temporary file with ASCII-safe name
            file_ext = os.path.splitext(video_path)[1]
            temp_fd, temp_video_path = tempfile.mkstemp(suffix=file_ext, prefix='temp_video_')
            os.close(temp_fd)
            shutil.copy2(video_path, temp_video_path)
            self.log(f"Created temporary file for upload")
            video_path = temp_video_path

        try:
            # Determine MIME type based on file extension
            import mimetypes
            file_ext = os.path.splitext(video_path)[1].lower()
            mime_type = mimetypes.guess_type(video_path)[0]

            # If mimetypes couldn't determine it, use common video types
            if not mime_type:
                mime_type_map = {
                    '.mp4': 'video/mp4',
                    '.mov': 'video/quicktime',
                    '.avi': 'video/x-msvideo',
                    '.mkv': 'video/x-matroska',
                    '.webm': 'video/webm',
                    '.flv': 'video/x-flv',
                    '.wmv': 'video/x-ms-wmv',
                    '.m4v': 'video/x-m4v',
                }
                mime_type = mime_type_map.get(file_ext, 'video/mp4')  # Default to mp4

            self.log(f"Uploading as {mime_type}...")

            # Upload video file to Gemini
            # Open the file in binary mode and pass the file object with mime_type
            with open(video_path, 'rb') as f:
                video_file = self.client.files.upload(file=f, config={'mime_type': mime_type})

            self.log(f"Video uploaded successfully!")

            # Wait for file to be processed
            while video_file.state == "PROCESSING":
                self.log("Waiting for Gemini to process video...")
                time.sleep(2)
                video_file = self.client.files.get(name=video_file.name)

            if video_file.state == "FAILED":
                raise Exception("Gemini failed to process video")

            self.log("Requesting transcription from Gemini...")

            # Request transcription
            prompt = """Please transcribe this video completely and accurately.

For the output format, provide timestamps in [START -> END] format followed by the spoken text.
Use HH:MM:SS format for timestamps.
Segment the transcription by sentences or natural speech breaks.

Example format:
[00:00:00 -> 00:00:05] First sentence spoken in the video.
[00:00:05 -> 00:00:12] Second sentence or phrase.
[00:00:12 -> 00:00:20] Third sentence continues here.

Please transcribe the entire video following this format."""

            # Add delay before transcription request to avoid rate limits
            time.sleep(config.GEMINI_API_DELAY_SECONDS)

            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[video_file, prompt],
                    config={
                        'temperature': 0.1,  # Low temperature for accurate transcription
                        'max_output_tokens': 8000,
                    }
                )
                transcript_text = response.text

            except Exception as e:
                error_msg = str(e)
                # Check if it's a quota error
                if 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower() or '429' in error_msg:
                    self.log("⚠️ Gemini API quota exceeded!")
                    self.log("The transcript has already been saved. You can:")
                    self.log("1. Wait a few minutes and run the pipeline again")
                    self.log("2. Or switch to TRANSCRIPTION_METHOD=local in .env")
                    raise Exception(f"Gemini API quota exceeded. Please wait and try again, or use local transcription. Error: {error_msg}")
                else:
                    raise

            # Delete the uploaded file to save quota
            self.client.files.delete(name=video_file.name)
            self.log("Transcription complete!")

            # Format the transcript
            formatted_transcript = self._format_transcript(transcript_text, video_path)

            return formatted_transcript

        finally:
            # Clean up temporary file if it was created
            if temp_video_path and os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                    self.log("Cleaned up temporary file")
                except Exception as e:
                    self.log(f"Warning: Could not delete temporary file: {e}")

    def _transcribe_with_openai(self, video_path: str) -> str:
        """
        Transcribe video using OpenAI Whisper API

        Args:
            video_path: Path to the video file

        Returns:
            Formatted transcript string
        """
        self.log("Extracting audio from video for OpenAI Whisper API...")

        # Extract audio to temporary file
        audio_path = self._extract_audio(video_path)

        try:
            self.log("Uploading audio to OpenAI Whisper API...")

            with open(audio_path, "rb") as audio_file:
                # Use Whisper API with verbose_json for timestamps
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]
                )

            self.log("Transcription complete!")

            # Format the response
            transcript_lines = []
            transcript_lines.append(f"Transcription for: {os.path.basename(video_path)}")
            transcript_lines.append("-" * 50)
            transcript_lines.append("")

            for segment in response.segments:
                start = str(datetime.timedelta(seconds=int(segment['start'])))
                end = str(datetime.timedelta(seconds=int(segment['end'])))
                text = segment['text'].strip()
                transcript_lines.append(f"[{start} -> {end}] {text}")

            return "\n".join(transcript_lines)

        finally:
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                self.log(f"Cleaned up temporary audio file")

    def _transcribe_with_anthropic(self, video_path: str) -> str:
        """
        Transcribe video using Claude API
        Note: Claude doesn't support direct video/audio, so we extract audio and send text prompt

        Args:
            video_path: Path to the video file

        Returns:
            Formatted transcript string
        """
        self.log("Note: Claude API doesn't support direct audio/video transcription.")
        self.log("Falling back to local Whisper for transcription...")

        # Import whisper for fallback
        import whisper

        # Add ffmpeg to PATH if it exists in current directory
        local_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg.exe')
        if os.path.exists(local_ffmpeg):
            os.environ["PATH"] = os.getcwd() + os.pathsep + os.environ.get("PATH", "")

        # Load Whisper model
        self.log(f"Loading Whisper model '{config.WHISPER_MODEL}'...")
        model = whisper.load_model(config.WHISPER_MODEL)

        self.log(f"Transcribing: {os.path.basename(video_path)}")
        result = model.transcribe(video_path)

        # Format transcript with timestamps
        transcript_lines = []
        transcript_lines.append(f"Transcription for: {os.path.basename(video_path)}")
        transcript_lines.append("-" * 50)
        transcript_lines.append("")

        for segment in result["segments"]:
            start = str(datetime.timedelta(seconds=int(segment["start"])))
            end = str(datetime.timedelta(seconds=int(segment["end"])))
            text = segment["text"].strip()
            transcript_lines.append(f"[{start} -> {end}] {text}")

        self.log("Transcription complete!")
        return "\n".join(transcript_lines)

    def _extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video file using ffmpeg

        Args:
            video_path: Path to the video file

        Returns:
            Path to extracted audio file
        """
        # Create temporary audio file
        temp_dir = tempfile.gettempdir()
        audio_filename = f"temp_audio_{os.getpid()}.mp3"
        audio_path = os.path.join(temp_dir, audio_filename)

        # Add ffmpeg to PATH if it exists in current directory
        local_ffmpeg = os.path.join(os.getcwd(), 'ffmpeg.exe')
        if os.path.exists(local_ffmpeg):
            os.environ["PATH"] = os.getcwd() + os.pathsep + os.environ.get("PATH", "")

        # Extract audio using ffmpeg
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',
            '-ar', '16000',  # 16kHz sample rate (optimal for Whisper)
            '-ac', '1',  # Mono
            '-b:a', '64k',  # Lower bitrate for smaller file
            '-y',  # Overwrite output file
            audio_path
        ]

        self.log(f"Extracting audio with ffmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"FFmpeg failed: {result.stderr}")

        self.log(f"Audio extracted to: {audio_path}")
        return audio_path

    def _format_transcript(self, transcript_text: str, video_path: str) -> str:
        """
        Format raw transcript text into standard format

        Args:
            transcript_text: Raw transcript from AI
            video_path: Path to video file

        Returns:
            Formatted transcript string
        """
        lines = []
        lines.append(f"Transcription for: {os.path.basename(video_path)}")
        lines.append("-" * 50)
        lines.append("")

        # Add the AI's transcript
        lines.append(transcript_text)

        return "\n".join(lines)
